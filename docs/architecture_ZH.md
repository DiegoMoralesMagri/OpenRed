# O-Red 技术架构

## 系统概览

O-Red 由三层主要组件组成，协同工作以构建去中心化社交网络：

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   服务器 A      │    │   服务器 B      │    │   服务器 C      │
│  (用户)         │    │  (用户)         │    │  (用户)         │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │Node Client│  │◄──►│  │Node Client│  │◄──►│  │Node Client│  │
│  │    +DB    │  │    │  │    +DB    │  │    │  │    +DB    │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      中央 API             │
                    │   （注册服务）            │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   节点目录           │  │
                    │  │   服务发现           │  │
                    │  │   消息路由           │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## 详细组件

### 1. 中央 API（中央注册）

职责：
- 注册并验证新节点
- 维护活动节点目录
- 提供定位用户的发现服务
- 在节点之间路由消息
- 管理证书和安全

技术：
- 后端：FastAPI（Python）或 Express.js（Node.js）
- 数据库：PostgreSQL 用于持久化
- 缓存：Redis 提升性能
- 安全：JWT 用于认证，TLS 用于加密

主要端点：

```
POST /api/v1/nodes/register     # 注册新节点
GET  /api/v1/nodes/discover     # 按条件发现节点
POST /api/v1/messages/route     # 在节点之间路由消息
GET  /api/v1/nodes/{id}/status  # 节点状态
```

### 2. 节点客户端（用户应用）

职责：
- 完整的用户界面（SPA）
- 管理用户本地数据
- 与中央 API 通信
- 与其他节点直接通信
- 自动安装与配置

技术：
- 前端：React 或 Vue.js，具有 PWA 能力
- 本地后端：Node.js + Express 或 Python + Flask
- 数据库：为可移植性使用 SQLite，可选 PostgreSQL
- 安装器：用于自动部署的 shell/batch 脚本

本地数据模式：

```sql
-- 用户配置文件
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    display_name VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(255),
    node_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP
);

-- 帖子
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    content TEXT,
    media_urls JSON,
    visibility VARCHAR(50), -- public, friends, private
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 连接（好友/关注者）
CREATE TABLE connections (
    id INTEGER PRIMARY KEY,
    target_node_id VARCHAR(255),
    target_username VARCHAR(255),
    target_server_url VARCHAR(255),
    relationship_type VARCHAR(50), -- friend, follower, blocked
    status VARCHAR(50), -- pending, accepted, rejected
    created_at TIMESTAMP
);
```

### 3. 通信协议

**OpenRed 联邦（ORF）：**

```json
{
  "version": "1.0",
  "type": "message_type",
  "from": {
    "node_id": "unique_node_identifier",
    "server_url": "https://user-server.com",
    "username": "john_doe"
  },
  "to": {
    "node_id": "target_node_identifier",
    "server_url": "https://target-server.com",
    "username": "jane_smith"
  },
  "timestamp": "2025-09-19T10:30:00Z",
  "payload": {
    // 与消息类型相关的内容
  },
  "signature": "cryptographic_signature"
}
```

消息类型：
- `friend_request`：好友/关注请求
- `post_share`：分享帖子
- `direct_message`：私信
- `activity_update`：活动更新
- `content_sync`：内容同步

## 数据流

### 1. 注册新节点

```
1. 用户在其服务器上安装 Node Client
2. Node Client 生成加密密钥
3. Node Client 联系中央 API 进行注册
4. 中央 API 验证并分配唯一 node_id
5. Node Client 存储 node_id 并更新状态
6. 节点变得可被其他用户发现
```

### 2. 用户间通信

```
1. 用户 A 通过中央 API 查找用户 B
2. 中央 API 返回节点 B 的连接信息
3. 用户 A 将消息直接发送到节点 B
4. 节点 B 验证签名并处理消息
5. 节点 B 可直接回复用户 A
```

### 3. 内容分享

```
1. 用户 A 在其节点发布新内容
2. 节点 A 通知中央 API 有新发布
3. 用户 A 的好友通过其节点收到通知
4. 内容保存在节点 A；仅共享元数据
5. 其他用户可请求获取完整内容
```

## 安全与隐私

### 加密
- 传输中：所有通信使用 TLS 1.3
- 静态存储：敏感数据使用 AES-256 加密
- 端到端：私信使用公钥加密

### 身份验证
- 节点间：使用公/私钥的加密签名
- 用户：JWT 令牌与自动轮换
- 中央 API：节点认证使用 OAuth2

### 验证
- 消息完整性验证
- 防重放攻击
- 限速以防止垃圾信息和 DoS

## 部署与维护

### 自动安装

```bash
# 自动安装脚本
curl -sSL https://o-red.org/install.sh | bash

# 或手动下载
wget https://o-red.org/releases/latest/ored-installer.tar.gz
tar -xzf ored-installer.tar.gz
./install.sh
```

### 自动配置
- 服务器环境检测
- 自动配置数据库
- SSL 证书生成
- Web 代理配置（nginx/apache）

### 更新
- 自动更新系统
- 语义化版本控制
- 自动数据迁移
- 失败时回滚
