🌐 **Navigation Multilingue** | **Multilingual Navigation**
- [🇫🇷 Français](#français) | [🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇨🇳 中文](#中文)

---

## Français

# OpenRed Central API v3.0

## 🚀 API Centrale Ultra-Minimaliste

Cette API sert uniquement d'**annuaire de découverte** pour l'écosystème OpenRed décentralisé.

### 📋 Fonctionnalités

- **Annuaire des nœuds** : ID ↔ URL mapping
- **Génération de tokens** : Tokens asymétriques pour établissement P2P
- **Distribution automatique** : Envoi des tokens aux nœuds
- **Aucun stockage permanent** : Pas de données utilisateur

### 🔄 Endpoints

```
POST /api/v3/nodes/register     - Enregistrement d'un nœud
POST /api/v3/tokens/request     - Demande de connexion P2P
GET  /api/v3/nodes/discover     - Découverte des nœuds
GET  /api/v3/health             - Statut de l'API
```

### 🏗️ Structure

```
central-api/
├── main.py                 # API principale (à créer)
├── crypto/                 # Moteur cryptographique (à créer)
├── models/                 # Modèles de données (à créer)
├── .env                    # Configuration
├── requirements.txt        # Dépendances
└── README.md              # Documentation
```

---

## English

# OpenRed Central API v3.0

## 🚀 Ultra-Minimalist Central API

This API serves only as a **discovery directory** for the decentralized OpenRed ecosystem.

### 📋 Features

- **Node directory**: ID ↔ URL mapping
- **Token generation**: Asymmetric tokens for P2P establishment
- **Automatic distribution**: Token sending to nodes
- **No permanent storage**: No user data

### 🔄 Endpoints

```
POST /api/v3/nodes/register     - Node registration
POST /api/v3/tokens/request     - P2P connection request
GET  /api/v3/nodes/discover     - Node discovery
GET  /api/v3/health             - API status
```

### 🏗️ Structure

```
central-api/
├── main.py                 # Main API (to create)
├── crypto/                 # Cryptographic engine (to create)
├── models/                 # Data models (to create)
├── .env                    # Configuration
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

---

## Español

# OpenRed Central API v3.0

## 🚀 API Central Ultra-Minimalista

Esta API sirve únicamente como **directorio de descubrimiento** para el ecosistema OpenRed descentralizado.

### 📋 Funcionalidades

- **Directorio de nodos**: Mapeo ID ↔ URL
- **Generación de tokens**: Tokens asimétricos para establecimiento P2P
- **Distribución automática**: Envío de tokens a nodos
- **Sin almacenamiento permanente**: Sin datos de usuario

### 🔄 Endpoints

```
POST /api/v3/nodes/register     - Registro de nodo
POST /api/v3/tokens/request     - Solicitud de conexión P2P
GET  /api/v3/nodes/discover     - Descubrimiento de nodos
GET  /api/v3/health             - Estado de la API
```

### 🏗️ Estructura

```
central-api/
├── main.py                 # API principal (por crear)
├── crypto/                 # Motor criptográfico (por crear)
├── models/                 # Modelos de datos (por crear)
├── .env                    # Configuración
├── requirements.txt        # Dependencias
└── README.md              # Documentación
```

---

## 中文

# OpenRed Central API v3.0

## 🚀 超极简主义中央API

此API仅作为去中心化OpenRed生态系统的**发现目录**。

### 📋 功能

- **节点目录**：ID ↔ URL映射
- **令牌生成**：P2P建立的非对称令牌
- **自动分发**：向节点发送令牌
- **无永久存储**：无用户数据

### 🔄 端点

```
POST /api/v3/nodes/register     - 节点注册
POST /api/v3/tokens/request     - P2P连接请求
GET  /api/v3/nodes/discover     - 节点发现
GET  /api/v3/health             - API状态
```

### 🏗️ 结构

```
central-api/
├── main.py                 # 主API（待创建）
├── crypto/                 # 加密引擎（待创建）
├── models/                 # 数据模型（待创建）
├── .env                    # 配置
├── requirements.txt        # 依赖
└── README.md              # 文档
```

---

🌐 **Navigation** | **导航**
- [🇫🇷 Français](#français) | [🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇨🇳 中文](#中文)
├── main.py             # Point d'entrée
└── README.md           # Documentation
```

## Installation

```bash
cd central-api
pip install -r requirements.txt
python main.py
```

## Endpoints

- `POST /api/v1/nodes/register` - Enregistrement d'un node
- `GET /api/v1/nodes/discover` - Découverte de nodes
- `POST /api/v1/messages/route` - Routage de messages
- `GET /api/v1/nodes/{id}/status` - Statut d'un node