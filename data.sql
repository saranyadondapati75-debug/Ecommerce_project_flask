-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: ecomdb
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
-- Table structure for table `admindata`
--

DROP TABLE IF EXISTS `admindata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admindata` (
  `adminid` binary(16) NOT NULL,
  `admin_username` varchar(50) NOT NULL,
  `admin_useremail` varchar(50) NOT NULL,
  `admin_address` tinytext NOT NULL,
  `admin_phoneno` varchar(10) DEFAULT NULL,
  `admin_image` varchar(20) DEFAULT NULL,
  `admin_agree` enum('on','off') DEFAULT NULL,
  `otp` char(6) DEFAULT NULL,
  `otp_expiry_time` datetime DEFAULT NULL,
  `account_status` enum('active','inactive','suspended') DEFAULT NULL,
  `admin_userpassword` varbinary(255) DEFAULT NULL,
  PRIMARY KEY (`adminid`),
  UNIQUE KEY `admin_useremail` (`admin_useremail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admindata`
--

LOCK TABLES `admindata` WRITE;
/*!40000 ALTER TABLE `admindata` DISABLE KEYS */;
INSERT INTO `admindata` VALUES (_binary '£Ks\ÿ¸\Ò∫[\n\0\'\0\0','Nikitha','siddamnikitha94@gmail.com','Vijayawada',NULL,NULL,'on',NULL,NULL,'active',_binary '$2b$12$vqiI17uEOkuGpjPmQaMxkeiAFaZO43FKOAaU/jfI6EMPSua24qXFW'),(_binary 'Óú§j\Œ\’\Ò±⁄Ω\ËUÓ≠î','Saranya','saranyadondapati75@gmail.com','ABC Colony',NULL,NULL,'on',NULL,NULL,'active',_binary '$2b$12$3a35uPLWi8MWsNbRH7WFPOojH7XrtPvLjBELCAWFBTeFoD6HBDj5.');
/*!40000 ALTER TABLE `admindata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `cartid` binary(16) NOT NULL,
  `itemid` binary(16) NOT NULL,
  `userid` binary(16) NOT NULL,
  `cart_quantity` int unsigned DEFAULT NULL,
  PRIMARY KEY (`cartid`),
  UNIQUE KEY `itemid` (`itemid`,`userid`),
  KEY `userid` (`userid`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`itemid`) REFERENCES `items` (`itemid`) ON DELETE CASCADE,
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `userdata` (`userid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `itemid` binary(16) NOT NULL,
  `item_name` longtext,
  `item_desc` longtext,
  `item_about` longtext,
  `item_price` decimal(20,4) DEFAULT NULL,
  `item_stock` int unsigned DEFAULT '1',
  `item_category` enum('home_appliences','Grocery','Fashion','Electronics','Sports','Toys') DEFAULT NULL,
  `item_imagename` varchar(20) DEFAULT NULL,
  `adminid` binary(16) DEFAULT NULL,
  `item_createdate` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`itemid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES (_binary '!\¬\ﬁ%\–˙\Ò≥g\—\‡\Ú≥','Men\'s Bomber Jacket Fashion Stylish Lightweight Windbreaker Spring Fall Casual Jackets for Men','Fabric typePolyester\r\nCare instructionsHand Wash Only\r\nOriginImported\r\n','XiaoYouYu Fabric: polyester; Lightweight, soft fabric for your comfort\r\nXiaoYouYu Design: 2 side pockets, 1 deep inner pocket\r\nXiaoYouYu Feature: ribbed collar, hem and cuffs, full zip, long sleeves for warmth and style\r\nXiaoYouYu Style: classic lightweight bomber jacket for men, easy to match, suitable for winter, autumn, spring.\r\nXiaoYouYu Occassion: not only suitable for daily wear, but also for work, street fashion, party and golf',990.0000,4,'Fashion','L0eN2q.jpg',_binary 'Óú§j\Œ\’\Ò±⁄Ω\ËUÓ≠î','2026-10-26 10:30:15'),(_binary 'k¿P\ÿA\Òò\n\0\'\0\0','medicube PDRN Collagen Volume Multi Balm Stick, Firming Face & Body Balm','This item cannot be shipped to your selected delivery location. Please choose a different delivery location.','Volufiline, NAD Stick Balm for the Look of Fine Lines, Under-Eyes, Neck, Plumping & Radiance for Line Care, Korean Skincare',700.0000,3,'Fashion','U4nA8c.jpg',_binary 'Óú§j\Œ\’\Ò±⁄Ω\ËUÓ≠î','2026-11-04 16:48:11'),(_binary 'pa>\ÿ\ﬁ\Òåb\n\0\'\0\0','Women Chunky Sneakers Lightweight Lace-Up Casual Sports Shoes Breathable Mesh Running Walking Shoes (Pink) - NID36763','Closure typeLace-Up\r\nHeel typeNo Heel\r\nWater resistance levelNot Water Resistant\r\nStyleSneaker\r\nOuter materialMesh\r\nInner materialMesh\r\nCountry of OriginIndia','Breathable & Lightweight : Crafted with air-flow materials to keep your feet cool and comfortable.\r\nSoft Cushioned Insole : Provides superior comfort and support for long hours of wear.\r\nVersatile Footwear Choice : Ideal for daily wear, office looks, weekend outings, or parties.\r\nPremium Build Quality : Durable stitching and finish ensure long-lasting wear and elegance.',536.0000,0,'Fashion','T2yY6z.jpg',_binary 'Óú§j\Œ\’\Ò±⁄Ω\ËUÓ≠î','2026-11-05 11:32:10'),(_binary 'Ü4\∆p\Œ\⁄\Ò±⁄Ω\ËUÓ≠î','10 inch Tablet with Keyboard - Android 16 Tablet with 24GB+256GB+2TB Expand 2026 Gemini AI Tablet PC with 8-Core, 5G WiFi, 8000mAh, GMS, GPS, 2-in-1 Electronic Tablet with Case, Mouse, Stylus (Pink)','Brand	PYNAREL\r\nModel Name	T901\r\nMemory Storage Capacity	2 TB\r\nScreen Size	10 inches\r\nDisplay Resolution Maximum	1280*800 pixels','Powerful Performance Combination: 24GB RAM + 256GB + 2TB Expansion„Äë This Android tablet comes with upgraded 24GB RAM (6GB+18GB virtual expansion) and 256GB large storage. This PYNAREL tablet\'s runs on a low-power 1.6GHz processor, ensuring faster and more stable running and data reading speed. Supporting up to Max 2TB microSD card expansion (card not included) , this tablets solves storage shortage issues for long-term use. With GMS certification, this 2026 tablet fully supports all Google apps for seamless downloading and browsing. Its generous memory configuration makes this tablet ideal for professional office work, online learning and all-day entertainment multitasking\r\n„ÄêAndroid 16 + Gemini AI: A New Benchmark for Smart and Smooth Performance„ÄëPYNAREL electronics tablet adopts the latest 2026 Android 16 OS with official Google GMS certification. This gaming tablet delivers personalized security protection, lightning-fast app launches and stunning Netflix multimedia experiences. Built-in Gemini AI engine empowers this AI google tablet with intelligent task optimization and faster app responses for smarter overall performance. Powered by the T606 octa-core processor, this tablet with Keyboard bundle ensures ultra-smooth and stable operation for multitasking, study, office work and daily applications',49989.0000,14,'Electronics','I3jD1y.jpg',_binary 'Óú§j\Œ\’\Ò±⁄Ω\ËUÓ≠î','2026-10-23 17:38:57');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `order_detailsid` int unsigned NOT NULL AUTO_INCREMENT,
  `orderid` int unsigned DEFAULT NULL,
  `itemid` binary(16) DEFAULT NULL,
  `item_name` longtext,
  `item_price` decimal(10,2) DEFAULT NULL,
  `item_quantity` int unsigned DEFAULT NULL,
  `sub_total` decimal(10,2) DEFAULT NULL,
  `item_category` enum('home_appliences','Grocery','Fashion','Electronics','Sports','Toys') DEFAULT NULL,
  `item_imagename` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`order_detailsid`),
  KEY `orderid` (`orderid`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`orderid`) REFERENCES `orders` (`orderid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,_binary '!\¬\ﬁ%\–˙\Ò≥g\—\‡\Ú≥','Men\'s Bomber Jacket Fashion Stylish Lightweight Windbreaker Spring Fall Casual Jackets for Men',990.00,5,4950.00,'Fashion','L0eN2q.jpg'),(2,1,_binary 'Ü4\∆p\Œ\⁄\Ò±⁄Ω\ËUÓ≠î','10 inch Tablet with Keyboard - Android 16 Tablet with 24GB+256GB+2TB Expand 2026 Gemini AI Tablet PC with 8-Core, 5G WiFi, 8000mAh, GMS, GPS, 2-in-1 Electronic Tablet with Case, Mouse, Stylus (Pink)',49989.00,2,99978.00,'Electronics','I3jD1y.jpg'),(3,2,_binary 'Ü4\∆p\Œ\⁄\Ò±⁄Ω\ËUÓ≠î','10 inch Tablet with Keyboard - Android 16 Tablet with 24GB+256GB+2TB Expand 2026 Gemini AI Tablet PC with 8-Core, 5G WiFi, 8000mAh, GMS, GPS, 2-in-1 Electronic Tablet with Case, Mouse, Stylus (Pink)',49989.00,1,49989.00,'Electronics','I3jD1y.jpg'),(4,3,_binary '\˝>ä\ÿ\ﬁ\Òåb\n\0\'\0\0','Arihant All in One English Core Class 12 for CBSE Exam 2026-27 | NCERT Based Complete Theory, Practice Exercises, CBQs, A-R, Sample Papers & Mind Maps | Revised Edition as per Latest Syllabus',15000.00,4,60000.00,'home_appliences','X1kU2c.jpg'),(5,3,_binary 'pa>\ÿ\ﬁ\Òåb\n\0\'\0\0','Women Chunky Sneakers Lightweight Lace-Up Casual Sports Shoes Breathable Mesh Running Walking Shoes (Pink) - NID36763',536.00,1,536.00,'Fashion','T2yY6z.jpg'),(6,3,_binary 'k¿P\ÿA\Òò\n\0\'\0\0','medicube PDRN Collagen Volume Multi Balm Stick, Firming Face & Body Balm',700.00,4,2800.00,'Fashion','U4nA8c.jpg'),(7,4,_binary '!\¬\ﬁ%\–˙\Ò≥g\—\‡\Ú≥','Men\'s Bomber Jacket Fashion Stylish Lightweight Windbreaker Spring Fall Casual Jackets for Men',990.00,1,990.00,'Fashion','L0eN2q.jpg'),(8,5,_binary 'k¿P\ÿA\Òò\n\0\'\0\0','medicube PDRN Collagen Volume Multi Balm Stick, Firming Face & Body Balm',700.00,3,2100.00,'Fashion','U4nA8c.jpg'),(9,5,_binary 'Ü4\∆p\Œ\⁄\Ò±⁄Ω\ËUÓ≠î','10 inch Tablet with Keyboard - Android 16 Tablet with 24GB+256GB+2TB Expand 2026 Gemini AI Tablet PC with 8-Core, 5G WiFi, 8000mAh, GMS, GPS, 2-in-1 Electronic Tablet with Case, Mouse, Stylus (Pink)',49989.00,3,149967.00,'Electronics','I3jD1y.jpg'),(10,5,_binary '\˝>ä\ÿ\ﬁ\Òåb\n\0\'\0\0','Arihant All in One English Core Class 12 for CBSE Exam 2026-27 | NCERT Based Complete Theory, Practice Exercises, CBQs, A-R, Sample Papers & Mind Maps | Revised Edition as per Latest Syllabus',15000.00,4,60000.00,'home_appliences','X1kU2c.jpg');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `orderid` int unsigned NOT NULL AUTO_INCREMENT,
  `razorpay_ordid` varchar(255) DEFAULT NULL,
  `razorpay_payment` varchar(255) DEFAULT NULL,
  `userid` binary(16) DEFAULT NULL,
  `total_amount` decimal(20,4) DEFAULT NULL,
  `delivery` int unsigned DEFAULT '40',
  `tax` decimal(10,2) DEFAULT NULL,
  `grand_total` decimal(20,4) DEFAULT NULL,
  `status` varchar(6) DEFAULT 'paid',
  PRIMARY KEY (`orderid`),
  KEY `userid` (`userid`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `userdata` (`userid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'order_Tu0ExfYNN0Dzit','pay_Tu0FnK19ceQ3pi',_binary '\èÆ\Ú–ö\Òö6^î\ÕF\Ù\˜',104928.0000,40,5246.40,110214.4000,'paid'),(2,'order_TuOSeQkbdPsoe6','pay_TuOTij7yCHe2xp',_binary '\èÆ\Ú–ö\Òö6^î\ÕF\Ù\˜',49989.0000,40,2499.45,52528.4500,'paid'),(3,'order_TwP1fUrbqzRYJx','pay_TwP2vFNt36ErNm',_binary '\èÆ\Ú–ö\Òö6^î\ÕF\Ù\˜',63336.0000,40,3166.80,66542.8000,'paid'),(4,'order_TwRBOQor6BLQtf','pay_TwRC56dLkRShmI',_binary '\èÆ\Ú–ö\Òö6^î\ÕF\Ù\˜',990.0000,40,49.50,1079.5000,'paid'),(5,'order_TwRTBO0iAeKWIc','pay_TwRUPbH88QYaHY',_binary 'x4ôñ\ÿ˘\Ò∫[\n\0\'\0\0',212067.0000,40,10603.35,222710.3500,'paid');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userdata`
--

DROP TABLE IF EXISTS `userdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userdata` (
  `userid` binary(16) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `user_email` varchar(50) NOT NULL,
  `user_address` varchar(255) NOT NULL,
  `user_userpassword` varchar(255) NOT NULL,
  `user_phoneno` varchar(20) DEFAULT NULL,
  `otp` varchar(6) DEFAULT NULL,
  `otp_expiry_time` datetime DEFAULT NULL,
  `account_status` enum('inactive','active','suspended') DEFAULT NULL,
  `user_gender` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`userid`),
  UNIQUE KEY `user_email` (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userdata`
--

LOCK TABLES `userdata` WRITE;
/*!40000 ALTER TABLE `userdata` DISABLE KEYS */;
INSERT INTO `userdata` VALUES (_binary '\rS(ˇ–Ñ\Òö6^î\ÕF\Ù\˜','saranya','saranyadondapati75@gmail.com','vijayawada','Saranya@123','6303819716',NULL,NULL,'active',NULL),(_binary '\»Tï\ÿ\Î\Òåb\n\0\'\0\0','nikkitha','nikithasiddamsetti50@gmail.com','hyd','$2b$12$.I2loDUBJm9LGMqDpX39kexYelJXd4W24r.W9TsoYJircOzx8X/Gm','9878786766',NULL,NULL,'active','Female'),(_binary 'x4ôñ\ÿ˘\Ò∫[\n\0\'\0\0','Nikitha','siddamnikitha94@gmail.com','Vijayawada','$2b$12$CoQ05PtYtyVY4IVVJT.d8u8b8K0o/Us3OM8QHs8ugi3RxgsSZ0QnG','9005634567',NULL,NULL,'active','Female'),(_binary '\èÆ\Ú–ö\Òö6^î\ÕF\Ù\˜','saranya','saranyadondapati33@gmail.com','vijayawada','$2b$12$sFwyhhTMa.PByGerIlOLTOegBKPdBYK3p4nYNnry3Q2AsEVi51MP.','6303819716',NULL,NULL,'active',NULL);
/*!40000 ALTER TABLE `userdata` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-05 22:05:15
