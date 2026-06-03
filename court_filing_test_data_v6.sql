-- 法院自动立案系统 - 完整数据库备份
-- 生成时间: 2026-05-18

-- 表: agents
DROP TABLE IF EXISTS `agents`;
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代理人信息表';

INSERT INTO `agents` (`id`, `case_id`, `agent_type`, `agent_name`, `agent_gender`, `agent_cert_type`, `agent_cert_no`, `agent_phone`, `agent_license_no`, `agent_law_firm`, `created_at`) VALUES
(1, 2, '律师', '王律师', '男', '居民身份证', '110101198505051234', '13600136001', '11101201510123456', '北京大成律师事务所', '2026-05-18 11:27:45'),
(2, 3, '员工', '赵员工', '女', '居民身份证', '440301199510101234', '13600136002', NULL, '深圳科技有限公司', '2026-05-18 11:28:11'),
(3, 4, '律师', '李律师', '男', '居民身份证', '310101198808081234', '13600136003', '13101201810876543', '上海锦天城律师事务所', '2026-05-18 11:28:36'),
(4, 5, '律师', '张律师', '女', '居民身份证', '440106199212121234', '13600136004', '14401202020456789', '广州金杜律师事务所', '2026-05-18 11:29:01'),
(5, 6, '律师', '孙律师', '男', '居民身份证', '330102198010101234', '13600136005', '13301201010567890', '杭州天册律师事务所', '2026-05-18 11:29:28');

