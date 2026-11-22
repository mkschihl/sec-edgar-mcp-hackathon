"""SEC EDGAR agent wrapper for Phoenix evaluation.

Connects to the live Code Engine MCP endpoint over streamable-HTTP transport,
instruments LangChain traces to Phoenix, and exposes a task factory compatible
with phoenix.client.experiments.run_experiment().

The MCP tools are fetched from the live Code Engine server and wrapped as
LangChain StructuredTools using the MCP Python SDK directly (no langchain-mcp-adapters
required).

Usage (smoke test):
    cd eval/phoenix
    python agent.py

Environment variables (from .env at repo root):
    WATSONX_URL        — watsonx.ai regional endpoint, e.g. https://ca-tor.ml.cloud.ibm.com
    WATSONX_API_KEY    — IBM Cloud API key (SDK exchanges for IAM token automatically)
    WATSONX_PROJECT_ID — watsonx.ai project ID (project > Manage > General > Details)
    AGENT_MODEL        — watsonx.ai model ID for the agent-under-test (must support tool calling)
                         default: meta-llama/llama-3-3-70b-instruct
    MCP_ENDPOINT       — Code Engine /mcp URL (default: https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp)
    PHOENIX_ENDPOINT   — Phoenix OTLP endpoint (default: http://localhost:4317)
    PHOENIX_PROJECT    — Phoenix project name (default: sec-edgar-eval)
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_MCP_ENDPOINT = (
    "https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp"
)
DEFAULT_PHOENIX_OTLP = "http://localhost:4317"
DEFAULT_PROJECT = "sec-edgar-eval"


# ---------------------------------------------------------------------------
# MCP → LangChain tool conversion
# ---------------------------------------------------------------------------

def _build_json_schema(mcp_tool) -> dict:
    """Return a JSON Schema dict for a MCP tool's input_schema."""
    schema = mcp_tool.input_schema or {}
    # Ensure it has the JSON Schema type wrapper
    if "type" not in schema:
        schema = {"type": "object", "properties": schema}
    return schema


def _make_langchain_tool(mcp_tool, session):
    """Wrap a single MCP tool as a LangChain StructuredTool."""
    from langchain_core.tools import StructuredTool

    tool_name: str = mcp_tool.name
    description: str = mcp_tool.description or ""
    input_schema = _build_json_schema(mcp_tool)

    async def _acall(**kwargs: Any) -> str:
        result = await session.call_tool(tool_name, arguments=kwargs)
        # result.content is a list of content blocks; join text blocks
        parts = []
        for block in (result.content or []):
            if hasattr(block, "text"):
                parts.append(block.text)
            else:
                parts.append(str(block))
        return "\n".join(parts) if parts else "(no output)"

    def _call(**kwargs: Any) -> str:
        return asyncio.run(_acall(**kwargs))

    # Build args_schema from the MCP tool's JSON Schema
    try:
        from pydantic import create_model
        from pydantic.fields import FieldInfo

        props = input_schema.get("properties", {})
        required_fields = set(input_schema.get("required", []))
        field_defs: dict[str, Any] = {}
        for field_name, field_schema in props.items():
            py_type: type = str  # default to str for simplicity
            fs_type = field_schema.get("type", "string")
            if fs_type == "integer":
                py_type = int
            elif fs_type == "number":
                py_type = float
            elif fs_type == "boolean":
                py_type = bool
            elif fs_type == "array":
                py_type = list
            field_description = field_schema.get("description", "")
            if field_name in required_fields:
                field_defs[field_name] = (py_type, FieldInfo(description=field_description))
            else:
                default = field_schema.get("default", None)
                field_defs[field_name] = (
                    py_type,
                    FieldInfo(default=default, description=field_description),
                )
        DynamicSchema = create_model(f"{tool_name}_schema", **field_defs)
    except Exception:
        DynamicSchema = None  # type: ignore

    return StructuredTool(
        name=tool_name,
        description=description,
        func=_call,
        coroutine=_acall,
        args_schema=DynamicSchema,
    )


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------


