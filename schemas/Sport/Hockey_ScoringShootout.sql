-- MySQL dump 10.13  Distrib 5.7.37, for Linux (x86_64)
--
-- Host: relational.fit.cvut.cz    Database: Hockey
-- ------------------------------------------------------
-- Server version	5.5.5-10.3.15-MariaDB-log

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
-- Table structure for table `ScoringShootout`
--

DROP TABLE IF EXISTS `ScoringShootout`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ScoringShootout` (
  `playerID` varchar(255) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `stint` int(11) DEFAULT NULL,
  `tmID` varchar(255) DEFAULT NULL,
  `S` int(11) DEFAULT NULL,
  `G` int(11) DEFAULT NULL,
  `GDG` int(11) DEFAULT NULL,
  KEY `ScoringShootout_playerID` (`playerID`) USING BTREE,
  KEY `ScoringShootout_year_tmID` (`year`,`tmID`) USING BTREE,
  CONSTRAINT `ScoringShootout_ibfk_1` FOREIGN KEY (`playerID`) REFERENCES `Master` (`playerID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ScoringShootout_ibfk_2` FOREIGN KEY (`year`, `tmID`) REFERENCES `Teams` (`year`, `tmID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-02-20 19:46:03
