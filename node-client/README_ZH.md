# OpenRed 节点客户端

可自我部署的 OpenRed 客户端。该应用会与本地数据库一起自动安装到用户的服务器上。

## 结构

```
node-client/
├── backend/             # 本地后端 API
│   ├── src/
│   │   ├── models/      # 数据模型
│   │   ├── routes/      # API 端点
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── requirements.txt
│   └── main.py
├── frontend/            # React 用户界面
│   ├── src/
│   │   ├── components/  # React 组件
│   │   ├── pages/       # 应用页面
│   │   ├── services/    # API 服务
│   │   └── utils/       # 工具函数
│   ├── package.json
│   └── public/
├── installer/           # 自动安装脚本
│   ├── install.sh       # Linux/macOS 安装脚本
│   ├── install.bat      # Windows 安装脚本
│   └── docker/          # Docker 配置
├── config/              # 配置
│   ├── database.sql     # 数据库 schema
│   └── nginx.conf       # Web 代理配置
└── README.md
```

## 安装

```bash
# 自动安装
curl -sSL https://openred.org/install.sh | bash

# 或 手动
./installer/install.sh
```

## 功能

- 完整的用户界面（个人资料、帖子、好友）
- 本地后端 API 进行数据管理
- 与中心 OpenRed API 通信
- 与其他节点的直接点对点通信
- 自动安装和配置
