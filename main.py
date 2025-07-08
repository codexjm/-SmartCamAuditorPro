#!/usr/bin/env python3
"""
SmartCam Auditor - Panel Web
Punto de entrada principal para la interfaz web
"""

from web_panel import create_app

if __name__ == "__main__":
    print("=" * 60)
    print("🔒 SmartCam Auditor - Panel Web v2.0")
    print("=" * 60)
    print("🌐 Servidor iniciado en: http://localhost:5000")
    print("📱 Acceso remoto en: http://0.0.0.0:5000")
    print("⚠️  Para uso en redes autorizadas únicamente")
    print("🛡️  Modo empresarial activado")
    print("=" * 60)
    
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
