"""Public ASGI entry point for the observer UI, HTTP API, and remote MCP.

Run locally with::

    python -m nowhere.remote

The Streamable HTTP MCP endpoint is available at ``/mcp``.  The existing
observer UI and JSON endpoints remain available from the same process.
"""

from __future__ import annotations

import os
import threading

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from nowhere.server import mcp
from nowhere.web import app as observer_app


async def healthz(_request) -> JSONResponse:
    """Small deployment health check that does not mutate journey state."""
    return JSONResponse({"ok": True, "service": "nowhere"})


# Stateless MCP transport is a better fit for hosted services: ChatGPT may send
# consecutive protocol requests through different HTTP connections, while the
# journey itself remains continuous in Nowhere's persisted WorldState.
mcp_app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",
    stateless_http=True,
    json_response=True,
)

# FastMCP's lifespan must be passed to the parent app so its Streamable HTTP
# session manager is started.  Reuse the observer routes instead of mounting a
# second Starlette app, which also keeps the static UI at the original paths.
app = Starlette(
    routes=[
        Route("/healthz", healthz),
        *mcp_app.routes,
        *observer_app.routes,
    ],
    lifespan=mcp_app.lifespan,
)


def _preload_knowledge() -> None:
    """Warm the optional knowledge index without delaying server startup."""
    try:
        from nowhere.knowledge import _get_zim

        _get_zim()
    except Exception:
        pass


def main() -> None:
    threading.Thread(target=_preload_knowledge, daemon=True).start()
    uvicorn.run(
        "nowhere.remote:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8080")),
        log_level=os.environ.get("LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
