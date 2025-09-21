# 使用示例 - OpenRed 中央 API v2.0

本文档提供 OpenRed 中央 API v2.0 的完整使用示例，包括 SDK 集成、认证、节点管理和消息传递。

## 🚀 快速开始

### 初始配置

```python
import asyncio
import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import jwt
import json

class OpenRedClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.private_key = None
        self.public_key = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
```

## 🔐 认证和安全

### 1. RSA 密钥生成

```python
def generate_rsa_keypair():
    """生成用于认证的 RSA 密钥对。"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    
    # PEM 序列化
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

# 使用示例
private_key_pem, public_key_pem = generate_rsa_keypair()
print("私钥已生成并安全存储")
```

### 2. 节点注册

```python
async def register_node(client: OpenRedClient, node_info: dict):
    """在 OpenRed 网络中注册新节点。"""
    
    # 加载私钥
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    client.private_key = private_key
    
    # 注册数据
    registration_data = {
        "node_id": node_info["node_id"],
        "name": node_info["name"],
        "type": node_info["type"],
        "capabilities": node_info["capabilities"],
        "public_key": public_key_pem.decode('utf-8'),
        "endpoint": node_info["endpoint"],
        "metadata": node_info.get("metadata", {})
    }
    
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/register",
        json=registration_data
    ) as response:
        if response.status == 201:
            result = await response.json()
            print(f"节点注册成功: {result['node_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"注册错误: {error}")

# 使用示例
node_config = {
    "node_id": "node-001",
    "name": "主节点",
    "type": "gateway",
    "capabilities": ["routing", "storage", "compute"],
    "endpoint": "https://node001.openred.io:8443",
    "metadata": {
        "region": "eu-west-1",
        "version": "2.0.0"
    }
}

async with OpenRedClient() as client:
    await register_node(client, node_config)
```

### 3. 挑战/响应认证

```python
async def authenticate_node(client: OpenRedClient, node_id: str):
    """使用挑战/响应系统认证节点。"""
    
    # 步骤 1: 请求挑战
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/login",
        json={"node_id": node_id}
    ) as response:
        if response.status == 200:
            challenge_data = await response.json()
            challenge = challenge_data["challenge"]
        else:
            raise Exception("无法获取挑战")
    
    # 步骤 2: 签名挑战
    signature = client.private_key.sign(
        challenge.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # 步骤 3: 发送签名响应
    auth_response = {
        "node_id": node_id,
        "challenge": challenge,
        "signature": signature.hex()
    }
    
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/verify",
        json=auth_response
    ) as response:
        if response.status == 200:
            tokens = await response.json()
            client.access_token = tokens["access_token"]
            client.refresh_token = tokens["refresh_token"]
            print("认证成功")
            return tokens
        else:
            raise Exception("认证失败")

# 使用示例
async with OpenRedClient() as client:
    client.private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    await authenticate_node(client, "node-001")
```

## 🌐 节点管理

### 1. 节点发现

```python
async def discover_nodes(client: OpenRedClient, filters: dict = None):
    """发现网络中可用的节点。"""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    params = {}
    
    if filters:
        if "type" in filters:
            params["type"] = filters["type"]
        if "capabilities" in filters:
            params["capabilities"] = ",".join(filters["capabilities"])
        if "region" in filters:
            params["region"] = filters["region"]
    
    async with client.session.get(
        f"{client.base_url}/api/v1/nodes",
        headers=headers,
        params=params
    ) as response:
        if response.status == 200:
            nodes = await response.json()
            print(f"发现 {len(nodes['nodes'])} 个节点")
            return nodes["nodes"]
        else:
            raise Exception("节点发现过程中出错")

# 使用示例
async with OpenRedClient() as client:
    # 需要预先认证
    await authenticate_node(client, "node-001")
    
    # 发现所有节点
    all_nodes = await discover_nodes(client)
    
    # 仅发现存储节点
    storage_nodes = await discover_nodes(client, {
        "type": "storage",
        "capabilities": ["storage"]
    })
```

### 2. 节点状态更新

```python
async def update_node_status(client: OpenRedClient, node_id: str, status_data: dict):
    """更新节点状态和元数据。"""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    update_data = {
        "status": status_data["status"],
        "load": status_data.get("load", 0),
        "available_resources": status_data.get("available_resources", {}),
        "metadata": status_data.get("metadata", {}),
        "last_seen": status_data.get("last_seen")
    }
    
    async with client.session.put(
        f"{client.base_url}/api/v1/nodes/{node_id}",
        headers=headers,
        json=update_data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"节点 {node_id} 状态已更新")
            return result
        else:
            error = await response.text()
            raise Exception(f"更新错误: {error}")

# 使用示例
status_update = {
    "status": "active",
    "load": 0.65,
    "available_resources": {
        "cpu": 75,
        "memory": 80,
        "storage": 90
    },
    "metadata": {
        "version": "2.0.1",
        "uptime": "72h",
        "connections": 150
    }
}

await update_node_status(client, "node-001", status_update)
```

### 3. 自动心跳

