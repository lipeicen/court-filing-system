# 法院自动立案系统 - Windows 部署指南

## 环境要求

- Windows 10/11 或 Windows Server 2019+
- Python 3.11+
- MySQL 8.0+
- Chrome 浏览器

## 部署步骤

### 1. 安装 Python 依赖

```cmd
cd C:\court-auto-filing
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
playwright install chromium
```

### 2. 安装 MySQL 并初始化数据库

```cmd
mysql -u root -p < database\schema.sql
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，修改数据库密码等配置：

```cmd
copy .env.example .env
```

编辑 `.env`：
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=court_filing

# 法院账号（从数据库 system_users 表读取，此处可留空）
COURT_USERNAME=
COURT_PASSWORD=
```

### 4. 启动管理后台

```cmd
venv\Scripts\activate.bat
python admin_app.py
```

访问 http://localhost:5000

### 5. 同步立案状态（手动或定时）

手动执行：
```cmd
run_sync.bat
```

或创建 Windows 计划任务定时执行 `sync_filing_status.py`。

### 6. 自动立案

```cmd
venv\Scripts\activate.bat
python final_auto_upload_db_v3.py
```

## 目录结构

```
court-auto-filing/
├── admin_app.py              # Flask 管理后台
├── final_auto_upload_db_v3.py  # 自动立案脚本
├── sync_filing_status.py   # 立案状态同步
├── run_sync.bat            # 同步启动批处理
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量示例
├── database/
│   └── schema.sql          # 数据库初始化脚本
├── admin/
│   └── templates/          # 管理页面模板
├── uploads/                # 案件材料上传目录
└── screenshots/            # 截图目录
```

## 服务部署（可选）

使用 NSSM 将管理后台注册为 Windows 服务：

```cmd
nssm install CourtFiling "C:\court-auto-filing\venv\Scripts\python.exe" "C:\court-auto-filing\admin_app.py"
nssm start CourtFiling
```

## 常见问题

1. **MySQL 连接失败**：检查 `.env` 中数据库配置
2. **Playwright 报错**：执行 `playwright install chromium`
3. **同步脚本闪退**：检查 `sync_filing_status.py` 中数据库密码配置
