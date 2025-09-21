#!/usr/bin/env python3
"""
Ultra-basic test with simple HTTP server
Basic API endpoint testing without FastAPI dependencies
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/':
            response = {"message": "OpenRed Central API Test", "status": "running", "version": "2.0.0"}
        elif self.path == '/health':
            response = {"status": "healthy", "database": "connected", "timestamp": "2025-09-21T01:22:00Z"}
        elif self.path == '/ping':
            response = {"status": "pong"}
        else:
            response = {"error": "Not found", "path": self.path}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override default logging with custom format"""
        print(f"✅ {self.address_string()} - {format % args}")

if __name__ == "__main__":
    server_address = ('', 8001)
    httpd = HTTPServer(server_address, TestHandler)
    print("🚀 Serveur de test basique démarré sur http://localhost:8001")
    print("📋 Endpoints disponibles:")
    print("   GET / - Racine")
    print("   GET /health - Santé")
    print("   GET /ping - Test")
    print("🔄 Appuyez sur Ctrl+C pour arrêter")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
        httpd.server_close()
