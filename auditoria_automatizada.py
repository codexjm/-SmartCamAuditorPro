#!/usr/bin/env python3
"""
SmartCam Auditor v2.0 Pro - Script de Ejemplo con Configuración
Autor: Cybersecurity Team
Fecha: 2025-07-08

Este script demuestra cómo usar el sistema con configuración personalizada.
"""

import sys
import os
import time
from datetime import datetime

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar funciones principales
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.login_tester import testear_credenciales

def configurar_sistema():
    """Configura el sistema y muestra la configuración actual"""
    print("=" * 60)
    print("🔧 SMARTCAM AUDITOR v2.0 PRO - CONFIGURACIÓN AUTOMATIZADA")
    print("=" * 60)
    
    # Leer configuración
    try:
        import json
        with open("config/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Configuración cargada exitosamente:")
        print(f"   📡 Red objetivo: {config.get('network_range', 'No especificada')}")
        print(f"   🔌 Puertos de cámaras: {config.get('camera_ports', [])}")
        print(f"   🧵 Hilos máximos: {config.get('scan_settings', {}).get('max_threads', 'Por defecto')}")
        print(f"   ⏱️ Timeout: {config.get('scan_settings', {}).get('timeout', 'Por defecto')}s")
        
        # Verificar configuración de Telegram
        telegram_configured = (
            config.get('telegram_bot_token') != "TU_TOKEN" and 
            config.get('telegram_chat_id') != "TU_CHAT_ID" and
            config.get('notification_settings', {}).get('enable_telegram', False)
        )
        
        if telegram_configured:
            print("   📱 Notificaciones Telegram: ✅ CONFIGURADAS")
        else:
            print("   📱 Notificaciones Telegram: ⚠️ NO CONFIGURADAS")
            print("      Para habilitar Telegram, edita config/config.json:")
            print("      - telegram_bot_token: Token de tu bot")
            print("      - telegram_chat_id: ID de tu chat")
        
        return config
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return {}

