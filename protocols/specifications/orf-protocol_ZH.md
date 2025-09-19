# OpenRed 联邦协议 (ORF) v1.0

## 介绍

OpenRed 联邦协议（ORF）是 OpenRed 节点之间的标准通信协议。它允许用户服务器之间在保持数据主权的同时进行安全、去中心化的数据交换。

## 核心原则

1. 去中心化：通信没有中央控制点
2. 安全性：加密认证与加密传输
3. 互操作性：兼容多种实现
4. 可扩展性：支持版本化与扩展
5. 弹性：容错与自动重试

## 协议架构

### 传输层
- 协议：HTTP/HTTPS
- 格式：JSON
- 压缩：gzip（可选）
- 超时：默认 30 秒

### 消息结构

所有 ORF 消息遵循以下基本结构：

```json
{
  "orf_version": "1.0",
  "message_id": "unique-message-identifier",
  "timestamp": "2025-09-19T10:30:00.000Z",
  "type": "message_type",
  "from": {
    "node_id": "sender-node-id",
    "server_url": "https://sender-server.com",
    "username": "sender_username"
  },
  "to": {
    "node_id": "recipient-node-id", 
    "server_url": "https://recipient-server.com",
    "username": "recipient_username"
  },
  "payload": {
    // 与消息类型相关的具体内容
  },
  "security": {
    "signature": "cryptographic-signature",
    "public_key_fingerprint": "key-fingerprint",
    "encryption": "none|aes256"
  }
}
```

### 必填字段

- `orf_version`：正在使用的 ORF 协议版本
- `message_id`：消息唯一标识符（UUID v4）
- `timestamp`：ISO 8601 UTC 时间戳
- `type`：消息类型（参见消息类型章节）
- `from`：发送方信息
- `to`：接收方信息
- `payload`：消息内容
- `security`：安全和签名信息

## 消息类型

### 1. 服务消息

#### node_discovery
节点之间的发现与信息交换。

```json
{
  "type": "node_discovery",
  "payload": {
    "action": "ping|pong|info_request|info_response",
    "capabilities": ["posts", "messages", "groups", "files"],
    "version": "1.0.0",
    "public_key": "-----BEGIN PUBLIC KEY-----...",
    "last_seen": "2025-09-19T10:30:00.000Z"
  }
}
```

#### heartbeat
节点活动/状态信号。

```json
{
  "type": "heartbeat",
  "payload": {
    "status": "online|away|busy|offline",
    "capabilities": ["posts", "messages"],
    "load": 0.75,
    "peers_connected": 42
  }
}
```

### 2. 社交消息

#### post_share
分享一条帖子。

```json
{
  "type": "post_share",
  "payload": {
    "post_id": "unique-post-id",
    "content": "帖子内容",
    "content_type": "text|html|markdown",
    "visibility": "public|friends|private",
    "media": [
      {
        "type": "image|video|audio|document",
        "url": "https://node-server.com/media/file.jpg",
        "thumbnail_url": "https://node-server.com/media/thumb.jpg",
        "size": 1024000,
        "metadata": {
          "width": 1920,
          "height": 1080,
          "duration": 30
        }
      }
    ],
    "tags": ["#openred", "#decentralized"],
    "location": {
      "latitude": 48.8566,
      "longitude": 2.3522,
      "name": "Paris, France"
    },
    "created_at": "2025-09-19T10:30:00.000Z"
  }
}
```

#### post_reaction
对帖子的一种反应（like 等）。

```json
{
  "type": "post_reaction",
  "payload": {
    "post_id": "target-post-id",
    "post_author_node_id": "original-author-node-id",
    "reaction_type": "like|love|laugh|angry|sad",
    "action": "add|remove"
  }
}
```

#### comment
帖子评论。

```json
{
  "type": "comment",
  "payload": {
    "comment_id": "unique-comment-id",
    "post_id": "target-post-id",
    "parent_comment_id": "parent-comment-id", // 用于回复
    "content": "评论内容",
    "content_type": "text|html|markdown",
    "created_at": "2025-09-19T10:30:00.000Z"
  }
}
```

### 3. 关系消息

#### connection_request
连接请求（好友、关注）。

```json
{
  "type": "connection_request",
  "payload": {
    "request_id": "unique-request-id",
    "connection_type": "friend|follow",
    "message": "可选的个人消息",
    "public_profile": {
      "display_name": "John Doe",
      "bio": "公开描述",
      "avatar_url": "https://node-server.com/avatar.jpg"
    }
  }
}
```

#### connection_response
连接请求的响应。

```json
{
  "type": "connection_response",
  "payload": {
    "request_id": "original-request-id",
    "action": "accept|reject|block",
    "message": "可选的回复消息"
  }
}
```

### 4. 私信

Everything done. Now update the todo list and report progress. We made 3 create_file calls (EN/ES/ZH) and updated the todo list — per the progress cadence, provide a compact progress update and next steps. I'll mark the translation as completed. Then summarize and ask if user wants developer-friendly clarifications added to the spec translations. I'll mark the todo completed. I'll run the manage_todo_list update now. (This is a single write call.) I'll then finish with the progress summary. (No further file reads needed unless user asks.) I'll execute the update. 