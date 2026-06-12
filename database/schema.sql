-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: court_filing
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
-- Current Database: `court_filing`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `court_filing` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `court_filing`;

--
-- Table structure for table `agents`
--

DROP TABLE IF EXISTS `agents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agents` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '代理人ID',
  `case_id` int NOT NULL COMMENT '关联案件ID',
  `agent_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人类型:律师/近亲属/工作人员',
  `agent_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人姓名',
  `agent_gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人性别:男/女',
  `agent_cert_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人证件类型',
  `agent_cert_no` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人证件号码',
  `agent_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人手机号',
  `agent_license_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '执业证件号码(律师执业证号)',
  `agent_law_firm` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人所在律所',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `case_id` (`case_id`),
  CONSTRAINT `agents_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代理人信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `case_files`
--

DROP TABLE IF EXISTS `case_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `case_files` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_id` int NOT NULL COMMENT '案件ID',
  `file_category` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '材料类别',
  `file_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '文件名',
  `file_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '文件路径',
  `upload_status` int DEFAULT '0' COMMENT '上传状态:0未上传 1已上传',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `case_id` (`case_id`),
  CONSTRAINT `case_files_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1061 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cases`
--

DROP TABLE IF EXISTS `cases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '案件编号',
  `case_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '案件名称',
  `preserve_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '诉讼保全',
  `preserve_category` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '保全类别:诉前保全/诉讼保全',
  `case_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '案件类型:刑事/民事/行政',
  `court_case_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '法院案号',
  `case_reason` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '案由',
  `delivery_address` text COLLATE utf8mb4_unicode_ci COMMENT '送达地址',
  `contact_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系人姓名',
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系人电话',
  `is_urgent` tinyint DEFAULT '0' COMMENT '是否加急:0否/1是',
  `apply_date` date DEFAULT NULL COMMENT '申请日期',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `applicant_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '申请人姓名',
  `applicant_id` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人身份证号',
  `applicant_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人手机号',
  `applicant_address` text COLLATE utf8mb4_unicode_ci COMMENT '申请人地址',
  `applicant_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '自然人',
  `applicant_uscc` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人统一社会信用代码',
  `respondent_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人姓名',
  `respondent_id` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人身份证号',
  `respondent_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人手机号',
  `respondent_address` text COLLATE utf8mb4_unicode_ci,
  `respondent_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '自然人',
  `respondent_uscc` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人统一社会信用代码',
  `preserve_amount` decimal(15,2) DEFAULT NULL COMMENT '保全金额',
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请法院',
  `court_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '法院代码',
  `guarantee_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '提供保证人',
  `guarantee_value` decimal(15,2) DEFAULT NULL COMMENT '担保价值',
  `status` int DEFAULT '0' COMMENT '状态:0待提交 1已提交',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `applicant_cert_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '身份证',
  `applicant_cert_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人证照号码',
  `applicant_nature` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '单位性质:机关/事业单位/企业/社会团体/民办非企业单位/其他',
  `applicant_legal_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '法定代表人',
  `applicant_legal_title` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '法定代表人职务',
  `applicant_tel` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人固定电话',
  `applicant_reg_address` text COLLATE utf8mb4_unicode_ci COMMENT '单位注册地',
  `applicant_reg_country` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '中国',
  `applicant_country` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '中国',
  `applicant_gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人性别',
  `applicant_birth` date DEFAULT NULL COMMENT '申请人出生日期',
  `applicant_age` int DEFAULT NULL,
  `applicant_nation` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '汉族',
  `respondent_cert_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '身份证',
  `respondent_country` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '中国',
  `respondent_birth` date DEFAULT NULL COMMENT '被申请人出生日期',
  `respondent_age` int DEFAULT NULL COMMENT '被申请人年龄',
  `respondent_gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人性别',
  `respondent_nation` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '汉族',
  `respondent_tel` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人固定电话',
  `respondent_residence` text COLLATE utf8mb4_unicode_ci COMMENT '被申请人经常居住地',
  `non_litigation_period` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '非诉期间',
  `has_guarantee` tinyint DEFAULT '1' COMMENT '担保情况:0无/1有',
  `submitter_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '提交身份人',
  `guarantor_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '担保人',
  `guarantee_property_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `guarantee_remark` text COLLATE utf8mb4_unicode_ci COMMENT '担保说明',
  `applicant_birth_place` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人出生地/籍贯',
  `applicant_email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人电子邮箱',
  `applicant_postcode` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人邮编',
  `respondent_nature` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '单位性质:机关/事业单位/企业/社会团体/民办非企业单位/其他',
  `respondent_legal_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人法定代表人',
  `respondent_legal_title` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人法定代表人职务',
  `respondent_reg_address` text COLLATE utf8mb4_unicode_ci COMMENT '被申请人单位注册地',
  `respondent_reg_country` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '中国',
  `case_source` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '案件来源',
  `case_priority` int DEFAULT '0' COMMENT '案件优先级:0普通/1高',
  `guarantee_property_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `guarantee_object` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '担保物名称',
  `pledge_property_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '质押财产类型',
  `mortgage_property_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '抵押财产类型',
  `created_by` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '创建者账号',
  `filing_status` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=208 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `property_clues`
--

DROP TABLE IF EXISTS `property_clues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `property_clues` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_id` int NOT NULL COMMENT '案件ID',
  `property_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '财产类型',
  `description` text COLLATE utf8mb4_unicode_ci,
  `owner` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '财产所有人',
  `bank_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开户银行',
  `bank_account` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '银行账号',
  `amount` decimal(15,2) DEFAULT NULL COMMENT '数额',
  `currency` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT 'CNY' COMMENT '币种',
  `property_value` decimal(15,2) DEFAULT NULL COMMENT '财产价值',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `property_province` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '房产坐落位置-省份',
  `property_city` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `property_area` decimal(15,2) DEFAULT NULL,
  `property_area_unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `property_location` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '房产坐落位置-项目',
  `property_cert_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '房产证号',
  `property_detail_location` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '房产具体位置',
  `vehicle_brand_model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车辆品牌型号',
  `vehicle_plate_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车牌号',
  `vehicle_location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `vehicle_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `invested_company` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被投资企业名称',
  `stock_account` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '证券账户',
  `stock_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '股票代码',
  `stock_quantity` int DEFAULT NULL COMMENT '股票数量',
  `stock_reg_location` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '发行单位注册地',
  `stock_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fund_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fund_quantity` int DEFAULT NULL,
  `bond_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bond_face_value` decimal(15,2) DEFAULT NULL,
  `equipment_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stock_company_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '持股公司名称',
  `stock_ratio` decimal(5,2) DEFAULT NULL COMMENT '出资比例(%)',
  PRIMARY KEY (`id`),
  KEY `case_id` (`case_id`),
  CONSTRAINT `property_clues_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=215 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_config`
--

DROP TABLE IF EXISTS `system_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `config_value` text COLLATE utf8mb4_unicode_ci COMMENT '配置值',
  `config_desc` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配置说明',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_users`
