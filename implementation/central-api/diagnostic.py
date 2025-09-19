#!/usr/bin/env python3
# FR: Script de diagnostic pour O2Switch
# EN: Diagnostic script for O2Switch
# ES: Script de diagnóstico para O2Switch
# ZH: O2Switch诊断脚本

import sys
import os
import json
from datetime import datetime

def diagnostic():
    """Diagnostic complet de l'environnement"""
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": sys.version,
        "python_path": sys.path,
        "working_directory": os.getcwd(),
        "environment_vars": dict(os.environ),
        "modules_available": [],
        "errors": []
    }
    
    # Test des modules requis
    required_modules = ['fastapi', 'uvicorn', 'pydantic', 'starlette']
    
    for module in required_modules:
        try:
            __import__(module)
            result["modules_available"].append(f"{module}: OK")
        except ImportError as e:
            result["errors"].append(f"{module}: MISSING - {str(e)}")
    
    # Test d'écriture
    try:
        with open('/tmp/test_write.txt', 'w') as f:
            f.write('test')
        os.remove('/tmp/test_write.txt')
        result["file_system"] = "WRITABLE"
    except Exception as e:
        result["errors"].append(f"File system: {str(e)}")
    
    return result

if __name__ == "__main__":
    # Pour utilisation web
    print("Content-Type: application/json\n")
    print(json.dumps(diagnostic(), indent=2))