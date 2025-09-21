# === OpenRed Central API v2.0 Docker Container ===
# Multi-stage Docker build for production deployment
# Construcción Docker multi-etapa para despliegue en producción
# 用于生产部署的多阶段 Docker 构建

# Build stage | Etapa de construcción | 构建阶段
FROM python:3.11-slim as builder

# Set build arguments | Establecer argumentos de construcción | 设置构建参数
ARG BUILD_ENV=production
ENV BUILD_ENV=${BUILD_ENV}

# Install system dependencies | Instalar dependencias del sistema | 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory | Establecer directorio de trabajo | 设置工作目录
WORKDIR /app

# Copy requirements | Copiar requisitos | 复制需求
COPY requirements.txt .

# Install Python dependencies | Instalar dependencias de Python | 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage | Etapa de producción | 生产阶段
FROM python:3.11-slim as production

# Install runtime dependencies | Instalar dependencias de tiempo de ejecución | 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user | Crear usuario no root | 创建非 root 用户
RUN groupadd -r openred && useradd -r -g openred openred

# Set work directory | Establecer directorio de trabajo | 设置工作目录
WORKDIR /app

# Copy installed packages from builder | Copiar paquetes instalados del constructor | 从构建器复制已安装的包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code | Copiar código de aplicación | 复制应用程序代码
COPY . .

# Create necessary directories | Crear directorios necesarios | 创建必要的目录
RUN mkdir -p logs backups && \
    chown -R openred:openred /app

# Set environment variables | Establecer variables de entorno | 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Health check | Verificación de salud | 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user | Cambiar a usuario no root | 切换到非 root 用户
USER openred

# Expose port | Exponer puerto | 暴露端口
EXPOSE 8000 9090

# Default command | Comando por defecto | 默认命令
CMD ["python", "main_new.py"]

# Development stage | Etapa de desarrollo | 开发阶段
FROM production as development

# Switch back to root for development tools | Cambiar a root para herramientas de desarrollo | 切换回 root 用于开发工具
USER root

# Install development dependencies | Instalar dependencias de desarrollo | 安装开发依赖
RUN pip install --no-cache-dir \
    pytest-cov \
    pytest-xdist \
    pre-commit \
    watchdog

# Copy development configuration | Copiar configuración de desarrollo | 复制开发配置
COPY .env.example .env

# Switch back to application user | Cambiar de vuelta al usuario de aplicación | 切换回应用程序用户
USER openred

# Development command with hot reload | Comando de desarrollo con recarga automática | 带热重载的开发命令
CMD ["python", "-m", "uvicorn", "main_new:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
