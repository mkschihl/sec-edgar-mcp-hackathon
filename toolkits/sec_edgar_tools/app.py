"""HTTP entrypoint for remote (Code Engine) deployment.

When the PORT environment variable is set (injected by Code Engine / any
container host), this module runs the FastMCP server over streamable-HTTP
on 0.0.0.0:PORT.  The stdio path used by the Orchestrate local toolkit
(server.py __main__) is unchanged.
"""

from __future__ import annotations

import os

from server import mcp  # re-use the fully configured FastMCP instance

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
    )
