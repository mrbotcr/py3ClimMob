-- MySQL dump 10.13  Distrib 8.0.21, for Linux (x86_64)
--
-- Host: localhost    Database: climmobv4
-- ------------------------------------------------------
-- Server version	8.0.21-0ubuntu0.20.04.4

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
-- Table structure for table `activitylog`
--

DROP TABLE IF EXISTS `activitylog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activitylog` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `log_user` varchar(80) NOT NULL,
  `log_datetime` datetime DEFAULT NULL,
  `log_type` varchar(3) DEFAULT NULL,
  `log_message` text,
  PRIMARY KEY (`log_id`),
  KEY `ix_activitylog_log_user` (`log_user`),
  CONSTRAINT `fk_activitylog_user1` FOREIGN KEY (`log_user`) REFERENCES `user` (`user_name`)
) ENGINE=InnoDB AUTO_INCREMENT=288 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activitylog`
--

LOCK TABLES `activitylog` WRITE;
/*!40000 ALTER TABLE `activitylog` DISABLE KEYS */;
/*!40000 ALTER TABLE `activitylog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('ac44678ec11e');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apilog`
--

DROP TABLE IF EXISTS `apilog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apilog` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `log_datetime` datetime DEFAULT NULL,
  `log_ip` varchar(45) DEFAULT NULL,
  `log_user` varchar(80) NOT NULL,
  `log_uuid` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `ix_apilog_log_user` (`log_user`),
  CONSTRAINT `fk_apilog_user1` FOREIGN KEY (`log_user`) REFERENCES `user` (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apilog`
--

