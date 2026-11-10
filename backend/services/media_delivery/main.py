import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError
from .config import get_settings
from .database import check_database, engine
from .service import AssetNotFound, AssetUnavailable, list_outputs, list_thumbnails, resolve_output, resolve_thumbnail

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()

app = FastAPI(title="Media Delivery Service", version="1.0.0",
              description="Read-only delivery API for completed transcoded videos and thumbnails.",
              lifespan=lifespan)

def unavailable(exc: AssetUnavailable):
    raise HTTPException(status_code=503, detail=str(exc)) from exc

@app.get("/health/live", tags=["Health"])
def health_live():
    return {"status": "ok", "service": settings.service_name}

@app.get("/health/ready", tags=["Health"])
def health_ready():
    try:
        check_database()
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Media catalog database unavailable")

@app.get("/api/v1/videos/{video_id}/assets", tags=["Media"])
def get_video_assets(video_id: str, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    try:
        outputs = list_outputs(video_id, min(limit, settings.max_page_size), offset)
        thumbnails = list_thumbnails(video_id)
        return {"video_id": video_id, "transcoded_outputs": outputs["items"], "output_total": outputs["total"],
                "thumbnails": thumbnails["items"], "thumbnail_total": thumbnails["total"]}
    except AssetUnavailable as exc:
        unavailable(exc)

@app.get("/api/v1/videos/{video_id}/outputs", tags=["Media"])
def get_video_outputs(video_id: str, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    try:
        return list_outputs(video_id, min(limit, settings.max_page_size), offset)
    except AssetUnavailable as exc:
        unavailable(exc)

@app.get("/api/v1/videos/{video_id}/stream", tags=["Delivery"])
def stream_video(video_id: str, profile: str = Query("720p", min_length=2, max_length=16)):
    try:
        path = resolve_output(video_id, profile)
    except AssetNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AssetUnavailable as exc:
        unavailable(exc)
    return FileResponse(path, media_type="video/mp4", headers={
        "Cache-Control": settings.stream_cache_control, "X-Content-Type-Options": "nosniff"})

@app.get("/api/v1/videos/{video_id}/download", tags=["Delivery"])
def download_video(video_id: str, profile: str = Query("720p", min_length=2, max_length=16)):
    try:
        path = resolve_output(video_id, profile)
    except AssetNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AssetUnavailable as exc:
        unavailable(exc)
    return FileResponse(path, media_type="video/mp4", filename=f"{video_id}-{profile}{path.suffix.lower()}",
                        headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})

@app.get("/api/v1/videos/{video_id}/thumbnails", tags=["Thumbnails"])
def get_thumbnails(video_id: str):
    return list_thumbnails(video_id)

@app.get("/api/v1/videos/{video_id}/thumbnails/{profile}", tags=["Thumbnails"])
def get_thumbnail(video_id: str, profile: str):
    try:
        path = resolve_thumbnail(video_id, profile)
    except AssetNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="image/jpeg",
                        headers={"Cache-Control": settings.stream_cache_control, "X-Content-Type-Options": "nosniff"})
