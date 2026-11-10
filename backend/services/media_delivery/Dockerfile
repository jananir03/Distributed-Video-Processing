FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home-dir /app app
COPY backend/services/media_delivery/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend/services/media_delivery/ /app/media_delivery/
RUN chown -R app:app /app
USER app
EXPOSE 8000
CMD ["uvicorn", "media_delivery.main:app", "--host", "0.0.0.0", "--port", "8000"]
