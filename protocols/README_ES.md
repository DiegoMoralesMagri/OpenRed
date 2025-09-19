# Protocolos de Comunicación OpenRed

Esta carpeta contiene las especificaciones e implementaciones de los protocolos de comunicación entre los nodos OpenRed.

## Estructura

```
protocols/
├── specifications/      # Especificaciones de protocolos
│   ├── orf-protocol.md  # Protocolo de Federación OpenRed
│   ├── security.md      # Especificaciones de seguridad
│   └── message-types.md # Tipos de mensajes soportados
├── implementations/     # Implementaciones de los protocolos
│   ├── python/          # Implementación en Python
│   ├── javascript/      # Implementación en JavaScript/Node.js
│   └── rust/            # Implementación en Rust (rendimiento)
├── examples/            # Ejemplos de uso
└── tests/               # Pruebas de conformidad
```

## Protocolos Principales

### 1. Protocolo de Federación OpenRed (ORF)
Protocolo principal para la comunicación entre nodos, basado en JSON sobre HTTP/HTTPS.

### 2. Seguridad y Criptografía
- Autenticación mediante firmas criptográficas
- Cifrado de extremo a extremo para mensajes privados
- Validación de integridad de mensajes

### 3. Tipos de Mensajes
- Mensajes de servicio (heartbeat, descubrimiento)
- Mensajes sociales (posts, comentarios, reacciones)
- Mensajes privados cifrados
- Notificaciones y actualizaciones
