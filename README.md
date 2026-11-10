# Distributed Video Processing & Transcoding Platform

A microservices-based video processing platform that allows users to upload videos, process them asynchronously, generate multiple resolutions, create thumbnails, and stream or download processed videos.

## Project Overview

The Distributed Video Processing Platform is designed to handle video processing tasks using an event-driven microservices architecture.

The system accepts video uploads, creates transcoding jobs, processes videos in the background, and makes the generated outputs available for playback and download.

A React-based frontend provides a simple interface to upload videos, monitor processing status, view generated thumbnails, and play processed videos.

## Key Features

- Video upload with file validation.
- Asynchronous video processing.
- Distributed processing using RabbitMQ.
- Multiple video resolutions: 360p, 480p, and 720p.
- Automatic thumbnail generation.
- Video metadata management.
- Processing job tracking and status monitoring.
- Video streaming and downloading.
- Centralized API Gateway.
- Docker-based service deployment.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Frontend | React, TypeScript, Vite |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy |
| Message Broker | RabbitMQ |
| Cache | Redis |
| Video Processing | FFmpeg |
| Containerization | Docker, Docker Compose |
| Charts | Recharts |

## Microservices Architecture

The application consists of the following services:

| Service | Responsibility |
|---|---|
| API Gateway | Central entry point for frontend requests |
| Video Upload Service | Handles video uploads and file storage |
| Video Metadata Service | Stores and manages video metadata |
| Transcoding Orchestrator | Creates and coordinates transcoding jobs |
| Transcoding Worker | Processes videos into multiple resolutions |
| Thumbnail Service | Generates video thumbnails |
| Media Delivery Service | Handles video streaming and downloads |

## Prerequisites

Install the following before running the project:

- Python 3.12
- Node.js and npm
- Docker Desktop
- Docker Compose
- Git

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Distributed_Video_Processing
```

### 2. Configure Environment Variables

Create or update the `.env` file using the project's environment configuration.

Configure the required database credentials, service URLs, RabbitMQ connection, Redis connection, and other application settings.

Do not commit passwords, secret keys, or other sensitive values to version control.

### 3. Start Backend Services

Build and start the services using Docker Compose:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

### 4. Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend in your browser:

```text
http://localhost:5173
```

## API Documentation

The API Gateway provides centralized API access.

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

## Frontend Features

The frontend provides the following functionality:

- Dashboard with video processing statistics.
- Video upload interface.
- Video library with uploaded videos.
- Individual video processing details.
- Transcoding job status.
- Generated thumbnail previews.
- Video playback for available resolutions.
- Processed video downloads.
