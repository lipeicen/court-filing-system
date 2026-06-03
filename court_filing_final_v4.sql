-- 法院自动立案系统数据库完整备份 (最终版)
-- 生成时间: 2026-05-18
-- 包含3个测试案件 + 完整字段

CREATE DATABASE IF NOT EXISTS court_filing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE court_filing;

-- agents表
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代理人信息表';

-- agents表数据 (3条)
INSERT INTO agents (id, case_id, agent_type, agent_name, agent_gender, agent_cert_type, agent_cert_no, agent_phone, agent_license_no, agent_law_firm, created_at) VALUES (1, 1, '律师', '王律师', '男', '居民身份证', '110101198001011234', '13800138003', '11101201510123456', '北京市某某律师事务所', 2026-05-18 09:57:18);
INSERT INTO agents (id, case_id, agent_type, agent_name, agent_gender, agent_cert_type, agent_cert_no, agent_phone, agent_license_no, agent_law_firm, created_at) VALUES (2, 2, '律师', '赵律师', '女', '居民身份证', '110101198502021234', '13800138004', '11101201810234567', '北京市某某律师事务所', 2026-05-18 09:57:18);
INSERT INTO agents (id, case_id, agent_type, agent_name, agent_gender, agent_cert_type, agent_cert_no, agent_phone, agent_license_no, agent_law_firm, created_at) VALUES (4, 4, '律师', '陈律师', '男', '居民身份证', '440301198801011234', '13800138006', '14403201510123456', '深圳市某某律师事务所', 2026-05-18 10:06:52);

