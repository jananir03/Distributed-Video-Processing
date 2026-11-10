-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: transcoding_orchestrator_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `transcoding_consumed_events`
--

DROP TABLE IF EXISTS `transcoding_consumed_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transcoding_consumed_events` (
  `event_id` varchar(128) NOT NULL,
  `event_type` varchar(128) NOT NULL,
  `processed_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transcoding_consumed_events`
--

LOCK TABLES `transcoding_consumed_events` WRITE;
/*!40000 ALTER TABLE `transcoding_consumed_events` DISABLE KEYS */;
INSERT INTO `transcoding_consumed_events` VALUES ('54577814-c13c-42af-8a54-a545b600e6d5','video.uploaded','2026-11-04 14:18:59'),('817f6a33-ea9b-4145-9d35-42c1cc255eed','video.uploaded','2026-11-04 19:18:56'),('9d1c8933-14fa-45d9-978c-b09884d6d4c3','video.uploaded','2026-11-05 05:24:56');
/*!40000 ALTER TABLE `transcoding_consumed_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transcoding_jobs`
--

DROP TABLE IF EXISTS `transcoding_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transcoding_jobs` (
  `id` varchar(36) NOT NULL,
  `video_id` varchar(36) NOT NULL,
  `source_event_id` varchar(128) NOT NULL,
  `source_path` varchar(1024) NOT NULL,
  `profile` varchar(32) NOT NULL,
  `status` varchar(24) NOT NULL,
  `priority` int NOT NULL,
  `attempt_count` int NOT NULL,
  `max_attempts` int NOT NULL,
  `error_message` text,
  `output_path` varchar(1024) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_job_video_profile` (`video_id`,`profile`),
  KEY `ix_transcoding_jobs_status` (`status`),
  KEY `ix_transcoding_jobs_video_id` (`video_id`),
  KEY `ix_transcoding_jobs_source_event_id` (`source_event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transcoding_jobs`
--

LOCK TABLES `transcoding_jobs` WRITE;
/*!40000 ALTER TABLE `transcoding_jobs` DISABLE KEYS */;
INSERT INTO `transcoding_jobs` VALUES ('03d73133-3457-48eb-8270-8bd55f7d0e32','9135161f-715c-41b5-b093-11e8bb2d126d','54577814-c13c-42af-8a54-a545b600e6d5','3b53f6c99db04b64be7f8b60302030f0.mp4','480p','completed',5,0,3,NULL,'transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/480p.mp4','2026-11-04 14:18:59','2026-11-04 16:46:46'),('174fe466-0510-4242-83a2-5ba3003a4128','9135161f-715c-41b5-b093-11e8bb2d126d','54577814-c13c-42af-8a54-a545b600e6d5','3b53f6c99db04b64be7f8b60302030f0.mp4','720p','completed',5,0,3,NULL,'transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/720p.mp4','2026-11-04 14:18:59','2026-11-04 16:47:18'),('8eaf312d-bde1-47a9-b19d-b1561e8a88a1','9135161f-715c-41b5-b093-11e8bb2d126d','54577814-c13c-42af-8a54-a545b600e6d5','3b53f6c99db04b64be7f8b60302030f0.mp4','360p','completed',5,0,3,NULL,'transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/360p.mp4','2026-11-04 14:18:59','2026-11-04 16:46:26'),('94bbb868-8483-45b8-a36c-cdcdb55447f3','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','817f6a33-ea9b-4145-9d35-42c1cc255eed','350c98094d3e4cc898717d757953ae81.mp4','360p','completed',5,0,3,NULL,'transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/360p.mp4','2026-11-04 19:18:56','2026-11-04 19:18:59'),('a40f9dd9-3719-4535-86e0-8f6999655622','07b2cb50-80b8-46df-b436-04088893cbcc','9d1c8933-14fa-45d9-978c-b09884d6d4c3','988c6b1d147b4c5d9cfe3888e5592c23.mp4','480p','completed',5,0,3,NULL,'transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/480p.mp4','2026-11-05 05:24:56','2026-11-05 05:25:04'),('a5954b7d-242c-4a61-ab51-1489694386bd','07b2cb50-80b8-46df-b436-04088893cbcc','9d1c8933-14fa-45d9-978c-b09884d6d4c3','988c6b1d147b4c5d9cfe3888e5592c23.mp4','720p','completed',5,0,3,NULL,'transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/720p.mp4','2026-11-05 05:24:56','2026-11-05 05:25:15'),('e7554686-de19-457b-87e0-41d414cd8f90','07b2cb50-80b8-46df-b436-04088893cbcc','9d1c8933-14fa-45d9-978c-b09884d6d4c3','988c6b1d147b4c5d9cfe3888e5592c23.mp4','360p','completed',5,0,3,NULL,'transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/360p.mp4','2026-11-05 05:24:56','2026-11-05 05:25:20'),('ea627fa0-ebcc-4334-a481-5d399d16c4d1','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','817f6a33-ea9b-4145-9d35-42c1cc255eed','350c98094d3e4cc898717d757953ae81.mp4','480p','completed',5,0,3,NULL,'transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/480p.mp4','2026-11-04 19:18:56','2026-11-04 19:19:01'),('efe3e757-48a5-41a3-9c2a-c4ef958b8dd2','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','817f6a33-ea9b-4145-9d35-42c1cc255eed','350c98094d3e4cc898717d757953ae81.mp4','720p','completed',5,0,3,NULL,'transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/720p.mp4','2026-11-04 19:18:56','2026-11-04 19:19:00');
/*!40000 ALTER TABLE `transcoding_jobs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transcoding_outbox_events`
--

DROP TABLE IF EXISTS `transcoding_outbox_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transcoding_outbox_events` (
  `id` varchar(36) NOT NULL,
  `dedupe_key` varchar(255) NOT NULL,
  `exchange_name` varchar(255) NOT NULL,
  `routing_key` varchar(255) NOT NULL,
  `payload` json NOT NULL,
  `published_at` datetime DEFAULT NULL,
  `attempts` int NOT NULL,
  `last_error` text,
  `created_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_transcoding_outbox_dedupe` (`dedupe_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transcoding_outbox_events`
--

LOCK TABLES `transcoding_outbox_events` WRITE;
/*!40000 ALTER TABLE `transcoding_outbox_events` DISABLE KEYS */;
INSERT INTO `transcoding_outbox_events` VALUES ('1a488a64-ca8e-4d81-a089-a0aa9c5e64a5','a40f9dd9-3719-4535-86e0-8f6999655622:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"a40f9dd9-3719-4535-86e0-8f6999655622\", \"attempt\": 0, \"profile\": \"480p\", \"event_id\": \"f9343c50-712e-445e-9113-9cb25b6e3f0e\", \"priority\": 5, \"video_id\": \"07b2cb50-80b8-46df-b436-04088893cbcc\", \"created_at\": \"2026-11-05T05:24:56.374884+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"988c6b1d147b4c5d9cfe3888e5592c23.mp4\", \"source_event_id\": \"9d1c8933-14fa-45d9-978c-b09884d6d4c3\"}','2026-11-05 05:24:58',0,NULL,'2026-11-05 05:24:56'),('23c3385d-b9f4-45d2-a109-4b0e37792a50','8eaf312d-bde1-47a9-b19d-b1561e8a88a1:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"8eaf312d-bde1-47a9-b19d-b1561e8a88a1\", \"attempt\": 0, \"profile\": \"360p\", \"event_id\": \"1d6fd88c-a5a9-4b4d-a906-2bfd34309525\", \"priority\": 5, \"video_id\": \"9135161f-715c-41b5-b093-11e8bb2d126d\", \"created_at\": \"2026-11-04T14:18:59.414931+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"3b53f6c99db04b64be7f8b60302030f0.mp4\", \"source_event_id\": \"54577814-c13c-42af-8a54-a545b600e6d5\"}','2026-11-04 14:53:12',625,NULL,'2026-11-04 14:18:59'),('c14400b2-4834-4920-9f32-f994e84a2842','03d73133-3457-48eb-8270-8bd55f7d0e32:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"03d73133-3457-48eb-8270-8bd55f7d0e32\", \"attempt\": 0, \"profile\": \"480p\", \"event_id\": \"aad00ed0-0eb1-4f83-90f4-f666e6509dbb\", \"priority\": 5, \"video_id\": \"9135161f-715c-41b5-b093-11e8bb2d126d\", \"created_at\": \"2026-11-04T14:18:59.419311+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"3b53f6c99db04b64be7f8b60302030f0.mp4\", \"source_event_id\": \"54577814-c13c-42af-8a54-a545b600e6d5\"}','2026-11-04 14:53:12',0,NULL,'2026-11-04 14:18:59'),('d5a6c45e-5678-4fc3-ab0e-a93ec12ecd84','94bbb868-8483-45b8-a36c-cdcdb55447f3:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"94bbb868-8483-45b8-a36c-cdcdb55447f3\", \"attempt\": 0, \"profile\": \"360p\", \"event_id\": \"e35e39eb-3ee3-4b1b-af66-b715011a3aaa\", \"priority\": 5, \"video_id\": \"e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e\", \"created_at\": \"2026-11-04T19:18:56.848559+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"350c98094d3e4cc898717d757953ae81.mp4\", \"source_event_id\": \"817f6a33-ea9b-4145-9d35-42c1cc255eed\"}','2026-11-04 19:18:57',0,NULL,'2026-11-04 19:18:56'),('de4e2241-009d-41cb-bcbf-b659c99e4417','174fe466-0510-4242-83a2-5ba3003a4128:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"174fe466-0510-4242-83a2-5ba3003a4128\", \"attempt\": 0, \"profile\": \"720p\", \"event_id\": \"383974f3-973a-4b13-8f6c-08318a556e2c\", \"priority\": 5, \"video_id\": \"9135161f-715c-41b5-b093-11e8bb2d126d\", \"created_at\": \"2026-11-04T14:18:59.421911+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"3b53f6c99db04b64be7f8b60302030f0.mp4\", \"source_event_id\": \"54577814-c13c-42af-8a54-a545b600e6d5\"}','2026-11-04 14:53:12',0,NULL,'2026-11-04 14:18:59'),('e4179a39-ffff-4449-868f-91469181707b','efe3e757-48a5-41a3-9c2a-c4ef958b8dd2:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"efe3e757-48a5-41a3-9c2a-c4ef958b8dd2\", \"attempt\": 0, \"profile\": \"720p\", \"event_id\": \"eed10d72-78a2-4d3b-9642-d697b2848ec2\", \"priority\": 5, \"video_id\": \"e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e\", \"created_at\": \"2026-11-04T19:18:56.857554+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"350c98094d3e4cc898717d757953ae81.mp4\", \"source_event_id\": \"817f6a33-ea9b-4145-9d35-42c1cc255eed\"}','2026-11-04 19:18:57',0,NULL,'2026-11-04 19:18:56'),('e813ee4c-11c4-4feb-857e-9d3d3720a0f7','ea627fa0-ebcc-4334-a481-5d399d16c4d1:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"ea627fa0-ebcc-4334-a481-5d399d16c4d1\", \"attempt\": 0, \"profile\": \"480p\", \"event_id\": \"0fd872c9-decb-4840-9c44-741974fb2dc4\", \"priority\": 5, \"video_id\": \"e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e\", \"created_at\": \"2026-11-04T19:18:56.855096+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"350c98094d3e4cc898717d757953ae81.mp4\", \"source_event_id\": \"817f6a33-ea9b-4145-9d35-42c1cc255eed\"}','2026-11-04 19:18:57',0,NULL,'2026-11-04 19:18:56'),('ef3d1726-889e-45ca-8485-851f4a239d03','a5954b7d-242c-4a61-ab51-1489694386bd:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"a5954b7d-242c-4a61-ab51-1489694386bd\", \"attempt\": 0, \"profile\": \"720p\", \"event_id\": \"bff4c647-f38f-418f-b020-a943961725bd\", \"priority\": 5, \"video_id\": \"07b2cb50-80b8-46df-b436-04088893cbcc\", \"created_at\": \"2026-11-05T05:24:56.377111+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"988c6b1d147b4c5d9cfe3888e5592c23.mp4\", \"source_event_id\": \"9d1c8933-14fa-45d9-978c-b09884d6d4c3\"}','2026-11-05 05:24:58',0,NULL,'2026-11-05 05:24:56'),('fd29d450-d688-4fc9-b037-0ba04a5703cc','e7554686-de19-457b-87e0-41d414cd8f90:transcoding.requested','video.transcoding','transcoding.requested','{\"job_id\": \"e7554686-de19-457b-87e0-41d414cd8f90\", \"attempt\": 0, \"profile\": \"360p\", \"event_id\": \"4c2cfd57-fffa-495d-aff6-fac526fa9802\", \"priority\": 5, \"video_id\": \"07b2cb50-80b8-46df-b436-04088893cbcc\", \"created_at\": \"2026-11-05T05:24:56.368928+00:00\", \"event_type\": \"transcoding.requested\", \"source_path\": \"988c6b1d147b4c5d9cfe3888e5592c23.mp4\", \"source_event_id\": \"9d1c8933-14fa-45d9-978c-b09884d6d4c3\"}','2026-11-05 05:24:58',0,NULL,'2026-11-05 05:24:56');
/*!40000 ALTER TABLE `transcoding_outbox_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'transcoding_orchestrator_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-05 13:29:08
