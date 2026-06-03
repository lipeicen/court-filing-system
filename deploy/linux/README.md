# 法院保全案件管理系统 - Linux 部署

## 快速开始

```bash
# 1. 解压到 /opt
cd /opt
unzip court-filing-linux.zip
cd court-auto-filing

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 3. 创建目录
mkdir -p uploads screenshots

# 4. 配置数据库
mysql -u root -p < database/schema.sql

# 5. 设置环境变量
export DB_PASSWORD=your_password

# 6. 启动
./start.sh
```

## Systemd 服务

```bash
sudo cp court-filing.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable court-filing
sudo systemctl start court-filing
```
