-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: thumbnail_db
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
-- Table structure for table `thumbnail_records`
--

DROP TABLE IF EXISTS `thumbnail_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `thumbnail_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `job_id` varchar(36) NOT NULL,
  `video_id` varchar(36) NOT NULL,
  `profile` varchar(32) NOT NULL,
  `source_path` text NOT NULL,
  `thumbnail_path` text,
  `status` varchar(20) NOT NULL,
  `attempts` int NOT NULL,
  `error_message` text,
  `next_retry_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_thumbnail_job_id` (`job_id`),
  KEY `ix_thumbnail_records_status` (`status`),
  KEY `ix_thumbnail_records_job_id` (`job_id`),
  KEY `ix_thumbnail_records_video_id` (`video_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `thumbnail_records`
--

LOCK TABLES `thumbnail_records` WRITE;
/*!40000 ALTER TABLE `thumbnail_records` DISABLE KEYS */;
INSERT INTO `thumbnail_records` VALUES (1,'8eaf312d-bde1-47a9-b19d-b1561e8a88a1','9135161f-715c-41b5-b093-11e8bb2d126d','360p','transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/360p.mp4','thumbnails/9135161f-715c-41b5-b093-11e8bb2d126d/360p.jpg','completed',1,NULL,NULL,'2026-11-04 19:06:44','2026-11-04 19:06:45'),(2,'03d73133-3457-48eb-8270-8bd55f7d0e32','9135161f-715c-41b5-b093-11e8bb2d126d','480p','transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/480p.mp4','thumbnails/9135161f-715c-41b5-b093-11e8bb2d126d/480p.jpg','completed',1,NULL,NULL,'2026-11-04 19:06:45','2026-11-04 19:06:45'),(3,'174fe466-0510-4242-83a2-5ba3003a4128','9135161f-715c-41b5-b093-11e8bb2d126d','720p','transcoded/9135161f-715c-41b5-b093-11e8bb2d126d/720p.mp4','thumbnails/9135161f-715c-41b5-b093-11e8bb2d126d/720p.jpg','completed',1,NULL,NULL,'2026-11-04 19:06:45','2026-11-04 19:06:45'),(4,'94bbb868-8483-45b8-a36c-cdcdb55447f3','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','360p','transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/360p.mp4','thumbnails/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/360p.jpg','completed',1,NULL,NULL,'2026-11-04 19:19:07','2026-11-04 19:19:08'),(5,'ea627fa0-ebcc-4334-a481-5d399d16c4d1','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','480p','transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/480p.mp4','thumbnails/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/480p.jpg','completed',1,NULL,NULL,'2026-11-04 19:19:08','2026-11-04 19:19:08'),(6,'efe3e757-48a5-41a3-9c2a-c4ef958b8dd2','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','720p','transcoded/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/720p.mp4','thumbnails/e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e/720p.jpg','completed',1,NULL,NULL,'2026-11-04 19:19:08','2026-11-04 19:19:08'),(7,'a40f9dd9-3719-4535-86e0-8f6999655622','07b2cb50-80b8-46df-b436-04088893cbcc','480p','transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/480p.mp4','thumbnails/07b2cb50-80b8-46df-b436-04088893cbcc/480p.jpg','completed',1,NULL,NULL,'2026-11-05 05:25:06','2026-11-05 05:25:07'),(8,'a5954b7d-242c-4a61-ab51-1489694386bd','07b2cb50-80b8-46df-b436-04088893cbcc','720p','transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/720p.mp4','thumbnails/07b2cb50-80b8-46df-b436-04088893cbcc/720p.jpg','completed',1,NULL,NULL,'2026-11-05 05:25:18','2026-11-05 05:25:18'),(9,'e7554686-de19-457b-87e0-41d414cd8f90','07b2cb50-80b8-46df-b436-04088893cbcc','360p','transcoded/07b2cb50-80b8-46df-b436-04088893cbcc/360p.mp4','thumbnails/07b2cb50-80b8-46df-b436-04088893cbcc/360p.jpg','completed',1,NULL,NULL,'2026-11-05 05:25:28','2026-11-05 05:25:28');
/*!40000 ALTER TABLE `thumbnail_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'thumbnail_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-05 13:29:09