-- 表: case_files
DROP TABLE IF EXISTS `case_files`;
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
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `case_files` (`id`, `case_id`, `file_category`, `file_name`, `file_path`, `upload_status`, `created_at`) VALUES
(10, 2, '保全申请书', '01_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026001\保全申请书\01_保全申请书.pdf', 0, '2026-05-18 11:27:45'),
(11, 2, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\03_申请人证照.pdf', 0, '2026-05-18 11:27:45'),
(12, 2, '身份证明材料', '04_被申请人身份证.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\04_被申请人身份证.pdf', 0, '2026-05-18 11:27:45'),
(13, 2, '身份证明材料', '05_代理人授权书.pdf', 'C:\court-auto-filing\uploads\保全2026001\身份证明材料\05_代理人授权书.pdf', 0, '2026-05-18 11:27:45'),
(14, 2, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026001\证据材料\证据材料.doc', 0, '2026-05-18 11:27:45'),
(15, 2, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\06_担保函.pdf', 0, '2026-05-18 11:27:45'),
(16, 2, '担保材料', '07_保证人证照.pdf', 'C:\court-auto-filing\uploads\保全2026001\担保材料\07_保证人证照.pdf', 0, '2026-05-18 11:27:45'),
(17, 2, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026001\起诉状\起诉状.doc', 0, '2026-05-18 11:27:45'),
(18, 2, '其他材料', '其他材料.doc', 'C:\court-auto-filing\uploads\保全2026001\其他材料\其他材料.doc', 0, '2026-05-18 11:27:45'),
(19, 3, '保全申请书', '02_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026002\保全申请书\02_保全申请书.pdf', 0, '2026-05-18 11:28:11'),
(20, 3, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026002\身份证明材料\03_申请人证照.pdf', 0, '2026-05-18 11:28:11'),
(21, 3, '身份证明材料', '04_被申请人身份证.pdf', 'C:\court-auto-filing\uploads\保全2026002\身份证明材料\04_被申请人身份证.pdf', 0, '2026-05-18 11:28:11'),
(22, 3, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026002\证据材料\证据材料.doc', 0, '2026-05-18 11:28:11'),
(23, 3, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026002\担保材料\06_担保函.pdf', 0, '2026-05-18 11:28:11'),
(24, 3, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026002\起诉状\起诉状.doc', 0, '2026-05-18 11:28:11'),
(25, 4, '保全申请书', '03_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026003\保全申请书\03_保全申请书.pdf', 0, '2026-05-18 11:28:36'),
(26, 4, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026003\身份证明材料\03_申请人证照.pdf', 0, '2026-05-18 11:28:36'),
(27, 4, '身份证明材料', '04_被申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026003\身份证明材料\04_被申请人证照.pdf', 0, '2026-05-18 11:28:36'),
(28, 4, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026003\证据材料\证据材料.doc', 0, '2026-05-18 11:28:36'),
(29, 4, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026003\担保材料\06_担保函.pdf', 0, '2026-05-18 11:28:36'),
(30, 4, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026003\起诉状\起诉状.doc', 0, '2026-05-18 11:28:36'),
(31, 4, '其他材料', '其他材料.doc', 'C:\court-auto-filing\uploads\保全2026003\其他材料\其他材料.doc', 0, '2026-05-18 11:28:36'),
(32, 5, '保全申请书', '04_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026004\保全申请书\04_保全申请书.pdf', 0, '2026-05-18 11:29:01'),
(33, 5, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026004\身份证明材料\03_申请人证照.pdf', 0, '2026-05-18 11:29:01'),
(34, 5, '身份证明材料', '04_被申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026004\身份证明材料\04_被申请人证照.pdf', 0, '2026-05-18 11:29:01'),
(35, 5, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026004\证据材料\证据材料.doc', 0, '2026-05-18 11:29:01'),
(36, 5, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026004\担保材料\06_担保函.pdf', 0, '2026-05-18 11:29:01'),
(37, 5, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026004\起诉状\起诉状.doc', 0, '2026-05-18 11:29:01'),
(38, 6, '保全申请书', '05_保全申请书.pdf', 'C:\court-auto-filing\uploads\保全2026005\保全申请书\05_保全申请书.pdf', 0, '2026-05-18 11:29:28'),
(39, 6, '身份证明材料', '03_申请人证照.pdf', 'C:\court-auto-filing\uploads\保全2026005\身份证明材料\03_申请人证照.pdf', 0, '2026-05-18 11:29:28'),
(40, 6, '身份证明材料', '04_被申请人身份证.pdf', 'C:\court-auto-filing\uploads\保全2026005\身份证明材料\04_被申请人身份证.pdf', 0, '2026-05-18 11:29:28'),
(41, 6, '证据材料', '证据材料.doc', 'C:\court-auto-filing\uploads\保全2026005\证据材料\证据材料.doc', 0, '2026-05-18 11:29:28'),
(42, 6, '担保材料', '06_担保函.pdf', 'C:\court-auto-filing\uploads\保全2026005\担保材料\06_担保函.pdf', 0, '2026-05-18 11:29:28'),
(43, 6, '起诉状', '起诉状.doc', 'C:\court-auto-filing\uploads\保全2026005\起诉状\起诉状.doc', 0, '2026-05-18 11:29:28'),
(44, 6, '其他材料', '其他材料.doc', 'C:\court-auto-filing\uploads\保全2026005\其他材料\其他材料.doc', 0, '2026-05-18 11:29:28');

-- 表: cases
DROP TABLE IF EXISTS `cases`;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `cases` (`id`, `case_no`, `case_name`, `preserve_type`, `preserve_category`, `case_type`, `court_case_no`, `case_reason`, `delivery_address`, `contact_name`, `contact_phone`, `is_urgent`, `apply_date`, `remark`, `applicant_name`, `applicant_id`, `applicant_phone`, `applicant_address`, `applicant_type`, `applicant_uscc`, `respondent_name`, `respondent_id`, `respondent_phone`, `respondent_type`, `respondent_uscc`, `preserve_amount`, `court_name`, `court_code`, `guarantee_type`, `guarantee_value`, `status`, `created_at`, `updated_at`, `applicant_cert_type`, `applicant_cert_no`, `applicant_nature`, `applicant_legal_person`, `applicant_legal_title`, `applicant_tel`, `applicant_reg_address`, `applicant_country`, `applicant_gender`, `applicant_birth`, `applicant_nation`, `respondent_cert_type`, `respondent_country`, `respondent_birth`, `respondent_age`, `respondent_gender`, `respondent_nation`, `respondent_tel`, `respondent_residence`, `non_litigation_period`, `has_guarantee`, `submitter_type`, `guarantor_name`, `guarantee_object`, `guarantee_remark`, `applicant_birth_place`, `applicant_email`, `applicant_postcode`, `respondent_nature`, `respondent_legal_person`, `respondent_legal_title`, `respondent_reg_address`, `case_source`, `case_priority`) VALUES
(2, '保全2026001', '借款合同纠纷-诉前保全', '财产保全', '诉前保全', NULL, NULL, '借款合同纠纷', NULL, '李小二', '13800138001', 0, NULL, NULL, '李小二', '110101199001011234', '13800138001', '北京市朝阳区建国路88号', '自然人', NULL, '李小三', '110101199002021234', '13900139001', '自然人', NULL, '100000.00', '北京市朝阳区人民法院', '110105', '保证', '100000.00', 0, '2026-05-18 11:27:45', '2026-05-18 11:27:45', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '男', '1990-01-01', '汉族', NULL, NULL, NULL, NULL, '男', '汉族', NULL, NULL, NULL, 1, '律师', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0),
(3, '保全2026002', '买卖合同纠纷-诉讼保全', '财产保全', '诉讼保全', '民事', '(2026)粤0304民初1234号', '买卖合同纠纷', NULL, '张三', '13800138002', 0, NULL, NULL, '深圳科技有限公司', '91440300MA5G123456', '0755-12345678', '深圳市福田区深南大道1001号', '法人', '91440300MA5G123456', '李四', '440301199003031234', '13800138002', '自然人', NULL, '500000.00', '深圳市福田区人民法院', '440304', '保险', '500000.00', 0, '2026-05-18 11:28:11', '2026-05-18 11:28:11', NULL, NULL, '有限责任公司', '张三', '执行董事', '0755-12345678', '深圳市福田区', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '男', '汉族', NULL, NULL, NULL, 1, '员工', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0),
(4, '保全2026003', '知识产权侵权-证据保全', '证据保全', '诉讼保全', '民事', '(2026)沪0106民初5678号', '知识产权侵权纠纷', NULL, '王五', '13800138003', 0, NULL, NULL, '王五', '310101199505051234', '13800138003', '上海市静安区南京西路1688号', '自然人', NULL, '上海创新科技公司', '91310106MA1FY12345', '021-87654321', '法人', NULL, '200000.00', '上海市静安区人民法院', '310106', '保函', '200000.00', 0, '2026-05-18 11:28:36', '2026-05-18 11:28:36', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '女', '1995-05-05', '汉族', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, '律师', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0),
(5, '保全2026004', '不正当竞争-行为保全', '行为保全', '诉前保全', NULL, NULL, '不正当竞争纠纷', NULL, '陈总', '13800138004', 0, NULL, NULL, '广州贸易公司', '91440101MA5G789012', '020-87654321', '广州市天河区珠江新城华夏路10号', '法人', '91440101MA5G789012', '广州竞争对手公司', '91440101MA5G654321', '020-12345678', '法人', NULL, '300000.00', '广州市天河区人民法院', '440106', '现金', '300000.00', 0, '2026-05-18 11:29:01', '2026-05-18 11:29:01', NULL, NULL, '股份有限公司', '陈总', '董事长', '020-87654321', '广州市天河区', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, '律师', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0),
(6, '保全2026005', '股权转让纠纷-诉讼保全', '财产保全', '诉讼保全', '民事', '(2026)浙0102民初9012号', '股权转让纠纷', NULL, '赵六', '13800138005', 0, NULL, NULL, '赵六', '330102199010101234', '13800138005', '杭州市上城区解放路88号', '自然人', NULL, '钱七', '330102198808081234', '13800138006', '自然人', NULL, '800000.00', '杭州市上城区人民法院', '330102', '保证', '800000.00', 0, '2026-05-18 11:29:28', '2026-05-18 11:29:28', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '男', '1990-10-10', '汉族', NULL, NULL, NULL, NULL, '女', '汉族', NULL, NULL, NULL, 1, '律师', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0);

-- 表: property_clues
DROP TABLE IF EXISTS `property_clues`;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `property_clues` (`id`, `case_id`, `property_type`, `owner`, `bank_name`, `bank_account`, `amount`, `currency`, `property_value`, `created_at`, `property_province`, `property_location`, `property_cert_no`) VALUES
(2, 2, '银行存款', '李小三', '中国工商银行北京分行', '6222021234567890123', '100000.00', 'CNY', '100000.00', '2026-05-18 11:27:45', NULL, NULL, NULL),
(3, 3, '房产', '李四', NULL, NULL, '500000.00', 'CNY', '500000.00', '2026-05-18 11:28:11', '广东省', '深圳市福田区香蜜湖街道香梅路2026号', '粤(2025)深圳市不动产权第0012345号'),
(4, 4, '股权', '上海创新科技公司', '上海浦东发展银行静安支行', '6225211234567890', '200000.00', 'CNY', '200000.00', '2026-05-18 11:28:36', NULL, NULL, NULL),
(5, 5, '车辆', '广州竞争对手公司', '中国建设银行广州分行', '6227009876543210', '300000.00', 'CNY', '300000.00', '2026-05-18 11:29:01', NULL, NULL, NULL),
(6, 6, '股票', '钱七', '中信证券杭州解放路营业部', '8888888888', '800000.00', 'CNY', '800000.00', '2026-05-18 11:29:28', NULL, NULL, NULL);

-- 表: system_config
DROP TABLE IF EXISTS `system_config`;
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

INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_desc`, `created_at`, `updated_at`) VALUES
(1, 'login_username', '13723715831', '法院系统登录账号', '2026-05-18 09:56:38', '2026-05-18 09:56:38'),
(2, 'login_password', 'HU1234pp', '法院系统登录密码', '2026-05-18 09:56:38', '2026-05-18 09:56:38'),
(3, 'default_submitter', '其他代理人', '默认提交身份人', '2026-05-18 09:56:38', '2026-05-18 09:56:38'),
(4, 'default_agent_type', '律师', '默认代理人类型', '2026-05-18 09:56:38', '2026-05-18 09:56:38');
