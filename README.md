# 法院保全案件管理系统

## 分支说明

| 分支 | 用途 | 部署方式 |
|------|------|---------|
| `master` | 主分支（当前代码） | - |
| `windows` | Windows 部署版 | 直接运行 `python admin_app.py` |
| `linux` | Linux 部署版 | `./start.sh` 或 systemd |
| `docker` | Docker 部署版 | `docker-compose up -d` |

## 快速开始

```bash
# Windows
git clone -b windows https://github.com/lipeicen/court-filing-system.git

# Linux
git clone -b linux https://github.com/lipeicen/court-filing-system.git

# Docker
git clone -b docker https://github.com/lipeicen/court-filing-system.git
```

## 功能

- 案件增删改查
- 财产线索管理
- 文件上传/批量上传
- Excel 批量导入
- 自动立案（Playwright）
- 多用户登录/注册
