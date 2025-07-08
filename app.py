#!/usr/bin/env python3
"""
SmartCam Auditor v2.0 Pro - Ejecutor Simple
Versión minimalista para desarrollo rápido
"""

from web_panel import create_app

if __name__ == "__main__":
    print("🔒 SmartCam Auditor v2.0 Pro - Modo Desarrollo")
    print("🌐 Servidor: http://localhost:5000")
    print("🔐 Login: admin / smartcam2024")
    
    app = create_app()
    app.run(debug=True)
