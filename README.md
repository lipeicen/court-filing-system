# 法院保全案件管理系统 - Docker 部署

## 快速启动

```bash
cd deploy/docker

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止
docker-compose down
```

## 访问

- 管理后台: http://localhost:5000
- MySQL: localhost:3306 (root/lijiayu123)

## 数据持久化

- MySQL数据: Docker volume `mysql_data`
- 上传文件: Docker volume `uploads`
- 截图: Docker volume `screenshots`

## 重建

```bash
docker-compose down -v  # 清除数据
docker-compose up --build -d
```
