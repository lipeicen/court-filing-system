# 法院保全案件管理系统 - Windows 部署文档

## 一、环境要求

- Windows 10/11 或 Windows Server 2019+
- Python 3.11+
- MySQL 8.0+
- Chrome 浏览器
- Git（可选，用于拉取代码）

## 二、前置准备

### 1. 安装 Python
从官网下载并安装 Python 3.11+：
https://www.python.org/downloads/

安装时勾选 **Add Python to PATH**。

### 2. 安装 MySQL
下载并安装 MySQL 8.0 Community Server：
https://dev.mysql.com/downloads/mysql/

安装时设置 root 密码，并记住。

### 3. 安装 Chrome
下载安装 Google Chrome 浏览器。

## 三、获取代码

### 方式一：Git 克隆
```cmd
cd C:\
git clone https://github.com/lipeicen/court-filing-system.git court-auto-filing
```

### 方式二：直接解压
将项目压缩包解压到 `C:\court-auto-filing\`。

## 四、安装 Python 依赖

```cmd
cd C:\court-auto-filing
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
playwright install chromium
```

说明：
- `venv` 是 Python 虚拟环境，避免污染系统 Python
- `requirements.txt` 包含 Flask、PyMySQL、ddddocr、Playwright 等依赖
- `playwright install chromium` 安装 Chromium 浏览器内核

## 五、初始化数据库

### 1. 创建数据库
使用 MySQL 客户端或命令行登录：

```cmd
mysql -u root -p
```

执行：
```sql
CREATE DATABASE court_filing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 导入表结构
```cmd
mysql -u root -p court_filing < database\schema.sql
```

### 3. 创建专用用户（可选）
```sql
CREATE USER 'court_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON court_filing.* TO 'court_user'@'localhost';
FLUSH PRIVILEGES;
```

## 六、配置环境变量

### 1. 复制示例配置文件
```cmd
copy .env.example .env
```

### 2. 编辑 `.env`
用记事本或 VS Code 打开 `.env`：

```ini
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_NAME=court_filing

# 法院账号（系统从数据库 system_users 表读取，此处可留空）
COURT_USERNAME=
COURT_PASSWORD=你的法院密码

# 验证码服务：ocr 为本地识别，manual 为手动
CAPTCHA_SERVICE=ocr

# Flask 配置
FLASK_ENV=production
```

注意：
- `.env` 文件包含敏感信息，**不要提交到 Git**
- 已加入 `.gitignore`，不会误传

## 七、启动管理后台

管理后台是 Flask 网页端，用于案件管理、财产线索、立案状态同步等。

### 方式一：命令行启动（临时测试）

```cmd
cd C:\court-auto-filing
venv\Scripts\activate.bat
python admin_app.py
```

访问：http://127.0.0.1:5000

默认管理员账号：`admin` / `admin123`

按 `Ctrl + C` 停止。

### 方式二：注册为 Windows 服务（推荐生产环境）

使用 NSSM（Non-Sucking Service Manager）将管理后台注册为系统服务，实现：
- 开机自动启动
- 后台运行，无需保持命令行窗口
- 崩溃后自动重启

#### 7.1 下载 NSSM

访问：https://nssm.cc/download

下载后解压，根据系统选择：
- 64 位系统：`nssm-2.24/win64/nssm.exe`
- 32 位系统：`nssm-2.24/win32/nssm.exe`

