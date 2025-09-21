# 技术文档 - OpenRed Central API v2.0

## 执行摘要

OpenRed Central API v2.0 是使用 FastAPI 构建的现代 REST API，为 OpenRed 生态系统提供集中式服务。该 API 管理节点发现、服务间通信和审计日志，具有异步架构和多语言结构化日志记录功能。

## 系统架构

### 概览
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    网页客户端    │    │  OpenRed中央    │    │     数据库      │
│                 │◄──►│   API v2.0      │◄──►│    SQLite       │
│   (前端应用)     │    │   (FastAPI)     │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Redis 缓存     │
                       │   (可选)        │
                       └─────────────────┘
```

### 核心组件

1. **FastAPI 服务器**: 带有 REST 端点的应用程序核心
2. **数据库引擎**: 支持 SQLite/PostgreSQL 的 SQLAlchemy ORM
3. **日志系统**: 多语言结构化 JSON 日志记录
4. **加密服务**: 安全令牌和身份验证处理
5. **审计系统**: 完整的管理操作日志记录

## API 端点

### 系统健康端点

#### GET /health
**描述**: 检查 API 及其组件的健康状态

**示例响应**:
```json
{
    "status": "healthy",
    "version": "2.0.0",
    "timestamp": "2025-09-21T02:04:52Z",
    "uptime_seconds": 1234.56,
    "services": {
        "database": "connected",
        "redis": "connected",
        "crypto": "initialized"
    }
}
```

#### GET /
**描述**: 包含项目信息的主页

**响应**: 包含基本文档和系统状态的 HTML 页面

### 节点管理

#### GET /api/discover
**描述**: 发现 OpenRed 网络中的所有活跃节点

**查询参数**:
- `status` (可选): 按节点状态过滤 (active, inactive, maintenance)
- `service` (可选): 按服务类型过滤

**示例响应**:
```json
{
    "nodes": [
        {
            "node_id": "node-001",
            "host": "192.168.1.100",
            "port": 8001,
            "status": "active",
            "services": ["storage", "processing"],
            "last_seen": "2025-09-21T02:04:52Z",
            "metadata": {
                "version": "1.0.0",
                "capabilities": ["async", "backup"]
            }
        }
    ],
    "total_nodes": 1,
    "active_nodes": 1
}
```

#### POST /api/nodes
**描述**: 在网络中注册新节点

**请求体**:
```json
{
    "node_id": "new-node-001",
    "host": "192.168.1.200",
    "port": 8002,
    "status": "active",
    "services": ["api", "storage"],
    "metadata": {
        "version": "2.0.0",
        "description": "主存储节点"
    }
}
```

**成功响应**:
```json
{
    "success": true,
    "message": "节点注册成功",
    "node_id": "new-node-001",
    "registered_at": "2025-09-21T02:04:52Z"
}
```

#### GET /nodes
**描述**: 节点管理的网页界面

**响应**: 包含交互式节点列表的 HTML 页面

## 数据库架构

### 表: nodes
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id VARCHAR(255) UNIQUE NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    services TEXT, -- JSON 数组
    metadata TEXT, -- JSON 对象
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 表: messages
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node VARCHAR(255) NOT NULL,
    to_node VARCHAR(255),
    message_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT, -- JSON 对象
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);
```

### 表: auth_sessions
```sql
CREATE TABLE auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 表: audit_logs
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    target VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata TEXT, -- JSON 对象
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 配置变量

### 环境变量
```bash
# 数据库配置
DATABASE_URL="sqlite:///openred_prod.db"
# 或使用 PostgreSQL:
# DATABASE_URL="postgresql://user:password@localhost/openred"

# 服务器配置
HOST="0.0.0.0"
PORT="8000"
WORKERS="4"

# 安全配置
SECRET_KEY="你的超级安全密钥"
JWT_SECRET="你的jwt密钥"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"

# Redis 配置 (可选)
REDIS_URL="redis://localhost:6379/0"
REDIS_PASSWORD="你的redis密码"

# 日志配置
LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_FILE="openred_api.log"

# CORS 配置
CORS_ENABLED="false"
CORS_ORIGINS="http://localhost:3000,https://your-domain.com"

