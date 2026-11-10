import logging
from collections.abc import AsyncIterator

import httpx
from fastapi import HTTPException, Request
from starlette.responses import Response, StreamingResponse

log = logging.getLogger(__name__)

HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "host", "content-length",
}
RESPONSE_HEADERS = {
    "accept-ranges", "cache-control", "content-disposition", "content-encoding",
    "content-language", "content-length", "content-range", "content-type", "etag",
    "expires", "last-modified", "pragma", "retry-after", "vary",
}


async def proxy_request(
    request: Request, client: httpx.AsyncClient, upstream_base: str, upstream_path: str
) -> Response:
    """Forward a request without buffering uploads or media responses."""
    target_url = upstream_base.rstrip("/") + "/" + upstream_path.lstrip("/")
    if request.url.query:
        target_url += "?" + request.url.query

    request_headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
        and key.lower() not in {"origin", "access-control-request-method", "access-control-request-headers"}
    }
    correlation_id = getattr(request.state, "correlation_id", None)
    if correlation_id:
        request_headers["x-correlation-id"] = correlation_id

    async def request_body() -> AsyncIterator[bytes]:
        async for chunk in request.stream():
            yield chunk

    try:
        outgoing = client.build_request(
            method=request.method,
            url=target_url,
            headers=request_headers,
            content=request_body() if request.method not in {"GET", "HEAD"} else None,
        )
        upstream = await client.send(outgoing, stream=True)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail={
            "code": "DOWNSTREAM_TIMEOUT", "message": "The requested backend service timed out."
        }) from exc
    except httpx.HTTPError as exc:
        log.exception("Downstream request failed: %s %s", request.method, request.url.path)
        raise HTTPException(status_code=502, detail={
            "code": "DOWNSTREAM_UNAVAILABLE", "message": "The requested backend service is unavailable."
        }) from exc

    response_headers = {
        key: value for key, value in upstream.headers.items()
        if key.lower() in RESPONSE_HEADERS and key.lower() not in HOP_BY_HOP_HEADERS
    }
    if correlation_id:
        response_headers["x-correlation-id"] = correlation_id

    if request.method == "HEAD" or upstream.status_code in {204, 304}:
        await upstream.aclose()
        return Response(status_code=upstream.status_code, headers=response_headers)

    async def response_body() -> AsyncIterator[bytes]:
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()

    return StreamingResponse(
        response_body(), status_code=upstream.status_code, headers=response_headers, media_type=None
    )
