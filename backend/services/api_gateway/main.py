
import copy
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .config import settings
from .proxy import proxy_request


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

log = logging.getLogger("api_gateway")


# Gateway namespaces and their corresponding upstream services.
# The upstream path suffix is preserved according to each service's
# configured path transformation.
SERVICES = {
    "upload": {
        "url": settings.video_upload_url,
        "prefix": "/api/v1/upload",
        "strip": "",
    },
    "metadata": {
        "url": settings.video_metadata_url,
        "prefix": "/api/v1/metadata",
        "strip": "/metadata",
    },
    "orchestrator": {
        "url": settings.transcoding_orchestrator_url,
        "prefix": "/api/v1/orchestrator",
        "strip": "",
    },
    "media": {
        "url": settings.media_delivery_url,
        "prefix": "/api/v1/media",
        "strip": "/api/v1",
    },
    "thumbnails": {
        "url": settings.thumbnail_service_url,
        "prefix": "/api/v1/thumbnails",
        "strip": "/thumbnails",
    },
}

EXCLUDED_PATH_PREFIXES = (
    "/health/",
    "/internal/",
)


def _rewrite_refs(value: Any, prefix: str) -> Any:
    """Prefix component references to avoid OpenAPI naming collisions."""

    if isinstance(value, dict):
        return {
            key: _rewrite_refs(item, prefix)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            _rewrite_refs(item, prefix)
            for item in value
        ]

    if isinstance(value, str) and value.startswith("#/components/"):
        parts = value.split("/", 3)

        if len(parts) == 4:
            return f"#/components/{parts[2]}/{prefix}_{parts[3]}"

    return value


def _make_handler(service: dict[str, str]):
    """Create a request handler that forwards requests upstream."""

    async def handler(request: Request):
        suffix = request.url.path[len(service["prefix"]):]

        if service["strip"]:
            suffix = service["strip"] + suffix

        return await proxy_request(
            request,
            request.app.state.http_client,
            service["url"],
            suffix,
        )

    return handler


def _public_path(
    service: dict[str, str],
    upstream_path: str,
) -> str:
    """Convert an upstream path into its public gateway path."""

    suffix = upstream_path
    strip = service["strip"]

    if strip and suffix.startswith(strip):
        suffix = suffix[len(strip):] or "/"

    return service["prefix"] + (
        suffix if suffix.startswith("/") else "/" + suffix
    )


