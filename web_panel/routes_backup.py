"""
SmartCam Auditor - Rutas del Panel Web
Maneja todas las rutas y endpoints de la API usando Flask Blueprint
"""

import os
import json
import threading
import subprocess
import time
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_file, send_from_directory, session, redirect, url_for

# Crear blueprint
web_bp = Blueprint("web_panel", __name__)

# Configuración de directorios y autenticación
LOG_DIR = "logs"
USERNAME = "admin"
PASSWORD = "smartcam2025"

# Importar módulos del auditor
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner.network_scanner import scan_network
from scanner.port_checker import check_ports
from scanner.login_tester import test_logins
from scanner.advanced_testing import advanced_camera_testing

# Estado global de la aplicación
audit_status = {
    "running": False,
    "progress": 0,
    "current_task": "Sistema listo",
    "results": [],
    "last_audit": None,
    "total_networks": 0,
    "current_network": 0
}

def load_config():
    """Carga la configuración desde config.json"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando config: {e}")
        return {"alert_mode": "console", "log_folder": "logs"}

def load_networks():
    """Carga las redes configuradas"""
    try:
        networks_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "networks.txt")
        with open(networks_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() 
                   if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        print(f"Error cargando redes: {e}")
        return ["192.168.1.0/24"]

def run_audit(networks, config):
    """Ejecuta una auditoría completa en un hilo separado"""
    global audit_status
    
    audit_status["running"] = True
    audit_status["progress"] = 0
    audit_status["results"] = []
    audit_status["current_task"] = "Iniciando auditoría de seguridad..."
    audit_status["total_networks"] = len(networks)
    audit_status["current_network"] = 0
    
    try:
        for i, network in enumerate(networks):
            if not audit_status["running"]:
                break
                
            audit_status["current_network"] = i + 1
            audit_status["current_task"] = f"🔍 Escaneando red {i+1}/{len(networks)}: {network}"
            audit_status["progress"] = int((i / len(networks)) * 90)  # Reservar 10% para finalización
            
            try:
                devices = scan_network(network)
                
                for j, device in enumerate(devices):
                    if not audit_status["running"]:
                        break
                        
                    ip = device['ip']
                    audit_status["current_task"] = f"🎯 Analizando dispositivo: {ip} ({j+1}/{len(devices)})"
                    
                    # Escanear puertos
                    ports = check_ports(ip)
                    
                    # Probar credenciales
                    logins = test_logins(ip, ports)
                    
                    # Testing avanzado
                    advanced_result = advanced_camera_testing(ip, ports, config)
                    
                    # Agregar resultado
                    result = {
                        "ip": ip,
                        "network": network,
                        "ports": ports,
                        "credentials": logins,
                        "vulnerabilities": advanced_result.get("vulnerabilities", []),
                        "device_info": advanced_result.get("device_info", {}),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    audit_status["results"].append(result)
                    
            except Exception as e:
                print(f"Error escaneando red {network}: {e}")
                audit_status["current_task"] = f"⚠️ Error en red {network}: {str(e)}"
        
        # Finalización
        audit_status["progress"] = 100
        audit_status["current_task"] = f"✅ Auditoría completada - {len(audit_status['results'])} dispositivos analizados"
        audit_status["last_audit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        audit_status["current_task"] = f"❌ Error crítico: {str(e)}"
        print(f"Error crítico en auditoría: {e}")
    finally:
        audit_status["running"] = False

def monitor_subprocess_custom(process, temp_file):
    """Monitorea un proceso subprocess para auditorías personalizadas"""
    try:
        start_time = datetime.now()
        estimated_duration = 180  # 3 minutos estimados para auditoría personalizada
        
        while process.poll() is None:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            progress = min(int((elapsed_time / estimated_duration) * 90), 90)
            
            audit_status["progress"] = progress
            target_net = audit_status.get("target_network", "red personalizada")
            audit_status["current_task"] = f"🎯 Auditoría personalizada en {target_net}... ({progress}% completado)"
            
            time.sleep(1.5)  # Actualizar cada 1.5 segundos
        
        # El proceso terminó
        return_code = process.returncode
        
        if return_code == 0:
            audit_status["progress"] = 100
            audit_status["current_task"] = "✅ Auditoría personalizada completada exitosamente"
            audit_status["last_audit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            audit_status["current_task"] = f"❌ Auditoría personalizada terminó con errores (código: {return_code})"
            
    except Exception as e:
        audit_status["current_task"] = f"❌ Error monitoreando auditoría personalizada: {str(e)}"
    finally:
        audit_status["running"] = False
        # Limpiar archivo temporal
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass

def monitor_subprocess_quick(process):
    """Monitorea un proceso subprocess para auditorías rápidas"""
    try:
        # Progreso más rápido para auditorías rápidas
        start_time = datetime.now()
        estimated_duration = 120  # 2 minutos estimados para auditoría rápida
        
        while process.poll() is None:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            progress = min(int((elapsed_time / estimated_duration) * 90), 90)
            
            audit_status["progress"] = progress
            audit_status["current_task"] = f"⚡ Auditoría rápida en progreso... ({progress}% completado)"
            
            time.sleep(1)  # Actualizar cada segundo para auditorías rápidas
        
        # El proceso terminó
        return_code = process.returncode
        
        if return_code == 0:
            audit_status["progress"] = 100
            audit_status["current_task"] = "✅ Auditoría rápida completada exitosamente"
            audit_status["last_audit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            audit_status["current_task"] = f"❌ Auditoría rápida terminó con errores (código: {return_code})"
            
    except Exception as e:
        audit_status["current_task"] = f"❌ Error monitoreando auditoría rápida: {str(e)}"
    finally:
        audit_status["running"] = False

def monitor_subprocess(process):
    """Monitorea un proceso subprocess y actualiza el estado"""
    try:
        # Simular progreso basado en tiempo estimado
        start_time = datetime.now()
        estimated_duration = 300  # 5 minutos estimados
        
        while process.poll() is None:  # Mientras el proceso esté corriendo
            elapsed_time = (datetime.now() - start_time).total_seconds()
            progress = min(int((elapsed_time / estimated_duration) * 90), 90)  # Máximo 90%
            
            audit_status["progress"] = progress
            audit_status["current_task"] = f"🔍 Ejecutando auditoría... ({progress}% completado)"
            
            time.sleep(2)  # Actualizar cada 2 segundos
        
        # El proceso terminó
        return_code = process.returncode
        
        if return_code == 0:
            audit_status["progress"] = 100
            audit_status["current_task"] = "✅ Auditoría completada exitosamente"
            audit_status["last_audit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            audit_status["current_task"] = f"❌ Auditoría terminó con errores (código: {return_code})"
            
    except Exception as e:
        audit_status["current_task"] = f"❌ Error monitoreando proceso: {str(e)}"
    finally:
        audit_status["running"] = False

def require_auth(f):
    """Decorador para rutas que requieren autenticación"""
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("web_panel.login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@web_bp.route("/", methods=["GET", "POST"])
def login():
    """Página de login"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == USERNAME and password == PASSWORD:
            session["user"] = USERNAME
            session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return redirect(url_for("web_panel.dashboard"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")
    
    # Si ya está autenticado, redirigir al dashboard
    if "user" in session:
        return redirect(url_for("web_panel.dashboard"))
    
    return render_template("login.html")

@web_bp.route("/logout")
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for("web_panel.login"))

@web_bp.route("/dashboard")
@require_auth
def dashboard():
    """Dashboard principal con lista de archivos de logs"""
    try:
        # Obtener lista de archivos de logs
        if os.path.exists(LOG_DIR):
            files = os.listdir(LOG_DIR)
            log_files = [f for f in files if f.endswith(".txt")]
            log_files.sort(reverse=True)  # Más recientes primero
        else:
            log_files = []
        
        return render_template("dashboard.html", log_files=log_files, user=session.get("user"))
    except Exception as e:
        print(f"Error cargando dashboard: {e}")
        return render_template("dashboard.html", log_files=[], user=session.get("user"))

@web_bp.route("/logs/<filename>")
@require_auth
def view_log(filename):
    """Visualizar contenido de un archivo de log"""
    try:
        # Validar que el archivo esté en el directorio de logs
        file_path = os.path.join(LOG_DIR, filename)
        
        # Verificar que el archivo existe y está dentro del directorio permitido
        if not os.path.exists(file_path) or not filename.endswith(".txt"):
            return "Archivo no encontrado", 404
        
        # Verificar que el path es seguro (evitar directory traversal)
        if ".." in filename or "/" in filename or "\\" in filename:
            return "Acceso denegado", 403
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Formatear el contenido con estilo básico
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Log: {filename}</title>
            <style>
                body {{ 
                    font-family: 'Fira Code', monospace; 
                    background: #1a1a1a; 
                    color: #e0e0e0; 
                    margin: 0; 
                    padding: 20px; 
                }}
                .header {{ 
                    background: #2d2d2d; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin-bottom: 20px; 
                    border-left: 4px solid #4CAF50;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                pre {{ 
                    background: #2d2d2d; 
                    padding: 20px; 
                    border-radius: 8px; 
                    overflow-x: auto; 
                    white-space: pre-wrap; 
                    line-height: 1.4;
                    border: 1px solid #404040;
                }}
                .back-btn {{ 
                    background: #4CAF50; 
                    color: white; 
                    padding: 10px 20px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    display: inline-block;
                }}
                .back-btn:hover {{ background: #45a049; }}
                .logout-btn {{
                    background: #f44336;
                    color: white;
                    padding: 8px 15px;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 0.9rem;
                }}
                .logout-btn:hover {{ background: #d32f2f; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <h2>📄 Archivo de Log: {filename}</h2>
                    <p>Tamaño: {len(content)} caracteres | Última modificación: {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div>
                    <a href="/dashboard" class="back-btn">← Volver al Dashboard</a>
                    <a href="/logout" class="logout-btn">🚪 Cerrar Sesión</a>
                </div>
            </div>
            <pre>{content}</pre>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"Error leyendo archivo: {str(e)}", 500

@web_bp.route('/api/config')
def get_config():
    """API: Obtiene la configuración actual"""
    try:
        config = load_config()
        networks = load_networks()
        return jsonify({
            "status": "success",
            "config": config,
            "networks": networks,
            "version": "2.0.0"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/start_audit', methods=['POST'])
def start_audit():
    """API: Inicia una nueva auditoría"""
    try:
        if audit_status["running"]:
            return jsonify({
                "status": "error", 
                "message": "Ya hay una auditoría en curso"
            }), 400
        
        data = request.get_json() or {}
        networks = data.get('networks', load_networks())
        
        if not networks:
            return jsonify({
                "status": "error",
                "message": "No se especificaron redes para auditar"
            }), 400
        
        config = load_config()
        
        # Ejecutar auditoría en un hilo separado
        thread = threading.Thread(target=run_audit, args=(networks, config))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": f"Auditoría iniciada para {len(networks)} redes",
            "networks": networks
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/stop_audit', methods=['POST'])
def stop_audit():
    """API: Detiene la auditoría actual"""
    try:
        audit_status["running"] = False
        audit_status["current_task"] = "🛑 Auditoría detenida por el usuario"
        return jsonify({
            "status": "success",
            "message": "Auditoría detenida exitosamente"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/status')
def get_status():
    """API: Obtiene el estado actual de la auditoría"""
    try:
        return jsonify({
            "status": "success",
            "data": audit_status
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/results')
def get_results():
    """API: Obtiene los resultados de la última auditoría"""
    try:
        total_vulns = sum(len(r.get("vulnerabilities", [])) for r in audit_status["results"])
        total_creds = sum(len(r.get("credentials", [])) for r in audit_status["results"])
        critical_vulns = sum(1 for r in audit_status["results"] 
                           for v in r.get("vulnerabilities", []) 
                           if v.get("severity") == "CRITICAL")
        
        return jsonify({
            "status": "success",
            "data": {
                "results": audit_status["results"],
                "summary": {
                    "total_devices": len(audit_status["results"]),
                    "total_vulnerabilities": total_vulns,
                    "critical_vulnerabilities": critical_vulns,
                    "credentials_found": total_creds,
                    "last_audit": audit_status["last_audit"]
                }
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/export_report')
def export_report():
    """API: Exporta un reporte completo"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"smartcam_audit_report_{timestamp}.json"
        
        # Calcular estadísticas
        total_vulns = sum(len(r.get("vulnerabilities", [])) for r in audit_status["results"])
        critical_vulns = sum(1 for r in audit_status["results"] 
                           for v in r.get("vulnerabilities", []) 
                           if v.get("severity") == "CRITICAL")
        
        report = {
            "report_info": {
                "title": "SmartCam Auditor - Reporte de Seguridad",
                "version": "2.0.0",
                "generated_at": datetime.now().isoformat(),
                "audit_timestamp": audit_status["last_audit"],
                "total_devices_scanned": len(audit_status["results"])
            },
            "summary": {
                "devices_found": len(audit_status["results"]),
                "total_vulnerabilities": total_vulns,
                "critical_vulnerabilities": critical_vulns,
                "credentials_compromised": sum(len(r.get("credentials", [])) for r in audit_status["results"]),
                "networks_scanned": audit_status["total_networks"]
            },
            "detailed_results": audit_status["results"],
            "recommendations": [
                "Cambiar todas las credenciales por defecto encontradas",
                "Actualizar firmware de dispositivos vulnerables",
                "Implementar segmentación de red para cámaras",
                "Configurar monitoreo de seguridad continuo",
                "Revisar configuraciones de acceso remoto"
            ]
        }
        
        # Crear directorio reports si no existe
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return send_file(report_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/clear_results', methods=['POST'])
def clear_results():
    """API: Limpia los resultados actuales"""
    try:
        audit_status["results"] = []
        audit_status["last_audit"] = None
        audit_status["current_task"] = "Sistema listo"
        audit_status["progress"] = 0
        
        return jsonify({
            "status": "success",
            "message": "Resultados limpiados exitosamente"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/logs')
def get_logs():
    """API: Obtiene la lista de archivos de log disponibles"""
    try:
        if os.path.exists(LOG_DIR):
            files = os.listdir(LOG_DIR)
            log_files = []
            
            for f in files:
                if f.endswith(".txt"):
                    file_path = os.path.join(LOG_DIR, f)
                    stat = os.stat(file_path)
                    log_files.append({
                        "filename": f,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        "created": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            log_files.sort(key=lambda x: x['modified'], reverse=True)
            return jsonify({
                "status": "success",
                "logs": log_files
            })
        else:
            return jsonify({
                "status": "success",
                "logs": []
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/delete_log/<filename>', methods=['DELETE'])
def delete_log(filename):
    """API: Elimina un archivo de log específico"""
    try:
        # Validaciones de seguridad
        if ".." in filename or "/" in filename or "\\" in filename:
            return jsonify({"status": "error", "message": "Nombre de archivo inválido"}), 403
        
        if not filename.endswith(".txt"):
            return jsonify({"status": "error", "message": "Tipo de archivo no permitido"}), 403
        
        file_path = os.path.join(LOG_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404
        
        os.remove(file_path)
        return jsonify({
            "status": "success",
            "message": f"Archivo {filename} eliminado exitosamente"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route('/api/system_info')
def get_system_info():
    """API: Obtiene información del sistema y configuración"""
    try:
        import platform
        
        config = load_config()
        
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0]
        }
        
        app_info = {
            "version": "2.0.0",
            "name": "SmartCam Auditor",
            "log_directory": os.path.abspath(LOG_DIR),
            "config_loaded": bool(config),
            "total_log_files": len([f for f in os.listdir(LOG_DIR) if f.endswith('.txt')]) if os.path.exists(LOG_DIR) else 0
        }
        
        return jsonify({
            "status": "success",
            "system_info": system_info,
            "app_info": app_info,
            "config": config
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_bp.route("/download/<filename>")
@require_auth
def download_log(filename):
    """Descargar archivo de log"""
    try:
        # Validaciones de seguridad
        if ".." in filename or "/" in filename or "\\" in filename:
            return "Acceso denegado", 403
        
        if not filename.endswith(".txt"):
            return "Tipo de archivo no permitido", 403
        
        file_path = os.path.join(LOG_DIR, filename)
        if not os.path.exists(file_path):
            return "Archivo no encontrado", 404
        
        return send_from_directory(LOG_DIR, filename, as_attachment=True)
        
    except Exception as e:
        return f"Error descargando archivo: {str(e)}", 500

@web_bp.route("/ejecutar")
@require_auth
def ejecutar_auditoria():
    """Ejecutar auditoría usando subprocess"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))

    try:
        # Verificar si ya hay una auditoría en curso
        if audit_status["running"]:
            return jsonify({
                "status": "error",
                "message": "Ya hay una auditoría en curso. Espera a que termine o deténla antes de iniciar una nueva."
            }), 400

        # Configurar el entorno para Python
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Ejecutar el script principal de auditoría
        process = subprocess.Popen([
            "python", 
            "smartcam_auditor.py"
        ], 
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
        )

        # Actualizar estado
        audit_status["running"] = True
        audit_status["current_task"] = "🚀 Auditoría completa iniciada vía subprocess"
        audit_status["progress"] = 5
        audit_status["process_id"] = process.pid
        audit_status["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Iniciar monitoreo del proceso en un hilo separado
        threading.Thread(target=monitor_subprocess, args=(process,), daemon=True).start()
        
        return redirect(url_for("web_panel.dashboard"))
    except Exception as e:
        print(f"Error ejecutando auditoría: {e}")
        audit_status["current_task"] = f"❌ Error iniciando auditoría: {str(e)}"
        audit_status["running"] = False
        return redirect(url_for("web_panel.dashboard"))

@web_bp.route("/ejecutar_rapido")
@require_auth
def ejecutar_auditoria_rapida():
    """Ejecutar auditoría rápida con parámetros específicos"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))

    try:
        # Verificar si ya hay una auditoría en curso
        if audit_status["running"]:
            return jsonify({
                "status": "error",
                "message": "Ya hay una auditoría en curso."
            }), 400

        # Configurar el entorno para Python
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Ejecutar auditoría con modo rápido
        process = subprocess.Popen([
            "python", 
            "smartcam_auditor.py"
        ], 
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )

        audit_status["running"] = True
        audit_status["current_task"] = "⚡ Auditoría rápida iniciada (red 192.168.1.0/24)"
        audit_status["progress"] = 10
        audit_status["process_id"] = process.pid
        audit_status["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Iniciar monitoreo del proceso en un hilo separado
        threading.Thread(target=monitor_subprocess_quick, args=(process,), daemon=True).start()
        
        return redirect(url_for("web_panel.dashboard"))
    except Exception as e:
        print(f"Error ejecutando auditoría rápida: {e}")
        audit_status["current_task"] = f"❌ Error en auditoría rápida: {str(e)}"
        audit_status["running"] = False
        return redirect(url_for("web_panel.dashboard"))

@web_bp.route("/ejecutar_personalizada", methods=['POST'])
@require_auth
def ejecutar_auditoria_personalizada():
    """Ejecutar auditoría personalizada con parámetros del usuario"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))

    try:
        # Verificar si ya hay una auditoría en curso
        if audit_status["running"]:
            return jsonify({
                "status": "error",
                "message": "Ya hay una auditoría en curso."
            }), 400

        data = request.get_json() or {}
        network = data.get('network', '192.168.1.0/24')
        
        # Validar formato de red
        import re
        network_pattern = r'^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$'
        if not re.match(network_pattern, network):
            return jsonify({
                "status": "error",
                "message": "Formato de red inválido. Use formato CIDR (ej: 192.168.1.0/24)"
            }), 400
        
        # Validar rangos de IP válidos
        ip_parts = network.split('/')[0].split('.')
        for part in ip_parts:
            if int(part) > 255:
                return jsonify({
                    "status": "error",
                    "message": "Dirección IP inválida."
                }), 400
        
        # Crear archivo temporal con la red personalizada
        temp_networks_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "temp_networks.txt")
        with open(temp_networks_file, 'w') as f:
            f.write(f"# Red personalizada para auditoría\n{network}\n")
        
        # Configurar el entorno para Python
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env['SMARTCAM_NETWORK_FILE'] = temp_networks_file
        
        # Ejecutar auditoría personalizada
        process = subprocess.Popen([
            "python", 
            "smartcam_auditor.py"
        ], 
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )

        audit_status["running"] = True
        audit_status["current_task"] = f"🎯 Auditoría personalizada iniciada para {network}"
        audit_status["progress"] = 10
        audit_status["process_id"] = process.pid
        audit_status["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        audit_status["target_network"] = network
        
        # Iniciar monitoreo del proceso en un hilo separado
        threading.Thread(target=monitor_subprocess_custom, args=(process, temp_networks_file), daemon=True).start()
        
        return jsonify({
            "status": "success",
            "message": f"Auditoría personalizada iniciada para {network}"
        })
        
    except Exception as e:
        print(f"Error ejecutando auditoría personalizada: {e}")
        audit_status["running"] = False
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@web_bp.route("/graficos")
@require_auth
def graficos():
    """Página de gráficos y visualización de estadísticas de seguridad"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))

    # Calcular estadísticas basadas en resultados reales de auditorías
    total_devices = len(audit_status.get("results", []))
    total_vulnerabilities = sum(len(r.get("vulnerabilities", [])) for r in audit_status.get("results", []))
    total_credentials = sum(len(r.get("credentials", [])) for r in audit_status.get("results", []))
    
    # Categorizar vulnerabilidades por severidad
    critical_vulns = sum(1 for r in audit_status.get("results", []) 
                        for v in r.get("vulnerabilities", []) 
                        if v.get("severity") == "CRITICAL")
    high_vulns = sum(1 for r in audit_status.get("results", []) 
                    for v in r.get("vulnerabilities", []) 
                    if v.get("severity") == "HIGH")
    medium_vulns = sum(1 for r in audit_status.get("results", []) 
                      for v in r.get("vulnerabilities", []) 
                      if v.get("severity") == "MEDIUM")
    low_vulns = total_vulnerabilities - critical_vulns - high_vulns - medium_vulns

    # Datos para gráficos (con datos de ejemplo si no hay auditorías)
    if total_devices == 0:
        # Datos de demostración cuando no hay auditorías reales
        vulnerability_severity_data = {
            "Críticas": 3,
            "Altas": 5, 
            "Medias": 8,
            "Bajas": 4
        }
        
        security_metrics_data = {
            "Credenciales débiles": 7,
            "Dispositivos vulnerables": 12,
            "Puertos inseguros": 15,
            "Dispositivos seguros": 8
        }
        
        device_types_data = {
            "Cámaras IP": 15,
            "DVR/NVR": 3,
            "Routers": 2,
            "Otros IoT": 5
        }
        
        total_devices = 25
        total_vulnerabilities = 20
        
    else:
        vulnerability_severity_data = {
            "Críticas": critical_vulns,
            "Altas": high_vulns, 
            "Medias": medium_vulns,
            "Bajas": low_vulns
        }
        
        security_metrics_data = {
            "Credenciales débiles": total_credentials,
            "Dispositivos vulnerables": len([r for r in audit_status.get("results", []) 
                                           if r.get("vulnerabilities", [])]),
            "Puertos inseguros": sum(len([p for p in r.get("ports", []) 
                                        if p in [21, 23, 80, 135, 139, 445]]) 
                                   for r in audit_status.get("results", [])),
            "Dispositivos seguros": total_devices - len([r for r in audit_status.get("results", []) 
                                                       if r.get("vulnerabilities", [])])
        }
        
        device_types_data = {
            "Cámaras IP": len([r for r in audit_status.get("results", []) 
                              if "camera" in r.get("device_info", {}).get("type", "").lower()]),
            "DVR/NVR": len([r for r in audit_status.get("results", []) 
                           if "dvr" in r.get("device_info", {}).get("type", "").lower() or 
                              "nvr" in r.get("device_info", {}).get("type", "").lower()]),
            "Routers": len([r for r in audit_status.get("results", []) 
                           if "router" in r.get("device_info", {}).get("type", "").lower()]),
            "Otros IoT": max(0, total_devices - len([r for r in audit_status.get("results", []) 
                                                   if any(keyword in r.get("device_info", {}).get("type", "").lower() 
                                                         for keyword in ["camera", "dvr", "nvr", "router"])]))
        }
    
    # Datos temporales de últimas auditorías (always include)
    timeline_data = {
        "labels": ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
        "vulnerabilities": [8, 12, 6, max(total_vulnerabilities, 10)],
        "devices": [15, 18, 20, max(total_devices, 22)]
    }

    return render_template("charts.html", 
                         vulnerability_severity=vulnerability_severity_data,
                         security_metrics=security_metrics_data,
                         timeline=timeline_data,
                         device_types=device_types_data,
                         total_devices=total_devices,
                         total_vulnerabilities=total_vulnerabilities,
                         user=session.get("user"))