class SECEdgarAgent:
    """LangChain ReAct agent connected to the SEC EDGAR MCP server via HTTP.

    Supports Phoenix OTLP tracing and Phoenix experiment task factories.
    """

    # Class-level flag: instrument once per process regardless of how many
    # SECEdgarAgent instances are created (re-instrumenting raises errors).
    _class_instrumented: bool = False

    def __init__(
        self,
        system_prompt_version: str = "v1",
        mcp_endpoint: str | None = None,
        phoenix_otlp_endpoint: str | None = None,
        project_name: str | None = None,
    ) -> None:
        self.system_prompt_version = system_prompt_version
        self.mcp_endpoint = mcp_endpoint or os.getenv("MCP_ENDPOINT", DEFAULT_MCP_ENDPOINT)
        self.phoenix_otlp_endpoint = phoenix_otlp_endpoint or os.getenv(
            "PHOENIX_ENDPOINT", DEFAULT_PHOENIX_OTLP
        )
        self.project_name = project_name or os.getenv("PHOENIX_PROJECT", DEFAULT_PROJECT)
        self._agent = None
        self._initialized = False
        self._http_transport = None
        self._instrumented = False

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Set up Phoenix instrumentation, MCP client, and LangChain agent."""
        if self._initialized:
            return

        # Phoenix OTLP tracing — instrument once per process, not once per instance
        if not SECEdgarAgent._class_instrumented:
            from openinference.instrumentation.langchain import LangChainInstrumentor
            from phoenix.otel import register

            tracer_provider = register(
                project_name=self.project_name,
                endpoint=self.phoenix_otlp_endpoint,
            )
            LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
            SECEdgarAgent._class_instrumented = True

        # MCP session over streamable-HTTP
        from mcp.client.streamable_http import streamable_http_client
        from mcp import ClientSession

        self._http_transport = streamable_http_client(self.mcp_endpoint)
        read, write = await self._http_transport.__aenter__()
        self._session = ClientSession(read, write)
        await self._session.__aenter__()
        await self._session.initialize()

        # Fetch available tools and wrap as LangChain tools
        tools_result = await self._session.list_tools()
        lc_tools = [_make_langchain_tool(t, self._session) for t in tools_result.tools]

        # Build the ReAct agent
        from langchain_ibm import ChatWatsonx
        from langgraph.prebuilt import create_react_agent

        llm = ChatWatsonx(
            model_id=os.getenv("AGENT_MODEL", "meta-llama/llama-3-3-70b-instruct"),
            temperature=0,
            # WATSONX_URL / WATSONX_API_KEY / WATSONX_PROJECT_ID are read from env
        )

        system_prompt = self._load_system_prompt()
        self._agent = create_react_agent(
            model=llm,
            tools=lc_tools,
            prompt=system_prompt,
            checkpointer=None,
        )
        # Increase recursion limit for multi-step chains (default is 10)
        self._recursion_limit = 15
        self._initialized = True

    def _load_system_prompt(self) -> str:
        """Load the system prompt for the requested version.

        Supports:
          - "v1", "v2", ... → prompts/system_prompt_{version}.txt
          - "yaml"          → reads instructions: from agents/sec_edgar_agent.yaml
        """
        if self.system_prompt_version == "yaml":
            return self._load_yaml_prompt()
        prompt_file = PROMPTS_DIR / f"system_prompt_{self.system_prompt_version}.txt"
        if not prompt_file.exists():
            available = [p.stem for p in PROMPTS_DIR.glob("system_prompt_*.txt")]
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}. "
                f"Available versions: {available}"
            )
        return prompt_file.read_text()

    def _load_yaml_prompt(self) -> str:
        """Extract the instructions: field from agents/sec_edgar_agent.yaml."""
        import yaml  # bundled in venv

        agent_yaml = REPO_ROOT / "agents" / "sec_edgar_agent.yaml"
        if not agent_yaml.exists():
            raise FileNotFoundError(
                f"Agent YAML not found: {agent_yaml}. "
                "Cannot use system_prompt_version='yaml'."
            )
        data = yaml.safe_load(agent_yaml.read_text())
        # Try top-level `instructions` first (ADK flat schema), then nested `spec.instructions`
        instructions = data.get("instructions") or data.get("spec", {}).get("instructions", "")
        if not instructions:
            raise ValueError(
                f"No 'instructions' key found in {agent_yaml}. "
                "Check the YAML structure — expected a top-level 'instructions:' field."
            )
        return instructions

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    async def run(self, query: str) -> str:
        """Run the agent on a single query and return the final text response."""
        await self.initialize()
        result = await self._agent.ainvoke(
            {"messages": [("user", query)]},
            config={"recursion_limit": self._recursion_limit},
        )
        messages = result.get("messages", [])
        # The last message is the final assistant response
        for msg in reversed(messages):
            content = getattr(msg, "content", None)
            if content and isinstance(content, str) and content.strip():
                return content.strip()
        return str(result)

    # ------------------------------------------------------------------
    # Phoenix experiment task factory
    # ------------------------------------------------------------------

    def create_experiment_task(self) -> Callable:
        """Return a synchronous task function for phoenix.client.experiments.run_experiment().

        Phoenix expects task(example) -> dict with at least {"result": str}.
        Uses a dedicated event loop per call so multiple questions don't conflict.
        """

        def task(example) -> dict:
            query = example.input.get("query", "")
            loop = asyncio.new_event_loop()
            agent = SECEdgarAgent(
                system_prompt_version=self.system_prompt_version,
                mcp_endpoint=self.mcp_endpoint,
                phoenix_otlp_endpoint=self.phoenix_otlp_endpoint,
                project_name=self.project_name,
            )
            try:
                result = loop.run_until_complete(agent.run(query))
            finally:
                # Always close MCP session cleanly to avoid resource leaks
                try:
                    loop.run_until_complete(agent.close())
                except Exception:
                    pass
                loop.close()
            return {"result": result}

        return task

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(self) -> None:
        try:
            if hasattr(self, "_session"):
                await self._session.__aexit__(None, None, None)
            if self._http_transport is not None:
                await self._http_transport.__aexit__(None, None, None)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

async def _smoke_test() -> None:
    print("Initializing SECEdgarAgent (smoke test)...")
    agent = SECEdgarAgent(system_prompt_version="v1")

    # Skip Phoenix tracing for smoke test if no endpoint is configured
    # by monkey-patching register to a no-op
    import phoenix.otel as px_otel
    from opentelemetry.sdk.trace import TracerProvider

    _orig_register = px_otel.register

    def _noop_register(*args, **kwargs):
        print("  [smoke test] Phoenix OTLP tracing skipped (no server running).")
        return TracerProvider()

    px_otel.register = _noop_register

    try:
        await agent.initialize()
        print(f"  MCP endpoint : {agent.mcp_endpoint}")
        print(f"  Tools loaded : {len(agent._agent.tools) if hasattr(agent._agent, 'tools') else 'n/a'}")
        print()

        test_query = "What is the SIC code for Apple (AAPL)?"
        print(f"Query: {test_query}")
        print("-" * 60)
        response = await agent.run(test_query)
        print(f"Response:\n{response}")
    finally:
        px_otel.register = _orig_register
        await agent.close()


def main() -> None:
    asyncio.run(_smoke_test())


if __name__ == "__main__":
    main()
