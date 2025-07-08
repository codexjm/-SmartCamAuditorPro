#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEMOSTRACIÓN FINAL: SmartCam Auditor + Nmap + IA

Este script demuestra la integración completa de:
1. SmartCam Auditor (escaneo de dispositivos IoT)
2. Nmap (escaneo de red profesional) 
3. Análisis de IA con YOLO (análisis de streams RTSP)
"""

import os
import sys
import time

# Agregar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_instalaciones():
    """Verifica que todas las herramientas estén instaladas"""
    print("🔍 VERIFICACIÓN DE INSTALACIONES")
    print("=" * 50)
    
    resultados = {}
    
    # 1. Verificar Nmap
    try:
        from scanner.nmap_integration import NmapScanner
        nmap = NmapScanner()
        if nmap.is_available():
            print("✅ Nmap: Instalado y funcional")
            version = nmap.get_version()
            if version:
                print(f"   📋 {version.split('(')[0].strip()}")
            resultados['nmap'] = True
        else:
            print("❌ Nmap: No disponible")
            resultados['nmap'] = False
    except Exception as e:
        print(f"❌ Nmap: Error - {e}")
        resultados['nmap'] = False
    
    # 2. Verificar SmartCam Auditor
    try:
        from scanner.network_scanner import NetworkScanner
        scanner = NetworkScanner()
        print("✅ SmartCam Auditor: Disponible")
        resultados['smartcam'] = True
    except Exception as e:
        print(f"❌ SmartCam Auditor: Error - {e}")
        resultados['smartcam'] = False
    
    # 3. Verificar módulo de IA
    try:
        from scanner.image_ai_analyzer import verificar_disponibilidad_ia
        estado_ia = verificar_disponibilidad_ia()
        if estado_ia['ai_disponible']:
            print("✅ Análisis de IA: Disponible")
            print(f"   📷 OpenCV: {estado_ia['version_opencv']}")
            print(f"   🧠 YOLO: {len(estado_ia['modelos_yolo_disponibles'])} modelos")
            resultados['ia'] = True
        else:
            print("❌ Análisis de IA: No disponible")
            resultados['ia'] = False
    except Exception as e:
        print(f"❌ Análisis de IA: Error - {e}")
        resultados['ia'] = False
    
    # 4. Verificar Python y dependencias básicas
    try:
        import socket, threading, subprocess, json
        print("✅ Dependencias Python: Disponibles")
        resultados['python'] = True
    except Exception as e:
        print(f"❌ Dependencias Python: Error - {e}")
        resultados['python'] = False
    
    return resultados

def demo_nmap_basico():
    """Demostración básica de nmap"""
    print("\n🔍 DEMO: Nmap Básico")
    print("-" * 30)
    
    try:
        from scanner.nmap_integration import NmapScanner
        nmap = NmapScanner()
        
        if not nmap.is_available():
            print("❌ Nmap no disponible")
            return
        
        print("📡 Escaneando localhost...")
        resultado = nmap.scan_network('127.0.0.1/32', '-sn')
        
        if resultado['success']:
            print(f"✅ Hosts encontrados: {len(resultado['hosts'])}")
            for host in resultado['hosts']:
                print(f"   📍 {host}")
        else:
            print(f"❌ Error: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Error en demo de nmap: {e}")

def demo_smartcam_basico():
    """Demostración básica de SmartCam"""
    print("\n🤖 DEMO: SmartCam Auditor Básico")
    print("-" * 35)
    
    try:
        from scanner.network_scanner import NetworkScanner
        
        # Configuración rápida para demo
        scanner = NetworkScanner(timeout=0.5, max_threads=20)
        
        print("📡 Escaneando red local (demo rápido)...")
        
        # Escanear solo algunas IPs para demo rápido
        import ipaddress
        local_network = scanner.get_local_network()
        print(f"🌐 Red detectada: {local_network}")
        
        # Para demo, escanear solo unas pocas IPs
        network = ipaddress.IPv4Network(local_network, strict=False)
        demo_hosts = list(network.hosts())[:10]  # Solo primeras 10 IPs
        
        devices_found = []
        for ip in demo_hosts:
            device = scanner.scan_device(ip)
            if device:
                devices_found.append(device)
        
        print(f"✅ Escaneo completado")
        print(f"🎯 Dispositivos encontrados: {len(devices_found)}")
        
        for device in devices_found:
            print(f"   📍 {device['ip']} - {device['device_type']}")
            
    except Exception as e:
        print(f"❌ Error en demo de SmartCam: {e}")

def demo_ia_analyzer():
    """Demostración del analizador de IA"""
    print("\n🧠 DEMO: Analizador de IA")
    print("-" * 25)
    
    try:
        from scanner.image_ai_analyzer import analizar_rtsp, verificar_disponibilidad_ia
        
        estado = verificar_disponibilidad_ia()
        
        if not estado['ai_disponible']:
            print("❌ Sistema de IA no disponible")
            return
        
        print("✅ Sistema de IA listo")
        print(f"📷 OpenCV: {estado['version_opencv']}")
        print(f"🎯 Modelos YOLO: {len(estado['modelos_yolo_disponibles'])}")
        
        # Demo con URL ficticia (esperamos que falle pero maneje el error)
        print("\n📡 Probando análisis RTSP (URL de prueba)...")
        
        config = {
            'timeout': 2,
            'max_attempts': 1,
            'enable_logging': False
        }
        
        resultado = analizar_rtsp("rtsp://test:test@127.0.0.1:554/test", config=config)
        
        if resultado:
            print("✅ La función maneja URLs correctamente")
        else:
            print("✅ Error manejado correctamente (esperado con URL de prueba)")
            
    except Exception as e:
        print(f"❌ Error en demo de IA: {e}")

def mostrar_comandos_utiles():
    """Muestra comandos útiles para el usuario"""
    print("\n💡 COMANDOS ÚTILES")
    print("=" * 50)
    
    print("\n🔍 NMAP:")
    print("   nmap -sn 192.168.1.0/24        # Escaneo de ping")
    print("   nmap -p 80,443,554 192.168.1.1 # Escaneo de puertos específicos")
    print("   nmap -A 192.168.1.1            # Escaneo agresivo")
    
    print("\n🤖 SMARTCAM AUDITOR:")
    print("   python smartcam_auditor.py     # Escáner principal")
    print("   python escaneo_hibrido_nmap.py # Escaneo híbrido")
    
    print("\n🧠 ANÁLISIS DE IA:")
    print("   from scanner.image_ai_analyzer import analizar_rtsp")
    print("   imagen = analizar_rtsp('rtsp://admin:admin@192.168.1.100:554')")
    
    print("\n📁 ARCHIVOS IMPORTANTES:")
    print("   scanner/network_scanner.py     # Escáner principal")
    print("   scanner/nmap_integration.py   # Integración Nmap")
    print("   scanner/image_ai_analyzer.py  # Análisis de IA")
    print("   escaneo_hibrido_nmap.py       # Escaneo combinado")

def main():
    """Función principal de demostración"""
    print("🚀 SMARTCAM AUDITOR - DEMOSTRACIÓN COMPLETA")
    print("Nmap + SmartCam + Análisis de IA")
    print("=" * 60)
    
    # Verificar instalaciones
    resultados = verificar_instalaciones()
    
    # Ejecutar demos según disponibilidad
    if resultados.get('nmap'):
        demo_nmap_basico()
    
    if resultados.get('smartcam'):
        demo_smartcam_basico()
    
    if resultados.get('ia'):
        demo_ia_analyzer()
    
    # Mostrar comandos útiles
    mostrar_comandos_utiles()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("🎉 DEMOSTRACIÓN COMPLETADA")
    print("=" * 60)
    
    disponibles = sum(resultados.values())
    total = len(resultados)
    
    print(f"📊 Componentes disponibles: {disponibles}/{total}")
    
    if disponibles == total:
        print("✅ ¡Sistema completamente funcional!")
        print("🚀 Listo para auditorías de seguridad")
    else:
        print("⚠️ Algunos componentes necesitan instalación")
        
        if not resultados.get('nmap'):
            print("   • Instalar Nmap: winget install Insecure.Nmap")
        if not resultados.get('ia'):
            print("   • Instalar IA: pip install opencv-python ultralytics")
    
    print("\n🎯 Para escaneo completo, ejecutar:")
    print("   python escaneo_hibrido_nmap.py")

if __name__ == "__main__":
    main()