async def _register_upstream_routes(app: FastAPI) -> None:
    """
    Register concrete upstream operations.

    The dedicated Thumbnail Service owns all public thumbnail operations.
    Duplicate thumbnail operations exposed by Media Delivery are excluded.
    """

    client: httpx.AsyncClient = app.state.http_client

    aggregated: dict[str, Any] = {
        "openapi": "3.1.0",
        "info": {
            "title": "Distributed Video Processing API Gateway",
            "version": "1.0.0",
            "description": (
                "Single frontend entry point for the concrete API operations "
                "published by Video Upload, Video Metadata, Transcoding "
                "Orchestrator, Media Delivery and Thumbnail Service. "
                "Operation paths and schemas are imported from each "
                "service's live OpenAPI document. "
                "Uploads and media streams are forwarded without buffering. "
                "Thumbnail operations are exposed only through the "
                "dedicated Thumbnail Service namespace."
            ),
        },
        "paths": {},
        "components": {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "requestBodies": {},
            "headers": {},
            "securitySchemes": {},
        },
        "tags": [
            {
                "name": "Gateway Health",
                "description": "Gateway liveness and readiness.",
            }
        ],
    }

    discovered = 0

    for name, service in SERVICES.items():

        try:
            response = await client.get(
                service["url"].rstrip("/") + "/openapi.json",
                timeout=httpx.Timeout(
                    settings.openapi_timeout_seconds,
                    connect=settings.connect_timeout_seconds,
                ),
            )

            response.raise_for_status()
            spec = response.json()

        except (httpx.HTTPError, ValueError) as exc:
            log.exception(
                "Unable to load OpenAPI from %s",
                name,
            )

            raise RuntimeError(
                f"Cannot load {name} OpenAPI document "
                f"from {service['url']}"
            ) from exc

        prefix = name
        components = spec.get("components", {})

        # Import and rename upstream OpenAPI components.
        for component_type, definitions in components.items():

            target = aggregated["components"].setdefault(
                component_type,
                {},
            )

            if isinstance(definitions, dict):

                for component_name, definition in definitions.items():

                    target[f"{prefix}_{component_name}"] = (
                        _rewrite_refs(definition, prefix)
                    )

        # Import upstream tags.
        for tag in spec.get("tags", []):

            aggregated["tags"].append({
                **tag,
                "name": f"{name}: {tag.get('name', 'default')}",
            })

        # Import actual upstream operations.
        for upstream_path, path_item in spec.get("paths", {}).items():

            if upstream_path.startswith(EXCLUDED_PATH_PREFIXES):
                continue

            # IMPORTANT:
            # Media Delivery also exposes thumbnail retrieval routes.
            # We keep thumbnail APIs exclusively under the dedicated
            # Thumbnail Service to avoid duplicate Swagger sections.
            if (
                name == "media"
                and "/thumbnails" in upstream_path
            ):
                log.info(
                    "Skipping duplicate Media Delivery thumbnail route: %s",
                    upstream_path,
                )
                continue

            public_path = _public_path(
                service,
                upstream_path,
            )

            rewritten_item = _rewrite_refs(
                copy.deepcopy(path_item),
                prefix,
            )

            for method, operation in list(rewritten_item.items()):

                if method.lower() not in {
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "head",
                    "options",
                }:
                    continue

                operation["tags"] = [
                    f"{name}: {tag}"
                    for tag in operation.get("tags", [name])
                ]

                old_id = operation.get(
                    "operationId",
                    f"{method}_{upstream_path.strip('/').replace('/', '_')}",
                )

                operation["operationId"] = f"{name}_{old_id}"

                route_path = public_path

                # Register actual upstream methods and paths.
                app.add_api_route(
                    route_path,
                    _make_handler(service),
                    methods=[method.upper()],
                    include_in_schema=False,
                    name=f"{name}_{method}_{upstream_path}",
                )

                discovered += 1

            aggregated["paths"][public_path] = rewritten_item

    app.state.aggregated_openapi = aggregated
    app.state.discovered_operations = discovered

    log.info(
        "Registered %d concrete upstream operations",
        discovered,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the shared asynchronous HTTP client."""

    timeout = httpx.Timeout(
        settings.request_timeout_seconds,
        connect=settings.connect_timeout_seconds,
    )

    limits = httpx.Limits(
        max_connections=settings.max_connections,
        max_keepalive_connections=settings.max_keepalive_connections,
    )

    app.state.http_client = httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        follow_redirects=False,
    )

    try:
        await _register_upstream_routes(app)
        yield

    finally:
        await app.state.http_client.aclose()


app = FastAPI(
    title="Distributed Video Processing API Gateway",
    version="1.0.0",
    description=(
        "Concrete API operations and schemas aggregated "
        "from the backend microservices."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)


# CORS configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Range",
        "If-Range",
        "If-None-Match",
        "If-Modified-Since",
        "X-Correlation-ID",
    ],
    expose_headers=[
        "Accept-Ranges",
        "Content-Range",
        "Content-Length",
        "ETag",
        "Last-Modified",
        "X-Correlation-ID",
    ],
)


@app.middleware("http")
async def request_context(
    request: Request,
    call_next,
):
    """Add correlation IDs, response headers and request logging."""

    correlation_id = (
        request.headers.get("x-correlation-id")
        or str(uuid.uuid4())
    )

    request.state.correlation_id = correlation_id
    started = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:

        log.exception(
            "Unhandled gateway error request_id=%s",
            correlation_id,
        )

        response = JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "GATEWAY_INTERNAL_ERROR",
                    "message": "Unexpected gateway error.",
                },
            },
        )

    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Content-Type-Options"] = "nosniff"

    log.info(
        "%s %s -> %s %.1fms request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
        correlation_id,
    )

    return response


@app.get(
    "/health/live",
    tags=["Gateway Health"],
    summary="Check gateway liveness",
)
async def live():
    return {
        "status": "ok",
        "service": settings.service_name,
    }


@app.get(
    "/health/ready",
    tags=["Gateway Health"],
    summary="Check gateway and upstream readiness",
)
async def ready():

    results = {}

    for name, service in SERVICES.items():

        try:
            response = await app.state.http_client.get(
                service["url"].rstrip("/") + "/health/live",
                timeout=httpx.Timeout(
                    3.0,
                    connect=2.0,
                ),
            )

            results[name] = (
                "connected"
                if response.is_success
                else f"http_{response.status_code}"
            )

        except httpx.HTTPError:
            results[name] = "unavailable"

    healthy = all(
        value == "connected"
        for value in results.values()
    )

    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "ok" if healthy else "degraded",
            "service": settings.service_name,
            "upstreams": results,
            "registered_operations": getattr(
                app.state,
                "discovered_operations",
                0,
            ),
        },
    )


async def _load_video_and_jobs(video_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load the source video and its transcoding jobs through service APIs."""
    client: httpx.AsyncClient = app.state.http_client

    try:
        video_response = await client.get(
            settings.video_upload_url.rstrip("/") + f"/videos/{video_id}"
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Video Upload Service timed out while retrieving the video.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Video Upload Service is unavailable.",
        ) from exc

    if video_response.status_code == 404:
        raise HTTPException(status_code=404, detail="Video not found.")
    if not video_response.is_success:
        raise HTTPException(
            status_code=502,
            detail=f"Video Upload Service returned HTTP {video_response.status_code}.",
        )

    try:
        video = video_response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Video Upload Service returned an invalid response.",
        ) from exc

    try:
        jobs_response = await client.get(
            settings.transcoding_orchestrator_url.rstrip("/") + "/jobs",
            params={"video_id": video_id, "limit": 200, "offset": 0},
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Transcoding Orchestrator timed out while retrieving jobs.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Transcoding Orchestrator is unavailable.",
        ) from exc

    if not jobs_response.is_success:
        raise HTTPException(
            status_code=502,
            detail=f"Transcoding Orchestrator returned HTTP {jobs_response.status_code}.",
        )

    try:
        jobs_payload = jobs_response.json()
        jobs = jobs_payload.get("items", [])
        if not isinstance(jobs, list):
            raise ValueError("The jobs response 'items' field is not a list")
    except (ValueError, AttributeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Transcoding Orchestrator returned an invalid jobs response.",
        ) from exc

    return video, jobs


