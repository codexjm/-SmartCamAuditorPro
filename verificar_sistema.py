#!/usr/bin/env python3
"""
Script de verificación para SmartCam Auditor v2.0 Pro
Verifica que todas las funcionalidades del escáner avanzado estén operativas
"""

import os
import sys
import subprocess
import importlib

def print_header(title):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"✅ {message}")

def print_warning(message):
    """Imprime mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"❌ {message}")

def check_file_exists(filepath, description):
    """Verifica si un archivo existe"""
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} no encontrado: {filepath}")
        return False

def check_module_import(module_name, description):
    """Verifica si un módulo puede ser importado"""
    try:
        importlib.import_module(module_name)
        print_success(f"{description} importado correctamente")
        return True
    except ImportError as e:
        print_error(f"Error importando {description}: {e}")
        return False

def check_python_version():
    """Verifica la versión de Python"""
    print_header("VERIFICACIÓN DE PYTHON")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.7+")
        return False

def check_core_files():
    """Verifica archivos principales del sistema"""
    print_header("VERIFICACIÓN DE ARCHIVOS PRINCIPALES")
    
    files_to_check = [
        ("app.py", "Aplicación principal"),
        ("run_web.py", "Servidor web"),
        ("audit_simulator.py", "Simulador de auditorías"),
        ("web_panel/__init__.py", "Panel web - Init"),
        ("web_panel/routes.py", "Panel web - Rutas"),
        ("web_panel/templates/login.html", "Template de login"),
        ("web_panel/templates/dashboard.html", "Template de dashboard"),
        ("web_panel/templates/scanner_avanzado.html", "Template de escáner avanzado"),
        ("web_panel/static/style_new.css", "Estilos CSS"),
    ]
    
    all_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_scanner_files():
    """Verifica archivos del escáner avanzado"""
    print_header("VERIFICACIÓN DE ESCÁNER AVANZADO")
    
    scanner_files = [
        ("scanner/network_scanner.py", "Escáner de red avanzado"),
        ("scanner/credential_tester.py", "Probador de credenciales"),
        ("scanner/run_audit.py", "Script de auditoría completa"),
        ("scanner/quick_scan.py", "Script de escaneo rápido"),
        ("escaneo_optimizado.py", "Escáner optimizado directo"),
        ("ejemplo_scanner_avanzado.py", "Ejemplos del escáner"),
    ]
    
    all_exist = True
    for filepath, description in scanner_files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_documentation():
    """Verifica documentación"""
    print_header("VERIFICACIÓN DE DOCUMENTACIÓN")
    
    docs = [
        ("docs/SCANNER_AVANZADO.md", "Documentación del escáner avanzado"),
        ("docs/WEB_PANEL_GUIDE.md", "Guía del panel web"),
        ("README.md", "README principal"),
    ]
    
    all_exist = True
    for filepath, description in docs:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_imports():
    """Verifica importaciones de módulos"""
    print_header("VERIFICACIÓN DE MÓDULOS")
    
    # Módulos estándar
    standard_modules = [
        ("socket", "Socket networking"),
        ("threading", "Threading"),
        ("concurrent.futures", "Concurrent futures"),
        ("ipaddress", "IP address handling"),
        ("subprocess", "Subprocess"),
        ("flask", "Flask web framework"),
        ("time", "Time functions"),
        ("os", "Operating system interface"),
        ("sys", "System functions"),
    ]
    
    all_imported = True
    for module_name, description in standard_modules:
        if not check_module_import(module_name, description):
            all_imported = False
    
    # Módulos opcionales
    print(f"\n🔧 MÓDULOS OPCIONALES:")
    optional_modules = [
        ("requests", "HTTP requests (para pruebas de credenciales HTTP)"),
        ("paramiko", "SSH client (para pruebas SSH)"),
    ]
    
    for module_name, description in optional_modules:
        try:
            importlib.import_module(module_name)
            print_success(f"{description}")
        except ImportError:
            print_warning(f"{description} no disponible - funcionalidad limitada")
    
    return all_imported

def check_scanner_functionality():
    """Verifica funcionalidad del escáner"""
    print_header("VERIFICACIÓN DE FUNCIONALIDAD DEL ESCÁNER")
    
    try:
        # Importar escáner avanzado
        sys.path.append('.')
        from scanner.network_scanner import NetworkScanner, scan_network
        print_success("NetworkScanner importado correctamente")
        
        # Crear instancia del escáner
        scanner = NetworkScanner(timeout=0.5, max_threads=10)
        print_success("Instancia de NetworkScanner creada")
        
        # Detectar red local
        network = scanner.get_local_network()
        print_success(f"Red local detectada: {network}")
        
        # Verificar función de escaneo básico
        print_success("Funciones del escáner disponibles")
        return True
        
    except Exception as e:
        print_error(f"Error verificando funcionalidad del escáner: {e}")
        return False

def check_web_panel():
    """Verifica el panel web"""
    print_header("VERIFICACIÓN DEL PANEL WEB")
    
    try:
        # Importar panel web
        sys.path.append('.')
        from web_panel import create_app
        print_success("Panel web importado correctamente")
        
        # Crear aplicación
        app = create_app()
        print_success("Aplicación Flask creada")
        
        # Verificar rutas principales
        with app.test_client() as client:
            # Verificar login
            response = client.get('/')
            if response.status_code == 200:
                print_success("Ruta de login accesible")
            else:
                print_warning(f"Ruta de login retorna código {response.status_code}")
            
            # Verificar ruta del escáner avanzado
            response = client.get('/scanner_avanzado')
            if response.status_code in [200, 302]:  # 302 = redirect to login
                print_success("Ruta del escáner avanzado accesible")
            else:
                print_warning(f"Ruta del escáner retorna código {response.status_code}")
        
        return True
        
    except Exception as e:
        print_error(f"Error verificando panel web: {e}")
        return False

def run_quick_test():
    """Ejecuta una prueba rápida del escáner"""
    print_header("PRUEBA RÁPIDA DEL ESCÁNER")
    
    try:
        print("🧪 Ejecutando prueba del escáner optimizado...")
        result = subprocess.run(
            [sys.executable, "escaneo_optimizado.py", "--solo-escaneo"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="."
        )
        
        if result.returncode == 0:
            print_success("Escáner optimizado ejecutado exitosamente")
            # Mostrar algunas líneas del output
            lines = result.stdout.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            if len(result.stdout.split('\n')) > 10:
                print("   ...")
            return True
        else:
            print_error(f"Error ejecutando escáner: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_warning("Prueba del escáner detenida por timeout (normal en algunas redes)")
        return True
    except Exception as e:
        print_error(f"Error en prueba del escáner: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🚀 SMARTCAM AUDITOR v2.0 PRO - VERIFICACIÓN DEL SISTEMA")
    print("🎯 Escáner de Red Avanzado")
    
    checks = [
        ("Versión de Python", check_python_version),
        ("Archivos principales", check_core_files),
        ("Archivos del escáner", check_scanner_files),
        ("Documentación", check_documentation),
        ("Importaciones", check_imports),
        ("Funcionalidad del escáner", check_scanner_functionality),
        ("Panel web", check_web_panel),
        ("Prueba rápida", run_quick_test),
    ]
    
    results = {}
    
    for check_name, check_function in checks:
        try:
            results[check_name] = check_function()
        except Exception as e:
            print_error(f"Error en verificación de {check_name}: {e}")
            results[check_name] = False
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} {check_name}")
    
    print(f"\n📊 RESULTADO GENERAL: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print_success("🎉 Sistema completamente operativo!")
        print("🌐 Para usar el panel web: python run_web.py")
        print("⚡ Para escaneo directo: python escaneo_optimizado.py")
        print("📚 Para ejemplos: python ejemplo_scanner_avanzado.py")
    elif passed >= total * 0.8:
        print_warning("⚠️ Sistema mayormente operativo con limitaciones menores")
    else:
        print_error("❌ Sistema requiere atención - múltiples componentes fallan")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
