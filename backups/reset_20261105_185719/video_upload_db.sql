-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: video_upload_db
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumed_events`
--

LOCK TABLES `consumed_events` WRITE;
/*!40000 ALTER TABLE `consumed_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `consumed_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upload_outbox_events`
--

DROP TABLE IF EXISTS `upload_outbox_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `upload_outbox_events` (
  `id` varchar(36) NOT NULL,
  `aggregate_id` varchar(36) NOT NULL,
  `event_type` varchar(100) NOT NULL,
  `payload_json` text NOT NULL,
  `created_at` datetime NOT NULL,
  `published_at` datetime DEFAULT NULL,
  `attempts` bigint NOT NULL,
  `last_error` text,
  PRIMARY KEY (`id`),
  KEY `ix_upload_outbox_events_published_at` (`published_at`),
  KEY `ix_upload_outbox_events_event_type` (`event_type`),
  KEY `ix_upload_outbox_events_aggregate_id` (`aggregate_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upload_outbox_events`
--

LOCK TABLES `upload_outbox_events` WRITE;
/*!40000 ALTER TABLE `upload_outbox_events` DISABLE KEYS */;
INSERT INTO `upload_outbox_events` VALUES ('54577814-c13c-42af-8a54-a545b600e6d5','9135161f-715c-41b5-b093-11e8bb2d126d','video.uploaded','{\"event_id\":\"54577814-c13c-42af-8a54-a545b600e6d5\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-04T14:18:57.982360+00:00\",\"video\":{\"id\":\"9135161f-715c-41b5-b093-11e8bb2d126d\",\"original_filename\":\"EXO-LUCKY_ONE.mp4\",\"storage_path\":\"3b53f6c99db04b64be7f8b60302030f0.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":54149671,\"sha256\":\"15fd38f0b8a6d6245ac83028dcbd7e5d302ad0cca30e5abb6487ce6167daff03\"}}','2026-11-04 14:18:58','2026-11-04 14:18:59',1,NULL),('6fd32a70-cf91-4ff9-9ec2-0fc9988a062b','f38ead32-f913-4ef3-ac87-e6fe084717fb','video.uploaded','{\"event_id\":\"6fd32a70-cf91-4ff9-9ec2-0fc9988a062b\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-03T17:46:33.099774+00:00\",\"video\":{\"id\":\"f38ead32-f913-4ef3-ac87-e6fe084717fb\",\"original_filename\":\"Bigbang.mp4\",\"storage_path\":\"D:\\\\Projects\\\\Distributed_Video_Processing\\\\docker\\\\media\\\\cda0875efa0a43dcbe1e918d61cac74e.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":33986021,\"sha256\":\"d5894dad4298152e251056f2d582bd307caef2de416a4f4e12384ba8e3669c6b\"}}','2026-11-03 17:46:33','2026-11-03 18:02:43',1,NULL),('817f6a33-ea9b-4145-9d35-42c1cc255eed','e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','video.uploaded','{\"event_id\":\"817f6a33-ea9b-4145-9d35-42c1cc255eed\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-04T19:18:55.461328+00:00\",\"video\":{\"id\":\"e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e\",\"original_filename\":\"cortis.mp4\",\"storage_path\":\"350c98094d3e4cc898717d757953ae81.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":2264976,\"sha256\":\"696e10112c896b4bd9f3a3e1e7914148269d76c5e1a778fd9fbc43bef5292f7e\"}}','2026-11-04 19:18:55','2026-11-04 19:18:57',1,NULL),('9d1c8933-14fa-45d9-978c-b09884d6d4c3','07b2cb50-80b8-46df-b436-04088893cbcc','video.uploaded','{\"event_id\":\"9d1c8933-14fa-45d9-978c-b09884d6d4c3\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-05T05:24:54.674208+00:00\",\"video\":{\"id\":\"07b2cb50-80b8-46df-b436-04088893cbcc\",\"original_filename\":\"video.mp4\",\"storage_path\":\"988c6b1d147b4c5d9cfe3888e5592c23.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":9259804,\"sha256\":\"76b6486abfc03905c048b56e6814417b8ea3c636433fd8174a78d2746749fa7a\"}}','2026-11-05 05:24:55','2026-11-05 05:24:56',1,NULL),('b142ab50-856a-432b-aa2d-6a4d2d686b58','a6b23a86-e7e1-442b-aa7b-01d9671f4744','video.uploaded','{\"event_id\":\"b142ab50-856a-432b-aa2d-6a4d2d686b58\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-03T18:25:24.063645+00:00\",\"video\":{\"id\":\"a6b23a86-e7e1-442b-aa7b-01d9671f4744\",\"original_filename\":\"LE-SSERAFIM.mp4\",\"storage_path\":\"fdf67e84631945399874a193cbfc2866.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":16364911,\"sha256\":\"8afc8ef5821d0653bed17ad417e86d97e04614eb40ab3d399501ca07e287c1bf\"}}','2026-11-03 18:25:24','2026-11-03 18:25:24',1,NULL),('ba3f91a4-e24e-40cb-98f2-2800e731ede8','2e166ffb-0307-437a-9edf-acf9fa8a3ee0','video.uploaded','{\"event_id\":\"ba3f91a4-e24e-40cb-98f2-2800e731ede8\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-03T19:37:47.805038+00:00\",\"video\":{\"id\":\"2e166ffb-0307-437a-9edf-acf9fa8a3ee0\",\"original_filename\":\"Rainy-day.mp4\",\"storage_path\":\"d697c01ca79c408fbacf78b4747d315b.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":1202708,\"sha256\":\"0f488f7e017d59f49565091a4ff5f323b92b2a5e5ccae5836602f436123f4404\"}}','2026-11-03 19:37:48','2026-11-03 19:37:48',1,NULL),('ef60e6fd-1937-4c80-85d8-4957907e3dab','01fff1cf-c5f8-4d1e-8b99-37b1d7d581a9','video.uploaded','{\"event_id\":\"ef60e6fd-1937-4c80-85d8-4957907e3dab\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-04T05:10:38.248171+00:00\",\"video\":{\"id\":\"01fff1cf-c5f8-4d1e-8b99-37b1d7d581a9\",\"original_filename\":\"BAD-ATEEZ.mp4\",\"storage_path\":\"25ffdd973c684ca884d376f8dd9824d4.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":13237264,\"sha256\":\"7cf6247040f08741a390f5f80bf960a4a9ac70fdd3845ebc2d7c4c0b83772eaf\"}}','2026-11-04 05:10:38','2026-11-04 05:10:39',1,NULL),('f2f3ab6f-4ff5-4e87-9f1f-c70890419763','c2158154-5df8-455a-888b-64f0b33851f0','video.uploaded','{\"event_id\":\"f2f3ab6f-4ff5-4e87-9f1f-c70890419763\",\"event_type\":\"video.uploaded\",\"occurred_at\":\"2026-11-03T17:44:28.809836+00:00\",\"video\":{\"id\":\"c2158154-5df8-455a-888b-64f0b33851f0\",\"original_filename\":\"exo_love_shot.mp4\",\"storage_path\":\"D:\\\\Projects\\\\Distributed_Video_Processing\\\\docker\\\\media\\\\4962d69e7b9b4b628c179656c181da06.mp4\",\"content_type\":\"video/mp4\",\"file_extension\":\".mp4\",\"file_size_bytes\":10685978,\"sha256\":\"f16e8b235554ce7c497e57bc9ed19dec0afbdd333a9bf1a915de148c6a505f88\"}}','2026-11-03 17:44:29','2026-11-03 18:02:43',527,NULL);
/*!40000 ALTER TABLE `upload_outbox_events` ENABLE KEYS */;
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
  KEY `ix_video_metadata_sha256` (`sha256`),
  KEY `ix_video_metadata_video_id` (`video_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `video_metadata`
