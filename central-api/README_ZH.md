# OpenRed 中央 API v2.0 - 完整文档

## 🚀 概述

**OpenRed 中央 API v2.0** 是 OpenRed 分布式生态系统中央 API 的完全重新设计。此版本带来安全、可扩展和高效的架构，用于管理网络节点的注册、发现和通信。

## ✨ v2.0 新功能

### 🔐 增强安全性
- **加密身份验证** 使用 RSA 签名
- **JWT 自动轮换** (短期令牌 + 刷新)
- **自适应速率限制** 按端点和 IP
- **端到端加密** 敏感数据
- **完整审计日志** 支持匿名化

### ⚡ 性能和可扩展性
- **无状态架构** 用于水平扩展
- **分布式 Redis 缓存** 提升性能
- **优化数据库** 使用复合索引
- **实时监控和指标**
- **智能负载均衡**

### 🛡️ 高级保护
- **OWASP 安全标头**
- **CSRF/XSS 保护**
- **严格数据验证**
- **异常检测**
- **断路器模式**

## 📁 项目架构

```
central-api/
├── SECURITY_REQUIREMENTS_*.md    # 详细安全要求
├── ARCHITECTURE_*.md            # 完整技术文档
├── main_new.py                  # 优化的主入口点
├── requirements.txt             # 更新的依赖项
├── src/
│   ├── core/                    # 配置和核心服务
│   │   ├── config.py           # 集中配置
│   │   ├── security.py         # 加密服务
│   │   └── logging.py          # 安全结构化日志
│   ├── models/
│   │   ├── database.py         # 优化的 SQLAlchemy 模型
│   │   └── schemas.py          # Pydantic 验证模式
│   ├── services/
│   │   ├── auth_service.py     # 完整身份验证服务
│   │   ├── node_service.py     # 节点管理
│   │   └── message_service.py  # 消息路由
│   ├── middleware/
│   │   ├── rate_limiting.py    # 高级速率限制
│   │   ├── security_headers.py # 安全标头
│   │   └── request_logging.py  # 请求日志
│   ├── api/v1/                 # 版本化 API 路由
│   └── utils/                  # 工具和助手
└── docs/                       # 详细文档
```

## 🔧 安装和配置

### 1. 安装依赖项

```bash
cd central-api
pip install -r requirements.txt
```

### 2. 配置环境变量

创建包含所需配置的 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/openred_central
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis 配置
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# JWT 配置
JWT_SECRET_KEY=your-secure-jwt-secret-256-bits
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 安全配置
ENCRYPTION_KEY=your-32-byte-encryption-key
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# 网络配置
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000","https://openred.io"]

# 监控配置
MONITORING_ENABLED=true
METRICS_PORT=9090
LOG_LEVEL=INFO
```

### 3. 设置数据库

```bash
# 安装 PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb openred_central
sudo -u postgres createuser openred_user

# 运行迁移
alembic upgrade head
```

### 4. 设置 Redis

```bash
# 安装 Redis
# Ubuntu/Debian  
sudo apt-get install redis-server

# 配置 Redis (可选)
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 🚀 运行

### 开发模式

```bash
# 开发模式，自动重新加载
python main_new.py --env development

# 或直接使用 uvicorn
uvicorn main_new:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
# 优化的生产模式
python main_new.py --env production

# 或使用 gunicorn
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API 端点

### 🔐 身份验证

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/auth/register` | 注册新节点 |
| POST | `/api/v1/auth/login` | 登录 |
| POST | `/api/v1/auth/refresh` | 刷新 JWT 令牌 |
| POST | `/api/v1/auth/logout` | 注销 |
| GET | `/api/v1/auth/verify` | 验证有效令牌 |

### 🌐 节点管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/nodes` | 列出所有节点 |
| GET | `/api/v1/nodes/{node_id}` | 获取特定节点 |
| PUT | `/api/v1/nodes/{node_id}` | 更新节点信息 |
| DELETE | `/api/v1/nodes/{node_id}` | 注销节点 |
| POST | `/api/v1/nodes/{node_id}/heartbeat` | 节点心跳 |

