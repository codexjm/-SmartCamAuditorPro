#!/usr/bin/env python3
"""
Script de configuración y validación para SmartCam Auditor
Configura el entorno y valida que todo funcione correctamente
"""

import os
import json
import sys
import subprocess
from pathlib import Path

def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    print("[*] Creando estructura de directorios...")
    
    directories = [
        "config",
        "logs", 
        "scanner",
        "reports",
        "backup",
        ".vscode"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"    [+] Directorio creado: {directory}")

def validate_dependencies():
    """Valida que las dependencias estén instaladas"""
    print("\n[*] Validando dependencias...")
    
    required_packages = ["requests", "json"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"    [+] {package}: OK")
        except ImportError:
            print(f"    [!] {package}: FALTANTE")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n[!] Instalar dependencias faltantes:")
        print(f"    pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_enhanced_config():
    """Crea configuración mejorada"""
    print("\n[*] Creando configuración mejorada...")
    
    enhanced_config = {
        "alert_mode": "console",
        "log_folder": "logs",
        "advanced_scanning": True,
        "timeout_settings": {
            "port_scan": 1,
            "http_request": 3,
            "ssl_check": 5
        },
        "reporting": {
            "generate_html": True,
            "generate_json": True,
            "generate_csv": True
        },
        "scan_intensity": "aggressive",
        "concurrent_threads": 20,
        "company_info": {
            "name": "Security Solutions Corp",
            "auditor": "SmartCam Team",
            "contact": "security@company.com"
        }
    }
    
    with open("config/config.json", "w", encoding="utf-8") as f:
        json.dump(enhanced_config, f, indent=4)
    
    print("    [+] Configuración mejorada creada en config/config.json")

def create_network_templates():
    """Crea plantillas de redes para diferentes escenarios"""
    print("\n[*] Creando plantillas de redes...")
    
    # Redes comunes para empresas
    networks_enterprise = """# Configuración para auditorías empresariales
# Redes corporativas típicas

# Redes de oficina principales
192.168.1.0/24
192.168.10.0/24
10.0.0.0/24

# Redes de seguridad/cámaras
192.168.100.0/24
10.10.10.0/24

# Redes de invitados (opcional)
# 192.168.50.0/24

# Para auditorías específicas, descomentar según necesidad:
# 172.16.1.0/24
# 10.1.1.0/24"""

    with open("config/networks_enterprise.txt", "w", encoding="utf-8") as f:
        f.write(networks_enterprise)
    
    # Redes para testing/laboratorio
    networks_lab = """# Configuración para laboratorio de pruebas
# Redes controladas para testing

# Red local de laboratorio
192.168.99.0/24

# Redes de prueba virtuales
10.99.99.0/24

# Red específica para cámaras de prueba
192.168.200.0/24"""

    with open("config/networks_lab.txt", "w", encoding="utf-8") as f:
        f.write(networks_lab)
    
    print("    [+] Plantilla empresarial: config/networks_enterprise.txt")
    print("    [+] Plantilla laboratorio: config/networks_lab.txt")

def create_advanced_credentials():
    """Crea base de datos extendida de credenciales"""
    print("\n[*] Creando base de credenciales extendida...")
    
    extended_credentials = [
        # Credenciales básicas
        {"user": "admin", "pass": "admin"},
        {"user": "admin", "pass": "1234"},
        {"user": "root", "pass": "root"},
        {"user": "user", "pass": "user"},
        
        # Credenciales específicas por marca
        {"user": "admin", "pass": "admin123"},
        {"user": "admin", "pass": "password"},
        {"user": "admin", "pass": "12345"},
        {"user": "admin", "pass": ""},
        
        # Hikvision específicas
        {"user": "admin", "pass": "12345"},
        {"user": "root", "pass": "12345"},
        
        # Dahua específicas  
        {"user": "admin", "pass": "admin"},
        {"user": "888888", "pass": "888888"},
        {"user": "666666", "pass": "666666"},
        
        # Axis específicas
        {"user": "root", "pass": "pass"},
        {"user": "admin", "pass": "1234"},
        
        # Credenciales genéricas IoT
        {"user": "support", "pass": "support"},
        {"user": "service", "pass": "service"},
        {"user": "guest", "pass": "guest"},
        {"user": "operator", "pass": "operator"}
    ]
    
    with open("config/credentials_extended.json", "w", encoding="utf-8") as f:
        json.dump(extended_credentials, f, indent=4)
    
    print("    [+] Base de credenciales extendida creada")

def create_test_script():
    """Crea script de prueba automática"""
    print("\n[*] Creando script de prueba automática...")
    
    test_script = '''#!/usr/bin/env python3
"""
Script de prueba automática para SmartCam Auditor
Ejecuta pruebas de validación del sistema
"""

def test_modules():
    """Prueba la importación de todos los módulos"""
    print("[TEST] Probando importación de módulos...")
    
    try:
        from scanner.network_scanner import scan_network
        print("    [+] network_scanner: OK")
    except Exception as e:
        print(f"    [!] network_scanner: ERROR - {e}")
        return False
    
    try:
        from scanner.port_checker import check_ports
        print("    [+] port_checker: OK")
    except Exception as e:
        print(f"    [!] port_checker: ERROR - {e}")
        return False
    
    try:
        from scanner.login_tester import test_logins
        print("    [+] login_tester: OK")
    except Exception as e:
        print(f"    [!] login_tester: ERROR - {e}")
        return False
    
    try:
        from scanner.log_manager import save_log
        print("    [+] log_manager: OK")
    except Exception as e:
        print(f"    [!] log_manager: ERROR - {e}")
        return False
    
    try:
        from scanner.advanced_testing import advanced_camera_testing
        print("    [+] advanced_testing: OK")
    except Exception as e:
        print(f"    [!] advanced_testing: ERROR - {e}")
        return False
    
    return True

def test_config_files():
    """Prueba que los archivos de configuración existan"""
    print("\\n[TEST] Probando archivos de configuración...")
    
    import os
    required_files = [
        "config/config.json",
        "config/credentials.json", 
        "config/networks.txt"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"    [+] {file}: OK")
        else:
            print(f"    [!] {file}: FALTANTE")
            all_exist = False
    
    return all_exist

def test_network_connectivity():
    """Prueba conectividad básica"""
    print("\\n[TEST] Probando conectividad de red...")
    
    import socket
    
    # Probar conectividad local
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("8.8.8.8", 53))
        sock.close()
        
        if result == 0:
            print("    [+] Conectividad de red: OK")
            return True
        else:
            print("    [!] Conectividad de red: ERROR")
            return False
    except Exception as e:
        print(f"    [!] Error de conectividad: {e}")
        return False

if __name__ == "__main__":
    print("=== SMARTCAM AUDITOR - PRUEBAS AUTOMÁTICAS ===\\n")
    
    all_tests_passed = True
    
    # Ejecutar todas las pruebas
    if not test_modules():
        all_tests_passed = False
    
    if not test_config_files():
        all_tests_passed = False
    
    if not test_network_connectivity():
        all_tests_passed = False
    
    print("\\n" + "="*50)
    if all_tests_passed:
        print("[SUCCESS] Todas las pruebas pasaron correctamente!")
        print("El SmartCam Auditor está listo para usar.")
    else:
        print("[ERROR] Algunas pruebas fallaron.")
        print("Revisar los errores antes de usar el auditor.")
    print("="*50)
'''
    
    with open("test_system.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("    [+] Script de prueba creado: test_system.py")

def create_launcher_script():
    """Crea script launcher con opciones"""
    print("\n[*] Creando script launcher...")
    
    launcher = '''#!/usr/bin/env python3
"""
Launcher para SmartCam Auditor con diferentes modos de operación
"""

import sys
import os
import shutil

def show_banner():
    print("="*60)
    print("         SMARTCAM AUDITOR - SECURITY SCANNER")
    print("              For Professional Use Only")
    print("="*60)
    print()

def show_menu():
    print("Selecciona el modo de operación:")
    print()
    print("1. Auditoría Empresarial (config/networks_enterprise.txt)")
    print("2. Auditoría de Laboratorio (config/networks_lab.txt)")
    print("3. Auditoría Personalizada (config/networks.txt)")
    print("4. Prueba del Sistema")
    print("5. Ver Reportes Anteriores")
    print("6. Configuración")
    print("0. Salir")
    print()

def run_audit(network_file):
    """Ejecuta auditoría con archivo de red específico"""
    
    # Backup del archivo actual
    if os.path.exists("config/networks.txt"):
        shutil.copy("config/networks.txt", "config/networks_backup.txt")
    
    # Copiar archivo seleccionado
    if os.path.exists(network_file):
        shutil.copy(network_file, "config/networks.txt")
        print(f"[*] Usando configuración: {network_file}")
        
        # Ejecutar auditoría
        os.system("python smartcam_auditor.py")
        
        # Restaurar backup si existe
        if os.path.exists("config/networks_backup.txt"):
            shutil.copy("config/networks_backup.txt", "config/networks.txt")
            os.remove("config/networks_backup.txt")
    else:
        print(f"[ERROR] No se encontró el archivo: {network_file}")

def main():
    show_banner()
    
    while True:
        show_menu()
        choice = input("Selecciona una opción (0-6): ").strip()
        
        if choice == "1":
            run_audit("config/networks_enterprise.txt")
        elif choice == "2":
            run_audit("config/networks_lab.txt")
        elif choice == "3":
            os.system("python smartcam_auditor.py")
        elif choice == "4":
            os.system("python test_system.py")
        elif choice == "5":
            print("\\n[*] Reportes disponibles en la carpeta 'logs/'")
            if os.path.exists("logs"):
                files = [f for f in os.listdir("logs") if f.endswith(".txt")]
                if files:
                    for i, file in enumerate(files, 1):
                        print(f"    {i}. {file}")
                else:
                    print("    No hay reportes disponibles")
            input("\\nPresiona Enter para continuar...")
        elif choice == "6":
            os.system("python setup.py")
        elif choice == "0":
            print("\\n[*] Saliendo...")
            break
        else:
            print("\\n[ERROR] Opción inválida")
        
        print()

if __name__ == "__main__":
    main()
'''
    
    with open("launcher.py", "w", encoding="utf-8") as f:
        f.write(launcher)
    
    print("    [+] Launcher creado: launcher.py")

def create_html_reporter():
    """Crea generador de reportes en HTML"""
    print("\n[*] Creando generador de reportes HTML...")
    
    html_reporter = '''"""
Generador de reportes HTML para SmartCam Auditor
"""

import json
import os
from datetime import datetime

def generate_html_report(results_list, config):
    """Genera un reporte HTML profesional"""
    
    html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCam Auditor - Reporte de Seguridad</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #007bff; margin: 0; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .metric { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .metric h3 { margin: 0; color: #495057; }
        .metric .number { font-size: 2em; font-weight: bold; color: #007bff; }
        .device { margin: 30px 0; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; }
        .device h3 { color: #495057; margin-top: 0; }
        .vulnerability { margin: 15px 0; padding: 15px; border-radius: 5px; }
        .critical { background-color: #f8d7da; border-left: 4px solid #dc3545; }
        .high { background-color: #fff3cd; border-left: 4px solid #ffc107; }
        .medium { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
        .low { background-color: #d4edda; border-left: 4px solid #28a745; }
        .severity { font-weight: bold; text-transform: uppercase; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 SmartCam Auditor</h1>
            <h2>Reporte de Evaluación de Seguridad</h2>
            <p>Generado el: {timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <h3>Dispositivos Analizados</h3>
                <div class="number">{total_devices}</div>
            </div>
            <div class="metric">
                <h3>Vulnerabilidades Críticas</h3>
                <div class="number" style="color: #dc3545;">{critical_count}</div>
            </div>
            <div class="metric">
                <h3>Vulnerabilidades Altas</h3>
                <div class="number" style="color: #ffc107;">{high_count}</div>
            </div>
            <div class="metric">
                <h3>Total de Hallazgos</h3>
                <div class="number">{total_findings}</div>
            </div>
        </div>
        
        {devices_html}
        
        <div class="footer">
            <p>SmartCam Auditor v1.0 - Para uso en redes autorizadas únicamente</p>
            <p>© 2025 Security Solutions Corp. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>"""
    
    # Calcular métricas
    total_devices = len(results_list)
    critical_count = 0
    high_count = 0
    total_findings = 0
    
    devices_html = ""
    
    for result in results_list:
        device_html = f'<div class="device"><h3>📹 Dispositivo: {result["ip"]}</h3>'
        
        vulnerabilities = result.get("vulnerabilities", [])
        if vulnerabilities:
            device_html += "<h4>Vulnerabilidades Encontradas:</h4>"
            for vuln in vulnerabilities:
                severity = vuln["severity"].lower()
                if severity == "critical":
                    critical_count += 1
                elif severity == "high":
                    high_count += 1
                total_findings += 1
                
                device_html += f"""
                <div class="vulnerability {severity}">
                    <span class="severity">{vuln["severity"]}</span>: {vuln["type"]}<br>
                    <small>{vuln["description"]}</small>
                </div>
                """
        else:
            device_html += "<p style='color: #28a745;'>✅ No se encontraron vulnerabilidades críticas</p>"
        
        device_html += "</div>"
        devices_html += device_html
    
    # Generar HTML final
    html_content = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_devices=total_devices,
        critical_count=critical_count,
        high_count=high_count,
        total_findings=total_findings,
        devices_html=devices_html
    )
    
    # Guardar archivo
    report_folder = config.get("log_folder", "logs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = f"{report_folder}/security_report_{timestamp}.html"
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[+] Reporte HTML generado: {html_file}")
    return html_file
'''
    
    with open("scanner/html_reporter.py", "w", encoding="utf-8") as f:
        f.write(html_reporter)
    
    print("    [+] Generador HTML creado: scanner/html_reporter.py")

def main():
    """Función principal de configuración"""
    print("=== SMARTCAM AUDITOR - CONFIGURACIÓN AVANZADA ===\n")
    
    # Ejecutar todas las configuraciones
    create_directory_structure()
    
    if not validate_dependencies():
        print("\n[!] Por favor instala las dependencias faltantes antes de continuar")
        return
    
    create_enhanced_config()
    create_network_templates()
    create_advanced_credentials()
    create_test_script()
    create_launcher_script()
    create_html_reporter()
    
    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\nPróximos pasos:")
    print("1. Ejecutar: python test_system.py (para validar)")
    print("2. Ejecutar: python launcher.py (para usar el auditor)")
    print("3. Configurar redes en config/networks_*.txt")
    print("\nArchivos creados:")
    print("- setup.py (este archivo)")
    print("- test_system.py (pruebas)")
    print("- launcher.py (launcher con menú)")
    print("- config/config.json (configuración mejorada)")
    print("- config/networks_enterprise.txt (redes empresariales)")
    print("- config/networks_lab.txt (redes de laboratorio)")
    print("- config/credentials_extended.json (credenciales extendidas)")
    print("- scanner/html_reporter.py (reportes HTML)")

if __name__ == "__main__":
    main()
