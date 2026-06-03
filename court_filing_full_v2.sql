-- 法院自动立案系统数据库结构 (完整版)
-- 数据库: court_filing
-- 生成时间: 2026-05-18
-- 包含字段: 33个 (cases表)

CREATE DATABASE IF NOT EXISTS court_filing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE court_filing;

-- 案件表 (33个字段)
CREATE TABLE `cases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '案件编号',
  `case_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '案件名称',
  `preserve_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '保全类型:财产保全/证据保全/行为保全',
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
  `applicant_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人类型:自然人/法人/非法人组织',
  `applicant_uscc` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人统一社会信用代码',
  `respondent_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人姓名',
  `respondent_id` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人身份证号',
  `respondent_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人手机号',
  `respondent_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人类型:自然人/法人/非法人组织',
  `respondent_uscc` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人统一社会信用代码',
  `preserve_amount` decimal(15,2) DEFAULT NULL COMMENT '保全金额',
  `court_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请法院',
  `court_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '法院代码',
  `guarantee_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '担保方式',
  `guarantee_value` decimal(15,2) DEFAULT NULL COMMENT '担保价值',
  `status` int DEFAULT '0' COMMENT '状态:0待提交 1已提交',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 财产线索表
CREATE TABLE `property_clues` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_id` int NOT NULL COMMENT '案件ID',
  `property_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '财产类型',
  `owner` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '财产所有人',
  `bank_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开户银行',
  `bank_account` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '银行账号',
  `amount` decimal(15,2) DEFAULT NULL COMMENT '数额',
  `currency` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT 'CNY' COMMENT '币种',
  `property_value` decimal(15,2) DEFAULT NULL COMMENT '财产价值',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `case_id` (`case_id`),
  CONSTRAINT `property_clues_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 材料文件表
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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入案件数据

INSERT INTO cases VALUES (1, '保全2026001', '测试保全案件001', '财产保全', '诉前保全', '民事', '(2026)京0105民初1234号', '借款合同纠纷', '北京市朝阳区xxx街道3号楼', '李小二', '13800138001', 0, 2026-05-15, '测试案件001', '李小二', '110101199001011234', '13800138001', '北京市朝阳区xxx街道', '自然人', NULL, '李小三', '110101199002021234', '13900139001', '自然人', NULL, 100000.00, '北京市朝阳区人民法院', '110105', '保证', 100000.00, 1, 2026-05-15 17:55:23, 2026-05-18 09:35:13);

INSERT INTO cases VALUES (2, '保全2026002', '测试保全案件002', '财产保全', '诉讼保全', '民事', '(2026)京0108民初5678号', '买卖合同纠纷', '北京市海淀区xxx街道5号楼', '张三', '13800138002', 1, 2026-05-16, '测试案件002-加急', '张三', '110101199003031234', '13800138002', '北京市海淀区xxx街道', '自然人', NULL, '李四', '110101199004041234', '13900139002', '自然人', NULL, 200000.00, '北京市海淀区人民法院', '110108', '保证', 200000.00, 0, 2026-05-15 17:59:32, 2026-05-18 09:35:13);

INSERT INTO property_clues VALUES (1, 1, '银行存款', '李小三', '中国工商银行北京分行', '6222021234567890123', 100000.00, 'CNY', 100000.00, 2026-05-15 17:55:23);

INSERT INTO property_clues VALUES (2, 2, '银行存款', '李四', '中国建设银行北京分行', '6227001234567890123', 200000.00, 'CNY', 200000.00, 2026-05-15 17:59:32);

INSERT INTO case_files VALUES (1, 1, '保全申请书', '01_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026001\保全申请书\01_保全申请书.pdf', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (2, 1, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\03_申请人证照.pdf', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (3, 1, '身份证明材料', '04_被申请人身份证.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\04_被申请人身份证.pdf', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (4, 1, '身份证明材料', '05_代理人授权书.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\05_代理人授权书.pdf', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (5, 1, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026001\证据材料\证据材料.doc', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (6, 1, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\06_担保函.pdf', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (7, 1, '担保材料', '07_保证人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\07_保证人证照.pdf', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (8, 1, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026001\起诉状\起诉状.doc', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (9, 1, '其他材料', '其他材料.doc', 'C:\court-auto-filing\uploads\保全2026001\其他材料\其他材料.doc', 0, 2026-05-15 17:55:23);

INSERT INTO case_files VALUES (10, 2, '保全申请书', '02_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026002\保全申请书\02_保全申请书.pdf', 0, 2026-05-15 18:00:02);

INSERT INTO case_files VALUES (11, 2, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026002\担保材料\06_担保函.pdf', 0, 2026-05-15 18:00:02);

INSERT INTO case_files VALUES (12, 2, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026002\证据材料\证据材料.doc', 0, 2026-05-15 18:00:02);

INSERT INTO case_files VALUES (13, 2, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026002\起诉状\起诉状.doc', 0, 2026-05-15 18:00:02);

INSERT INTO case_files VALUES (14, 2, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026002\身份证明材料\03_申请人证照.pdf', 0, 2026-05-15 18:00:02);
