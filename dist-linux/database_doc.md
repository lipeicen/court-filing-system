# 法院保全案件管理系统 - 数据库文档

数据库: `court_filing`

## agents

| 字段名 | 类型 | 允许空 | 默认值 | 备注 |
|--------|------|--------|--------|------|
| id | int | NO |  | 代理人ID |
| case_id | int | NO |  | 关联案件ID |
| agent_type | varchar(20) | YES |  | 代理人类型:律师/近亲属/工作人员 |
| agent_name | varchar(50) | YES |  | 代理人姓名 |
| agent_gender | varchar(10) | YES |  | 代理人性别:男/女 |
| agent_cert_type | varchar(20) | YES |  | 代理人证件类型 |
| agent_cert_no | varchar(18) | YES |  | 代理人证件号码 |
| agent_phone | varchar(20) | YES |  | 代理人手机号 |
| agent_license_no | varchar(50) | YES |  | 执业证件号码(律师执业证号) |
| agent_law_firm | varchar(100) | YES |  | 代理人所在律所 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | 创建时间 |

**索引:**

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | BTREE |
| case_id | case_id | BTREE |

**表备注:** 代理人信息表

---

## case_files

| 字段名 | 类型 | 允许空 | 默认值 | 备注 |
|--------|------|--------|--------|------|
| id | int | NO |  |  |
| case_id | int | NO |  | 案件ID |
| file_category | varchar(30) | YES |  | 材料类别 |
| file_name | varchar(100) | YES |  | 文件名 |
| file_path | varchar(255) | YES |  | 文件路径 |
| upload_status | int | YES | 0 | 上传状态:0未上传 1已上传 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |  |

**索引:**

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | BTREE |
| case_id | case_id | BTREE |

---

## cases

| 字段名 | 类型 | 允许空 | 默认值 | 备注 |
|--------|------|--------|--------|------|
| id | int | NO |  |  |
| case_no | varchar(50) | NO |  | 案件编号 |
| case_name | varchar(100) | YES |  | 案件名称 |
| preserve_type | varchar(20) | YES | 诉讼保全 |  |
| preserve_category | varchar(20) | YES |  | 保全类别:诉前保全/诉讼保全 |
| case_type | varchar(20) | YES |  | 案件类型:刑事/民事/行政 |
| court_case_no | varchar(50) | YES |  | 法院案号 |
| case_reason | varchar(200) | YES |  | 案由 |
| delivery_address | text | YES |  | 送达地址 |
| contact_name | varchar(50) | YES |  | 联系人姓名 |
| contact_phone | varchar(20) | YES |  | 联系人电话 |
| is_urgent | tinyint | YES | 0 | 是否加急:0否/1是 |
| apply_date | date | YES |  | 申请日期 |
| remark | text | YES |  | 备注 |
| applicant_name | varchar(50) | NO |  | 申请人姓名 |
| applicant_id | varchar(18) | YES |  | 申请人身份证号 |
| applicant_phone | varchar(20) | YES |  | 申请人手机号 |
| applicant_address | text | YES |  | 申请人地址 |
| applicant_type | varchar(20) | YES | 自然人 |  |
| applicant_uscc | varchar(50) | YES |  | 申请人统一社会信用代码 |
| respondent_name | varchar(50) | YES |  | 被申请人姓名 |
| respondent_id | varchar(18) | YES |  | 被申请人身份证号 |
| respondent_phone | varchar(20) | YES |  | 被申请人手机号 |
| respondent_address | text | YES |  |  |
| respondent_type | varchar(20) | YES | 自然人 |  |
| respondent_uscc | varchar(50) | YES |  | 被申请人统一社会信用代码 |
| preserve_amount | decimal(15,2) | YES |  | 保全金额 |
| court_name | varchar(100) | YES |  | 申请法院 |
| court_code | varchar(20) | YES |  | 法院代码 |
| guarantee_type | varchar(20) | YES | 提供保证人 |  |
| guarantee_value | decimal(15,2) | YES |  | 担保价值 |
| status | int | YES | 0 | 状态:0待提交 1已提交 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |  |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP |  |
| applicant_cert_type | varchar(20) | YES | 身份证 |  |
| applicant_cert_no | varchar(50) | YES |  | 申请人证照号码 |
| applicant_nature | varchar(50) | YES |  | 单位性质:机关/事业单位/企业/社会团体/民办非企业单位/其他 |
| applicant_legal_person | varchar(50) | YES |  | 法定代表人 |
| applicant_legal_title | varchar(50) | YES |  | 法定代表人职务 |
| applicant_tel | varchar(20) | YES |  | 申请人固定电话 |
| applicant_reg_address | text | YES |  | 单位注册地 |
| applicant_reg_country | varchar(50) | YES | 中国 |  |
| applicant_country | varchar(20) | YES | 中国 |  |
| applicant_gender | varchar(10) | YES |  | 申请人性别 |
| applicant_birth | date | YES |  | 申请人出生日期 |
| applicant_age | int | YES |  |  |
| applicant_nation | varchar(20) | YES | 汉族 |  |
| respondent_cert_type | varchar(20) | YES | 身份证 |  |
| respondent_country | varchar(20) | YES | 中国 |  |
| respondent_birth | date | YES |  | 被申请人出生日期 |
| respondent_age | int | YES |  | 被申请人年龄 |
| respondent_gender | varchar(10) | YES |  | 被申请人性别 |
| respondent_nation | varchar(20) | YES | 汉族 |  |
| respondent_tel | varchar(20) | YES |  | 被申请人固定电话 |
| respondent_residence | text | YES |  | 被申请人经常居住地 |
| non_litigation_period | varchar(20) | YES |  | 非诉期间 |
| has_guarantee | tinyint | YES | 1 | 担保情况:0无/1有 |
| submitter_type | varchar(20) | YES |  | 提交身份人 |
| guarantor_name | varchar(100) | YES |  | 担保人 |
| guarantee_property_name | varchar(100) | YES |  |  |
| guarantee_remark | text | YES |  | 担保说明 |
| applicant_birth_place | varchar(100) | YES |  | 申请人出生地/籍贯 |
| applicant_email | varchar(100) | YES |  | 申请人电子邮箱 |
| applicant_postcode | varchar(10) | YES |  | 申请人邮编 |
| respondent_nature | varchar(50) | YES |  | 单位性质:机关/事业单位/企业/社会团体/民办非企业单位/其他 |
| respondent_legal_person | varchar(50) | YES |  | 被申请人法定代表人 |
| respondent_legal_title | varchar(50) | YES |  | 被申请人法定代表人职务 |
| respondent_reg_address | text | YES |  | 被申请人单位注册地 |
| respondent_reg_country | varchar(50) | YES | 中国 |  |
| case_source | varchar(50) | YES |  | 案件来源 |
| case_priority | int | YES | 0 | 案件优先级:0普通/1高 |
| guarantee_property_type | varchar(100) | YES |  |  |
| guarantee_object | varchar(200) | YES |  | 担保物名称 |
| pledge_property_type | varchar(50) | YES |  | 质押财产类型 |
| mortgage_property_type | varchar(50) | YES |  | 抵押财产类型 |
| created_by | varchar(50) | YES |  | 创建者账号 |

