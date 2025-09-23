# OpenRed Central-API v3.0 🚀

**Servidor de directorio P2P ultra-minimalista con máxima empatía**

## 🎯 Visión

OpenRed Central-API es un servidor de directorio HTTP ultra-empático para redes P2P descentralizadas. Diseñado con la filosofía **"Código casero"** para cero dependencias externas críticas.

## ✨ Características

- 🚀 **OpenRed Micro-Engine** - Servidor HTTP personalizado (50KB vs 15MB FastAPI)
- 💖 **Máxima empatía** - Tolerancia de 6 meses entre latidos
- 🔐 **Seguridad asimétrica** - Tokens criptográficos preparados para quantum
- 🌍 **100,000 nodos** - Arquitectura ultra-escalable
- ⚡ **Cero framework** - Solo cryptography como dependencia
- 🛡️ **Estados empáticos** - Gestión avanzada del ciclo de vida de nodos

## 🏗️ Arquitectura

```
OpenRed Central-API (Directorio HTTP)
├── Registro de nodos P2P
├── Descubrimiento de pares 
├── Latido ultra-empático
├── Generación de tokens seguros
└── Estadísticas en tiempo real
```

**Separación clara:**
- **Central-API** = Directorio HTTP (este proyecto)
- **Node-API** = Comunicación P2P directa (proyecto separado)

## 🚀 Instalación

### Prerrequisitos
- Python 3.8+
- Git

### Instalación rápida

```bash
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install cryptography
python src/main.py
```

## 📡 Endpoints de API

### 🏠 Información
```http
GET /
```
Información básica del servidor

### 📝 Registro
```http
POST /register
Content-Type: application/json

{
  "node_id": "identificador_unico_nodo",
  "address": "192.168.1.100",
  "port": 8080,
  "public_key": "clave_publica_codificada_base64",
  "services": ["compartir_archivos", "mensajeria"]
}
```

### 🔍 Descubrimiento
```http
GET /discover?services=compartir_archivos&max_results=10
```

### 💓 Latido
```http
POST /heartbeat/{node_id}
```

### 📊 Estadísticas
```http
GET /stats
```

### 🔐 Tokens
```http
POST /security/token
Content-Type: application/json

{
  "node_id": "nodo_id_solicitante"
}
```

## 💖 Empatía y Estados de Nodos

| Estado | Descripción | Duración |
|--------|-------------|----------|
| `ACTIVE` | Nodo activo | Permanente |
| `PENDING_1ST` | Primera verificación pendiente | 48h |
| `RETRY_48H` | Reintentar después de 48h | 48h |
| `RETRY_2W` | Reintentar después de 2 semanas | 2 semanas |
| `RETRY_2M` | Reintentar después de 2 meses | 2 meses |
| `COMA` | Nodo en coma | Hasta 2 años |
| `DEAD` | Nodo declarado muerto | Permanente |

## ⚙️ Configuración

Archivo: `src/core/config.py`

```python
# Capacidad máxima
max_nodes: int = 100000

# Empatía temporal  
heartbeat_check_interval: int = 15552000  # 6 meses
initial_registration_lifetime: int = 31536000  # 1 año
max_coma_duration: int = 63072000  # 2 años

# Seguridad
min_key_size: int = 2048
token_lifetime_seconds: int = 300
```

## 🌟 Filosofía "Código Casero"

- **Micro-Engine personalizado** en lugar de FastAPI (50KB vs 15MB)
- **Cero framework web** - Análisis HTTP manual optimizado
- **Criptografía pura** - Sin JWT/OAuth complejos
- **Empatía técnica** - Máxima tolerancia a fallas de red
- **Arquitectura separada** - Central-API vs Node-API

## 📜 Licencia

Licencia MIT - Ver [LICENSE](LICENSE)

## 🤝 Contribución

1. Hacer fork del proyecto
2. Crear una rama de características (`git checkout -b feature/caracteristica-increible`)
3. Hacer commit de los cambios (`git commit -m 'Agregar característica increíble'`)
4. Hacer push a la rama (`git push origin feature/caracteristica-increible`)
5. Abrir un Pull Request

---

**OpenRed Central-API v3.0** - *Máxima empatía para redes P2P descentralizadas*