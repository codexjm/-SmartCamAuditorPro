#!/usr/bin/env python3
"""
SmartCam Auditor v2.0 Pro - Servidor Web Cyberpunk
Ejecuta el panel de control web con tema neón
"""

import os
import sys

# Añadir el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from web_panel import create_app

def print_banner():
    """Imprime el banner de inicio con estilo cyberpunk"""
    banner = """
    ╔══════════════════════════════════════════════╗
    ║      � SmartCam Auditor v2.0 Pro            ║
    ║           💀 CYBERPUNK EDITION 💀            ║
    ╚══════════════════════════════════════════════╝
    
    🌐 Panel Web: http://localhost:5000
    🔐 Usuario: admin | Contraseña: smartcam2024
    🎯 Tema: Neón Cyberpunk activado
    ⚡ Estado: Servidor iniciando...
    
    ⚠️  SOLO PARA REDES PROPIAS Y AUTORIZADAS ⚠️
    """
    print(banner)

def main():
    """Función principal del servidor web"""
    print_banner()
    
    app = create_app()
    
    try:
        print("🚀 Servidor iniciado exitosamente!")
        print("💻 Accede al panel web para comenzar auditorías")
        print("🔍 Presiona Ctrl+C para detener el servidor\n")
        
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False  # Evitar doble ejecución en modo debug
        )
    except KeyboardInterrupt:
        print("\n⏹️  Servidor detenido por el usuario")
        print("👋 ¡Hasta la vista, hacker!")
    except Exception as e:
        print(f"❌ Error crítico al iniciar el servidor: {e}")
        print("🔧 Verifica que el puerto 5000 esté disponible")

# Alternativa simple para ejecutar directamente
from web_panel import create_app

if __name__ == "__main__":
    main()
