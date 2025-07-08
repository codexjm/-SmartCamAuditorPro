"""
SmartCam Auditor - Módulo Web Panel
Panel de control web para auditorías de seguridad
"""

from flask import Flask

__version__ = "2.0.0"
__author__ = "SmartCam Security Team"

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    app.secret_key = "una_clave_segura_123"  # Necesario para sesiones
    
    # Configuración adicional de la aplicación
    app.config['JSON_AS_ASCII'] = False
    
    # Registrar blueprint
    from .routes import web_bp
    app.register_blueprint(web_bp)
    
    return app
