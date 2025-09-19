# 🤝 Guía de Contribución - O-Red

¡Gracias por tu interés en contribuir a O-Red! Este proyecto prospera gracias a su comunidad de colaboradores apasionados que comparten nuestra visión de una web descentralizada y ética.

## 🌟 Cómo Contribuir

Hay muchas formas de contribuir a O-Red, independientemente de tu nivel de experiencia:

### 🔧 Desarrollo
- Corregir errores
- Añadir nuevas funcionalidades
- Mejorar el rendimiento
- Refactorizar el código existente
- Crear pruebas

### 📚 Documentación
- Mejorar la documentación existente
- Escribir tutoriales
- Traducir a otros idiomas
- Corregir errores tipográficos
- Añadir ejemplos de código

### 🎨 Diseño y UX
- Mejorar la interfaz de usuario
- Crear maquetas
- Optimizar la experiencia de usuario
- Diseñar iconos y elementos visuales

### 🔒 Seguridad
- Identificar vulnerabilidades
- Realizar auditorías de seguridad
- Proponer mejoras de seguridad
- Probar la robustez del sistema

### 🌍 Comunidad
- Ayudar a nuevos usuarios
- Responder preguntas en los foros
- Organizar eventos
- Promocionar el proyecto

## 🚀 Inicio Rápido

### 1. Fork y Clonar

```bash
# Forkear el repositorio en GitHub y clonar tu fork
git clone https://github.com/TU_USERNAME/O-Red.git
cd O-Red

# Añadir el repositorio original como remote
git remote add upstream https://github.com/OriginalOwner/O-Red.git
```

### 2. Configurar el Entorno

```bash
# Seguir la guía de instalación
cd implementation
# Ver GUIDE_TEST_LOCAL.md para instrucciones detalladas
```

### 3. Crear una Rama

```bash
# Crear una rama para tu contribución
git checkout -b feature/mi-nueva-funcionalidad
# O
git checkout -b fix/correccion-de-bug
# O
git checkout -b docs/mejora-documentacion
```

## 📋 Tipos de Contribuciones

### 🐛 Informar de un Error

Antes de informar un error:
1. Comprueba si ya ha sido reportado en los [Issues](https://github.com/[USERNAME]/O-Red/issues)
2. Prueba con la versión más reciente del código
3. Prepara un ejemplo reproducible

**Plantilla para reportar un error:**

```markdown
## Descripción del Error
Una descripción clara y concisa del problema.

## Pasos para Reproducir
1. Ir a '...'
2. Hacer clic en '...'
3. Desplazarse hasta '...'
4. Ver el error

## Comportamiento Esperado
Una descripción clara de lo que debería ocurrir.

## Capturas de Pantalla
Si aplica, añade capturas de pantalla.

## Entorno
- SO: [p. ej. Ubuntu 20.04]
- Navegador: [p. ej. Chrome 94]
- Versión de Python: [p. ej. 3.9.7]
- Versión de Node.js: [p. ej. 16.14.0]

## Información Adicional
Cualquier otra información sobre el problema.
```

### ✨ Proponer una Funcionalidad

**Plantilla para solicitud de funcionalidad:**

```markdown
## Resumen de la Funcionalidad
Una descripción clara y concisa de la funcionalidad solicitada.

## Motivación
¿Por qué es útil esta funcionalidad? ¿Qué problema resuelve?

## Descripción Detallada
Descripción detallada de la funcionalidad propuesta.

## Alternativas Consideradas
¿Qué alternativas has considerado?

## Implementación Sugerida
Si tienes ideas sobre la implementación, compártelas aquí.
```

## 🔄 Proceso de Contribución

### 1. Desarrollo

```bash
# Mantén tu rama actualizada
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/mi-nueva-funcionalidad
git rebase main

# Haz tus cambios
# ...

# Añadir y commitear
git add .
git commit -m "feat: añadir nueva funcionalidad X"
```

### 2. Pruebas

Asegúrate de que todas las pruebas pasen:

```bash
# Pruebas API
cd central-api
python -m pytest app/tests/ -v

# Pruebas Frontend
cd ../web-interface
npm test

# Pruebas P2P
cd ../node-client
python -m pytest tests/ -v
```

### 3. Formateo de Código

Usamos herramientas de formateo automático:

```bash
# Python (API y Node Client)
pip install black isort
black .
isort .

# JavaScript/TypeScript (Interfaz Web)
npm run lint
npm run format
```

### 4. Convención de Commits

Seguimos la convención [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Tipos:**
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `docs`: cambios de documentación
- `style`: cambios que no afectan el código (espacios, formato, etc.)
- `refactor`: cambio de código que no corrige un bug ni añade una funcionalidad
- `perf`: cambio que mejora el rendimiento
- `test`: añadir pruebas o corregir pruebas existentes
- `chore`: cambios en herramientas de build o bibliotecas auxiliares

**Ejemplos:**
```bash
git commit -m "feat(api): añadir endpoint de gestion de nudos"
git commit -m "fix(ui): corregir bug de visualización en móvil"
git commit -m "docs: actualizar la guía de instalación"
git commit -m "test(p2p): añadir pruebas para descubrimiento de pares"
```

### 5. Pull Request

```bash
# Push tu rama
git push origin feature/mi-nueva-funcionalidad

# Abrir un Pull Request en GitHub
```

**Plantilla de Pull Request:**

```markdown
## Descripción
Descripción clara de lo que hace esta PR.

## Tipo de Cambio
- [ ] Corrección de bug (cambio que soluciona un problema)
- [ ] Nueva funcionalidad (cambio que añade funcionalidad)
- [ ] Cambio que rompe compatibilidad (fix o feature que rompería la funcionalidad existente)
- [ ] Este cambio requiere actualización de la documentación

## Pruebas
- [ ] He probado mis cambios localmente
- [ ] He añadido pruebas que demuestran que mi corrección es efectiva o que mi funcionalidad funciona
- [ ] Las pruebas unitarias nuevas y existentes pasan localmente con mis cambios

## Checklist
- [ ] Mi código sigue las directrices de estilo del proyecto
- [ ] He realizado una auto-revisión de mi código
- [ ] He comentado mi código, especialmente en las áreas difíciles de entender
- [ ] He hecho los cambios correspondientes en la documentación
- [ ] Mis cambios no generan nuevas advertencias
```

## 📐 Estándares de Código

... (the rest matches the English version) ...
