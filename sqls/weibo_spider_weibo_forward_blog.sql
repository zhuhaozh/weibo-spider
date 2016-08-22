-- MySQL dump 10.13  Distrib 5.7.13, for Linux (x86_64)
--
-- Host: localhost    Database: weibo_spider
-- ------------------------------------------------------
-- Server version	5.7.13-0ubuntu0.16.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `weibo_forward_blog`
--

DROP TABLE IF EXISTS `weibo_forward_blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weibo_forward_blog` (
  `wfbid` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` varchar(40) DEFAULT NULL,
  `like_num` int(11) DEFAULT NULL,
  `comment_num` int(11) DEFAULT NULL,
  `forward_num` int(11) DEFAULT NULL,
  `pic_num` int(11) DEFAULT NULL,
  `original_like_num` int(11) DEFAULT NULL,
  `original_comment_num` int(11) DEFAULT NULL,
  `original_forward_num` int(11) DEFAULT NULL,
  `original_pic_num` int(11) DEFAULT NULL,
  `via` varchar(50) DEFAULT NULL,
  `original_owner_id` varchar(30) DEFAULT NULL,
  `original_content` varchar(255) DEFAULT NULL,
  `forward_owner_id` varchar(30) DEFAULT NULL,
  `forward_content` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`wfbid`)
) ENGINE=InnoDB AUTO_INCREMENT=497 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weibo_forward_blog`
--

LOCK TABLES `weibo_forward_blog` WRITE;
/*!40000 ALTER TABLE `weibo_forward_blog` DISABLE KEYS */;
/*!40000 ALTER TABLE `weibo_forward_blog` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-08-20 11:33:20