# 监控配置
METRICS_ENABLED="true"
HEALTH_CHECK_INTERVAL="30"
```

### 配置文件 (config.json)
```json
{
    "database": {
        "type": "sqlite",
        "path": "openred_prod.db",
        "pool_size": 10,
        "max_overflow": 20
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4,
        "reload": false
    },
    "security": {
        "cors_enabled": false,
        "https_only": true,
        "max_request_size": "10MB"
    },
    "monitoring": {
        "enabled": true,
        "metrics_endpoint": "/metrics",
        "health_endpoint": "/health"
    },
    "logging": {
        "level": "INFO",
        "format": "json",
        "multilingual": true,
        "file": "logs/openred_api.log"
    }
}
```

## 日志系统

### 结构化日志格式
```json
{
    "timestamp": "2025-09-21T02:04:52.467203Z",
    "level": "info",
    "logger": "openred.central_api",
    "event": "Logging configured",
    "filename": "main_new.py",
    "lineno": 66,
    "multilingual": {
        "fr": "Configuration du logging terminée",
        "en": "Logging configured",
        "es": "Configuración de logging completada",
        "zh": "日志配置完成"
    }
}
```

### 日志类别
- **INFO**: 正常操作事件
- **WARNING**: 异常但非关键情况
- **ERROR**: 需要注意的错误
- **CRITICAL**: 影响操作的关键错误

## 安全系统

### JWT 身份验证
```python
# 令牌生成
token = jwt.encode({
    "node_id": "node-001",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow(),
    "iss": "openred-central-api"
}, secret_key, algorithm="HS256")
```

### 敏感数据加密
```python
# 使用加密服务
crypto_service = CryptoService()
encrypted_data = crypto_service.encrypt("敏感数据")
decrypted_data = crypto_service.decrypt(encrypted_data)
```

## 监控和指标

### 系统指标
- **CPU**: 处理器使用百分比
- **内存**: RAM 使用量（MB 和百分比）
- **磁盘**: 已用和可用空间
- **网络**: 发送/接收字节数

### API 指标
- **响应时间**: 每个端点的平均延迟
- **成功率**: 成功响应的百分比
- **吞吐量**: 每秒请求数 (RPS)
- **错误**: 错误计数和分类

### 数据库指标
- **连接**: 活跃连接和连接池
- **查询**: 平均执行时间
- **大小**: 表使用的空间

## 错误处理

### HTTP 状态码
- **200**: 操作成功
- **201**: 资源创建成功
- **400**: 错误请求
- **401**: 未认证
- **403**: 访问被禁止
- **404**: 资源未找到
- **409**: 冲突（例如：节点已存在）
- **422**: 验证错误
- **500**: 内部服务器错误

### 错误响应格式
```json
{
    "error": {
        "code": "NODE_ALREADY_EXISTS",
        "message": "具有此ID的节点已存在",
        "details": {
            "node_id": "duplicate-node",
            "existing_since": "2025-09-20T10:00:00Z"
        },
        "timestamp": "2025-09-21T02:04:52Z",
        "request_id": "req_123456789"
    }
}
```

## 开发和测试

### 开发环境设置
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 开发模式运行
python main_new.py
```

### 运行测试
```bash
# 集成测试
python test_integration_live.py

# 性能测试
python performance_optimizer.py

# 实时监控
python monitoring.py
```

## 可扩展性

### 多工作进程配置
```bash
# 使用 Uvicorn 多工作进程
uvicorn main_new:app --host 0.0.0.0 --port 8000 --workers 4

# 使用 Gunicorn
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 负载均衡
为了高可用性，在负载均衡器（如 nginx）后配置多个实例：

```nginx
upstream openred_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## 贡献

### 代码标准
- **风格**: Python 遵循 PEP 8
- **文档**: 公共函数使用中文文档字符串
- **测试**: 最低 80% 覆盖率
- **日志**: 使用结构化日志系统

### 开发流程
1. Fork 仓库
2. 创建功能分支: `git checkout -b feature/new-functionality`
3. 开发和测试更改
4. 创建带详细描述的 Pull Request

## 支持

### 附加文档
- **部署指南**: 参见 `DEPLOYMENT_ZH.md`
- **监控脚本**: 参见 `monitoring.py`
- **性能优化**: 参见 `performance_optimizer.py`

### 联系方式
- **仓库**: https://github.com/DiegoMoralesMagri/OpenRed
- **问题**: 通过 GitHub Issues 报告错误和请求功能
- **文档**: 提供多语言版本 (ES/EN/FR/ZH)

---

**OpenRed Central API v2.0** - OpenRed 生态系统的分布式管理系统
*文档更新时间: 2025年9月21日*