--

LOCK TABLES `video_metadata` WRITE;
/*!40000 ALTER TABLE `video_metadata` DISABLE KEYS */;
/*!40000 ALTER TABLE `video_metadata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `videos`
--

DROP TABLE IF EXISTS `videos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `videos` (
  `id` varchar(36) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `stored_filename` varchar(255) NOT NULL,
  `storage_path` varchar(1024) NOT NULL,
  `content_type` varchar(100) NOT NULL,
  `file_extension` varchar(12) NOT NULL,
  `file_size_bytes` bigint NOT NULL,
  `sha256` varchar(64) NOT NULL,
  `status` varchar(32) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_videos_sha256` (`sha256`),
  UNIQUE KEY `stored_filename` (`stored_filename`),
  KEY `ix_videos_sha256` (`sha256`),
  KEY `ix_videos_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `videos`
--

LOCK TABLES `videos` WRITE;
/*!40000 ALTER TABLE `videos` DISABLE KEYS */;
INSERT INTO `videos` VALUES ('01fff1cf-c5f8-4d1e-8b99-37b1d7d581a9','BAD-ATEEZ.mp4','25ffdd973c684ca884d376f8dd9824d4.mp4','25ffdd973c684ca884d376f8dd9824d4.mp4','video/mp4','.mp4',13237264,'7cf6247040f08741a390f5f80bf960a4a9ac70fdd3845ebc2d7c4c0b83772eaf','uploaded','2026-11-04 05:10:38','2026-11-04 05:10:38'),('07b2cb50-80b8-46df-b436-04088893cbcc','video.mp4','988c6b1d147b4c5d9cfe3888e5592c23.mp4','988c6b1d147b4c5d9cfe3888e5592c23.mp4','video/mp4','.mp4',9259804,'76b6486abfc03905c048b56e6814417b8ea3c636433fd8174a78d2746749fa7a','uploaded','2026-11-05 05:24:55','2026-11-05 05:24:55'),('2e166ffb-0307-437a-9edf-acf9fa8a3ee0','Rainy-day.mp4','d697c01ca79c408fbacf78b4747d315b.mp4','d697c01ca79c408fbacf78b4747d315b.mp4','video/mp4','.mp4',1202708,'0f488f7e017d59f49565091a4ff5f323b92b2a5e5ccae5836602f436123f4404','uploaded','2026-11-03 19:37:48','2026-11-03 19:37:48'),('9135161f-715c-41b5-b093-11e8bb2d126d','EXO-LUCKY_ONE.mp4','3b53f6c99db04b64be7f8b60302030f0.mp4','3b53f6c99db04b64be7f8b60302030f0.mp4','video/mp4','.mp4',54149671,'15fd38f0b8a6d6245ac83028dcbd7e5d302ad0cca30e5abb6487ce6167daff03','uploaded','2026-11-04 14:18:58','2026-11-04 14:18:58'),('a6b23a86-e7e1-442b-aa7b-01d9671f4744','LE-SSERAFIM.mp4','fdf67e84631945399874a193cbfc2866.mp4','fdf67e84631945399874a193cbfc2866.mp4','video/mp4','.mp4',16364911,'8afc8ef5821d0653bed17ad417e86d97e04614eb40ab3d399501ca07e287c1bf','uploaded','2026-11-03 18:25:24','2026-11-03 18:25:24'),('c2158154-5df8-455a-888b-64f0b33851f0','exo_love_shot.mp4','4962d69e7b9b4b628c179656c181da06.mp4','D:\\Projects\\Distributed_Video_Processing\\docker\\media\\4962d69e7b9b4b628c179656c181da06.mp4','video/mp4','.mp4',10685978,'f16e8b235554ce7c497e57bc9ed19dec0afbdd333a9bf1a915de148c6a505f88','uploaded','2026-11-03 17:44:29','2026-11-03 17:44:29'),('e494b9e7-b75e-412a-b5f8-f2e0b0d5d32e','cortis.mp4','350c98094d3e4cc898717d757953ae81.mp4','350c98094d3e4cc898717d757953ae81.mp4','video/mp4','.mp4',2264976,'696e10112c896b4bd9f3a3e1e7914148269d76c5e1a778fd9fbc43bef5292f7e','uploaded','2026-11-04 19:18:55','2026-11-04 19:18:55'),('f38ead32-f913-4ef3-ac87-e6fe084717fb','Bigbang.mp4','cda0875efa0a43dcbe1e918d61cac74e.mp4','D:\\Projects\\Distributed_Video_Processing\\docker\\media\\cda0875efa0a43dcbe1e918d61cac74e.mp4','video/mp4','.mp4',33986021,'d5894dad4298152e251056f2d582bd307caef2de416a4f4e12384ba8e3669c6b','uploaded','2026-11-03 17:46:33','2026-11-03 17:46:33');
/*!40000 ALTER TABLE `videos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'video_upload_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-05 13:29:06
