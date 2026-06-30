# 法院自动立案系统 v2.0

## 快速开始

### 1. 环境要求
- Python 3.8+
- Chrome 浏览器
- Windows 系统

### 2. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. 配置
复制 `.env.example` 到 `.env` 并填写：
```bash
copy .env.example .env
```

编辑 `.env`：
```
COURT_USERNAME=你的账号
COURT_PASSWORD=你的密码
```

### 4. 登录方式

#### 方式一：自动登录（推荐）
使用本地 OCR 自动识别验证码（ddddocr，无需第三方 API）

1. 确保已安装依赖：
```bash
pip install -r requirements.txt
```
2. 运行自动登录：
```bash
python auto_login.py
```

#### 方式二：手动登录
显示验证码图片，手动输入

```bash
python manual_login.py
```

#### 方式三：启动器（交互式）
```bash
python login_launcher.py
```

### 5. 使用系统

#### 初始化数据库
```bash
python main.py init-db
```

#### 创建案件
```bash
python main.py create-case --case-no CASE001
```

#### 处理案件（自动立案）
```bash
python main.py process 1
```

#### 批量处理
```bash
python main.py batch --limit 5
```

#### 查看案件列表
```bash
python main.py list
```

## 项目结构
```
court-auto-filing/
├── main.py                 # 主程序
├── config.py              # 配置文件
├── models/                # 数据模型
│   ├── __init__.py
│   └── models.py
├── core/                  # 核心模块
│   ├── base_browser.py    # 浏览器基类
│   └── browser_controller.py  # 法院浏览器控制
├── utils/                 # 工具模块
│   └── captcha_handler.py # 验证码处理
├── filing_service.py      # 立案服务
├── requirements.txt       # 依赖列表
├── .env                   # 环境变量
├── .env.example           # 环境变量示例
├── auto_login.py          # 自动登录脚本
├── manual_login.py        # 手动登录脚本
├── login_launcher.py      # 登录启动器
└── README.md              # 本文件
```

## 常见问题

### Q: 验证码识别失败？
A: 
- 确认已安装 `ddddocr`：`pip install ddddocr`
- 检查验证码图片是否清晰（见 `screenshots/captcha_auto.png`）
- 或者使用手动登录方式

### Q: 登录后会话过期？
A:
- 重新运行登录脚本
- 系统会自动保存会话到 `court_session.json`

### Q: 浏览器无法启动？
A:
- 检查 Chrome 是否安装
- 在 `.env` 中配置正确的 Chrome 路径：
```
BROWSER_EXECUTABLE_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
```

## 技术支持

如有问题，请检查日志文件：`logs/` 目录
