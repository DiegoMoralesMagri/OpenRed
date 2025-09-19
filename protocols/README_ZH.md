# OpenRed 通信协议

此文件夹包含 OpenRed 节点之间通信协议的规范与实现。

## 结构

```
protocols/
├── specifications/      # 协议规范
│   ├── orf-protocol.md  # OpenRed 联邦协议
│   ├── security.md      # 安全规范
│   └── message-types.md # 支持的消息类型
├── implementations/     # 协议实现
│   ├── python/          # Python 实现
│   ├── javascript/      # JavaScript/Node.js 实现
│   └── rust/            # Rust 实现（性能）
├── examples/            # 使用示例
└── tests/               # 合规性测试
```

## 主要协议

### 1. OpenRed 联邦协议 (ORF)
节点间通信的主要协议，基于 JSON 通过 HTTP/HTTPS。

### 2. 安全与加密
- 通过加密签名进行身份验证
- 私信的端到端加密
- 消息完整性验证

### 3. 消息类型
- 服务消息（heartbeat、发现）
- 社交消息（帖子、评论、反应）
- 加密的私信
- 通知与更新
