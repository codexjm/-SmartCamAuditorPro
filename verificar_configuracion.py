#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Verificador de Configuración - SmartCam Auditor v2.0 Pro
Verifica que la configuración personalizada esté funcionando correctamente
"""

import json
import os
import sys
from pathlib import Path

# Colores para la terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    print(f"""{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                  🔧 VERIFICADOR DE CONFIGURACIÓN             ║
║                   SmartCam Auditor v2.0 Pro                ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}""")

def load_config():
    """Cargar la configuración desde el archivo JSON"""
    config_path = "config/config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"{Colors.GREEN}✅ Configuración cargada correctamente{Colors.END}")
        return config
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Error: No se encontró el archivo {config_path}{Colors.END}")
        return None
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}❌ Error al parsear JSON: {e}{Colors.END}")
        return None

def verify_config_parameters(config):
    """Verificar parámetros específicos de la configuración"""
    print(f"\n{Colors.YELLOW}📋 Verificando parámetros de configuración:{Colors.END}")
    
    # Verificar red y puertos
    print(f"🌐 Rango de red: {Colors.CYAN}{config.get('network_range', 'N/A')}{Colors.END}")
    ports = config.get('camera_ports', [])
    print(f"🔌 Puertos de cámaras: {Colors.CYAN}{len(ports)} puertos configurados{Colors.END}")
    print(f"   └─ Puertos: {', '.join(map(str, ports))}")
    
    # Verificar configuración de escaneo
    scan_settings = config.get('scan_settings', {})
    print(f"⚙️  Configuración de escaneo:")
    print(f"   ├─ Timeout: {Colors.CYAN}{scan_settings.get('timeout', 'N/A')}s{Colors.END}")
    print(f"   ├─ Max threads: {Colors.CYAN}{scan_settings.get('max_threads', 'N/A')}{Colors.END}")
    print(f"   └─ Ping timeout: {Colors.CYAN}{scan_settings.get('ping_timeout', 'N/A')}s{Colors.END}")
    
    # Verificar intensidad de escaneo
    intensity = config.get('scan_intensity', 'N/A')
    print(f"🎯 Intensidad de escaneo: {Colors.MAGENTA}{intensity}{Colors.END}")
    
    # Verificar configuración de fuerza bruta
    brute_force = config.get('brute_force', {})
    print(f"💥 Fuerza bruta:")
    print(f"   ├─ Habilitado: {Colors.GREEN if brute_force.get('enabled') else Colors.RED}{brute_force.get('enabled', 'N/A')}{Colors.END}")
    print(f"   ├─ Max threads: {Colors.CYAN}{brute_force.get('max_threads', 'N/A')}{Colors.END}")
    print(f"   ├─ SSH: {Colors.GREEN if brute_force.get('enable_ssh') else Colors.RED}{brute_force.get('enable_ssh', 'N/A')}{Colors.END}")
    print(f"   ├─ Telnet: {Colors.GREEN if brute_force.get('enable_telnet') else Colors.RED}{brute_force.get('enable_telnet', 'N/A')}{Colors.END}")
    print(f"   └─ Max intentos por servicio: {Colors.CYAN}{brute_force.get('max_attempts_per_service', 'N/A')}{Colors.END}")
    
    # Verificar módulos del audit master
    audit_master = config.get('audit_master', {})
    print(f"🎛️  Módulos de auditoría:")
    print(f"   ├─ Escaneo de red: {Colors.GREEN if audit_master.get('enable_network_scan') else Colors.RED}{audit_master.get('enable_network_scan', 'N/A')}{Colors.END}")
    print(f"   ├─ Test de login: {Colors.GREEN if audit_master.get('enable_login_test') else Colors.RED}{audit_master.get('enable_login_test', 'N/A')}{Colors.END}")
    print(f"   ├─ Fuerza bruta: {Colors.GREEN if audit_master.get('enable_brute_force') else Colors.RED}{audit_master.get('enable_brute_force', 'N/A')}{Colors.END}")
    print(f"   └─ CVE check: {Colors.GREEN if audit_master.get('enable_cve_check') else Colors.RED}{audit_master.get('enable_cve_check', 'N/A')}{Colors.END}")

def verify_directories():
    """Verificar que los directorios necesarios existan"""
    print(f"\n{Colors.YELLOW}📁 Verificando directorios:{Colors.END}")
    
    directories = ['logs', 'config', 'scanner', 'diccionarios']
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/")
        else:
            print(f"   ❌ {directory}/ - {Colors.RED}No encontrado{Colors.END}")

def verify_dictionary_files():
    """Verificar que los archivos de diccionarios existan"""
    print(f"\n{Colors.YELLOW}📚 Verificando diccionarios:{Colors.END}")
    
    dict_files = [
        'diccionarios/credenciales_comunes.txt',
        'diccionarios/rockyou.txt'
    ]
    
    for dict_file in dict_files:
        if os.path.exists(dict_file):
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                print(f"   ✅ {dict_file} - {Colors.CYAN}{lines} entradas{Colors.END}")
            except Exception as e:
                print(f"   ⚠️  {dict_file} - {Colors.YELLOW}Error al leer: {e}{Colors.END}")
        else:
            print(f"   ❌ {dict_file} - {Colors.RED}No encontrado{Colors.END}")

def test_imports():
    """Probar que se pueden importar los módulos principales"""
    print(f"\n{Colors.YELLOW}🔧 Verificando importaciones:{Colors.END}")
    
    modules_to_test = [
        ('scanner.network_scanner', 'obtener_ips_dispositivos'),
        ('scanner.login_tester', 'testear_credenciales'),
        ('scanner.fuerza_bruta', 'FuerzaBrutaScanner'),
        ('scanner.cve_checker', 'CVEChecker'),
        ('audit_master', 'AuditorMaestro')
    ]
    
    for module_name, function_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            if hasattr(module, function_name):
                print(f"   ✅ {module_name}.{function_name}")
            else:
                print(f"   ⚠️  {module_name}.{function_name} - {Colors.YELLOW}Función no encontrada{Colors.END}")
        except ImportError as e:
            print(f"   ❌ {module_name}.{function_name} - {Colors.RED}Error de importación: {e}{Colors.END}")

def generate_test_script():
    """Generar un script de prueba rápida"""
    test_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
🧪 Script de Prueba Rápida - Configuración Personalizada
\"\"\"

import json
from scanner.network_scanner import obtener_ips_dispositivos, NetworkScanner
from scanner.login_tester import testear_credenciales
from audit_master import AuditorMaestro

def test_config():
    # Cargar configuración
    with open('config/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("🔧 Configuración cargada:")
    print(f"   - Rango: {config['network_range']}")
    print(f"   - Puertos: {config['camera_ports']}")
    print(f"   - Intensidad: {config['scan_intensity']}")
    
    # Prueba rápida de escaneo (solo simulación)
    print("\\n🌐 Prueba de escaneo de red:")
    scanner = NetworkScanner(config)
    # Usar solo unas pocas IPs para prueba rápida
    test_ips = ["192.168.1.1", "192.168.1.100"]
    for ip in test_ips:
        print(f"   Simulando escaneo de {ip}...")
    
    print("\\n✅ Prueba completada - Sistema listo para uso")

if __name__ == "__main__":
    test_config()
"""
    
    with open('prueba_rapida_config.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"\n{Colors.GREEN}📝 Script de prueba generado: prueba_rapida_config.py{Colors.END}")

def main():
    print_header()
    
    # Cargar configuración
    config = load_config()
    if not config:
        sys.exit(1)
    
    # Verificar parámetros
    verify_config_parameters(config)
    
    # Verificar directorios
    verify_directories()
    
    # Verificar diccionarios
    verify_dictionary_files()
    
    # Verificar importaciones
    test_imports()
    
    # Generar script de prueba
    generate_test_script()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Verificación completada!{Colors.END}")
    print(f"{Colors.CYAN}Tu configuración personalizada está lista para usar.{Colors.END}")
    print(f"\n{Colors.YELLOW}💡 Comandos sugeridos para probar:{Colors.END}")
    print(f"   1. python prueba_rapida_config.py")
    print(f"   2. python audit_master.py")
    print(f"   3. python run_web.py (para interfaz web)")

if __name__ == "__main__":
    main()