### 💬 消息传递

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/messages/send` | 在节点间发送消息 |
| GET | `/api/v1/messages/pending/{node_id}` | 获取待处理消息 |
| PUT | `/api/v1/messages/{message_id}/read` | 标记消息为已读 |
| GET | `/api/v1/messages/history` | 消息历史 |

### 📊 监控

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/health` | API 健康状态 |
| GET | `/api/v1/metrics` | 性能指标 |
| GET | `/api/v1/status` | 系统状态 |
| GET | `/docs` | 交互式 Swagger 文档 |
| GET | `/redoc` | ReDoc 文档 |

## 🔒 安全性

### 身份验证流程

1. **注册**: 节点发送 RSA 公钥证书
2. **挑战**: 服务器发送随机挑战
3. **响应**: 节点使用私钥签名挑战  
4. **验证**: 服务器验证签名
5. **令牌**: 颁发 JWT 访问 + 刷新令牌

### 安全功能

- ✅ **基于 RSA-2048 的加密身份验证**
- ✅ **JWT 令牌自动轮换** 每 15 分钟
- ✅ **使用 Redis 的自适应速率限制**
- ✅ **使用 AES-256 的敏感数据加密**
- ✅ **使用安全标头的 CSRF/XSS 保护**
- ✅ **支持匿名化的完整审计日志**
- ✅ **所有输入数据的严格验证**

## 📈 监控和指标

### 可用指标

- **性能**: 延迟、吞吐量、错误率
- **安全**: 身份验证尝试、速率违规
- **系统**: CPU 使用率、内存、数据库连接
- **业务**: 活跃节点、已处理消息、正常运行时间

### 仪表板

- **Prometheus**: 在 `/api/v1/metrics` 收集指标
- **Grafana**: 指标可视化和警报
- **健康检查**: `/api/v1/health` 端点用于监控

## 🐳 部署

### Docker

```bash
# 构建镜像
docker build -t openred-central-api .

# 运行容器
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  openred-central-api
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/openred
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: openred
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openred-central-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openred-central-api
  template:
    metadata:
      labels:
        app: openred-central-api
    spec:
      containers:
      - name: api
        image: openred-central-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: openred-secrets
              key: database-url
```

## 🧪 测试

### 单元测试

```bash
# 运行所有测试
pytest

# 带覆盖率的测试
pytest --cov=src

# 特定测试
pytest tests/test_auth.py
```

### 集成测试

```bash
# 完整 API 测试
pytest tests/integration/

# 负载测试
locust -f tests/load/locustfile.py
```

### 安全测试

```bash
# 漏洞分析
bandit -r src/

# 渗透测试
python tests/security/security_tests.py
```

## 📖 其他文档

- [**SECURITY_REQUIREMENTS.md**](SECURITY_REQUIREMENTS_ZH.md) - 详细安全要求
- [**ARCHITECTURE.md**](ARCHITECTURE_ZH.md) - 完整技术文档  
- [**EXAMPLES.md**](EXAMPLES_ZH.md) - 使用和集成示例
- [**API_REFERENCE.md**](docs/API_REFERENCE_ZH.md) - 完整 API 参考

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/new-feature`)
3. 提交更改 (`git commit -am 'Add new feature'`)
4. 推送到分支 (`git push origin feature/new-feature`)
5. 创建 Pull Request

## 📄 许可证

此项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🆘 支持

- **Issues**: [GitHub Issues](https://github.com/openred/central-api/issues)
- **讨论**: [GitHub Discussions](https://github.com/openred/central-api/discussions)
- **邮箱**: support@openred.io
- **文档**: [docs.openred.io](https://docs.openred.io)

---

**OpenRed 中央 API v2.0** - 构建安全分布式网络的未来 🚀

- `POST /api/v1/nodes/register` - 注册节点
- `GET /api/v1/nodes/discover` - 发现节点
- `POST /api/v1/messages/route` - 路由消息
- `GET /api/v1/nodes/{id}/status` - 节点状态
