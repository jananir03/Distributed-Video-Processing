-- Runs only when MySQL initializes an empty data directory.
-- Each service owns its schema. Services must access their own schema only.
CREATE DATABASE IF NOT EXISTS video_upload_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS video_metadata_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS transcoding_orchestrator_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS transcoding_worker_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS thumbnail_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS media_delivery_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
