# Cliente Nodo OpenRed

Cliente auto-desplegable para usuarios de OpenRed. Esta aplicación se instala automáticamente en el servidor del usuario junto con su base de datos local.

## Estructura

```
node-client/
├── backend/             # API backend local
│   ├── src/
│   │   ├── models/      # Modelos de datos
│   │   ├── routes/      # Endpoints de la API
│   │   ├── services/    # Lógica de negocio
│   │   └── utils/       # Utilidades
│   ├── requirements.txt
│   └── main.py
├── frontend/            # Interfaz de usuario React
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas de la aplicación
│   │   ├── services/    # Servicios API
│   │   └── utils/       # Utilidades
│   ├── package.json
│   └── public/
├── installer/           # Scripts de instalación automática
│   ├── install.sh       # Script de instalación Linux/macOS
│   ├── install.bat      # Script de instalación Windows
│   └── docker/          # Configuración Docker
├── config/              # Configuración
│   ├── database.sql     # Esquema de la base de datos
│   └── nginx.conf       # Configuración del proxy web
└── README.md
```

## Instalación

```bash
# Instalación automática
curl -sSL https://openred.org/install.sh | bash

# O manual
./installer/install.sh
```

## Funcionalidades

- Interfaz de usuario completa (perfil, publicaciones, amigos)
- API backend local para gestión de datos
- Comunicación con la API central de OpenRed
- Comunicación directa entre nodos
- Instalación y configuración automáticas
