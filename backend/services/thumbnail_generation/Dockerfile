
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app

COPY backend/services/thumbnail_generation/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/services/thumbnail_generation/ /app/thumbnail_generation/

RUN mkdir -p /app/media \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "thumbnail_generation.main:app", "--host", "0.0.0.0", "--port", "8000"]
