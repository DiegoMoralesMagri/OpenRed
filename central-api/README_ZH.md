# OpenRed 中央 API

用于 OpenRed 生态系统节点注册与发现的中央 API。

## 结构

```
central-api/
├── src/
│   ├── models/          # 数据模型
│   ├── routes/          # API 端点
│   ├── services/        # 业务逻辑
│   ├── utils/           # 工具
│   └── config/          # 配置
├── tests/               # 单元测试
├── requirements.txt     # Python 依赖
├── main.py              # 入口点
└── README.md            # 文档
```

## 安装

```bash
cd central-api
pip install -r requirements.txt
python main.py
```

## 端点

- `POST /api/v1/nodes/register` - 注册节点
- `GET /api/v1/nodes/discover` - 发现节点
- `POST /api/v1/messages/route` - 路由消息
- `GET /api/v1/nodes/{id}/status` - 节点状态
