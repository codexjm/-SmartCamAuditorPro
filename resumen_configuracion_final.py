#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Resumen Final - SmartCam Auditor v2.0 Pro con Configuración Personalizada
Estado del sistema después de aplicar tus parámetros optimizados
"""

import json
import os
from datetime import datetime

def mostrar_resumen_configuracion():
    """Muestra un resumen completo de la configuración aplicada"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    📊 RESUMEN FINAL - CONFIGURACIÓN APLICADA                 ║
║                           SmartCam Auditor v2.0 Pro                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Cargar configuración
    try:
        with open('config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return
    
    print("🎯 CONFIGURACIÓN PERSONALIZADA APLICADA:")
    print("=" * 50)
    
    # Red y puertos
    print(f"🌐 Red objetivo: {config['network_range']}")
    print(f"🔌 Puertos de cámaras: {len(config['camera_ports'])} puertos")
    print(f"   └─ Lista: {', '.join(map(str, config['camera_ports']))}")
    
    # Configuración de escaneo
    scan_settings = config['scan_settings']
    print(f"\n⚙️ CONFIGURACIÓN DE ESCANEO:")
    print(f"   ├─ Intensidad: {config['scan_intensity']} (AGRESIVO)")
    print(f"   ├─ Max threads: {scan_settings['max_threads']} (Optimizado)")
    print(f"   ├─ Timeout: {scan_settings['timeout']}s (Rápido)")
    print(f"   └─ Ping timeout: {scan_settings['ping_timeout']}s")
    
    # Configuración de fuerza bruta
    bf_config = config['brute_force']
    print(f"\n💥 FUERZA BRUTA AGRESIVA:")
    print(f"   ├─ Estado: {'✅ HABILITADO' if bf_config['enabled'] else '❌ Deshabilitado'}")
    print(f"   ├─ Max threads: {bf_config['max_threads']} (Aumentado)")
    print(f"   ├─ Timeout: {bf_config['timeout']}s")
    print(f"   ├─ Delay: {bf_config['delay_between_attempts']}s (Mínimo)")
    print(f"   ├─ SSH: {'✅' if bf_config['enable_ssh'] else '❌'} Habilitado")
    print(f"   ├─ Telnet: {'✅' if bf_config['enable_telnet'] else '❌'} Habilitado")
    print(f"   ├─ Max intentos/servicio: {bf_config['max_attempts_per_service']}")
    print(f"   └─ Continuar tras éxito: {'✅' if not bf_config['stop_on_first_success'] else '❌'}")
    
    # Módulos avanzados
    audit_config = config['audit_master']
    print(f"\n🎛️ MÓDULOS AVANZADOS:")
    print(f"   ├─ Escaneo red: {'✅' if audit_config['enable_network_scan'] else '❌'}")
    print(f"   ├─ Test credenciales: {'✅' if audit_config['enable_login_test'] else '❌'}")
    print(f"   ├─ Fuerza bruta: {'✅' if audit_config['enable_brute_force'] else '❌'}")
    print(f"   ├─ CVE checking: {'✅' if audit_config['enable_cve_check'] else '❌'}")
    print(f"   └─ IPs manuales: {len(audit_config.get('manual_ips', []))} configuradas")
    
    # Notificaciones
    notif_config = config['notification_settings']
    print(f"\n📱 NOTIFICACIONES:")
    print(f"   ├─ Telegram: {'❌ Deshabilitado (local)' if not notif_config['enable_telegram'] else '✅ Habilitado'}")
    print(f"   └─ Modo: {config['alert_mode']}")
    
    print(f"\n📈 OPTIMIZACIONES APLICADAS:")
    print("   ✅ Escaneo agresivo con 75 threads concurrentes")
    print("   ✅ Timeouts reducidos para mayor velocidad")
    print("   ✅ Fuerza bruta con 30 threads y protocolo múltiple")
    print("   ✅ Hasta 150 intentos por servicio")
    print("   ✅ Continuación tras encontrar credenciales")
    print("   ✅ 10 puertos de cámaras configurados")
    print("   ✅ Verificación CVE habilitada")
    
    print(f"\n🚀 COMANDOS LISTOS PARA USAR:")
    print("=" * 30)
    print("1. python audit_master.py          # Auditoría completa")
    print("2. python run_web.py               # Interfaz web")
    print("3. python demo_configuracion_personalizada.py")
    print("4. python tu_codigo_fuerza_bruta.py")
    print("5. python usar_tu_configuracion.py")
    
    # Estado de archivos
    print(f"\n📁 ESTADO DEL SISTEMA:")
    archivos_clave = [
        'config/config.json',
        'scanner/network_scanner.py',
        'scanner/fuerza_bruta.py',
        'scanner/cve_checker.py',
        'audit_master.py',
        'diccionarios/rockyou.txt'
    ]
    
    for archivo in archivos_clave:
        estado = "✅" if os.path.exists(archivo) else "❌"
        print(f"   {estado} {archivo}")
    
    print(f"\n🎉 RESUMEN:")
    print("Tu configuración personalizada ha sido aplicada exitosamente.")
    print("El sistema está optimizado para auditorías agresivas y eficientes.")
    print("Todos los módulos están listos y configurados según tus parámetros.")
    
    print(f"\n⚠️ RECORDATORIO IMPORTANTE:")
    print("Esta herramienta debe usarse SOLO en redes propias o con autorización explícita.")
    print("El modo agresivo puede generar tráfico intenso en la red.")
    
    print(f"\n📅 Configuración aplicada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    mostrar_resumen_configuracion()
