
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY backend/services/transcoding_worker/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/services/transcoding_worker /app/transcoding_worker

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "transcoding_worker.main:app", "--host", "0.0.0.0", "--port", "8000"]
