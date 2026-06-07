"""HTTP middleware."""

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from portfolio_assistant.webserver import request_id_ctx


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assigns a request id per request.

    The id is taken from the inbound ``X-Request-ID`` header or generated, made
    available to the logging layer via :data:`request_id_ctx`, and echoed back
    on the response so a call can be correlated across services.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response