**索引:**

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | BTREE |

---

## property_clues

| 字段名 | 类型 | 允许空 | 默认值 | 备注 |
|--------|------|--------|--------|------|
| id | int | NO |  |  |
| case_id | int | NO |  | 案件ID |
| property_type | varchar(20) | YES |  | 财产类型 |
| description | text | YES |  |  |
| owner | varchar(50) | YES |  | 财产所有人 |
| bank_name | varchar(100) | YES |  | 开户银行 |
| bank_account | varchar(50) | YES |  | 银行账号 |
| amount | decimal(15,2) | YES |  | 数额 |
| currency | varchar(10) | YES | CNY | 币种 |
| property_value | decimal(15,2) | YES |  | 财产价值 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |  |
| property_province | varchar(50) | YES |  | 房产坐落位置-省份 |
| property_city | varchar(50) | YES |  |  |
| property_area | decimal(15,2) | YES |  |  |
| property_area_unit | varchar(20) | YES |  |  |
| property_location | varchar(200) | YES |  | 房产坐落位置-项目 |
| property_cert_no | varchar(50) | YES |  | 房产证号 |
| property_detail_location | varchar(200) | YES |  | 房产具体位置 |
| vehicle_brand_model | varchar(100) | YES |  | 车辆品牌型号 |
| vehicle_plate_no | varchar(50) | YES |  | 车牌号 |
| vehicle_location | varchar(50) | YES |  |  |
| vehicle_type | varchar(50) | YES |  |  |
| invested_company | varchar(200) | YES |  | 被投资企业名称 |
| stock_account | varchar(50) | YES |  | 证券账户 |
| stock_code | varchar(50) | YES |  | 股票代码 |
| stock_quantity | int | YES |  | 股票数量 |
| stock_reg_location | varchar(100) | YES |  | 发行单位注册地 |
| stock_name | varchar(100) | YES |  |  |
| fund_name | varchar(100) | YES |  |  |
| fund_quantity | int | YES |  |  |
| bond_name | varchar(100) | YES |  |  |
| bond_face_value | decimal(15,2) | YES |  |  |
| equipment_name | varchar(100) | YES |  |  |
| stock_company_name | varchar(200) | YES |  | 持股公司名称 |
| stock_ratio | decimal(5,2) | YES |  | 出资比例(%) |

**索引:**

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | BTREE |
| case_id | case_id | BTREE |

---

## system_config

| 字段名 | 类型 | 允许空 | 默认值 | 备注 |
|--------|------|--------|--------|------|
| id | int | NO |  |  |
| config_key | varchar(50) | NO |  | 配置键 |
| config_value | text | YES |  | 配置值 |
| config_desc | varchar(200) | YES |  | 配置说明 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |  |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP |  |

**索引:**

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | BTREE |
| config_key | config_key | BTREE |

**表备注:** 系统配置表

---

## system_users

| 字段名 | 类型 | 允许空 | 默认值 | 备注 |
|--------|------|--------|--------|------|
| id | int | NO |  |  |
| username | varchar(50) | NO |  | 登录账号 |
| password | varchar(100) | NO |  | 登录密码 |
| user_type | varchar(20) | YES | 个人用户 | 用户类型 |
| is_active | tinyint(1) | YES | 1 | 是否启用 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |  |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP |  |

**索引:**

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | BTREE |
| username | username | BTREE |

**表备注:** 系统用户表

---

## users

| 字段名 | 类型 | 允许空 | 默认值 | 备注 |
|--------|------|--------|--------|------|
| id | int | NO |  |  |
| username | varchar(50) | NO |  | 登录账号 |
| password | varchar(100) | NO |  | 登录密码 |
| user_type | varchar(20) | YES | 个人用户 | 用户类型 |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |  |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP |  |

**索引:**

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | BTREE |
| username | username | BTREE |

**表备注:** 系统用户表

---
