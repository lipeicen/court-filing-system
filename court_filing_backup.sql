-- 法院自动立案系统数据库结构
-- 数据库: court_filing
-- 生成时间: 2026-05-15

CREATE DATABASE IF NOT EXISTS court_filing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE court_filing;

-- 案件表
CREATE TABLE `cases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_no` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '案件编号',
  `case_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '案件名称',
  `applicant_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '申请人姓名',
  `applicant_id` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人身份证号',
  `applicant_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人手机号',
  `applicant_address` text COLLATE utf8mb4_unicode_ci COMMENT '申请人地址',
  `respondent_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人姓名',
  `respondent_id` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人身份证号',
  `respondent_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人手机号',
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

INSERT INTO cases (id, case_no, case_name, applicant_name, applicant_id, applicant_phone, 
applicant_address, respondent_name, respondent_id, respondent_phone, preserve_amount, 
court_name, court_code, guarantee_type, guarantee_value, status, created_at, updated_at)
VALUES (1, '保全2026001', '测试保全案件001', '李小二', '110101199001011234', '13800138001', 
'北京市朝阳区xxx街道', '李小三', '110101199002021234', '13900139001', 100000.00, 
'北京市朝阳区人民法院', '110105', '保证', 100000.00, 1, '2026-05-15 17:55:23', '2026-05-18 09:09:40');

INSERT INTO cases (id, case_no, case_name, applicant_name, applicant_id, applicant_phone, 
applicant_address, respondent_name, respondent_id, respondent_phone, preserve_amount, 
court_name, court_code, guarantee_type, guarantee_value, status, created_at, updated_at)
VALUES (2, '保全2026002', '测试保全案件002', '张三', '110101199003031234', '13800138002', 
'北京市海淀区xxx街道', '李四', '110101199004041234', '13900139002', 200000.00, 
'北京市海淀区人民法院', '110108', '保证', 200000.00, 0, '2026-05-15 17:59:32', '2026-05-15 17:59:32');

INSERT INTO property_clues (id, case_id, property_type, owner, bank_name, bank_account, amount, currency, property_value, created_at)
VALUES (1, 1, '银行存款', '李小三', '中国工商银行北京分行', '6222021234567890123', 100000.00, 'CNY', 100000.00, '2026-05-15 17:55:23');

INSERT INTO property_clues (id, case_id, property_type, owner, bank_name, bank_account, amount, currency, property_value, created_at)
VALUES (2, 2, '银行存款', '李四', '中国建设银行北京分行', '6227001234567890123', 200000.00, 'CNY', 200000.00, '2026-05-15 17:59:32');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (1, 1, '保全申请书', '01_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026001\保全申请书\01_保全申请书.pdf', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (2, 1, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\03_申请人证照.pdf', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (3, 1, '身份证明材料', '04_被申请人身份证.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\04_被申请人身份证.pdf', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (4, 1, '身份证明材料', '05_代理人授权书.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\05_代理人授权书.pdf', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (5, 1, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026001\证据材料\证据材料.doc', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (6, 1, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\06_担保函.pdf', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (7, 1, '担保材料', '07_保证人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\07_保证人证照.pdf', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (8, 1, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026001\起诉状\起诉状.doc', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (9, 1, '其他材料', '其他材料.doc', 'C:\court-auto-filing\uploads\保全2026001\其他材料\其他材料.doc', 0, '2026-05-15 17:55:23');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (10, 2, '保全申请书', '02_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026002\保全申请书\02_保全申请书.pdf', 0, '2026-05-15 18:00:02');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (11, 2, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026002\担保材料\06_担保函.pdf', 0, '2026-05-15 18:00:02');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (12, 2, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026002\证据材料\证据材料.doc', 0, '2026-05-15 18:00:02');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (13, 2, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026002\起诉状\起诉状.doc', 0, '2026-05-15 18:00:02');

INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at)
VALUES (14, 2, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026002\身份证明材料\03_申请人证照.pdf', 0, '2026-05-15 18:00:02');
