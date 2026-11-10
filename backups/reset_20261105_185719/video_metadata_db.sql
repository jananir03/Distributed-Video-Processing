-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: video_metadata_db
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
-- Table structure for table `consumed_events`
--

DROP TABLE IF EXISTS `consumed_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumed_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` varchar(36) NOT NULL,
  `event_type` varchar(100) NOT NULL,
  `video_id` varchar(36) NOT NULL,
  `processed_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_consumed_events_event_id` (`event_id`),
  KEY `ix_consumed_events_video_id` (`video_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumed_events`
--

LOCK TABLES `consumed_events` WRITE;
/*!40000 ALTER TABLE `consumed_events` DISABLE KEYS */;
INSERT INTO `consumed_events` VALUES (1,'ba3f91a4-e24e-40cb-98f2-2800e731ede8','video.uploaded','2e166ffb-0307-437a-9edf-acf9fa8a3ee0','2026-11-03 19:37:48'),(2,'ef60e6fd-1937-4c80-85d8-4957907e3dab','video.uploaded','01fff1cf-c5f8-4d1e-8b99-37b1d7d581a9','2026-11-04 05:10:39'),(3,'6fd32a70-cf91-4ff9-9ec2-0fc9988a062b','video.uploaded','f38ead32-f913-4ef3-ac87-e6fe084717fb','2026-11-04 06:59:40'),(4,'b142ab50-856a-432b-aa2d-6a4d2d686b58','video.uploaded','a6b23a86-e7e1-442b-aa7b-01d9671f4744','2026-11-04 06:59:40'),(5,'f2f3ab6f-4ff5-4e87-9f1f-c70890419763','video.uploaded','c2158154-5df8-455a-888b-64f0b33851f0','2026-11-04 06:59:40'),(6,'54577814-c13c-42af-8a54-a545b600e6d5','video.uploaded','9135161f-715c-41b5-b093-11e8bb2d126d','2026-11-04 14:19:00'),(7,'817f6a33-ea9b-4145-9d35-42c1cc255eed','video.uploaded','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','2026-11-04 19:18:57'),(8,'9d1c8933-14fa-45d9-978c-b09884d6d4c3','video.uploaded','07b2cb50-80b8-46df-b436-04088893cbcc','2026-11-05 05:24:56');
/*!40000 ALTER TABLE `consumed_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `video_metadata`
--

DROP TABLE IF EXISTS `video_metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `video_metadata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `video_id` varchar(36) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `storage_path` varchar(1024) NOT NULL,
  `content_type` varchar(100) NOT NULL,
  `file_extension` varchar(20) NOT NULL,
  `file_size_bytes` bigint NOT NULL,
  `sha256` varchar(64) NOT NULL,
  `source_event_id` varchar(36) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_video_metadata_video_id` (`video_id`),
  KEY `ix_video_metadata_video_id` (`video_id`),
  KEY `ix_video_metadata_sha256` (`sha256`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `video_metadata`
--

LOCK TABLES `video_metadata` WRITE;
/*!40000 ALTER TABLE `video_metadata` DISABLE KEYS */;
INSERT INTO `video_metadata` VALUES (1,'2e166ffb-0307-437a-9edf-acf9fa8a3ee0','Rainy-day.mp4','/app/media/d697c01ca79c408fbacf78b4747d315b.mp4','video/mp4','.mp4',1202708,'0f488f7e017d59f49565091a4ff5f323b92b2a5e5ccae5836602f436123f4404','ba3f91a4-e24e-40cb-98f2-2800e731ede8','2026-11-03 19:37:48','2026-11-03 19:37:48'),(2,'01fff1cf-c5f8-4d1e-8b99-37b1d7d581a9','BAD-ATEEZ.mp4','/app/media/25ffdd973c684ca884d376f8dd9824d4.mp4','video/mp4','.mp4',13237264,'7cf6247040f08741a390f5f80bf960a4a9ac70fdd3845ebc2d7c4c0b83772eaf','ef60e6fd-1937-4c80-85d8-4957907e3dab','2026-11-04 05:10:39','2026-11-04 05:10:39'),(3,'f38ead32-f913-4ef3-ac87-e6fe084717fb','Bigbang.mp4','/app/media/cda0875efa0a43dcbe1e918d61cac74e.mp4','video/mp4','.mp4',33986021,'d5894dad4298152e251056f2d582bd307caef2de416a4f4e12384ba8e3669c6b','6fd32a70-cf91-4ff9-9ec2-0fc9988a062b','2026-11-04 06:59:40','2026-11-04 06:59:40'),(4,'a6b23a86-e7e1-442b-aa7b-01d9671f4744','LE-SSERAFIM.mp4','/app/media/fdf67e84631945399874a193cbfc2866.mp4','video/mp4','.mp4',16364911,'8afc8ef5821d0653bed17ad417e86d97e04614eb40ab3d399501ca07e287c1bf','b142ab50-856a-432b-aa2d-6a4d2d686b58','2026-11-04 06:59:40','2026-11-04 06:59:40'),(5,'c2158154-5df8-455a-888b-64f0b33851f0','exo_love_shot.mp4','/app/media/4962d69e7b9b4b628c179656c181da06.mp4','video/mp4','.mp4',10685978,'f16e8b235554ce7c497e57bc9ed19dec0afbdd333a9bf1a915de148c6a505f88','f2f3ab6f-4ff5-4e87-9f1f-c70890419763','2026-11-04 06:59:40','2026-11-04 06:59:40'),(6,'9135161f-715c-41b5-b093-11e8bb2d126d','EXO-LUCKY_ONE.mp4','/app/media/3b53f6c99db04b64be7f8b60302030f0.mp4','video/mp4','.mp4',54149671,'15fd38f0b8a6d6245ac83028dcbd7e5d302ad0cca30e5abb6487ce6167daff03','54577814-c13c-42af-8a54-a545b600e6d5','2026-11-04 14:19:00','2026-11-04 14:19:00'),(7,'e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','cortis.mp4','/app/media/350c98094d3e4cc898717d757953ae81.mp4','video/mp4','.mp4',2264976,'696e10112c896b4bd9f3a3e1e7914148269d76c5e1a778fd9fbc43bef5292f7e','817f6a33-ea9b-4145-9d35-42c1cc255eed','2026-11-04 19:18:57','2026-11-04 19:18:57'),(8,'07b2cb50-80b8-46df-b436-04088893cbcc','video.mp4','/app/media/988c6b1d147b4c5d9cfe3888e5592c23.mp4','video/mp4','.mp4',9259804,'76b6486abfc03905c048b56e6814417b8ea3c636433fd8174a78d2746749fa7a','9d1c8933-14fa-45d9-978c-b09884d6d4c3','2026-11-05 05:24:56','2026-11-05 05:24:56');
/*!40000 ALTER TABLE `video_metadata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'video_metadata_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-05 13:29:07
