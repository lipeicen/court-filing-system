# 法院保全案件管理系统 - Linux部署文档

## 一、环境要求

- Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- Python 3.8+
- MySQL 5.7+ / MariaDB 10.3+
- Chrome/Chromium 浏览器

## 二、安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-pip python3-venv mysql-server chromium-browser

# CentOS/RHEL
sudo yum install -y python3-pip mariadb-server chromium
```

## 三、创建目录

```bash
sudo mkdir -p /opt/court-auto-filing/uploads
sudo mkdir -p /opt/court-auto-filing/screenshots
cd /opt/court-auto-filing
```

## 四、上传代码

将本压缩包解压到 `/opt/court-auto-filing/`

```bash
unzip 法院保全系统-linux-v1.0.zip -d /opt/court-auto-filing/
```

## 五、安装Python依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## 六、数据库配置

### 6.1 创建数据库

```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE court_filing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'court_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON court_filing.* TO 'court_user'@'localhost';
FLUSH PRIVILEGES;
```

### 6.2 导入表结构

```bash
mysql -u court_user -p court_filing < database/schema.sql
```

## 七、配置环境变量

```bash
export DB_HOST=localhost
export DB_USER=court_user
export DB_PASSWORD=your_password
export DB_NAME=court_filing
export UPLOAD_FOLDER=/opt/court-auto-filing/uploads
```

或写入 `/opt/court-auto-filing/.env`：

```
DB_HOST=localhost
DB_USER=court_user
DB_PASSWORD=your_password
DB_NAME=court_filing
UPLOAD_FOLDER=/opt/court-auto-filing/uploads
```

## 八、启动服务

### 8.1 前台测试

```bash
cd /opt/court-auto-filing
source venv/bin/activate
python admin_app.py
```

访问 http://服务器IP:5000

### 8.2 后台运行（推荐）

```bash
nohup python admin_app.py > app.log 2>&1 &
```

### 8.3 systemd服务（生产环境）

创建 `/etc/systemd/system/court-filing.service`：

```ini
[Unit]
Description=Court Filing System
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/court-auto-filing
Environment=DB_HOST=localhost
Environment=DB_USER=court_user
Environment=DB_PASSWORD=your_password
Environment=DB_NAME=court_filing
Environment=UPLOAD_FOLDER=/opt/court-auto-filing/uploads
ExecStart=/opt/court-auto-filing/venv/bin/python admin_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable court-filing
sudo systemctl start court-filing
sudo systemctl status court-filing
```

## 九、Nginx反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /uploads {
        alias /opt/court-auto-filing/uploads;
    }
}
```

## 十、自动立案脚本

```bash
cd /opt/court-auto-filing
source venv/bin/activate
python final_auto_upload_db_v3.py
```

或用cron定时执行：

```bash
0 9 * * * cd /opt/court-auto-filing && venv/bin/python final_auto_upload_db_v3.py >> /var/log/auto_filing.log 2>&1
```

## 十一、防火墙

```bash
# 开放5000端口
sudo ufw allow 5000/tcp
# 或仅允许本地+Nginx
sudo ufw allow 80/tcp
```

## 十二、目录权限

```bash
sudo chown -R www-data:www-data /opt/court-auto-filing
sudo chmod -R 755 /opt/court-auto-filing
sudo chmod -R 775 /opt/court-auto-filing/uploads
```
## 十三、账号隔离的立案状态同步（v2.2 新增）

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
cd /opt/court-auto-filing
source venv/bin/activate
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