LOCK TABLES `apilog` WRITE;
/*!40000 ALTER TABLE `apilog` DISABLE KEYS */;
/*!40000 ALTER TABLE `apilog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assdetail`
--

DROP TABLE IF EXISTS `assdetail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assdetail` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `ass_cod` varchar(80) NOT NULL,
  `question_id` int NOT NULL,
  `section_user` varchar(80) NOT NULL,
  `section_project` varchar(80) NOT NULL,
  `section_assessment` varchar(80) NOT NULL,
  `section_id` int NOT NULL,
  `question_order` int DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`ass_cod`,`question_id`),
  KEY `fk_assdetail_section_user_asssection` (`section_user`,`section_project`,`section_assessment`,`section_id`),
  KEY `fk_assessment_asssection1_idx` (`section_user`,`section_project`,`section_id`),
  KEY `ix_assdetail_question_id` (`question_id`),
  CONSTRAINT `fk_assdetail_question_id_question` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_assdetail_section_user_asssection` FOREIGN KEY (`section_user`, `section_project`, `section_assessment`, `section_id`) REFERENCES `asssection` (`user_name`, `project_cod`, `ass_cod`, `section_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_assdetail_user_name_assessment` FOREIGN KEY (`user_name`, `project_cod`, `ass_cod`) REFERENCES `assessment` (`user_name`, `project_cod`, `ass_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assdetail`
--

LOCK TABLES `assdetail` WRITE;
/*!40000 ALTER TABLE `assdetail` DISABLE KEYS */;
/*!40000 ALTER TABLE `assdetail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assesment_jsonlog`
--

DROP TABLE IF EXISTS `assesment_jsonlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assesment_jsonlog` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `ass_cod` varchar(80) NOT NULL,
  `log_id` varchar(64) NOT NULL,
  `log_dtime` datetime DEFAULT NULL,
  `json_file` text,
  `log_file` text,
  `status` int DEFAULT NULL,
  `enum_id` varchar(80) NOT NULL,
  `enum_user` varchar(80) NOT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`ass_cod`,`log_id`),
  KEY `fk_assesment_jsonlog_enum_user_enumerator` (`enum_user`,`enum_id`),
  CONSTRAINT `fk_assesment_jsonlog_enum_user_enumerator` FOREIGN KEY (`enum_user`, `enum_id`) REFERENCES `enumerator` (`user_name`, `enum_id`),
  CONSTRAINT `fk_assesment_jsonlog_user_name_assessment` FOREIGN KEY (`user_name`, `project_cod`, `ass_cod`) REFERENCES `assessment` (`user_name`, `project_cod`, `ass_cod`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assesment_jsonlog`
--

LOCK TABLES `assesment_jsonlog` WRITE;
/*!40000 ALTER TABLE `assesment_jsonlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `assesment_jsonlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessment`
--

DROP TABLE IF EXISTS `assessment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessment` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `ass_cod` varchar(80) NOT NULL,
  `ass_desc` varchar(120) DEFAULT NULL,
  `ass_days` int DEFAULT NULL,
  `ass_status` int DEFAULT '0',
  `ass_final` int DEFAULT '0',
  PRIMARY KEY (`user_name`,`project_cod`,`ass_cod`),
  CONSTRAINT `fk_assessment_user_name_project` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessment`
--

LOCK TABLES `assessment` WRITE;
/*!40000 ALTER TABLE `assessment` DISABLE KEYS */;
/*!40000 ALTER TABLE `assessment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `asssection`
--

DROP TABLE IF EXISTS `asssection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asssection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `ass_cod` varchar(80) NOT NULL,
  `section_id` int NOT NULL,
  `section_name` varchar(120) DEFAULT NULL,
  `section_content` text,
  `section_order` int DEFAULT NULL,
  `section_private` int DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`ass_cod`,`section_id`),
  CONSTRAINT `fk_asssection_user_name_assessment` FOREIGN KEY (`user_name`, `project_cod`, `ass_cod`) REFERENCES `assessment` (`user_name`, `project_cod`, `ass_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asssection`
--

LOCK TABLES `asssection` WRITE;
/*!40000 ALTER TABLE `asssection` DISABLE KEYS */;
/*!40000 ALTER TABLE `asssection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat`
--

DROP TABLE IF EXISTS `chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat` (
  `user_name` varchar(80) NOT NULL,
  `chat_id` int NOT NULL,
  `chat_message` varchar(500) DEFAULT NULL,
  `chat_send` int DEFAULT NULL,
  `chat_read` int DEFAULT NULL,
  `chat_tofrom` int DEFAULT NULL,
  `chat_date` datetime DEFAULT NULL,
  PRIMARY KEY (`user_name`,`chat_id`),
  CONSTRAINT `fk_chat_user_name_user` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat`
--

LOCK TABLES `chat` WRITE;
/*!40000 ALTER TABLE `chat` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `country`
--

DROP TABLE IF EXISTS `country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `country` (
  `cnty_cod` varchar(3) NOT NULL,
  `cnty_name` varchar(120) DEFAULT NULL,
  `cnty_iso` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`cnty_cod`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `country`
--

LOCK TABLES `country` WRITE;
/*!40000 ALTER TABLE `country` DISABLE KEYS */;
INSERT INTO `country` VALUES ('AD','Andorra',NULL),('AE','United Arab Emirates',NULL),('AF','Afghanistan2',NULL),('AG','Antigua and Barbuda',NULL),('AI','Anguilla',NULL),('AL','Albania',NULL),('AM','Armenia',NULL),('AO','Angola',NULL),('AQ','Antarctica',NULL),('AR','Argentina',NULL),('AS','American Samoa',NULL),('AT','Austria',NULL),('AU','Australia',NULL),('AW','Aruba',NULL),('AX','Åland Islands',NULL),('AZ','Azerbaijan',NULL),('BA','Bosnia and Herzegovina',NULL),('BB','Barbados',NULL),('BD','Bangladesh',NULL),('BE','Belgium',NULL),('BF','Burkina Faso',NULL),('BG','Bulgaria',NULL),('BH','Bahrain',NULL),('BI','Burundi',NULL),('BJ','Benin',NULL),('BL','Saint Barthélemy',NULL),('BM','Bermuda',NULL),('BN','Brunei Darussalam',NULL),('BO','Bolivia',NULL),('BQ','Caribbean Netherlands ',NULL),('BR','Brazil',NULL),('BS','Bahamas',NULL),('BT','Bhutan',NULL),('BV','Bouvet Island',NULL),('BW','Botswana',NULL),('BY','Belarus',NULL),('BZ','Belize',NULL),('CA','Canada',NULL),('CC','Cocos (Keeling) Islands',NULL),('CD','Congo, Democratic Republic of',NULL),('CF','Central African Republic',NULL),('CG','Congo',NULL),('CH','Switzerland',NULL),('CI','Côte d\'Ivoire',NULL),('CK','Cook Islands',NULL),('CL','Chile',NULL),('CM','Cameroon',NULL),('CN','China',NULL),('CO','Colombia',NULL),('CR','Costa Rica',NULL),('CU','Cuba',NULL),('CV','Cape Verde',NULL),('CW','Curaçao',NULL),('CX','Christmas Island',NULL),('CY','Cyprus',NULL),('CZ','Czech Republic',NULL),('DE','Germany',NULL),('DJ','Djibouti',NULL),('DK','Denmark',NULL),('DM','Dominica',NULL),('DO','Dominican Republic',NULL),('DZ','Algeria',NULL),('EC','Ecuador',NULL),('EE','Estonia',NULL),('EG','Egypt',NULL),('EH','Western Sahara',NULL),('ER','Eritrea',NULL),('ES','Spain',NULL),('ET','Ethiopia',NULL),('FI','Finland',NULL),('FJ','Fiji',NULL),('FK','Falkland Islands',NULL),('FM','Micronesia, Federated States of',NULL),('FO','Faroe Islands',NULL),('FR','France',NULL),('GA','Gabon',NULL),('GB','United Kingdom',NULL),('GD','Grenada',NULL),('GE','Georgia',NULL),('GF','French Guiana',NULL),('GG','Guernsey',NULL),('GH','Ghana',NULL),('GI','Gibraltar',NULL),('GL','Greenland',NULL),('GM','Gambia',NULL),('GN','Guinea',NULL),('GP','Guadeloupe',NULL),('GQ','Equatorial Guinea',NULL),('GR','Greece',NULL),('GS','South Georgia and the South Sandwich Islands',NULL),('GT','Guatemala',NULL),('GU','Guam',NULL),('GW','Guinea-Bissau',NULL),('GY','Guyana',NULL),('HK','Hong Kong',NULL),('HM','Heard and McDonald Islands',NULL),('HN','Honduras',NULL),('HR','Croatia',NULL),('HT','Haiti',NULL),('HU','Hungary',NULL),('ID','Indonesia',NULL),('IE','Ireland',NULL),('IL','Israel',NULL),('IM','Isle of Man',NULL),('IN','India',NULL),('IO','British Indian Ocean Territory',NULL),('IQ','Iraq',NULL),('IR','Iran',NULL),('IS','Iceland',NULL),('IT','Italy',NULL),('JE','Jersey',NULL),('JM','Jamaica',NULL),('JO','Jordan',NULL),('JP','Japan',NULL),('KE','Kenya',NULL),('KG','Kyrgyzstan',NULL),('KH','Cambodia',NULL),('KI','Kiribati',NULL),('KM','Comoros',NULL),('KN','Saint Kitts and Nevis',NULL),('KP','North Korea',NULL),('KR','South Korea',NULL),('KW','Kuwait',NULL),('KY','Cayman Islands',NULL),('KZ','Kazakhstan',NULL),('LA','Lao People\'s Democratic Republic',NULL),('LB','Lebanon',NULL),('LC','Saint Lucia',NULL),('LI','Liechtenstein',NULL),('LK','Sri Lanka',NULL),('LR','Liberia',NULL),('LS','Lesotho',NULL),('LT','Lithuania',NULL),('LU','Luxembourg',NULL),('LV','Latvia',NULL),('LY','Libya',NULL),('MA','Morocco',NULL),('MC','Monaco',NULL),('MD','Moldova',NULL),('ME','Montenegro',NULL),('MF','Saint-Martin (France)',NULL),('MG','Madagascar',NULL),('MH','Marshall Islands',NULL),('MK','Macedonia',NULL),('ML','Mali',NULL),('MM','Myanmar',NULL),('MN','Mongolia',NULL),('MO','Macau',NULL),('MP','Northern Mariana Islands',NULL),('MQ','Martinique',NULL),('MR','Mauritania',NULL),('MS','Montserrat',NULL),('MT','Malta',NULL),('MU','Mauritius',NULL),('MV','Maldives',NULL),('MW','Malawi',NULL),('MX','Mexico',NULL),('MY','Malaysia',NULL),('MZ','Mozambique',NULL),('NA','Namibia',NULL),('NC','New Caledonia',NULL),('NE','Niger',NULL),('NF','Norfolk Island',NULL),('NG','Nigeria',NULL),('NI','Nicaragua',NULL),('NL','The Netherlands',NULL),('NO','Norway',NULL),('NP','Nepal',NULL),('NR','Nauru',NULL),('NU','Niue',NULL),('NZ','New Zealand',NULL),('OM','Oman',NULL),('PA','Panama',NULL),('PE','Peru',NULL),('PF','French Polynesia',NULL),('PG','Papua New Guinea',NULL),('PH','Philippines',NULL),('PK','Pakistan',NULL),('PL','Poland',NULL),('PM','St. Pierre and Miquelon',NULL),('PN','Pitcairn',NULL),('PR','Puerto Rico',NULL),('PS','Palestine, State of',NULL),('PT','Portugal',NULL),('PW','Palau',NULL),('PY','Paraguay',NULL),('QA','Qatar',NULL),('RE','Réunion',NULL),('RO','Romania',NULL),('RS','Serbia',NULL),('RU','Russian Federation',NULL),('RW','Rwanda',NULL),('SA','Saudi Arabia',NULL),('SB','Solomon Islands',NULL),('SC','Seychelles',NULL),('SD','Sudan',NULL),('SE','Sweden',NULL),('SG','Singapore',NULL),('SH','Saint Helena',NULL),('SI','Slovenia',NULL),('SJ','Svalbard and Jan Mayen Islands',NULL),('SK','Slovakia',NULL),('SL','Sierra Leone',NULL),('SM','San Marino',NULL),('SN','Senegal',NULL),('SO','Somalia',NULL),('SR','Suriname',NULL),('SS','South Sudan',NULL),('ST','Sao Tome and Principe',NULL),('SV','El Salvador',NULL),('SX','Sint Maarten (Dutch part)',NULL),('SY','Syria',NULL),('SZ','Swaziland',NULL),('TC','Turks and Caicos Islands',NULL),('TD','Chad',NULL),('TF','French Southern Territories',NULL),('TG','Togo',NULL),('TH','Thailand',NULL),('TJ','Tajikistan',NULL),('TK','Tokelau',NULL),('TL','Timor-Leste',NULL),('TM','Turkmenistan',NULL),('TN','Tunisia',NULL),('TO','Tonga',NULL),('TR','Turkey',NULL),('TT','Trinidad and Tobago',NULL),('TV','Tuvalu',NULL),('TW','Taiwan',NULL),('TZ','Tanzania',NULL),('UA','Ukraine',NULL),('UG','Uganda',NULL),('UM','United States Minor Outlying Islands',NULL),('US','United States',NULL),('UY','Uruguay',NULL),('UZ','Uzbekistan',NULL),('VA','Vatican',NULL),('VC','Saint Vincent and the Grenadines',NULL),('VE','Venezuela',NULL),('VG','Virgin Islands (British)',NULL),('VI','Virgin Islands (U.S.)',NULL),('VN','Vietnam',NULL),('VU','Vanuatu',NULL),('WF','Wallis and Futuna Islands',NULL),('WS','Samoa',NULL),('YE','Yemen',NULL),('YT','Mayotte',NULL),('ZA','South Africa',NULL),('ZM','Zambia',NULL),('ZW','Zimbabwe',NULL);
/*!40000 ALTER TABLE `country` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enumerator`
--

DROP TABLE IF EXISTS `enumerator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enumerator` (
  `user_name` varchar(80) NOT NULL,
  `enum_id` varchar(80) NOT NULL,
  `enum_name` varchar(120) DEFAULT NULL,
  `enum_password` varchar(80) DEFAULT NULL,
  `enum_active` tinyint DEFAULT NULL,
  PRIMARY KEY (`user_name`,`enum_id`),
  CONSTRAINT `fk_enumerator_user_name_user` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enumerator`
--

LOCK TABLES `enumerator` WRITE;
/*!40000 ALTER TABLE `enumerator` DISABLE KEYS */;
/*!40000 ALTER TABLE `enumerator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finishedtasks`
--

DROP TABLE IF EXISTS `finishedtasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finishedtasks` (
  `taskid` varchar(80) NOT NULL,
  `taskerror` int DEFAULT NULL,
  PRIMARY KEY (`taskid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finishedtasks`
--

LOCK TABLES `finishedtasks` WRITE;
/*!40000 ALTER TABLE `finishedtasks` DISABLE KEYS */;
/*!40000 ALTER TABLE `finishedtasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n`
--

DROP TABLE IF EXISTS `i18n`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n` (
  `lang_code` varchar(5) NOT NULL,
  `lang_name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`lang_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n`
--

LOCK TABLES `i18n` WRITE;
/*!40000 ALTER TABLE `i18n` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_asssection`
--

DROP TABLE IF EXISTS `i18n_asssection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_asssection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `ass_cod` varchar(80) NOT NULL,
  `section_id` int NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `section_name` varchar(120) DEFAULT NULL,
  `section_content` text,
  PRIMARY KEY (`user_name`,`project_cod`,`ass_cod`,`section_id`,`lang_code`),
  KEY `ix_i18n_asssection_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_asssection_lang_code_i18n` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_asssection_user_name_asssection` FOREIGN KEY (`user_name`, `project_cod`, `ass_cod`, `section_id`) REFERENCES `asssection` (`user_name`, `project_cod`, `ass_cod`, `section_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_asssection`
--

LOCK TABLES `i18n_asssection` WRITE;
/*!40000 ALTER TABLE `i18n_asssection` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_asssection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_prjalias`
--

DROP TABLE IF EXISTS `i18n_prjalias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_prjalias` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int NOT NULL,
  `alias_id` int NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`tech_id`,`alias_id`,`lang_code`),
  KEY `ix_i18n_prjalias_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_prjalias_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_prjalias_prjalias1` FOREIGN KEY (`user_name`, `project_cod`, `tech_id`, `alias_id`) REFERENCES `prjalias` (`user_name`, `project_cod`, `tech_id`, `alias_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_prjalias`
--

LOCK TABLES `i18n_prjalias` WRITE;
/*!40000 ALTER TABLE `i18n_prjalias` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_prjalias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_project`
--

DROP TABLE IF EXISTS `i18n_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_project` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `project_name` varchar(120) DEFAULT NULL,
  `project_abstract` text,
  PRIMARY KEY (`user_name`,`project_cod`,`lang_code`),
  KEY `ix_i18n_project_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_project_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_project_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_project`
--

LOCK TABLES `i18n_project` WRITE;
/*!40000 ALTER TABLE `i18n_project` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_qstoption`
--

DROP TABLE IF EXISTS `i18n_qstoption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_qstoption` (
  `question_id` int NOT NULL,
  `value_code` varchar(80) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `value_desc` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`question_id`,`value_code`,`lang_code`),
  KEY `ix_i18n_qstoption_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_qstoption_lang_code_i18n` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_qstoption_question_id_qstoption` FOREIGN KEY (`question_id`, `value_code`) REFERENCES `qstoption` (`question_id`, `value_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_qstoption`
--

LOCK TABLES `i18n_qstoption` WRITE;
/*!40000 ALTER TABLE `i18n_qstoption` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_qstoption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_question`
--

DROP TABLE IF EXISTS `i18n_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_question` (
  `question_id` int NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `question_desc` varchar(120) DEFAULT NULL,
  `question_notes` text,
  `question_unit` varchar(120) DEFAULT NULL,
  `question_posstm` varchar(120) DEFAULT NULL,
  `question_negstm` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`question_id`,`lang_code`),
  KEY `ix_i18n_question_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_question_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_question_question1` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_question`
--

LOCK TABLES `i18n_question` WRITE;
/*!40000 ALTER TABLE `i18n_question` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_regsection`
--

DROP TABLE IF EXISTS `i18n_regsection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_regsection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `section_id` int NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `section_name` varchar(120) DEFAULT NULL,
  `section_content` text,
  PRIMARY KEY (`user_name`,`project_cod`,`section_id`,`lang_code`),
  KEY `ix_i18n_regsection_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_regsection_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_regsection_regsection1` FOREIGN KEY (`user_name`, `project_cod`, `section_id`) REFERENCES `regsection` (`user_name`, `project_cod`, `section_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_regsection`
--

LOCK TABLES `i18n_regsection` WRITE;
/*!40000 ALTER TABLE `i18n_regsection` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_regsection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_techalias`
--

DROP TABLE IF EXISTS `i18n_techalias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_techalias` (
  `tech_id` int NOT NULL,
  `alias_id` int NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`tech_id`,`alias_id`,`lang_code`),
  KEY `ix_i18n_techalias_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_techalias_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_techalias_techalias1` FOREIGN KEY (`tech_id`, `alias_id`) REFERENCES `techalias` (`tech_id`, `alias_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_techalias`
--

LOCK TABLES `i18n_techalias` WRITE;
/*!40000 ALTER TABLE `i18n_techalias` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_techalias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `i18n_technology`
--

DROP TABLE IF EXISTS `i18n_technology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `i18n_technology` (
  `tech_id` int NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `tech_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`tech_id`,`lang_code`),
  KEY `ix_i18n_technology_lang_code` (`lang_code`),
  CONSTRAINT `fk_i18n_technology_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`),
  CONSTRAINT `fk_i18n_technology_technology1` FOREIGN KEY (`tech_id`) REFERENCES `technology` (`tech_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `i18n_technology`
--

LOCK TABLES `i18n_technology` WRITE;
/*!40000 ALTER TABLE `i18n_technology` DISABLE KEYS */;
/*!40000 ALTER TABLE `i18n_technology` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `package`
--

DROP TABLE IF EXISTS `package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `package` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `package_id` int NOT NULL,
  `package_code` varchar(45) DEFAULT NULL,
  `package_image` blob,
  PRIMARY KEY (`user_name`,`project_cod`,`package_id`),
  CONSTRAINT `fk_package_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `package`
--

LOCK TABLES `package` WRITE;
/*!40000 ALTER TABLE `package` DISABLE KEYS */;
/*!40000 ALTER TABLE `package` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pkgcomb`
--

DROP TABLE IF EXISTS `pkgcomb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pkgcomb` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `package_id` int NOT NULL,
  `comb_user` varchar(80) NOT NULL,
  `comb_project` varchar(80) NOT NULL,
  `comb_code` int NOT NULL,
  `comb_order` int DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`package_id`,`comb_user`,`comb_project`,`comb_code`),
  KEY `fk_pkgcomb_prjcombination1_idx` (`comb_user`,`comb_project`,`comb_code`),
  CONSTRAINT `fk_pkgcomb_package1` FOREIGN KEY (`user_name`, `project_cod`, `package_id`) REFERENCES `package` (`user_name`, `project_cod`, `package_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pkgcomb_prjcombination1` FOREIGN KEY (`comb_user`, `comb_project`, `comb_code`) REFERENCES `prjcombination` (`user_name`, `project_cod`, `comb_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pkgcomb`
--

LOCK TABLES `pkgcomb` WRITE;
/*!40000 ALTER TABLE `pkgcomb` DISABLE KEYS */;
/*!40000 ALTER TABLE `pkgcomb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prjalias`
--

DROP TABLE IF EXISTS `prjalias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prjalias` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int NOT NULL,
  `alias_id` int NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL,
  `tech_used` int DEFAULT NULL,
  `alias_used` int DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`tech_id`,`alias_id`),
  KEY `fk_prjalias_prjtech1_idx` (`user_name`,`project_cod`,`tech_id`),
  KEY `fk_prjalias_techalias1_idx` (`tech_used`,`alias_used`),
  CONSTRAINT `fk_prjalias_prjtech1` FOREIGN KEY (`user_name`, `project_cod`, `tech_id`) REFERENCES `prjtech` (`user_name`, `project_cod`, `tech_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_prjalias_techalias1` FOREIGN KEY (`tech_used`, `alias_used`) REFERENCES `techalias` (`tech_id`, `alias_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prjalias`
--

LOCK TABLES `prjalias` WRITE;
/*!40000 ALTER TABLE `prjalias` DISABLE KEYS */;
/*!40000 ALTER TABLE `prjalias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prjcnty`
--

DROP TABLE IF EXISTS `prjcnty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prjcnty` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `cnty_cod` varchar(3) NOT NULL,
  `cnty_contact` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`cnty_cod`),
  KEY `ix_prjcnty_cnty_cod` (`cnty_cod`),
  CONSTRAINT `fk_prjcnty_country1` FOREIGN KEY (`cnty_cod`) REFERENCES `country` (`cnty_cod`) ON DELETE CASCADE,
  CONSTRAINT `fk_prjcnty_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prjcnty`
--

LOCK TABLES `prjcnty` WRITE;
/*!40000 ALTER TABLE `prjcnty` DISABLE KEYS */;
/*!40000 ALTER TABLE `prjcnty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prjcombdet`
--

DROP TABLE IF EXISTS `prjcombdet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prjcombdet` (
  `prjcomb_user` varchar(80) NOT NULL,
  `prjcomb_project` varchar(80) NOT NULL,
  `comb_code` int NOT NULL,
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int NOT NULL,
  `alias_id` int NOT NULL,
  `alias_order` int DEFAULT NULL,
  PRIMARY KEY (`prjcomb_user`,`prjcomb_project`,`comb_code`,`user_name`,`project_cod`,`tech_id`,`alias_id`),
  KEY `fk_prjcombdet_prjalias1_idx` (`user_name`,`project_cod`,`tech_id`,`alias_id`),
  CONSTRAINT `fk_prjcombdet_prjalias1` FOREIGN KEY (`user_name`, `project_cod`, `tech_id`, `alias_id`) REFERENCES `prjalias` (`user_name`, `project_cod`, `tech_id`, `alias_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_prjcombdet_prjcombination1` FOREIGN KEY (`prjcomb_user`, `prjcomb_project`, `comb_code`) REFERENCES `prjcombination` (`user_name`, `project_cod`, `comb_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prjcombdet`
--

LOCK TABLES `prjcombdet` WRITE;
/*!40000 ALTER TABLE `prjcombdet` DISABLE KEYS */;
/*!40000 ALTER TABLE `prjcombdet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prjcombination`
--

DROP TABLE IF EXISTS `prjcombination`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prjcombination` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `comb_code` int NOT NULL,
  `comb_usable` tinyint DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`comb_code`),
  CONSTRAINT `fk_prjcombination_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prjcombination`
--

LOCK TABLES `prjcombination` WRITE;
/*!40000 ALTER TABLE `prjcombination` DISABLE KEYS */;
/*!40000 ALTER TABLE `prjcombination` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prjenumerator`
--

DROP TABLE IF EXISTS `prjenumerator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prjenumerator` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `enum_user` varchar(80) NOT NULL,
  `enum_id` varchar(80) NOT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`enum_user`,`enum_id`),
  KEY `fk_prjenumerator_enum_user_enumerator` (`enum_user`,`enum_id`),
  CONSTRAINT `fk_prjenumerator_enum_user_enumerator` FOREIGN KEY (`enum_user`, `enum_id`) REFERENCES `enumerator` (`user_name`, `enum_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_prjenumerator_user_name_project` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prjenumerator`
--

LOCK TABLES `prjenumerator` WRITE;
/*!40000 ALTER TABLE `prjenumerator` DISABLE KEYS */;
/*!40000 ALTER TABLE `prjenumerator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prjlang`
--

DROP TABLE IF EXISTS `prjlang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prjlang` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `lang_default` tinyint DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`lang_code`),
  KEY `ix_prjlang_lang_code` (`lang_code`),
  CONSTRAINT `fk_prjlang_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE CASCADE,
  CONSTRAINT `fk_prjlang_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prjlang`
--

LOCK TABLES `prjlang` WRITE;
/*!40000 ALTER TABLE `prjlang` DISABLE KEYS */;
/*!40000 ALTER TABLE `prjlang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prjtech`
--

DROP TABLE IF EXISTS `prjtech`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prjtech` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int NOT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`tech_id`),
  KEY `ix_prjtech_tech_id` (`tech_id`),
  CONSTRAINT `fk_prjtech_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE,
  CONSTRAINT `fk_prjtech_technology1` FOREIGN KEY (`tech_id`) REFERENCES `technology` (`tech_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prjtech`
--

LOCK TABLES `prjtech` WRITE;
/*!40000 ALTER TABLE `prjtech` DISABLE KEYS */;
/*!40000 ALTER TABLE `prjtech` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `celery_taskid` varchar(80) NOT NULL,
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `product_id` varchar(80) NOT NULL,
  `datetime_added` datetime DEFAULT NULL,
  `output_id` varchar(80) NOT NULL,
  `output_mimetype` varchar(80) NOT NULL,
  `process_name` varchar(80) NOT NULL,
  PRIMARY KEY (`celery_taskid`),
  KEY `fk_products_user_name_project` (`user_name`,`project_cod`),
  CONSTRAINT `fk_products_user_name_project` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `project_name` varchar(120) DEFAULT NULL,
  `project_abstract` text,
  `project_tags` text,
  `project_pi` varchar(120) DEFAULT NULL,
  `project_piemail` varchar(120) DEFAULT NULL,
  `project_active` tinyint DEFAULT '1',
  `project_public` tinyint DEFAULT '0',
  `project_numobs` int NOT NULL DEFAULT '0',
  `project_numcom` int NOT NULL,
  `project_lat` varchar(120) NOT NULL,
  `project_lon` varchar(120) NOT NULL,
  `project_creationdate` datetime NOT NULL,
  `extra` text,
  `project_dashboard` int DEFAULT '1',
  `project_assstatus` int DEFAULT '0',
  `project_regstatus` int DEFAULT '0',
  `project_createcomb` int DEFAULT '0',
  `project_createpkgs` int DEFAULT '0',
  `project_localvariety` int DEFAULT '0',
  `project_cnty` varchar(3) DEFAULT NULL,
  `project_registration_and_analysis` int DEFAULT '0',
  PRIMARY KEY (`user_name`,`project_cod`),
  KEY `ix_project_user_name` (`user_name`),
  KEY `ix_project_project_cnty` (`project_cnty`),
  CONSTRAINT `fk_project_project_cnty_country` FOREIGN KEY (`project_cnty`) REFERENCES `country` (`cnty_cod`),
  CONSTRAINT `fk_project_user1` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qstgroups`
--

DROP TABLE IF EXISTS `qstgroups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qstgroups` (
  `user_name` varchar(80) NOT NULL,
  `qstgroups_id` varchar(80) NOT NULL,
  `qstgroups_name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`user_name`,`qstgroups_id`),
  CONSTRAINT `fk_qstgroups_user_name_user` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qstgroups`
--

LOCK TABLES `qstgroups` WRITE;
/*!40000 ALTER TABLE `qstgroups` DISABLE KEYS */;
INSERT INTO `qstgroups` VALUES ('bioversity','4581ab3c093d','Uncategorized');
/*!40000 ALTER TABLE `qstgroups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qstoption`
--

DROP TABLE IF EXISTS `qstoption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qstoption` (
  `question_id` int NOT NULL,
  `value_code` varchar(80) NOT NULL,
  `value_desc` varchar(120) DEFAULT NULL,
  `value_isother` int DEFAULT '0',
  `value_isna` int DEFAULT '0',
  `value_order` int DEFAULT '0',
  PRIMARY KEY (`question_id`,`value_code`),
  CONSTRAINT `fk_qstoption_question_id_question` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qstoption`
--

LOCK TABLES `qstoption` WRITE;
/*!40000 ALTER TABLE `qstoption` DISABLE KEYS */;
INSERT INTO `qstoption` VALUES (180,'-777','Other',1,0,13),(180,'-888','Not applicable',0,1,14),(180,'1','Male',0,0,6),(180,'2','Female',0,0,7),(180,'3','Joint',0,0,8),(180,'4','Youth',0,0,9),(237,'1','Male',0,0,33),(237,'2','Female',0,0,34);
/*!40000 ALTER TABLE `qstoption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qstsubgroups`
--

DROP TABLE IF EXISTS `qstsubgroups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qstsubgroups` (
  `group_username` varchar(80) NOT NULL,
  `group_id` varchar(80) NOT NULL,
  `parent_username` varchar(80) NOT NULL,
  `parent_id` varchar(80) NOT NULL,
  PRIMARY KEY (`group_username`,`group_id`,`parent_username`,`parent_id`),
  KEY `fk_qstsubgroups_parent_username_qstgroups` (`parent_username`,`parent_id`),
  CONSTRAINT `fk_qstsubgroups_group_username_qstgroups` FOREIGN KEY (`group_username`, `group_id`) REFERENCES `qstgroups` (`user_name`, `qstgroups_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_qstsubgroups_parent_username_qstgroups` FOREIGN KEY (`parent_username`, `parent_id`) REFERENCES `qstgroups` (`user_name`, `qstgroups_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qstsubgroups`
--

LOCK TABLES `qstsubgroups` WRITE;
/*!40000 ALTER TABLE `qstsubgroups` DISABLE KEYS */;
/*!40000 ALTER TABLE `qstsubgroups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `question`
--

DROP TABLE IF EXISTS `question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `question` (
  `question_id` int NOT NULL AUTO_INCREMENT,
  `question_desc` varchar(120) DEFAULT NULL,
  `question_notes` text,
  `question_unit` varchar(120) DEFAULT NULL,
  `question_dtype` int DEFAULT NULL,
  `question_cmp` varchar(120) DEFAULT NULL,
  `question_reqinreg` tinyint DEFAULT '0',
  `question_reqinasses` tinyint DEFAULT '0',
  `question_optperprj` tinyint DEFAULT '0',
  `user_name` varchar(80) DEFAULT NULL,
  `question_posstm` varchar(120) DEFAULT NULL,
  `question_negstm` varchar(120) DEFAULT NULL,
  `question_twoitems` varchar(120) DEFAULT NULL,
  `question_moreitems` varchar(120) DEFAULT NULL,
  `question_requiredvalue` int DEFAULT NULL,
  `extra` text,
  `question_asskey` int DEFAULT '0',
  `question_code` varchar(120) DEFAULT NULL,
  `question_regkey` int DEFAULT '0',
  `question_overall` int DEFAULT '0',
  `question_perfstmt` varchar(120) DEFAULT NULL,
  `question_alwaysinasse` int DEFAULT '0',
  `question_alwaysinreg` int DEFAULT '0',
  `question_fname` int DEFAULT '0',
  `question_overallperf` int DEFAULT '0',
  `question_district` int DEFAULT '0',
  `question_father` int DEFAULT '0',
  `question_village` int DEFAULT '0',
  `qstgroups_id` varchar(80) DEFAULT NULL,
  `qstgroups_user` varchar(80) DEFAULT NULL,
  `question_visible` int DEFAULT '1',
  `question_name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`question_id`),
  KEY `ix_question_user_name` (`user_name`),
  KEY `fk_question_qstgroups_user_qstgroups` (`qstgroups_user`,`qstgroups_id`),
  CONSTRAINT `fk_question_qstgroups_user_qstgroups` FOREIGN KEY (`qstgroups_user`, `qstgroups_id`) REFERENCES `qstgroups` (`user_name`, `qstgroups_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_question_user1` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1530 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `question`
--

LOCK TABLES `question` WRITE;
/*!40000 ALTER TABLE `question` DISABLE KEYS */;
INSERT INTO `question` VALUES (162,'Package code','Dar un paquete al agricultor','',7,NULL,1,0,0,'bioversity',NULL,NULL,NULL,NULL,1,NULL,0,'QST162',1,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',1,'Package code'),(163,'Select the farmer','Para seleccionar a un agricultor antes registrado.','Seleccione un agricultor',8,NULL,0,1,0,'bioversity',NULL,NULL,NULL,NULL,1,NULL,1,'QST163',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',1,'Select the farmer'),(180,'Who controls the income','Who controls the income','',6,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,1,NULL,0,'whocontrolstheincome',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',1,'Who controls the income'),(199,'Farmer name','The name of the farmer','',1,NULL,1,0,0,'bioversity',NULL,NULL,NULL,NULL,1,NULL,0,'farmername',0,0,NULL,0,1,1,0,0,0,0,'4581ab3c093d','bioversity',1,'Farmer name'),(204,'Overall Characteristic','This is the overall Characteristic','',9,NULL,0,0,0,'bioversity','Overall, which option performed better?','Overall, which option performed worst?','Overall, which option performed better?','Overall, which option is at position {{pos}}?',1,NULL,0,'overallperf',0,1,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',1,'Overall Characteristic'),(205,'Overall performace','Overall performance against local','',10,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,1,NULL,0,'overallchar',0,0,'Overall, whichone is best {{option}} or what you usually use?',0,0,0,1,0,0,0,'4581ab3c093d','bioversity',1,'Overall performace'),(206,'Farm Geolocation','The location of the farm. This question should appear in the first assessment','',4,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,1,NULL,0,'farmgoelocation',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',1,'Farm Geolocation'),(233,'Name of the Father or Name of the Husband/Wife','know the name: Name of the Father or Name of the Husband/Wife','',27,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,0,NULL,0,'familiyofthefarmer',0,0,NULL,0,1,0,0,0,1,0,'4581ab3c093d','bioversity',0,'Name of the Father or Name of the Husband/Wife'),(234,'What is the village of the farmer?','Village\r\n','',27,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,0,NULL,0,'Village',0,0,NULL,0,1,0,0,0,0,1,'4581ab3c093d','bioversity',0,'What is the village of the farmer?'),(235,'What is the district of the farmer?','District','',27,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,0,NULL,0,'district',0,0,NULL,0,1,0,0,1,0,0,'4581ab3c093d','bioversity',0,'What is the district of the farmer?'),(236,'What is the farmer\'s Telephone?','telephone','',1,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,0,NULL,0,'telephone',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',0,'What is the farmer\'s Telephone?'),(237,'What is the gender ?','gender','',5,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,0,NULL,0,'gender',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',0,'What is the gender ?'),(238,'How old are you?','age','',3,NULL,0,0,0,'bioversity',NULL,NULL,NULL,NULL,0,NULL,0,'age',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',0,'How old are you?'),(239,'About energy','About energy','',9,NULL,0,0,0,'bioversity','Which color is most associated with energy?','which color is least associated with energy?','Which color represents more energy?','In terms of energy which color is at position {{pos}}',0,NULL,0,'energy',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',0,'About energy'),(240,'About love','Love','',9,NULL,0,0,0,'bioversity','Which color is most associated with love?','Which color is least associated with love?','Which color represents more love?','In terms of love which color is at position {{pos}}',0,NULL,0,'love',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',0,'About love'),(241,'About death','About death','',9,NULL,0,0,0,'bioversity','Which color is most associated with death?','Which color is least associated with death?','Which color represents more death?','In terms of death which color is at position {{pos}}',0,NULL,0,'death',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',0,'About death'),(242,'About intelligence','About Intelligence','',9,NULL,0,0,0,'bioversity','Which color is most associated with intelligence?','Which color is least associated with intelligence?','Which color represents more intelligence?','in terms of intelligence which color is at position {{pos}}',0,NULL,0,'intelligence',0,0,NULL,0,0,0,0,0,0,0,'4581ab3c093d','bioversity',0,'About intelligence');
/*!40000 ALTER TABLE `question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registry`
--

DROP TABLE IF EXISTS `registry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registry` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `question_id` int NOT NULL,
  `section_user` varchar(80) DEFAULT NULL,
  `section_project` varchar(80) DEFAULT NULL,
  `section_id` int DEFAULT NULL,
  `question_order` int DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`question_id`),
  KEY `fk_registry_regsection1_idx` (`section_user`,`section_project`,`section_id`),
  KEY `ix_registry_question_id` (`question_id`),
  CONSTRAINT `fk_registry_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE,
  CONSTRAINT `fk_registry_question1` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_registry_regsection1` FOREIGN KEY (`section_user`, `section_project`, `section_id`) REFERENCES `regsection` (`user_name`, `project_cod`, `section_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registry`
--

LOCK TABLES `registry` WRITE;
/*!40000 ALTER TABLE `registry` DISABLE KEYS */;
/*!40000 ALTER TABLE `registry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registry_jsonlog`
--

DROP TABLE IF EXISTS `registry_jsonlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registry_jsonlog` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `log_id` varchar(64) NOT NULL,
  `log_dtime` datetime DEFAULT NULL,
  `json_file` text,
  `log_file` text,
  `status` int DEFAULT NULL,
  `enum_id` varchar(80) NOT NULL,
  `enum_user` varchar(80) NOT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`log_id`),
  KEY `fk_registry_jsonlog_enum_user_enumerator` (`enum_user`,`enum_id`),
  CONSTRAINT `fk_registry_jsonlog_enum_user_enumerator` FOREIGN KEY (`enum_user`, `enum_id`) REFERENCES `enumerator` (`user_name`, `enum_id`),
  CONSTRAINT `fk_registry_jsonlog_user_name_project` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registry_jsonlog`
--

LOCK TABLES `registry_jsonlog` WRITE;
/*!40000 ALTER TABLE `registry_jsonlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `registry_jsonlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `regsection`
--

DROP TABLE IF EXISTS `regsection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `regsection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `section_id` int NOT NULL,
  `section_name` varchar(45) DEFAULT NULL,
  `section_content` text,
  `section_order` int DEFAULT NULL,
  `section_private` int DEFAULT NULL,
  PRIMARY KEY (`user_name`,`project_cod`,`section_id`),
  CONSTRAINT `fk_regsection_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regsection`
--

LOCK TABLES `regsection` WRITE;
/*!40000 ALTER TABLE `regsection` DISABLE KEYS */;
/*!40000 ALTER TABLE `regsection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sector`
--

DROP TABLE IF EXISTS `sector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sector` (
  `sector_cod` int NOT NULL AUTO_INCREMENT,
  `sector_name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`sector_cod`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sector`
--

LOCK TABLES `sector` WRITE;
/*!40000 ALTER TABLE `sector` DISABLE KEYS */;
INSERT INTO `sector` VALUES (1,'Bioversity International\r\n'),(2,'CGIAR Organization'),(3,'University'),(4,'Private organization'),(5,'Public organization');
/*!40000 ALTER TABLE `sector` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storageerrors`
--

DROP TABLE IF EXISTS `storageerrors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `storageerrors` (
  `fileuid` varchar(80) NOT NULL,
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `submission_type` varchar(80) DEFAULT NULL,
  `error_cod` varchar(80) DEFAULT NULL,
  `error_des` text,
  `error_table` varchar(120) DEFAULT NULL,
  `command_executed` text,
  `assessment_id` varchar(80) DEFAULT NULL,
  `error_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`fileuid`),
  KEY `fk_storageerrors_user_name_project` (`user_name`,`project_cod`),
  CONSTRAINT `fk_storageerrors_user_name_project` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storageerrors`
--

LOCK TABLES `storageerrors` WRITE;
/*!40000 ALTER TABLE `storageerrors` DISABLE KEYS */;
/*!40000 ALTER TABLE `storageerrors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tasks`
--

DROP TABLE IF EXISTS `tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tasks` (
  `taskid` varchar(80) NOT NULL,
  PRIMARY KEY (`taskid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tasks`
--

LOCK TABLES `tasks` WRITE;
/*!40000 ALTER TABLE `tasks` DISABLE KEYS */;
/*!40000 ALTER TABLE `tasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `techalias`
--

DROP TABLE IF EXISTS `techalias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `techalias` (
  `tech_id` int NOT NULL,
  `alias_id` int NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`tech_id`,`alias_id`),
  KEY `ix_techalias_tech_id` (`tech_id`),
  CONSTRAINT `fk_techalias_technology1` FOREIGN KEY (`tech_id`) REFERENCES `technology` (`tech_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `techalias`
--

LOCK TABLES `techalias` WRITE;
/*!40000 ALTER TABLE `techalias` DISABLE KEYS */;
INSERT INTO `techalias` VALUES (76,142,'Azul'),(76,143,'Blanco'),(76,144,'Rojo'),(76,145,'Negro'),(76,146,'Amarillo'),(76,1299,'tesfa'),(76,1300,'tesfa 1'),(76,1301,'magna 1'),(76,1302,'quncho 1'),(76,1303,'tseday1'),(76,1304,'boset1'),(76,1305,'dagem1'),(76,1306,'quncho22'),(76,1307,'tseday22'),(76,1308,'dagem22'),(76,1309,'tesfa22'),(76,2699,'Kora'),(76,2700,'Boset'),(76,2701,'Negus'),(76,2702,'Quncho'),(76,2703,'Tseday'),(76,2704,'Hibir'),(76,2705,'Gola'),(76,2706,'Simada'),(76,2707,'Flagot'),(76,2708,'Workiytu'),(76,2709,'Zobel'),(76,2710,'Lakech'),(76,2711,'Amarach'),(78,147,'Yellow'),(78,148,'Blue'),(78,149,'White'),(78,150,'Black'),(78,151,'Red'),(78,1558,'Wheat'),(78,1877,'Liban'),(78,1878,'Bulluk'),(78,1879,'Senate'),(78,1880,'Wane'),(78,1881,'Lemu'),(78,1882,'Dembel'),(78,1883,'Bika'),(78,1884,'Hiddasie'),(78,1885,'Oboro'),(78,1886,'Mandoyou'),(109,458,'INTA Fuerte Sequia'),(109,459,'INTA Rojo'),(109,460,'INTA Matagalpa'),(109,461,'INTA Ferroso'),(109,462,'INTA Centro Sur'),(109,600,'cvg'),(109,706,'Barley '),(109,741,'Nasir'),(109,742,'Awash 1'),(109,743,'Awash2'),(109,845,'SER 125'),(109,962,'intercroppinng'),(109,1351,'Highland Sorghum'),(109,1405,'Haricot Bean Varsities'),(109,1938,'tumsa,dedea,moti,shallo,welki,gebelcho,gora,alloshe,hachalu,obsie,dosha,mosisa'),(109,1995,'Awash 2'),(109,1996,'Awash Melka'),(109,1997,'Gofta'),(109,1998,'Ayenew'),(109,1999,'Kufanzik'),(109,2069,'Mangudo, King bird, Wane, Lemu, Ogolcho'),(109,2712,'SC Gadra'),(109,2713,'SC Ukulinga'),(109,2714,'SC Caldon'),(109,2715,'SC Caledon'),(109,2716,'SC Bounty'),(109,2749,'NUA 45'),(109,2750,'KHOLOPHETE'),(109,2751,'RED KIDNEY ');
/*!40000 ALTER TABLE `techalias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `technology`
--

DROP TABLE IF EXISTS `technology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `technology` (
  `tech_id` int NOT NULL AUTO_INCREMENT,
  `tech_name` varchar(45) DEFAULT NULL,
  `user_name` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`tech_id`),
  KEY `ix_technology_user_name` (`user_name`),
  CONSTRAINT `fk_crop_user1` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=651 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `technology`
--

LOCK TABLES `technology` WRITE;
/*!40000 ALTER TABLE `technology` DISABLE KEYS */;
INSERT INTO `technology` VALUES (76,'Colores','bioversity'),(78,'Colors','bioversity'),(109,'Bean varieties','bioversity');
/*!40000 ALTER TABLE `technology` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_name` varchar(80) NOT NULL,
  `user_fullname` varchar(120) DEFAULT NULL,
  `user_joindate` datetime DEFAULT NULL,
  `user_password` varchar(80) DEFAULT NULL,
  `user_organization` varchar(120) DEFAULT NULL,
  `user_email` varchar(120) DEFAULT NULL,
  `user_apikey` varchar(45) DEFAULT NULL,
  `user_about` text,
  `user_cnty` varchar(3) NOT NULL,
  `user_sector` int NOT NULL,
  `user_active` tinyint DEFAULT '1',
  `extra` text,
  PRIMARY KEY (`user_name`),
  KEY `ix_user_user_cnty` (`user_cnty`),
  KEY `ix_user_user_sector` (`user_sector`),
  CONSTRAINT `fk_user_lkpcountry` FOREIGN KEY (`user_cnty`) REFERENCES `country` (`cnty_cod`),
  CONSTRAINT `fk_user_lkpsector1` FOREIGN KEY (`user_sector`) REFERENCES `sector` (`sector_cod`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('bioversity','Bioversity',NULL,'Po31zJbdZ+eJuU50TvsmVQ==','Bioversity International','International','20abbf14-841a-4ae2-bc4f-5c0c051b2d8e','','CR',1,1,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-08-17 20:56:03
