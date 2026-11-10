# FrameFlow – Distributed Video Processing Frontend

A simple React + TypeScript dashboard for the Distributed Video Processing backend.

## Requirements
- Node.js 20 or newer (Node 24 is suitable)
- npm
- Existing backend services running through Docker Compose

## Setup
1. Extract this ZIP.
2. Open PowerShell in the extracted `video_frontend` directory.
3. Install dependencies:

```powershell
npm install
```

4. Create `.env` from the example:

```powershell
Copy-Item .env.example .env
```

5. Ensure `.env` contains:

```env
VITE_API_BASE_URL=http://localhost:8000
```

6. Start the development server:

```powershell
npm run dev
```

7. Open http://localhost:5173

## Backend connection
The frontend uses only the API Gateway at `http://localhost:8000`. It does not call individual microservice ports.

Implemented gateway calls:
- `GET /api/v1/upload/videos`
- `GET /api/v1/upload/videos/{video_id}`
- `POST /api/v1/upload/videos/upload` (multipart field: `file`)
- `GET /api/v1/videos/{video_id}/status`
- `POST /api/v1/videos/{video_id}/process`
- `GET /api/v1/orchestrator/jobs?video_id={video_id}`
- `GET /api/v1/media/videos/{video_id}/outputs`
- `GET /api/v1/thumbnails/{video_id}`
- `GET /api/v1/media/videos/{video_id}/stream?profile={profile}`
- `GET /api/v1/media/videos/{video_id}/download?profile={profile}`
- `GET /api/v1/thumbnails/{video_id}/{profile}`

The upload endpoint automatically triggers processing through the backend's upload event workflow. The dashboard's processing action calls the gateway's idempotent process endpoint; it does not manually retry failed jobs.

## Build for production

```powershell
npm run build
npm run preview
```

Build output is generated in `dist/`.

## Troubleshooting
- Confirm `docker compose ps` shows the API Gateway healthy on port 8000.
- Open http://localhost:8000/docs and confirm the gateway is reachable.
- Confirm gateway CORS allows `http://localhost:5173` (the backend configuration in the supplied project includes this origin).
- If a route returns 404, compare it with the live gateway Swagger because the gateway is the source of truth for public routes.
- Video playback and image previews require the relevant profile/thumbnail to have completed generation.