def _summarize_processing(video: dict[str, Any], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a video-level processing status from per-profile jobs."""
    if not jobs:
        overall_status = "awaiting_orchestrator"
    else:
        statuses = [str(job.get("status", "unknown")).lower() for job in jobs]
        if all(status == "completed" for status in statuses):
            overall_status = "completed"
        elif any(status == "processing" for status in statuses):
            overall_status = "processing"
        elif any(status == "queued" for status in statuses):
            overall_status = "queued"
        elif any(status == "failed" for status in statuses):
            overall_status = "failed" if all(
                status in {"failed", "completed", "cancelled"} for status in statuses
            ) else "partially_failed"
        elif all(status == "cancelled" for status in statuses):
            overall_status = "cancelled"
        else:
            overall_status = "unknown"

    return {
        "video_id": video.get("id"),
        "video_status": video.get("status"),
        "processing_status": overall_status,
        "total_jobs": len(jobs),
        "completed_jobs": sum(str(job.get("status", "")).lower() == "completed" for job in jobs),
        "failed_jobs": sum(str(job.get("status", "")).lower() == "failed" for job in jobs),
        "jobs": [
            {
                "job_id": job.get("id"),
                "profile": job.get("profile"),
                "status": job.get("status"),
                "attempt_count": job.get("attempt_count"),
                "max_attempts": job.get("max_attempts"),
                "error_message": job.get("error_message"),
                "output_path": job.get("output_path"),
                "created_at": job.get("created_at"),
                "updated_at": job.get("updated_at"),
            }
            for job in jobs
        ],
    }


@app.get(
    "/api/v1/videos/{video_id}/status",
    tags=["Video Processing"],
    summary="Get aggregated video processing status",
    include_in_schema=False,
)
async def get_video_processing_status(video_id: str):
    """Return upload status and all profile-job statuses for one video."""
    video, jobs = await _load_video_and_jobs(video_id)
    return _summarize_processing(video, jobs)


@app.post(
    "/api/v1/videos/{video_id}/process",
    tags=["Video Processing"],
    summary="Check or confirm video processing request",
    include_in_schema=False,
)
async def request_video_processing(video_id: str):
    """Idempotently confirm processing started by the upload event.

    The current backend starts transcoding automatically when the Video Upload
    Service publishes `video.uploaded`. There is no manual job-creation API in
    the existing Orchestrator. This endpoint therefore does not publish a
    second event or create duplicate jobs; it returns existing jobs, or 202
    while the original upload event is still being consumed.
    """
    video, jobs = await _load_video_and_jobs(video_id)
    result = _summarize_processing(video, jobs)
    result["message"] = (
        "Processing jobs already exist; this request is idempotent."
        if jobs
        else "The upload event starts processing automatically. The orchestrator has not created jobs yet; retry status shortly."
    )
    result["processing_trigger"] = "video.uploaded event"
    result["manual_retriggered"] = False

    return JSONResponse(
        status_code=200 if jobs else 202,
        content=result,
    )


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": settings.service_name,
        "docs": "/docs",
        "health": "/health/live",
    }


def custom_openapi():
    """Return the merged OpenAPI specification."""

    if app.openapi_schema:
        return app.openapi_schema

    schema = copy.deepcopy(
        getattr(
            app.state,
            "aggregated_openapi",
            None,
        )
    )

    if schema is None:
        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )

    schema.setdefault("paths", {})["/health/live"] = {
        "get": {
            "tags": ["Gateway Health"],
            "summary": "Check gateway liveness",
            "operationId": "gateway_live_health",
            "responses": {
                "200": {
                    "description": "Gateway is alive",
                },
            },
        },
    }

    schema["paths"]["/health/ready"] = {
        "get": {
            "tags": ["Gateway Health"],
            "summary": "Check gateway and upstream readiness",
            "operationId": "gateway_ready_health",
            "responses": {
                "200": {
                    "description": "All upstream services are reachable",
                },
                "503": {
                    "description": "One or more upstream services are unavailable",
                },
            },
        },
    }

    schema.setdefault("paths", {})["/api/v1/videos/{video_id}/status"] = {
        "get": {
            "tags": ["Video Processing"],
            "summary": "Get aggregated video processing status",
            "description": "Combines the uploaded video record with the status of each transcoding profile job.",
            "operationId": "gateway_get_video_processing_status",
            "parameters": [{
                "name": "video_id", "in": "path", "required": True,
                "schema": {"type": "string"},
            }],
            "responses": {
                "200": {"description": "Video and per-profile processing status."},
                "404": {"description": "Video not found."},
                "502": {"description": "An upstream service returned an invalid response or failed."},
                "504": {"description": "An upstream service timed out."},
            },
        }
    }

    schema["paths"]["/api/v1/videos/{video_id}/process"] = {
        "post": {
            "tags": ["Video Processing"],
            "summary": "Check or confirm video processing request",
            "description": (
                "Processing is automatically triggered by the video.uploaded event. "
                "This idempotent gateway operation returns existing profile jobs, "
                "or HTTP 202 while the orchestrator is still consuming the upload event. "
                "It does not publish a duplicate event or manually recreate jobs."
            ),
            "operationId": "gateway_request_video_processing",
            "parameters": [{
                "name": "video_id", "in": "path", "required": True,
                "schema": {"type": "string"},
            }],
            "responses": {
                "200": {"description": "Processing jobs already exist; current job states are returned."},
                "202": {"description": "Upload event has been emitted; orchestrator job creation is pending."},
                "404": {"description": "Video not found."},
                "502": {"description": "An upstream service returned an invalid response or failed."},
                "504": {"description": "An upstream service timed out."},
            },
        }
    }

    app.openapi_schema = schema

    return schema


app.openapi = custom_openapi