将 `nssm.exe` 复制到 `C:\Windows\System32\`（需要管理员权限），或放到项目目录使用完整路径。

#### 7.2 注册服务

以管理员身份运行 CMD：

```cmd
nssm install CourtFiling "C:\court-auto-filing\venv\Scripts\python.exe" "C:\court-auto-filing\admin_app.py"
```

服务名称为 `CourtFiling`，可以自定义。

#### 7.3 启动服务

```cmd
nssm start CourtFiling
```

#### 7.4 管理服务

- 打开服务管理器：`services.msc`
- 找到 `CourtFiling` 服务
- 可设置启动类型为「自动」
- 可手动停止/重启

#### 7.5 卸载服务

```cmd
nssm stop CourtFiling
nssm remove CourtFiling confirm
```

## 八、自动登录

系统使用本地 OCR（ddddocr）自动识别法院网站验证码，无需第三方 API。

```cmd
cd C:\court-auto-filing
venv\Scripts\activate.bat
python auto_login.py
```

登录成功后会保存会话，后续自动立案可直接使用。

如 OCR 识别失败，可改用：
```cmd
python manual_login.py
```

## 九、自动立案

```cmd
cd C:\court-auto-filing
venv\Scripts\activate.bat
python final_auto_upload_db_v3.py
```

该脚本会：
1. 读取数据库中待立案的案件
2. 自动登录法院网站
3. 填写案件信息、当事人信息、财产线索、担保信息等
4. 上传材料并提交立案

## 十、同步立案状态

手动执行：
```cmd
run_sync.bat
```

或创建 Windows 计划任务，定时执行 `sync_filing_status.py`：
```cmd
cd C:\court-auto-filing
venv\Scripts\activate.bat
python sync_filing_status.py
```

全量同步：
```cmd
python sync_filing_status.py --full
```

## 十一、目录结构

```
C:\court-auto-filing/
├── admin_app.py                 # Flask 管理后台主程序
├── final_auto_upload_db_v3.py   # 自动立案脚本
├── sync_filing_status.py        # 立案状态同步脚本
├── auto_login.py                # 自动登录（OCR）
├── manual_login.py              # 手动登录
├── run_sync.bat                 # 同步启动批处理
├── requirements.txt             # Python 依赖列表
├── .env                         # 环境变量（本地配置，不提交）
├── .env.example                 # 环境变量示例
├── database/
│   └── schema.sql               # 数据库初始化脚本
├── admin/
│   └── templates/               # 管理后台页面模板
├── uploads/                     # 案件材料上传目录
├── screenshots/                 # 截图目录（调试用）
└── logs/                        # 日志目录
```

## 十二、常见问题

### Q1: 管理后台启动失败，提示数据库连接错误？
A:
- 检查 MySQL 是否已启动
- 检查 `.env` 中 `DB_HOST`、`DB_USER`、`DB_PASSWORD`、`DB_NAME` 是否正确
- 确认数据库 `court_filing` 已创建并导入 `schema.sql`

### Q2: Playwright 提示找不到浏览器？
A:
```cmd
venv\Scripts\activate.bat
playwright install chromium
```

### Q3: 验证码识别失败？
A:
- 确认已安装 ddddocr：`pip install ddddocr`
- 检查 `screenshots/captcha_auto.png` 是否清晰
- 改用手动登录：`python manual_login.py`

### Q4: 同步脚本闪退？
A:
- 检查 `.env` 数据库配置
- 检查 `system_users` 表中是否有有效法院账号
- 查看日志文件 `logs/sync_filing_status.log`

### Q5: 服务注册后无法启动？
A:
- 检查 NSSM 是否已正确安装
- 检查 `C:\court-auto-filing` 路径是否正确
- 检查 `.env` 配置是否完整
- 查看 Windows 事件查看器中的服务错误日志

## 十三、更新系统

拉取最新代码后：
```cmd
cd C:\court-auto-filing
git pull origin master
venv\Scripts\activate.bat
pip install -r requirements.txt
```

如果注册了服务，更新后重启服务：
```cmd
nssm restart CourtFiling
```

---
## 十四、账号隔离的立案状态同步（v2.2 新增）

### 功能说明

系统支持多个法院账号（`system_users` 表）。同步立案状态时：

- 每个法院账号的案件会标记对应的 `account` 字段
- 后台 **我的立案** 页面按当前登录用户配置的法院账号过滤，只能看到本账号的案件
- **清除新增标记** 也只清除当前账号的案件

### 相关数据表

以下表均已增加 `account` 字段，用于存储同步来源账号：

- `filing_status_trial`
- `filing_status_execution`
- `filing_status_preservation`
- `filing_status_mediation`
- `filing_status_bankruptcy`
- `filing_status_petition`

### 配置方法

1. 登录后台管理
2. 进入 **系统配置**
3. 填写当前登录用户对应的法院登录账号、密码、身份
4. 保存后，该用户登录 **我的立案** 时只显示此法院账号下的案件

### 同步方式

#### 后台手动同步

在 **我的立案** 页面点击 **同步立案状态** 按钮，系统会启动 `sync_filing_status.py` 同步所有配置的法院账号，但列表只展示当前账号的数据。

#### 命令行全量同步

```bash
cd C:\court-auto-filing
venv\Scripts\activate.bat
python sync_filing_status.py --full
```

### 旧数据迁移

升级前已同步的数据 `account` 字段为空，不会显示在 **我的立案** 列表中。执行一次同步后，新数据会带上 `account`。

如需让旧数据也按账号显示，可在 MySQL 中手动更新：

```sql
USE court_filing_status;

UPDATE filing_status_trial SET account = '13149930995' WHERE account IS NULL;
UPDATE filing_status_execution SET account = '13149930995' WHERE account IS NULL;
UPDATE filing_status_preservation SET account = '13149930995' WHERE account IS NULL;
UPDATE filing_status_mediation SET account = '13149930995' WHERE account IS NULL;
UPDATE filing_status_bankruptcy SET account = '13149930995' WHERE account IS NULL;
UPDATE filing_status_petition SET account = '13149930995' WHERE account IS NULL;
```

将 `13149930995` 替换为实际的法院账号。

---

文档版本：v2.2
最后更新：2026-07-09
