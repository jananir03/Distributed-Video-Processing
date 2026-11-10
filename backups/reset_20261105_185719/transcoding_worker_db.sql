-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: transcoding_worker_db
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
-- Table structure for table `transcoding_worker_job_results`
--

DROP TABLE IF EXISTS `transcoding_worker_job_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transcoding_worker_job_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `job_id` varchar(36) NOT NULL,
  `video_id` varchar(36) NOT NULL,
  `profile` varchar(32) NOT NULL,
  `status` varchar(20) NOT NULL,
  `output_path` text,
  `error_message` text,
  `started_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_worker_result_job_id` (`job_id`),
  KEY `ix_transcoding_worker_job_results_video_id` (`video_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transcoding_worker_job_results`
--

LOCK TABLES `transcoding_worker_job_results` WRITE;
/*!40000 ALTER TABLE `transcoding_worker_job_results` DISABLE KEYS */;
INSERT INTO `transcoding_worker_job_results` VALUES (1,'8eaf312d-bde1-47a9-b19d-b1561e8a88a1','9135161f-715c-41b5-b093-11e8bb2d126d','360p','completed','transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/360p.mp4',NULL,'2026-11-04 16:46:11','2026-11-04 16:46:26','2026-11-04 16:46:26','2026-11-04 16:46:26'),(2,'03d73133-3457-48eb-8270-8bd55f7d0e32','9135161f-715c-41b5-b093-11e8bb2d126d','480p','completed','transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/480p.mp4',NULL,'2026-11-04 16:46:27','2026-11-04 16:46:47','2026-11-04 16:46:46','2026-11-04 16:46:46'),(3,'174fe466-0510-4242-83a2-5ba3003a4128','9135161f-715c-41b5-b093-11e8bb2d126d','720p','completed','transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/720p.mp4',NULL,'2026-11-04 16:46:47','2026-11-04 16:47:18','2026-11-04 16:47:18','2026-11-04 16:47:18'),(4,'94bbb868-8483-45b8-a36c-cdcdb55447f3','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','360p','completed','transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/360p.mp4',NULL,'2026-11-04 19:18:58','2026-11-04 19:18:59','2026-11-04 19:18:59','2026-11-04 19:18:59'),(5,'efe3e757-48a5-41a3-9c2a-c4ef958b8dd2','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','720p','completed','transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/720p.mp4',NULL,'2026-11-04 19:18:59','2026-11-04 19:19:01','2026-11-04 19:19:00','2026-11-04 19:19:00'),(6,'ea627fa0-ebcc-4334-a481-5d399d16c4d1','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','480p','completed','transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/480p.mp4',NULL,'2026-11-04 19:19:01','2026-11-04 19:19:01','2026-11-04 19:19:01','2026-11-04 19:19:01'),(7,'a40f9dd9-3719-4535-86e0-8f6999655622','07b2cb50-80b8-46df-b436-04088893cbcc','480p','completed','transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/480p.mp4',NULL,'2026-11-05 05:24:58','2026-11-05 05:25:05','2026-11-05 05:25:04','2026-11-05 05:25:04'),(8,'a5954b7d-242c-4a61-ab51-1489694386bd','07b2cb50-80b8-46df-b436-04088893cbcc','720p','completed','transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/720p.mp4',NULL,'2026-11-05 05:25:05','2026-11-05 05:25:16','2026-11-05 05:25:15','2026-11-05 05:25:15'),(9,'e7554686-de19-457b-87e0-41d414cd8f90','07b2cb50-80b8-46df-b436-04088893cbcc','360p','completed','transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/360p.mp4',NULL,'2026-11-05 05:25:16','2026-11-05 05:25:20','2026-11-05 05:25:20','2026-11-05 05:25:20');
/*!40000 ALTER TABLE `transcoding_worker_job_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transcoding_worker_processed_messages`
--

DROP TABLE IF EXISTS `transcoding_worker_processed_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transcoding_worker_processed_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_id` varchar(128) NOT NULL,
  `job_id` varchar(36) NOT NULL,
  `outcome` varchar(32) NOT NULL,
  `error_message` text,
  `processed_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_worker_processed_message_id` (`message_id`),
  KEY `ix_transcoding_worker_processed_messages_job_id` (`job_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transcoding_worker_processed_messages`
--

LOCK TABLES `transcoding_worker_processed_messages` WRITE;
/*!40000 ALTER TABLE `transcoding_worker_processed_messages` DISABLE KEYS */;
INSERT INTO `transcoding_worker_processed_messages` VALUES (1,'23c3385d-b9f4-45d2-a109-4b0e37792a50','8eaf312d-bde1-47a9-b19d-b1561e8a88a1','completed',NULL,'2026-11-04 16:46:26','2026-11-04 16:46:11','2026-11-04 16:46:26'),(2,'c14400b2-4834-4920-9f32-f994e84a2842','03d73133-3457-48eb-8270-8bd55f7d0e32','completed',NULL,'2026-11-04 16:46:47','2026-11-04 16:46:26','2026-11-04 16:46:46'),(3,'de4e2241-009d-41cb-bcbf-b659c99e4417','174fe466-0510-4242-83a2-5ba3003a4128','completed',NULL,'2026-11-04 16:47:18','2026-11-04 16:46:46','2026-11-04 16:47:18'),(4,'d5a6c45e-5678-4fc3-ab0e-a93ec12ecd84','94bbb868-8483-45b8-a36c-cdcdb55447f3','completed',NULL,'2026-11-04 19:18:59','2026-11-04 19:18:57','2026-11-04 19:18:59'),(5,'e4179a39-ffff-4449-868f-91469181707b','efe3e757-48a5-41a3-9c2a-c4ef958b8dd2','completed',NULL,'2026-11-04 19:19:01','2026-11-04 19:18:59','2026-11-04 19:19:00'),(6,'e813ee4c-11c4-4feb-857e-9d3d3720a0f7','ea627fa0-ebcc-4334-a481-5d399d16c4d1','completed',NULL,'2026-11-04 19:19:01','2026-11-04 19:19:00','2026-11-04 19:19:01'),(7,'1a488a64-ca8e-4d81-a089-a0aa9c5e64a5','a40f9dd9-3719-4535-86e0-8f6999655622','completed',NULL,'2026-11-05 05:25:05','2026-11-05 05:24:57','2026-11-05 05:25:04'),(8,'ef3d1726-889e-45ca-8485-851f4a239d03','a5954b7d-242c-4a61-ab51-1489694386bd','completed',NULL,'2026-11-05 05:25:16','2026-11-05 05:25:04','2026-11-05 05:25:15'),(9,'fd29d450-d688-4fc9-b037-0ba04a5703cc','e7554686-de19-457b-87e0-41d414cd8f90','completed',NULL,'2026-11-05 05:25:20','2026-11-05 05:25:15','2026-11-05 05:25:20');
/*!40000 ALTER TABLE `transcoding_worker_processed_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'transcoding_worker_db'
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