def ejecutar_auditoria_completa():
    """Ejecuta una auditoría completa con la configuración actual"""
    
    # Configurar sistema
    config = configurar_sistema()
    
    # Crear archivo de log único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/auditoria_automatizada_{timestamp}.log"
    
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    print(f"\n📝 Log de auditoría: {log_path}")
    print("\n" + "=" * 60)
    print("🔍 INICIANDO AUDITORÍA AUTOMATIZADA")
    print("=" * 60)
    
    # Escribir encabezado del log
    with open(log_path, "w", encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("SmartCam Auditor v2.0 Pro - Auditoría Automatizada\n")
        f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
    
    try:
        # FASE 1: Detección de dispositivos
        print("🔎 FASE 1: Detectando dispositivos en la red...")
        
        # Usar configuración para obtener rango de red
        rango_red = config.get('network_range', '192.168.1.0/24')
        
        with open(log_path, "a", encoding='utf-8') as f:
            f.write(f"[🔎 FASE 1: Detección de dispositivos]\n")
            f.write(f"Red objetivo: {rango_red}\n")
            f.write(f"Iniciado: {datetime.now().strftime('%H:%M:%S')}\n\n")
        
        # Detectar IPs usando la función del usuario
        ips_detectadas = obtener_ips_dispositivos()  # Usará la configuración automáticamente
        
        with open(log_path, "a", encoding='utf-8') as f:
            f.write(f"Dispositivos encontrados: {len(ips_detectadas)}\n")
            for ip in ips_detectadas:
                f.write(f" -> {ip}\n")
            f.write(f"Completado: {datetime.now().strftime('%H:%M:%S')}\n\n")
        
        if not ips_detectadas:
            print("⚠️ No se encontraron dispositivos activos.")
            with open(log_path, "a", encoding='utf-8') as f:
                f.write("❌ RESULTADO: No se encontraron dispositivos.\n")
            return
        
        print(f"✅ Encontrados {len(ips_detectadas)} dispositivos")
        
        # FASE 2: Pruebas de credenciales
        print("\n🔐 FASE 2: Probando credenciales débiles...")
        
        with open(log_path, "a", encoding='utf-8') as f:
            f.write(f"[🔐 FASE 2: Pruebas de credenciales]\n")
            f.write(f"IPs a probar: {len(ips_detectadas)}\n")
            f.write(f"Iniciado: {datetime.now().strftime('%H:%M:%S')}\n\n")
        
        # Probar credenciales usando la función del usuario
        resultados_credenciales = testear_credenciales(ips_detectadas)
        
        # Escribir resultados en el log
        with open(log_path, "a", encoding='utf-8') as f:
            f.write("\n[🔐 Resultado de pruebas de credenciales débiles:]\n")
            if resultados_credenciales:
                vulnerabilidades = 0
                for r in resultados_credenciales:
                    f.write(" -> " + r + "\n")
                    if "ÉXITO" in r or "vulnerable" in r.lower():
                        vulnerabilidades += 1
                f.write(f"\n⚠️ VULNERABILIDADES ENCONTRADAS: {vulnerabilidades}\n")
            else:
                f.write(" -> No se encontraron credenciales débiles.\n")
                f.write("✅ ESTADO: SEGURO\n")
            f.write(f"Completado: {datetime.now().strftime('%H:%M:%S')}\n\n")
        
        # FASE 3: Resumen final
        print("\n📊 FASE 3: Generando resumen final...")
        
        with open(log_path, "a", encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("📊 RESUMEN FINAL DE AUDITORÍA\n")
            f.write("=" * 60 + "\n")
            f.write(f"Dispositivos escaneados: {len(ips_detectadas)}\n")
            f.write(f"Credenciales probadas: {len(resultados_credenciales) if resultados_credenciales else 0}\n")
            f.write(f"Estado de seguridad: {'⚠️ REQUIERE ATENCIÓN' if resultados_credenciales else '✅ SEGURO'}\n")
            f.write(f"Auditoría completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("=" * 60)
        print("✅ AUDITORÍA COMPLETADA")
        print("=" * 60)
        print(f"📄 Reporte guardado en: {log_path}")
        
        if resultados_credenciales:
            print("⚠️ SE ENCONTRARON VULNERABILIDADES - Revisar el reporte")
        else:
            print("✅ ESTADO SEGURO - No se encontraron vulnerabilidades")
        
    except Exception as e:
        error_msg = f"❌ Error durante la auditoría: {e}"
        print(error_msg)
        with open(log_path, "a", encoding='utf-8') as f:
            f.write(f"\n{error_msg}\n")

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 60)
    print("🛡️ SMARTCAM AUDITOR v2.0 PRO - MENÚ PRINCIPAL")
    print("=" * 60)
    print("1. 🔧 Ver configuración actual")
    print("2. 🔍 Ejecutar auditoría completa")
    print("3. 📡 Probar solo detección de dispositivos")
    print("4. 🔐 Probar solo credenciales (requiere IPs)")
    print("5. 📱 Probar notificación Telegram")
    print("6. ❌ Salir")
    print("=" * 60)

def main():
    """Función principal"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (1-6): ").strip()
            
            if opcion == "1":
                configurar_sistema()
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "2":
                ejecutar_auditoria_completa()
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "3":
                print("\n🔍 Ejecutando detección de dispositivos...")
                ips = obtener_ips_dispositivos()
                print(f"✅ Detectados: {ips}")
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "4":
                ips_input = input("\nIngresa las IPs separadas por comas: ").strip()
                if ips_input:
                    ips = [ip.strip() for ip in ips_input.split(',')]
                    print(f"\n🔐 Probando credenciales en: {ips}")
                    resultados = testear_credenciales(ips)
                    print(f"✅ Resultados: {resultados}")
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "5":
                try:
                    from scanner.telegram_notifier import send_telegram_notification
                    resultado = send_telegram_notification("🧪 Prueba de notificación desde SmartCam Auditor v2.0 Pro")
                    if resultado:
                        print("✅ Notificación enviada correctamente")
                    else:
                        print("❌ Error enviando notificación o Telegram no configurado")
                except ImportError:
                    print("❌ Módulo de Telegram no disponible")
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "6":
                print("\n👋 ¡Gracias por usar SmartCam Auditor v2.0 Pro!")
                break
                
            else:
                print("❌ Opción inválida. Por favor selecciona 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
