# compare_live.py: run from repo root with venv/bin/python
import asyncio, json, sys
sys.path.insert(0, "toolkits/sec_edgar_tools")
from fastmcp import Client
from server import mcp

URL = "https://sec-edgar-tools-mks.2flzosib5d1z.ca-tor.codeengine.appdomain.cloud/mcp"
PROBE = ("sec_edgar_get_company_fact",
         {"identifier": "AAPL", "taxonomy": "us-gaap", "concept": "NetIncomeLoss", "limit": 5})

async def snapshot(target):
    async with Client(target) as c:
        tools = {t.name: [t.description, json.dumps(t.inputSchema, sort_keys=True)]
                 for t in await c.list_tools()}
        r = await c.call_tool(*PROBE)
        blocks = getattr(r, "content", r)
        return tools, json.loads(blocks[0].text)

async def main():
    (lt, lr), (rt, rr) = await snapshot(mcp), await snapshot(URL)
    for name in sorted(set(lt) | set(rt)):
        same = lt.get(name) == rt.get(name)
        print(f"{'SAME' if same else 'DIFF'}  {name}")
    print("probe output", "SAME" if lr == rr else "DIFF")
    if lr != rr:
        print(json.dumps({"local": lr, "live": rr}, indent=2)[:4000])

asyncio.run(main())