```python
import asyncio
from datetime import datetime

async def heartbeat_loop(client: OpenRedClient, node_id: str, interval: int = 30):
    """与中央 API 保持心跳连接。"""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    while True:
        try:
            heartbeat_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy",
                "metrics": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.4,
                    "network_in": 1024,
                    "network_out": 2048
                }
            }
            
            async with client.session.post(
                f"{client.base_url}/api/v1/nodes/{node_id}/heartbeat",
                headers=headers,
                json=heartbeat_data
            ) as response:
                if response.status == 200:
                    print(f"为 {node_id} 发送心跳")
                else:
                    print(f"心跳失败: {response.status}")
            
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"心跳错误: {e}")
            await asyncio.sleep(interval)

# 启动后台心跳
asyncio.create_task(heartbeat_loop(client, "node-001"))
```

## 💬 节点间消息传递

### 1. 发送消息

```python
async def send_message(client: OpenRedClient, message_data: dict):
    """向一个或多个节点发送消息。"""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    # 加密敏感内容
    if message_data.get("encrypt", False):
        # 这里您将实现端到端加密
        pass
    
    message_payload = {
        "from_node": message_data["from_node"],
        "to_nodes": message_data["to_nodes"],
        "message_type": message_data["message_type"],
        "content": message_data["content"],
        "priority": message_data.get("priority", "normal"),
        "ttl": message_data.get("ttl", 3600),
        "metadata": message_data.get("metadata", {})
    }
    
    async with client.session.post(
        f"{client.base_url}/api/v1/messages/send",
        headers=headers,
        json=message_payload
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"消息已发送: {result['message_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"发送错误: {error}")

# 使用示例
message = {
    "from_node": "node-001",
    "to_nodes": ["node-002", "node-003"],
    "message_type": "data_sync",
    "content": {
        "action": "sync_request",
        "data_hash": "abc123...",
        "timestamp": datetime.utcnow().isoformat()
    },
    "priority": "high",
    "ttl": 1800,
    "metadata": {
        "correlation_id": "sync-001",
        "retry_count": 0
    }
}

await send_message(client, message)
```

### 2. 接收消息

```python
async def get_pending_messages(client: OpenRedClient, node_id: str):
    """获取节点的待处理消息。"""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/messages/pending/{node_id}",
        headers=headers
    ) as response:
        if response.status == 200:
            messages = await response.json()
            print(f"获取了 {len(messages['messages'])} 条消息")
            return messages["messages"]
        else:
            raise Exception("获取消息时出错")

async def mark_message_read(client: OpenRedClient, message_id: str):
    """标记消息为已读。"""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.put(
        f"{client.base_url}/api/v1/messages/{message_id}/read",
        headers=headers
    ) as response:
        if response.status == 200:
            print(f"消息 {message_id} 已标记为已读")
        else:
            raise Exception("标记消息为已读时出错")

# 消息处理循环
async def message_processing_loop(client: OpenRedClient, node_id: str):
    """持续处理传入消息。"""
    
    while True:
        try:
            messages = await get_pending_messages(client, node_id)
            
            for message in messages:
                print(f"处理消息: {message['id']}")
                
                # 根据类型处理消息
                if message["message_type"] == "data_sync":
                    await handle_data_sync(message)
                elif message["message_type"] == "command":
                    await handle_command(message)
                
                # 标记为已读
                await mark_message_read(client, message["id"])
            
            await asyncio.sleep(5)  # 等待 5 秒
            
        except Exception as e:
            print(f"消息处理错误: {e}")
            await asyncio.sleep(10)
```

## 📊 监控和指标

### 1. 指标收集

```python
async def get_system_metrics(client: OpenRedClient):
    """从 API 获取系统指标。"""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/metrics",
        headers=headers
    ) as response:
        if response.status == 200:
            metrics = await response.text()
            return metrics
        else:
            raise Exception("获取指标时出错")

async def check_health(client: OpenRedClient):
    """检查 API 健康状态。"""
    
    async with client.session.get(
        f"{client.base_url}/api/v1/health"
    ) as response:
        if response.status == 200:
            health = await response.json()
            return health
        else:
            raise Exception("服务不可用")

# 监控示例
async def monitoring_dashboard():
    """简单监控仪表板。"""
    
    async with OpenRedClient() as client:
        await authenticate_node(client, "node-001")
        
        # 检查健康状态
        health = await check_health(client)
        print(f"API 状态: {health['status']}")
        print(f"运行时间: {health['uptime']}")
        
        # 获取指标
        metrics = await get_system_metrics(client)
        print("系统指标已获取")
        
        # 发现节点
        nodes = await discover_nodes(client)
        active_nodes = [n for n in nodes if n['status'] == 'active']
        print(f"活跃节点: {len(active_nodes)}")

await monitoring_dashboard()
```

## 🔄 高级令牌管理

### 1. 自动令牌轮换

