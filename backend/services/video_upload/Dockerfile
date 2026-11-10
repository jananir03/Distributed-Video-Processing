FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY backend/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r /app/requirements.txt

COPY backend/shared /app/shared
COPY backend/services/video_upload /app/services/video_upload

RUN mkdir -p /app/media && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "services.video_upload.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