-- case_files表
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
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- case_files表数据 (24条)
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (1, 1, '保全申请书', '01_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026001\保全申请书\01_保全申请书.pdf', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (2, 1, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\03_申请人证照.pdf', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (3, 1, '身份证明材料', '04_被申请人身份证.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\04_被申请人身份证.pdf', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (4, 1, '身份证明材料', '05_代理人授权书.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\05_代理人授权书.pdf', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (5, 1, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026001\证据材料\证据材料.doc', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (6, 1, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\06_担保函.pdf', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (7, 1, '担保材料', '07_保证人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\07_保证人证照.pdf', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (8, 1, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026001\起诉状\起诉状.doc', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (9, 1, '其他材料', '其他材料.doc', 'C:\court-auto-filing\uploads\保全2026001\其他材料\其他材料.doc', 0, 2026-05-15 17:55:23);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (10, 2, '保全申请书', '02_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026002\保全申请书\02_保全申请书.pdf', 0, 2026-05-15 18:00:02);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (11, 2, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026002\担保材料\06_担保函.pdf', 0, 2026-05-15 18:00:02);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (12, 2, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026002\证据材料\证据材料.doc', 0, 2026-05-15 18:00:02);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (13, 2, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026002\起诉状\起诉状.doc', 0, 2026-05-15 18:00:02);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (14, 2, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026002\身份证明材料\03_申请人证照.pdf', 0, 2026-05-15 18:00:02);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (25, 4, '保全申请书', '03_保全申请书.pdf', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (26, 4, '身份证明材料', '04_申请人营业执照.pdf', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (27, 4, '身份证明材料', '05_法定代表人身份证.pdf', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (28, 4, '身份证明材料', '06_代理人授权书.pdf', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (29, 4, '身份证明材料', '07_代理人执业证.pdf', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (30, 4, '起诉状', '起诉状.doc', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (31, 4, '立案受理通知书', '立案受理通知书.pdf', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (32, 4, '证据材料', '证据材料.doc', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (33, 4, '担保材料', '08_担保函.pdf', NULL, 0, 2026-05-18 10:06:52);
INSERT INTO case_files (id, case_id, file_category, file_name, file_path, upload_status, created_at) VALUES (34, 4, '担保材料', '09_保证人资质.pdf', NULL, 0, 2026-05-18 10:06:52);

-- cases表
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
  `applicant_cert_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人证照类型',
  `applicant_cert_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人证照号码',
  `applicant_nature` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人单位性质',
  `applicant_legal_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '法定代表人',
  `applicant_legal_title` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '法定代表人职务',
  `applicant_tel` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人固定电话',
  `applicant_reg_address` text COLLATE utf8mb4_unicode_ci COMMENT '单位注册地',
  `applicant_country` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '注册地国别或地区',
  `applicant_gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人性别',
  `applicant_birth` date DEFAULT NULL COMMENT '申请人出生日期',
  `applicant_nation` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人民族',
  `respondent_cert_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人证件类型',
  `respondent_country` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人国别或地区',
  `respondent_birth` date DEFAULT NULL COMMENT '被申请人出生日期',
  `respondent_age` int DEFAULT NULL COMMENT '被申请人年龄',
  `respondent_gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人性别',
  `respondent_nation` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人民族',
  `respondent_tel` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人固定电话',
  `respondent_residence` text COLLATE utf8mb4_unicode_ci COMMENT '被申请人经常居住地',
  `non_litigation_period` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '非诉期间',
  `has_guarantee` tinyint DEFAULT '1' COMMENT '担保情况:0无/1有',
  `submitter_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '提交身份人',
  `guarantor_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '担保人',
  `guarantee_object` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '担保物名称',
  `guarantee_remark` text COLLATE utf8mb4_unicode_ci COMMENT '担保说明',
  `applicant_birth_place` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人出生地/籍贯',
  `applicant_email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人电子邮箱',
  `applicant_postcode` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '申请人邮编',
  `respondent_nature` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人单位性质',
  `respondent_legal_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人法定代表人',
  `respondent_legal_title` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '被申请人法定代表人职务',
  `respondent_reg_address` text COLLATE utf8mb4_unicode_ci COMMENT '被申请人单位注册地',
  `case_source` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '案件来源',
  `case_priority` int DEFAULT '0' COMMENT '案件优先级:0普通/1高',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- cases表数据 (3条)
INSERT INTO cases (id, case_no, case_name, preserve_type, preserve_category, case_type, court_case_no, case_reason, delivery_address, contact_name, contact_phone, is_urgent, apply_date, remark, applicant_name, applicant_id, applicant_phone, applicant_address, applicant_type, applicant_uscc, respondent_name, respondent_id, respondent_phone, respondent_type, respondent_uscc, preserve_amount, court_name, court_code, guarantee_type, guarantee_value, status, created_at, updated_at, applicant_cert_type, applicant_cert_no, applicant_nature, applicant_legal_person, applicant_legal_title, applicant_tel, applicant_reg_address, applicant_country, applicant_gender, applicant_birth, applicant_nation, respondent_cert_type, respondent_country, respondent_birth, respondent_age, respondent_gender, respondent_nation, respondent_tel, respondent_residence, non_litigation_period, has_guarantee, submitter_type, guarantor_name, guarantee_object, guarantee_remark, applicant_birth_place, applicant_email, applicant_postcode, respondent_nature, respondent_legal_person, respondent_legal_title, respondent_reg_address, case_source, case_priority) VALUES (1, '保全2026001', '测试保全案件001', '财产保全', '诉前保全', NULL, NULL, NULL, '北京市朝阳区xxx街道3号楼', '李小二', '13800138001', 0, 2026-05-15, '测试案件001', '李小二', '110101199001011234', '13800138001', '北京市朝阳区xxx街道', '自然人', NULL, '李小三', '110101199002021234', '13900139001', '自然人', NULL, 100000.00, '北京市朝阳区人民法院', '110105', '保证', 100000.00, 1, 2026-05-15 17:55:23, 2026-05-18 10:07:18, '统一社会信用代码证', '91110000123456789X', '有限责任公司', '李小二', '执行董事', '010-12345678', '北京市朝阳区xxx街道1号楼', '中国', '男', 1990-01-01, '汉族', '居民身份证', '中国', 1990-02-02, 36, '男', '汉族', '010-87654321', '北京市朝阳区xxx街道2号楼', '30日', 1, '其他代理人', '北京市某某律师事务所', '信用担保', '由执业律师提供保证', '北京市', 'lixiaoer@example.com', '100000', NULL, NULL, NULL, NULL, '手动录入', 0);
INSERT INTO cases (id, case_no, case_name, preserve_type, preserve_category, case_type, court_case_no, case_reason, delivery_address, contact_name, contact_phone, is_urgent, apply_date, remark, applicant_name, applicant_id, applicant_phone, applicant_address, applicant_type, applicant_uscc, respondent_name, respondent_id, respondent_phone, respondent_type, respondent_uscc, preserve_amount, court_name, court_code, guarantee_type, guarantee_value, status, created_at, updated_at, applicant_cert_type, applicant_cert_no, applicant_nature, applicant_legal_person, applicant_legal_title, applicant_tel, applicant_reg_address, applicant_country, applicant_gender, applicant_birth, applicant_nation, respondent_cert_type, respondent_country, respondent_birth, respondent_age, respondent_gender, respondent_nation, respondent_tel, respondent_residence, non_litigation_period, has_guarantee, submitter_type, guarantor_name, guarantee_object, guarantee_remark, applicant_birth_place, applicant_email, applicant_postcode, respondent_nature, respondent_legal_person, respondent_legal_title, respondent_reg_address, case_source, case_priority) VALUES (2, '保全2026002', '测试保全案件002', '财产保全', '诉讼保全', '民事', '(2026)京0108民初5678号', '买卖合同纠纷', '北京市海淀区xxx街道5号楼', '张三', '13800138002', 1, 2026-05-16, '测试案件002-加急', '张三', '110101199003031234', '13800138002', '北京市海淀区xxx街道', '自然人', NULL, '李四', '110101199004041234', '13900139002', '自然人', NULL, 200000.00, '北京市海淀区人民法院', '110108', '保证', 200000.00, 0, 2026-05-15 17:59:32, 2026-05-18 10:07:18, '居民身份证', '110101199003031234', NULL, NULL, NULL, '010-11112222', '北京市海淀区xxx街道3号楼', '中国', '女', 1990-03-03, '汉族', '居民身份证', '中国', 1990-04-04, 36, '男', '回族', '010-22223333', '北京市海淀区xxx街道4号楼', NULL, 1, '律师', '张三', '个人保证', '由申请人本人提供担保', '北京市', 'zhangsan@example.com', '100080', NULL, NULL, NULL, NULL, '手动录入', 0);
INSERT INTO cases (id, case_no, case_name, preserve_type, preserve_category, case_type, court_case_no, case_reason, delivery_address, contact_name, contact_phone, is_urgent, apply_date, remark, applicant_name, applicant_id, applicant_phone, applicant_address, applicant_type, applicant_uscc, respondent_name, respondent_id, respondent_phone, respondent_type, respondent_uscc, preserve_amount, court_name, court_code, guarantee_type, guarantee_value, status, created_at, updated_at, applicant_cert_type, applicant_cert_no, applicant_nature, applicant_legal_person, applicant_legal_title, applicant_tel, applicant_reg_address, applicant_country, applicant_gender, applicant_birth, applicant_nation, respondent_cert_type, respondent_country, respondent_birth, respondent_age, respondent_gender, respondent_nation, respondent_tel, respondent_residence, non_litigation_period, has_guarantee, submitter_type, guarantor_name, guarantee_object, guarantee_remark, applicant_birth_place, applicant_email, applicant_postcode, respondent_nature, respondent_legal_person, respondent_legal_title, respondent_reg_address, case_source, case_priority) VALUES (4, '保全2026003', '测试保全案件003-法人', '财产保全', '诉讼保全', '民事', '(2026)粤0303民初9999号', '融资租赁合同纠纷', '深圳市福田区xxx大厦18层', '李经理', '0755-88889999', 0, 2026-05-18, '测试法人申请人案件', '深圳市某某融资租赁有限公司', '91440300123456789X', '0755-88889999', '深圳市福田区xxx大厦18层', '法人', '91440300123456789X', '赵小六', '440301199005056789', '13800138005', '自然人', NULL, 500000.00, '深圳市福田区人民法院', '440304', '保证', 500000.00, 0, 2026-05-18 10:06:52, 2026-05-18 10:06:52, '营业执照', '91440300123456789X', '有限责任公司', '王大明', '董事长', '0755-88889999', '深圳市福田区xxx大厦18层', '中国', '男', 1975-08-15, '汉族', '居民身份证', '中国', 1990-05-05, 36, '男', '汉族', '0755-66667777', '深圳市南山区xxx花园3栋', NULL, 1, '律师', '深圳市某某律师事务所', '信用担保', '由执业律师提供连带责任保证', '广东省深圳市', 'wang.daming@company.com', '518000', NULL, NULL, NULL, NULL, '批量导入', 1);

-- property_clues表
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
  `property_province` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '房产坐落位置-省份',
  `property_location` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '房产坐落位置-项目',
  `property_cert_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '房产证号',
  PRIMARY KEY (`id`),
  KEY `case_id` (`case_id`),
  CONSTRAINT `property_clues_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- property_clues表数据 (3条)
INSERT INTO property_clues (id, case_id, property_type, owner, bank_name, bank_account, amount, currency, property_value, created_at, property_province, property_location, property_cert_no) VALUES (1, 1, '银行存款', '李小三', '中国工商银行北京分行', '6222021234567890123', 100000.00, 'CNY', 100000.00, 2026-05-15 17:55:23, NULL, NULL, NULL);
INSERT INTO property_clues (id, case_id, property_type, owner, bank_name, bank_account, amount, currency, property_value, created_at, property_province, property_location, property_cert_no) VALUES (2, 2, '银行存款', '李四', '中国建设银行北京分行', '6227001234567890123', 200000.00, 'CNY', 200000.00, 2026-05-15 17:59:32, NULL, NULL, NULL);
INSERT INTO property_clues (id, case_id, property_type, owner, bank_name, bank_account, amount, currency, property_value, created_at, property_province, property_location, property_cert_no) VALUES (4, 4, '银行存款', '赵小六', '中国工商银行深圳分行', '6222001234567890123', 500000.00, 'CNY', 500000.00, 2026-05-18 10:06:52, NULL, NULL, NULL);

-- system_config表
CREATE TABLE `system_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `config_value` text COLLATE utf8mb4_unicode_ci COMMENT '配置值',
  `config_desc` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配置说明',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- system_config表数据 (4条)
INSERT INTO system_config (id, config_key, config_value, config_desc, created_at, updated_at) VALUES (1, 'login_username', '13723715831', '法院系统登录账号', 2026-05-18 09:56:38, 2026-05-18 09:56:38);
INSERT INTO system_config (id, config_key, config_value, config_desc, created_at, updated_at) VALUES (2, 'login_password', 'HU1234pp', '法院系统登录密码', 2026-05-18 09:56:38, 2026-05-18 09:56:38);
INSERT INTO system_config (id, config_key, config_value, config_desc, created_at, updated_at) VALUES (3, 'default_submitter', '其他代理人', '默认提交身份人', 2026-05-18 09:56:38, 2026-05-18 09:56:38);
INSERT INTO system_config (id, config_key, config_value, config_desc, created_at, updated_at) VALUES (4, 'default_agent_type', '律师', '默认代理人类型', 2026-05-18 09:56:38, 2026-05-18 09:56:38);

