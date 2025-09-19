#!/usr/bin/env python3
# FR: Point d'entrée pour cPanel O2Switch
# EN: Entry point for cPanel O2Switch
# ES: Punto de entrada para cPanel O2Switch
# ZH: cPanel O2Switch入口点

import sys
import os

# Ajouter le répertoire de l'application au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

try:
    from main_simple import app
    application = app  # cPanel cherche 'application'
except ImportError as e:
    # Fallback en cas d'erreur
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [f'Import Error: {str(e)}'.encode('utf-8')]