--

DROP TABLE IF EXISTS `system_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '登录账号',
  `password` varchar(100) NOT NULL COMMENT '登录密码',
  `user_type` varchar(20) DEFAULT '个人用户' COMMENT '用户类型',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '登录账号',
  `password` varchar(100) NOT NULL COMMENT '登录密码',
  `user_type` varchar(20) DEFAULT '个人用户' COMMENT '用户类型',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `court_filing_status`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `court_filing_status` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `court_filing_status`;

--
-- Table structure for table `account_sync_log`
--

DROP TABLE IF EXISTS `account_sync_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_sync_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '账号',
  `category` varchar(20) NOT NULL COMMENT '类别',
  `last_sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后同步时间',
  `total_cases` int DEFAULT '0' COMMENT '总案件数',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username_category` (`username`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='账号同步记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filing_status`
--

DROP TABLE IF EXISTS `filing_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filing_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) NOT NULL COMMENT '案件编号',
  `case_name` varchar(200) DEFAULT NULL COMMENT '案件名称',
  `court_name` varchar(100) DEFAULT NULL COMMENT '法院名称',
  `status` varchar(50) DEFAULT NULL COMMENT '立案状态',
  `status_code` varchar(20) DEFAULT NULL COMMENT '状态代码',
  `review_opinion` text COMMENT '审核意见',
  `apply_date` date DEFAULT NULL COMMENT '申请日期',
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '同步时间',
  `raw_data` json DEFAULT NULL COMMENT '原始数据',
  PRIMARY KEY (`id`),
  KEY `idx_case_no` (`case_no`),
  KEY `idx_status` (`status`),
  KEY `idx_sync_time` (`sync_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filing_status_bankruptcy`
--

DROP TABLE IF EXISTS `filing_status_bankruptcy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filing_status_bankruptcy` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `case_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `review_opinion` text COLLATE utf8mb4_unicode_ci,
  `apply_date` date DEFAULT NULL,
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_new` tinyint(1) DEFAULT '0' COMMENT '是否新增',
  `raw_data` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_case` (`case_name`,`court_name`,`apply_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filing_status_execution`
--

DROP TABLE IF EXISTS `filing_status_execution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filing_status_execution` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `case_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `review_opinion` text COLLATE utf8mb4_unicode_ci,
  `apply_date` date DEFAULT NULL,
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_new` tinyint(1) DEFAULT '0' COMMENT '是否新增',
  `raw_data` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_case` (`case_name`,`court_name`,`apply_date`)
) ENGINE=InnoDB AUTO_INCREMENT=254 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filing_status_mediation`
--

DROP TABLE IF EXISTS `filing_status_mediation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filing_status_mediation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `case_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `review_opinion` text COLLATE utf8mb4_unicode_ci,
  `apply_date` date DEFAULT NULL,
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_new` tinyint(1) DEFAULT '0' COMMENT '是否新增',
  `raw_data` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_case` (`case_name`,`court_name`,`apply_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filing_status_petition`
--

DROP TABLE IF EXISTS `filing_status_petition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filing_status_petition` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `case_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `review_opinion` text COLLATE utf8mb4_unicode_ci,
  `apply_date` date DEFAULT NULL,
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_new` tinyint(1) DEFAULT '0' COMMENT '是否新增',
  `raw_data` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_case` (`case_name`,`court_name`,`apply_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filing_status_preservation`
--

DROP TABLE IF EXISTS `filing_status_preservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filing_status_preservation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `case_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `review_opinion` text COLLATE utf8mb4_unicode_ci,
  `apply_date` date DEFAULT NULL,
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_new` tinyint(1) DEFAULT '0' COMMENT '是否新增',
  `raw_data` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_case` (`case_name`,`court_name`,`apply_date`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filing_status_trial`
--

DROP TABLE IF EXISTS `filing_status_trial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filing_status_trial` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `case_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `review_opinion` text COLLATE utf8mb4_unicode_ci,
  `apply_date` date DEFAULT NULL,
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_new` tinyint(1) DEFAULT '0' COMMENT '是否新增',
  `raw_data` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_case` (`case_name`,`court_name`,`apply_date`)
) ENGINE=InnoDB AUTO_INCREMENT=1464 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sync_log`
--

DROP TABLE IF EXISTS `sync_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sync_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sync_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_cases` int DEFAULT '0',
  `updated_cases` int DEFAULT '0',
  `error_msg` text,
  PRIMARY KEY (`id`),
  KEY `idx_sync_time` (`sync_time`)
) ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-12 13:51:34