```python
import time
import jwt

async def refresh_access_token(client: OpenRedClient):
    """自动刷新访问令牌。"""
    
    if not client.refresh_token:
        raise Exception("没有可用的刷新令牌")
    
    headers = {"Authorization": f"Bearer {client.refresh_token}"}
    
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/refresh",
        headers=headers
    ) as response:
        if response.status == 200:
            tokens = await response.json()
            client.access_token = tokens["access_token"]
            if "refresh_token" in tokens:
                client.refresh_token = tokens["refresh_token"]
            print("令牌刷新成功")
            return True
        else:
            print("令牌刷新失败")
            return False

def is_token_expired(token: str) -> bool:
    """检查 JWT 令牌是否过期。"""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")
        if exp:
            return time.time() > exp
        return False
    except:
        return True

async def ensure_valid_token(client: OpenRedClient):
    """确保有效令牌可用。"""
    
    if not client.access_token or is_token_expired(client.access_token):
        success = await refresh_access_token(client)
        if not success:
            raise Exception("无法续期令牌")
```

## 🛠️ 工具和助手

### 1. 带错误处理的完整客户端

```python
class OpenRedAPIError(Exception):
    """API 错误的自定义异常。"""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EnhancedOpenRedClient(OpenRedClient):
    """具有高级功能的 OpenRed 客户端。"""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 retry_attempts: int = 3, timeout: int = 30):
        super().__init__(base_url)
        self.retry_attempts = retry_attempts
        self.timeout = timeout
    
    async def _make_request(self, method: str, endpoint: str, 
                           data: dict = None, headers: dict = None):
        """进行带重试和错误处理的请求。"""
        
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        
        # 如果可用，添加令牌
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.request(
                    method, url, json=data, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status < 400:
                        if response.content_type == 'application/json':
                            return await response.json()
                        else:
                            return await response.text()
                    elif response.status == 401:
                        # 令牌过期，尝试刷新
                        if await refresh_access_token(self):
                            continue
                        else:
                            raise OpenRedAPIError("认证失败", 401)
                    else:
                        error_text = await response.text()
                        raise OpenRedAPIError(f"API 错误: {error_text}", response.status)
            
            except asyncio.TimeoutError:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError("请求超时")
                await asyncio.sleep(2 ** attempt)  # 指数退避
            
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError(f"网络错误: {str(e)}")
                await asyncio.sleep(2 ** attempt)
    
    async def register_and_authenticate(self, node_config: dict):
        """在一个操作中注册和认证节点。"""
        
        # 生成 RSA 密钥
        private_key_pem, public_key_pem = generate_rsa_keypair()
        self.private_key = serialization.load_pem_private_key(
            private_key_pem, password=None
        )
        
        # 将公钥添加到配置中
        node_config["public_key"] = public_key_pem.decode('utf-8')
        
        # 注册节点
        registration_result = await self._make_request(
            "POST", "/api/v1/auth/register", node_config
        )
        
        # 认证节点
        await authenticate_node(self, node_config["node_id"])
        
        return registration_result
```

### 2. 配置和日志

```python
import logging
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class NodeConfig:
    """OpenRed 节点配置。"""
    node_id: str
    name: str
    type: str
    capabilities: List[str]
    endpoint: str
    api_url: str = "http://localhost:8000"
    log_level: str = "INFO"
    heartbeat_interval: int = 30
    message_poll_interval: int = 5
    metadata: Optional[dict] = None

def setup_logging(level: str = "INFO"):
    """为 OpenRed 应用程序配置日志。"""
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('openred_client.log')
        ]
    )
    
    return logging.getLogger('openred_client')

# 完整示例应用程序
async def main():
    """使用 OpenRed API 的示例应用程序。"""
    
    logger = setup_logging("INFO")
    
    config = NodeConfig(
        node_id="example-node-001",
        name="示例节点",
        type="compute",
        capabilities=["processing", "storage"],
        endpoint="https://example-node.openred.io:8443",
        api_url="http://localhost:8000"
    )
    
    async with EnhancedOpenRedClient(config.api_url) as client:
        try:
            # 注册和认证
            logger.info("注册节点...")
            await client.register_and_authenticate(config.__dict__)
            
            # 启动后台任务
            heartbeat_task = asyncio.create_task(
                heartbeat_loop(client, config.node_id, config.heartbeat_interval)
            )
            message_task = asyncio.create_task(
                message_processing_loop(client, config.node_id)
            )
            
            logger.info("节点运行中")
            
            # 保持任务运行
            await asyncio.gather(heartbeat_task, message_task)
            
        except Exception as e:
            logger.error(f"应用程序错误: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 总结

这些示例涵盖了使用 OpenRed 中央 API v2.0 的所有基本方面：

1. **使用 RSA 和 JWT 的安全认证**
2. **完整的节点管理**（注册、发现、更新）
3. **可靠和安全的节点间消息传递**
4. **实时监控和指标**
5. **具有自动轮换的高级令牌管理**
6. **具有错误处理和重试逻辑的强大客户端**

为了成功集成，请确保：
- 实现适当的私钥管理
- 处理网络错误和超时
- 维护详细的调试日志
- 测试所有错误场景
- 监控性能指标

OpenRed API v2.0 为构建安全高效的分布式应用程序提供了坚实的基础。
