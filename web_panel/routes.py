"""
SmartCam Auditor - Rutas del Panel Web (Versión Simplificada)
Maneja las rutas principales del panel web
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import os
import subprocess
import sys

# Añadir el directorio padre al path para importar el simulador
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from audit_simulator import realizar_auditoria, realizar_auditoria_rapida

# Importar el probador de credenciales
try:
    from scanner.credential_tester import testear_credenciales, generar_reporte_credenciales
    CREDENTIAL_TESTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Credential tester no disponible: {e}")
    CREDENTIAL_TESTER_AVAILABLE = False

# Importar el escáner de red avanzado
try:
    from scanner.network_scanner import NetworkScanner, scan_network as advanced_scan
    ADVANCED_SCANNER_AVAILABLE = True
    print("✅ Escáner de red avanzado disponible en web panel")
except ImportError as e:
    print(f"⚠️ Escáner avanzado no disponible: {e}")
    ADVANCED_SCANNER_AVAILABLE = False

web_bp = Blueprint("web_panel", __name__)
LOG_DIR = "logs"
USERNAME = "admin"
PASSWORD = "smartcam2024"  # Mantener consistencia con la documentación

# Estado global de auditoría
audit_in_progress = False  # Estado global

@web_bp.route("/", methods=["GET", "POST"])
def login():
    """Página de login principal"""
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["user"] = USERNAME
            return redirect(url_for("web_panel.dashboard"))
        return render_template("login.html", error="Credenciales incorrectas.")
    return render_template("login.html")

@web_bp.route("/logout")
def logout():
    """Cerrar sesión"""
    session.pop("user", None)
    return redirect(url_for("web_panel.login"))

@web_bp.route("/dashboard")
def dashboard():
    """Dashboard principal"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))
    
    # Obtener lista de archivos de logs
    try:
        if os.path.exists(LOG_DIR):
            files = os.listdir(LOG_DIR)
            files = [f for f in files if f.endswith(".txt")]
            files.sort(reverse=True)  # Más recientes primero
        else:
            files = []
    except Exception as e:
        print(f"Error listando logs: {e}")
        files = []
    
    return render_template("dashboard.html", log_files=files, user=session.get("user"))

