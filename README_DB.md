# 法院自动立案系统 - MySQL数据库版本

## 文件说明

| 文件 | 功能 |
|------|------|
| final_auto_upload_db.py | 数据库驱动版自动立案脚本 |
| case_manager.py | 案件管理工具 |
| db_init_case.py | 创建新案件示例 |

## 数据库配置

- host: localhost
- user: root
- password: lijiayu123
- database: court_filing

## 使用方法

### 1. 查看案件列表
```bash
python case_manager.py list
```

### 2. 查看案件详情
```bash
python case_manager.py show 保全2026001
```

### 3. 运行自动立案（使用数据库数据）
```bash
# 默认使用保全2026001
python final_auto_upload_db.py

# 指定案件
python final_auto_upload_db.py 保全2026001
python final_auto_upload_db.py 保全2026002
```

## 当前测试案件

| 案件编号 | 申请人 | 被申请人 | 保全金额 |
|---------|--------|---------|---------|
| 保全2026001 | 李小二 | 李小三 | 100,000 |
| 保全2026002 | 张三 | 李四 | 200,000 |

## 数据库表结构

- cases: 案件信息
- property_clues: 财产线索
- case_files: 材料文件
