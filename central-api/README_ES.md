# API Central OpenRed

API central para el registro y descubrimiento de nodos del ecosistema OpenRed.

## Estructura

```
central-api/
├── src/
│   ├── models/          # Modelos de datos
│   ├── routes/          # Endpoints API
│   ├── services/        # Lógica de negocio
│   ├── utils/           # Utilidades
│   └── config/          # Configuración
├── tests/               # Tests unitarios
├── requirements.txt     # Dependencias Python
├── main.py              # Punto de entrada
└── README.md            # Documentación
```

## Instalación

```bash
cd central-api
pip install -r requirements.txt
python main.py
```

## Endpoints

- `POST /api/v1/nodes/register` - Registrar un nodo
- `GET /api/v1/nodes/discover` - Descubrir nodos
- `POST /api/v1/messages/route` - Enrutar mensajes
- `GET /api/v1/nodes/{id}/status` - Estado de un nodo
