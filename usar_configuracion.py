#!/usr/bin/env python3
"""
Ejemplo de uso de configuración JSON para SmartCam Auditor
"""

import json
import sys
import os

def cargar_configuracion():
    """Carga la configuración desde el archivo JSON"""
    try:
        # Leer config
        with open("config/config.json") as f:
            config = json.load(f)
        
        # Extraer puertos objetivo
        PUERTOS_OBJETIVO = config.get("camera_ports", [80, 554])
        
        print("✅ Configuración cargada exitosamente:")
        print(f"   📡 Red objetivo: {config.get('network_range', 'No definida')}")
        print(f"   🔌 Puertos objetivo: {PUERTOS_OBJETIVO}")
        print(f"   ⚙️  Timeout: {config.get('scan_settings', {}).get('timeout', 'Por defecto')}")
        print(f"   🧵 Max hilos: {config.get('scan_settings', {}).get('max_threads', 'Por defecto')}")
        
        return config, PUERTOS_OBJETIVO
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo config/config.json")
        print("💡 Asegúrate de que el archivo existe en la carpeta config/")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

def escanear_con_configuracion():
    """Realiza un escaneo usando la configuración JSON"""
    # Cargar configuración
    config, PUERTOS_OBJETIVO = cargar_configuracion()
    
    # Importar módulos después de verificar la configuración
    try:
        from scanner.network_scanner import obtener_ips_dispositivos
        from scanner.login_tester import testear_credenciales
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        sys.exit(1)
    
    print("\n🔍 Iniciando escaneo con configuración personalizada...")
    print("=" * 60)
    
    # Obtener rango de red de la configuración
    network_range = config.get('network_range', '192.168.1.0/24')
    
    # Detectar IPs usando la configuración
    print(f"🔎 Escaneando red: {network_range}")
    ips_detectadas = obtener_ips_dispositivos(network_range)
    
    if not ips_detectadas:
        print("⚠️  No se encontraron dispositivos activos.")
        return
    
    print(f"\n✅ Dispositivos encontrados: {len(ips_detectadas)}")
    print(f"📍 IPs: {ips_detectadas}")
    
    # Mostrar qué puertos se van a probar
    print(f"\n🔌 Puertos configurados para probar: {PUERTOS_OBJETIVO}")
    
    # Probar credenciales
    print("\n🔐 Probando credenciales...")
    resultados = testear_credenciales(ips_detectadas)
    
    # Mostrar resultados
    print("\n📊 RESULTADOS:")
    print("-" * 40)
    if resultados:
        print("🚨 CREDENCIALES DÉBILES ENCONTRADAS:")
        for resultado in resultados:
            print(f"  ⚠️  {resultado}")
    else:
        print("✅ No se encontraron credenciales débiles.")
    
    # Guardar resultados si está configurado
    if config.get('logging', {}).get('save_to_file', False):
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"logs/escaneo_config_{timestamp}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Escaneo SmartCam Auditor - {timestamp}\n")
            f.write(f"Red escaneada: {network_range}\n")
            f.write(f"Puertos objetivo: {PUERTOS_OBJETIVO}\n")
            f.write(f"IPs encontradas: {ips_detectadas}\n")
            f.write(f"Vulnerabilidades: {resultados}\n")
        
        print(f"\n📄 Log guardado en: {log_file}")

def mostrar_configuracion_actual():
    """Muestra la configuración actual del sistema"""
    try:
        with open("config/config.json") as f:
            config = json.load(f)
        
        print("🔧 CONFIGURACIÓN ACTUAL:")
        print("=" * 50)
        print(f"📡 Rango de red: {config.get('network_range', 'No definido')}")
        print(f"🔌 Puertos de cámaras: {config.get('camera_ports', [])}")
        
        scan_settings = config.get('scan_settings', {})
        print(f"⏱️  Timeout: {scan_settings.get('timeout', 'Por defecto')} segundos")
        print(f"🧵 Hilos máximos: {scan_settings.get('max_threads', 'Por defecto')}")
        
        # Telegram settings
        telegram_enabled = config.get('telegram_bot_token', 'TU_TOKEN') != 'TU_TOKEN'
        print(f"📱 Telegram: {'✅ Configurado' if telegram_enabled else '❌ No configurado'}")
        
        print("\n💡 Para cambiar la configuración, edita el archivo config/config.json")
        
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")

def main():
    """Función principal"""
    print("🔒 SmartCam Auditor v2.0 Pro - Configuración JSON")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--config':
        mostrar_configuracion_actual()
        return
    
    # Verificar que existe el directorio de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("📁 Creado directorio de logs")
    
    try:
        escanear_con_configuracion()
    except KeyboardInterrupt:
        print("\n\n⏹️  Escaneo interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error durante el escaneo: {e}")

if __name__ == "__main__":
    main()