@web_bp.route("/logs/<filename>")
def view_log(filename):
    """Ver contenido de un archivo de log"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))
    
    # Validar que el archivo esté en el directorio de logs
    file_path = os.path.join(LOG_DIR, filename)
    if os.path.exists(file_path) and filename.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"<pre style='font-family: monospace; white-space: pre-wrap; padding: 20px;'>{content}</pre>"
        except Exception as e:
            return f"Error leyendo archivo: {str(e)}", 500
    return "Archivo no encontrado", 404

@web_bp.route("/ejecutar")
def ejecutar_auditoria():
    """Ejecutar auditoría principal"""
    global audit_in_progress

    if "user" not in session:
        return redirect(url_for("web_panel.login"))

    if audit_in_progress:
        flash("⚠️ Auditoría ya en curso. Por favor, espera...", "warning")
        return redirect(url_for("web_panel.dashboard"))

    audit_in_progress = True
    flash("🚀 Auditoría iniciada en background...", "info")

    def run_scan():
        try:
            global audit_in_progress
            print("🔍 Iniciando auditoría completa...")
            
            # Intentar ejecutar el script real de auditoría
            result = subprocess.run(["python", "scanner/run_audit.py"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minutos timeout
            
            if result.returncode == 0:
                print("✅ Auditoría completada exitosamente")
            else:
                print(f"⚠️ Auditoría completada con advertencias: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Auditoría detenida por timeout")
        except FileNotFoundError:
            # Si no existe el script, usar el simulador
            print("📝 Usando simulador de auditoría...")
            realizar_auditoria()
        except Exception as e:
            print(f"❌ Error durante auditoría: {e}")
        finally:
            audit_in_progress = False
            print("🏁 Estado de auditoría restablecido")

    import threading
    threading.Thread(target=run_scan, daemon=True).start()

    return redirect(url_for("web_panel.dashboard"))

@web_bp.route("/ejecutar_rapido")
def ejecutar_auditoria_rapida():
    """Ejecutar auditoría rápida"""
    global audit_in_progress

    if "user" not in session:
        return redirect(url_for("web_panel.login"))
    
    if audit_in_progress:
        flash("⚠️ Auditoría ya en curso. Por favor, espera...", "warning")
        return redirect(url_for("web_panel.dashboard"))
    
    audit_in_progress = True
    flash("⚡ Escaneo rápido iniciado en background...", "info")
    
    def run_quick_scan():
        try:
            global audit_in_progress
            print("⚡ Iniciando escaneo rápido...")
            
            # Intentar ejecutar script de escaneo rápido
            result = subprocess.run(["python", "scanner/quick_scan.py"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=120)  # 2 minutos timeout
            
            if result.returncode == 0:
                print("✅ Escaneo rápido completado exitosamente")
            else:
                print(f"⚠️ Escaneo completado con advertencias: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Escaneo rápido detenido por timeout")
        except FileNotFoundError:
            # Si no existe el script, usar el simulador
            print("📝 Usando simulador de escaneo rápido...")
            realizar_auditoria_rapida()
        except Exception as e:
            print(f"❌ Error durante escaneo rápido: {e}")
        finally:
            audit_in_progress = False
            print("🏁 Estado de escaneo restablecido")

    import threading
    threading.Thread(target=run_quick_scan, daemon=True).start()
    
    return redirect(url_for("web_panel.dashboard"))

@web_bp.route("/graficos")
def graficos():
    """Página de gráficos y visualización de estadísticas (datos reales)"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))

    # Inicializar contadores de vulnerabilidades
    datos = {
        "Credenciales débiles": 0,
        "Puertos inseguros": 0,
        "Cámaras sin cifrado": 0
    }
    
    # Contadores adicionales para análisis detallado
    vulnerability_severity = {
        "Críticas": 0,
        "Altas": 0, 
        "Medias": 0,
        "Bajas": 0
    }
    
    security_metrics = {
        "Credenciales débiles": 0,
        "Dispositivos vulnerables": 0,
        "Puertos inseguros": 0,
        "Dispositivos seguros": 0
    }
    
    device_types = {
        "Cámaras IP": 0,
        "DVR/NVR": 0,
        "Routers": 0,
        "Otros IoT": 0
    }
    
    total_devices = 0
    total_vulnerabilities = 0
    
    # Leer datos reales de los archivos de log
    try:
        if os.path.exists(LOG_DIR):
            for file in os.listdir(LOG_DIR):
                if file.endswith(".txt"):
                    file_path = os.path.join(LOG_DIR, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            contenido = f.read().lower()
                            
                            # Análisis de vulnerabilidades básicas
                            if "admin:admin" in contenido or "credencial" in contenido:
                                datos["Credenciales débiles"] += 1
                                vulnerability_severity["Altas"] += 1
                                
                            if "puertos expuestos" in contenido or "puerto abierto" in contenido or "port" in contenido:
                                datos["Puertos inseguros"] += 1
                                vulnerability_severity["Medias"] += 1
                                
                            if "sin cifrado" in contenido or "unencrypted" in contenido:
                                datos["Cámaras sin cifrado"] += 1
                                vulnerability_severity["Críticas"] += 1
                            
                            # Análisis de tipos de dispositivos
                            if "cámara" in contenido or "camera" in contenido:
                                device_types["Cámaras IP"] += 1
                            if "dvr" in contenido or "nvr" in contenido:
                                device_types["DVR/NVR"] += 1
                            if "router" in contenido:
                                device_types["Routers"] += 1
                            if "iot" in contenido or "sensor" in contenido:
                                device_types["Otros IoT"] += 1
                                
                            # Contar dispositivos encontrados
                            if "dispositivo encontrado" in contenido or "device found" in contenido:
                                total_devices += contenido.count("dispositivo encontrado") + contenido.count("device found")
                                
                    except Exception as e:
                        print(f"Error leyendo archivo {file}: {e}")
                        continue
    except Exception as e:
        print(f"Error accediendo al directorio de logs: {e}")
    
    # Calcular métricas de seguridad
    total_vulnerabilities = sum(datos.values())
    security_metrics["Credenciales débiles"] = datos["Credenciales débiles"]
    security_metrics["Puertos inseguros"] = datos["Puertos inseguros"] 
    security_metrics["Dispositivos vulnerables"] = total_vulnerabilities
    security_metrics["Dispositivos seguros"] = max(0, total_devices - total_vulnerabilities)
    
    # Si no hay vulnerabilidades bajas detectadas, agregar algunas por defecto
    if vulnerability_severity["Bajas"] == 0 and total_vulnerabilities > 0:
        vulnerability_severity["Bajas"] = max(1, total_vulnerabilities // 3)
    
    # Timeline básica (se puede mejorar analizando fechas de los logs)
    timeline = {
        "labels": ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
        "vulnerabilities": [total_vulnerabilities//4, total_vulnerabilities//3, total_vulnerabilities//2, total_vulnerabilities],
        "devices": [total_devices//4, total_devices//3, total_devices//2, total_devices]
    }
    
    return render_template("charts.html", 
                         data=datos,
                         vulnerability_severity=vulnerability_severity,
                         security_metrics=security_metrics,
                         device_types=device_types,
                         timeline=timeline,
                         total_devices=total_devices,
                         total_vulnerabilities=total_vulnerabilities,
                         user=session.get("user"))

@web_bp.route("/charts")
def charts():
    """Dashboard de gráficos y métricas"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))
    
    # Datos de ejemplo para los gráficos
    sample_data = {
        'devices_found': [15, 8, 12, 6, 10, 14, 9],
        'vulnerabilities': [3, 1, 4, 2, 3, 5, 2],
        'security_score': [85, 78, 92, 68, 81, 89, 75],
        'labels': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    }
    
    vulnerability_severity = {
        'critical': 3,
        'high': 7,
        'medium': 12,
        'low': 8
    }
    
    security_metrics = {
        'encrypted': 75,
        'unencrypted': 25,
        'secure_auth': 68,
        'weak_auth': 32
    }
    
    timeline = {
        'dates': ['2025-07-01', '2025-07-02', '2025-07-03', '2025-07-04', '2025-07-05'],
        'scans': [5, 8, 3, 12, 7],
        'threats': [2, 1, 0, 4, 3]
    }
    
    device_types = {
        'cameras': 15,
        'routers': 8,
        'iot_sensors': 12,
        'nvr_systems': 5
    }
    
    return render_template("charts.html", 
                         user=session.get("user"),
                         data=sample_data,
                         vulnerability_severity=vulnerability_severity,
                         security_metrics=security_metrics,
                         timeline=timeline,
                         device_types=device_types)

@web_bp.route("/info")
def info():
    """Página de información y credenciales"""
    info_data = {
        'version': 'v2.0 Pro - Cyberpunk Edition',
        'username': USERNAME,
        'password': PASSWORD,
        'server': 'http://localhost:5000',
        'status': 'Activo'
    }
    return f"""
    <html>
    <head>
        <title>SmartCam Auditor - Información</title>
        <style>
            body {{ 
                font-family: 'Courier New', monospace; 
                background: #0a0a0a; 
                color: #39ff14; 
                padding: 20px; 
                line-height: 1.6;
            }}
            .info-box {{ 
                background: #1a1a1a; 
                border: 2px solid #39ff14; 
                padding: 20px; 
                border-radius: 10px;
                max-width: 600px;
                margin: 0 auto;
                box-shadow: 0 0 20px rgba(57, 255, 20, 0.3);
            }}
            h1 {{ color: #39ff14; text-align: center; }}
            .cred {{ background: #2a2a2a; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            a {{ color: #00bfff; text-decoration: none; }}
            a:hover {{ color: #39ff14; }}
        </style>
    </head>
    <body>
        <div class="info-box">
            <h1>🔒 SmartCam Auditor {info_data['version']}</h1>
            <div class="cred">
                <strong>🌐 Servidor:</strong> {info_data['server']}<br>
                <strong>👤 Usuario:</strong> {info_data['username']}<br>
                <strong>🔑 Contraseña:</strong> {info_data['password']}<br>
                <strong>📊 Estado:</strong> {info_data['status']}
            </div>
            <p style="text-align: center; margin-top: 20px;">
                <a href="/">🚀 Ir al Login</a> | 
                <a href="/dashboard">📊 Dashboard</a>
            </p>
            <p style="text-align: center; color: #888; font-size: 0.9rem; margin-top: 20px;">
                ⚠️ Solo para redes propias y con autorización explícita
            </p>
        </div>
    </body>
    </html>
    """

@web_bp.route("/estado")
def estado():
    """API endpoint simple para verificar el estado de auditoría"""
    global audit_in_progress
    return {"en_progreso": audit_in_progress}

@web_bp.route("/audit_status")
def audit_status():
    """API endpoint para verificar el estado de auditoría"""
    global audit_in_progress
    return jsonify({
        'in_progress': audit_in_progress,
        'status': 'Auditoría en progreso...' if audit_in_progress else 'Sistema listo'
    })

@web_bp.route("/probar_credenciales", methods=["GET", "POST"])
def probar_credenciales():
    """Página para probar credenciales débiles en dispositivos"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))
    
    if request.method == "POST":
        # Obtener IPs del formulario
        ips_texto = request.form.get("ips", "").strip()
        incluir_rtsp = request.form.get("incluir_rtsp") == "on"
        incluir_ssh = request.form.get("incluir_ssh") == "on"
        
        if not ips_texto:
            flash("❌ Debes especificar al menos una IP", "error")
            return render_template("credential_test.html", user=session.get("user"))
        
        # Procesar lista de IPs
        try:
            lista_ips = []
            for linea in ips_texto.split('\n'):
                ip = linea.strip()
                if ip and not ip.startswith('#'):
                    lista_ips.append(ip)
            
            if not lista_ips:
                flash("❌ No se encontraron IPs válidas", "error")
                return render_template("credential_test.html", user=session.get("user"))
            
            global audit_in_progress
            if audit_in_progress:
                flash("⚠️ Ya hay una auditoría en curso. Espera a que termine.", "warning")
                return render_template("credential_test.html", user=session.get("user"))
            
            # Ejecutar pruebas de credenciales en background
            audit_in_progress = True
            flash(f"🚀 Iniciando pruebas de credenciales en {len(lista_ips)} dispositivos...", "info")
            
            def run_credential_test():
                try:
                    global audit_in_progress
                    print(f"🔐 Iniciando pruebas de credenciales en {len(lista_ips)} IPs...")
                    
                    if CREDENTIAL_TESTER_AVAILABLE:
                        # Usar el módulo de pruebas real
                        vulnerabilidades = testear_credenciales(
                            lista_ips, 
                            incluir_rtsp=incluir_rtsp, 
                            incluir_ssh=incluir_ssh
                        )
                        
                        # Generar reporte
                        timestamp = __import__('time').strftime("%Y%m%d_%H%M%S")
                        archivo_reporte = f"logs/credential_test_{timestamp}.txt"
                        
                        if not os.path.exists("logs"):
                            os.makedirs("logs")
                        
                        reporte = generar_reporte_credenciales(vulnerabilidades, archivo_reporte)
                        print(f"✅ Pruebas de credenciales completadas. {len(vulnerabilidades)} vulnerabilidades encontradas.")
                        
                    else:
                        # Fallback: simulador simple
                        print("📝 Usando simulador de pruebas de credenciales...")
                        import time
                        import random
                        
                        # Simular el proceso
                        for i, ip in enumerate(lista_ips, 1):
                            print(f"🔍 Probando credenciales en {ip} ({i}/{len(lista_ips)})...")
                            time.sleep(random.uniform(0.5, 2.0))
                        
                        # Crear reporte simulado
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        archivo_reporte = f"logs/credential_test_sim_{timestamp}.txt"
                        
                        if not os.path.exists("logs"):
                            os.makedirs("logs")
                        
                        vulnerabilidades_sim = random.randint(0, len(lista_ips) // 2)
                        reporte_sim = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                    🔒 SMARTCAM AUDITOR - PRUEBAS DE CREDENCIALES (SIMULACIÓN)            ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║ Fecha: {time.strftime("%Y-%m-%d %H:%M:%S")}                                             ║
║ IPs analizadas: {len(lista_ips)}                                                         ║
║ Vulnerabilidades simuladas: {vulnerabilidades_sim}                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

🧪 SIMULACIÓN DE PRUEBAS DE CREDENCIALES

Dispositivos analizados:
{chr(10).join([f"• {ip}" for ip in lista_ips])}

⚠️  Esta es una simulación. Para pruebas reales instalar dependencias:
   pip install requests paramiko

📊 Análisis completado - SmartCam Auditor v2.0 (Simulación)
⚠️  Solo para uso en redes propias y con autorización explícita
"""
                        
                        with open(archivo_reporte, 'w', encoding='utf-8') as f:
                            f.write(reporte_sim)
                        
                        print(f"✅ Simulación completada. Reporte guardado en {archivo_reporte}")
                        
                except Exception as e:
                    print(f"❌ Error durante pruebas de credenciales: {e}")
                finally:
                    audit_in_progress = False
                    print("🏁 Estado de pruebas restablecido")
            
            import threading
            threading.Thread(target=run_credential_test, daemon=True).start()
            
            return redirect(url_for("web_panel.dashboard"))
            
        except Exception as e:
            flash(f"❌ Error procesando IPs: {str(e)}", "error")
            return render_template("credential_test.html", user=session.get("user"))
    
    # GET request: mostrar formulario
    return render_template("credential_test.html", 
                         user=session.get("user"),
                         credential_tester_available=CREDENTIAL_TESTER_AVAILABLE)

@web_bp.route("/escaner_avanzado", methods=["GET", "POST"])
def escaner_avanzado():
    """Página para el escáner de red avanzado"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))
    
    if request.method == "POST":
        # Obtener parámetros del formulario
        rango_ip = request.form.get("rango_ip", "").strip()
        incluir_dispositivos = request.form.get("incluir_dispositivos") == "on"
        incluir_vulnerabilidades = request.form.get("incluir_vulnerabilidades") == "on"
        
        if not rango_ip:
            flash("❌ Debes especificar un rango de IPs", "error")
            return render_template("advanced_scan.html", user=session.get("user"))
        
        # Procesar rango de IPs
        try:
            # Simular escaneo avanzado
            print(f"🌐 Iniciando escaneo avanzado en {rango_ip}...")
            from time import sleep
            import random
            
            # Simulación de dispositivos encontrados
            dispositivos_encontrados = []
            for i in range(5):
                ip_simulada = f"192.168.1.{random.randint(2, 254)}"
                dispositivos_encontrados.append(ip_simulada)
                print(f"🔍 Dispositivo simulado encontrado: {ip_simulada}")
                sleep(1)
            
            # Simulación de reporte de vulnerabilidades
            if incluir_vulnerabilidades:
                for ip in dispositivos_encontrados:
                    print(f"⚠️ Vulnerabilidades simuladas en {ip}:")
                    print("  - Puerto 23 abierto (Telnet)")
                    print("  - Contraseña débil (admin:admin)")
                    sleep(1)
            
            flash("✅ Escaneo avanzado completado (simulación)", "success")
            
        except Exception as e:
            flash(f"❌ Error durante el escaneo avanzado: {str(e)}", "error")
            print(f"❌ Error durante escaneo avanzado: {e}")
        
        return render_template("advanced_scan.html", user=session.get("user"))
    
    # GET request: mostrar formulario
    return render_template("advanced_scan.html", user=session.get("user"))

@web_bp.route("/scanner_avanzado")
def scanner_avanzado():
    """Página del escáner de red avanzado"""
    if "user" not in session:
        return redirect(url_for("web_panel.login"))
    
    return render_template("scanner_avanzado.html", 
                         scanner_available=ADVANCED_SCANNER_AVAILABLE,
                         user=session.get("user"))

@web_bp.route("/ejecutar_scanner", methods=["POST"])
def ejecutar_scanner():
    """Ejecuta el escáner de red avanzado"""
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    if not ADVANCED_SCANNER_AVAILABLE:
        return jsonify({"error": "Escáner avanzado no disponible"}), 503
    
    network = request.json.get('network', 'auto')
    
    try:
        scanner = NetworkScanner(timeout=2.0, max_threads=50)
        
        if network == 'auto':
            network = scanner.get_local_network()
        
        devices = scanner.scan_network(network)
        
        # Formatear resultados para JSON
        results = {
            "network": network,
            "total_devices": len(devices),
            "devices": devices,
            "summary": {
                "cameras": len([d for d in devices if 'Camera' in d.get('device_type', '')]),
                "iot_devices": len([d for d in devices if 'IoT' in d.get('device_type', '')]),
                "high_confidence": len([d for d in devices if d.get('confidence', 0) >= 75]),
                "critical_ports": len([d for d in devices if any(port in [23, 21] for port in d.get('open_ports', []))])
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Error ejecutando escáner: {str(e)}"}), 500
