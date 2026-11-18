import asyncio, json, sys, difflib
sys.path.insert(0, "toolkits/sec_edgar_tools")
from fastmcp import Client
from server import mcp

URL = "https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp"

async def tools(target):
    async with Client(target) as c:
        return {t.name: (t.description or "", json.dumps(t.input_schema, indent=1, sort_keys=True))
                for t in await c.list_tools()}

async def main():
    local, live = await tools(mcp), await tools(URL)
    for name in sorted(local):
        if local[name] != live.get(name):
            print(f"\n######## {name}")
            for part, label in ((0, "DESCRIPTION"), (1, "SCHEMA")):
                d = list(difflib.unified_diff(live[name][part].splitlines(),
                                              local[name][part].splitlines(),
                                              "LIVE", "LOCAL", lineterm=""))
                if d:
                    print(f"--- {label} ---")
                    print("\n".join(d))

asyncio.run(main())