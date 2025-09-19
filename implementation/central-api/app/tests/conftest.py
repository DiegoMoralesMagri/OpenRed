# FR: Fichier: conftest.py — Fixtures pytest partagées pour les tests
# EN: File: conftest.py — Shared pytest fixtures for tests
# ES: Archivo: conftest.py — Fixtures pytest compartidas para las pruebas
# ZH: 文件: conftest.py — 测试的共享 pytest 夹具

# Configuration des tests pour pytest
import pytest
import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration pour les tests asynchrones
@pytest.fixture(scope="session")
def event_loop():
    """Créer une boucle d'événements pour les tests asynchrones."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Configuration des variables d'environnement pour les tests
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Configuration de l'environnement de test."""
    os.environ.update({
        "TESTING": "true",
        "DATABASE_URL": "sqlite+aiosqlite:///./test.db",
        "SECRET_KEY": "test_secret_key_for_testing_only",
        "REDIS_URL": "redis://localhost:6379/1",  # Base de données Redis séparée pour les tests
        "LOG_LEVEL": "DEBUG",
        "RATE_LIMIT_ENABLED": "false",  # Désactiver le rate limiting pour les tests
    })
    
    yield
    
    # Nettoyage après les tests
    test_db = Path("./test.db")
    if test_db.exists():
        test_db.unlink()

# Marks personnalisés pour organiser les tests
def pytest_configure(config):
    """Configuration personnalisée de pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

# Configuration des options de ligne de commande
def pytest_addoption(parser):
    """Ajouter des options personnalisées à pytest."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--run-integration", action="store_true", default=False, help="run integration tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modifier la collection de tests basée sur les options."""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)