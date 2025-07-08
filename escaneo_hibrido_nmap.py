#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartCam Auditor con integración de Nmap

Este script combina el escaneo avanzado de SmartCam Auditor con las capacidades de Nmap
para obtener un escaneo más completo y preciso de dispositivos IoT y cámaras IP.
"""

import os
import sys
import time

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner.network_scanner import NetworkScanner
from scanner.nmap_integration import NmapScanner

def registrar_log(mensaje, nivel="INFO"):
    """Función de logging simple"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{nivel}] {mensaje}")

def escaneo_hibrido_red(network_range="192.168.1.0/24"):
    """
    Realiza un escaneo híbrido usando tanto SmartCam Auditor como Nmap
    
    Args:
        network_range (str): Rango de red a escanear
    
    Returns:
        dict: Resultados combinados del escaneo
    """
    registrar_log("🚀 Iniciando escaneo híbrido SmartCam + Nmap")
    registrar_log(f"🎯 Red objetivo: {network_range}")
    
    resultados = {
        'network_range': network_range,
        'nmap_results': None,
        'smartcam_results': None,
        'combined_hosts': [],
        'statistics': {}
    }
    
    # Inicializar escáneres
    nmap_scanner = NmapScanner()
    smartcam_scanner = NetworkScanner()
    
    # Fase 1: Descubrimiento rápido con Nmap
    registrar_log("📡 Fase 1: Descubrimiento de hosts con Nmap...")
    
    if nmap_scanner.is_available():
        start_time = time.time()
        nmap_result = nmap_scanner.scan_network(network_range, '-sn')
        nmap_time = time.time() - start_time
        
        if nmap_result['success']:
            nmap_hosts = nmap_result['hosts']
            registrar_log(f"✅ Nmap encontró {len(nmap_hosts)} hosts en {nmap_time:.2f}s")
            resultados['nmap_results'] = nmap_result
        else:
            registrar_log(f"❌ Error en Nmap: {nmap_result['error']}")
            nmap_hosts = []
    else:
        registrar_log("⚠️ Nmap no disponible, saltando fase 1")
        nmap_hosts = []
    
    # Fase 2: Escaneo detallado con SmartCam Auditor
    registrar_log("🔍 Fase 2: Análisis detallado con SmartCam Auditor...")
    
    start_time = time.time()
    smartcam_devices = smartcam_scanner.scan_network(network_range)
    smartcam_time = time.time() - start_time
    
    registrar_log(f"✅ SmartCam analizó la red en {smartcam_time:.2f}s")
    registrar_log(f"🎯 SmartCam identificó {len(smartcam_devices)} dispositivos IoT/cámaras")
    
    resultados['smartcam_results'] = smartcam_devices
    
    # Fase 3: Escaneo de puertos detallado con Nmap para dispositivos identificados
    if nmap_scanner.is_available() and smartcam_devices:
        registrar_log("🔧 Fase 3: Escaneo de puertos detallado con Nmap...")
        
        camera_ports = "22,23,80,443,554,8000,8080,8081,8554,9999,10001"
        
        for device in smartcam_devices:
            ip = device['ip']
            registrar_log(f"   🔍 Escaneando puertos de {ip}...")
            
            port_result = nmap_scanner.scan_ports(ip, camera_ports)
            
            if port_result['success']:
                device['nmap_ports'] = port_result['open_ports']
                nmap_port_numbers = [p['port'] for p in port_result['open_ports']]
                
                # Comparar con los puertos encontrados por SmartCam
                smartcam_ports = device.get('open_ports', [])
                
                # Agregar puertos adicionales encontrados por Nmap
                additional_ports = set(nmap_port_numbers) - set(smartcam_ports)
                if additional_ports:
                    device['additional_ports_nmap'] = list(additional_ports)
                    registrar_log(f"   🎯 Nmap encontró puertos adicionales: {list(additional_ports)}")
                
                # Combinar información de servicios
                device['nmap_services'] = {}
                for port_info in port_result['open_ports']:
                    device['nmap_services'][port_info['port']] = port_info['service']
            else:
                registrar_log(f"   ❌ Error escaneando puertos de {ip}")
    
    # Fase 4: Combinar y analizar resultados
    registrar_log("📊 Fase 4: Análisis y combinación de resultados...")
    
    # Crear lista combinada de hosts únicos
    all_hosts = set()
    
    # Agregar hosts de Nmap
    if nmap_hosts:
        all_hosts.update(nmap_hosts)
    
    # Agregar hosts de SmartCam
    smartcam_ips = [device['ip'] for device in smartcam_devices]
    all_hosts.update(smartcam_ips)
    
    # Crear información detallada para cada host
    combined_hosts = []
    
    for ip in sorted(all_hosts):
        host_info = {
            'ip': ip,
            'detected_by': [],
            'device_type': 'Unknown',
            'confidence': 0,
            'open_ports': [],
            'services': [],
            'risk_assessment': 'LOW'
        }
        
        # Información de Nmap
        if ip in nmap_hosts:
            host_info['detected_by'].append('nmap')
        
        # Información de SmartCam
        smartcam_device = next((d for d in smartcam_devices if d['ip'] == ip), None)
        if smartcam_device:
            host_info['detected_by'].append('smartcam')
            host_info['device_type'] = smartcam_device['device_type']
            host_info['confidence'] = smartcam_device['confidence']
            host_info['open_ports'] = smartcam_device['open_ports']
            host_info['services'] = smartcam_device['services']
            
            # Información adicional de Nmap si existe
            if 'nmap_ports' in smartcam_device:
                host_info['nmap_detailed_ports'] = smartcam_device['nmap_ports']
                host_info['nmap_services'] = smartcam_device.get('nmap_services', {})
            
            # Evaluar riesgo
            if smartcam_device.get('critical_cves', 0) > 0:
                host_info['risk_assessment'] = 'CRITICAL'
            elif smartcam_device.get('cve_count', 0) > 0:
                host_info['risk_assessment'] = 'HIGH'
            elif 'Camera' in smartcam_device['device_type']:
                host_info['risk_assessment'] = 'MEDIUM'
        
        combined_hosts.append(host_info)
    
    resultados['combined_hosts'] = combined_hosts
    
    # Estadísticas finales
    stats = {
        'total_hosts_found': len(combined_hosts),
        'nmap_only': len([h for h in combined_hosts if h['detected_by'] == ['nmap']]),
        'smartcam_only': len([h for h in combined_hosts if h['detected_by'] == ['smartcam']]),
        'both_scanners': len([h for h in combined_hosts if len(h['detected_by']) == 2]),
        'cameras_detected': len([h for h in combined_hosts if 'Camera' in h['device_type']]),
        'iot_devices': len([h for h in combined_hosts if 'IoT' in h['device_type']]),
        'high_risk_devices': len([h for h in combined_hosts if h['risk_assessment'] in ['HIGH', 'CRITICAL']])
    }
    
    resultados['statistics'] = stats
    
    return resultados

def mostrar_resumen_escaneo(resultados):
    """Muestra un resumen detallado de los resultados del escaneo"""
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL ESCANEO HÍBRIDO")
    print("=" * 70)
    
    stats = resultados['statistics']
    
    print(f"🎯 Red escaneada: {resultados['network_range']}")
    print(f"📡 Total de hosts encontrados: {stats['total_hosts_found']}")
    print(f"🔍 Solo Nmap: {stats['nmap_only']}")
    print(f"🤖 Solo SmartCam: {stats['smartcam_only']}")
    print(f"🔗 Ambos escáneres: {stats['both_scanners']}")
    print()
    
    print(f"📹 Cámaras IP detectadas: {stats['cameras_detected']}")
    print(f"🏠 Dispositivos IoT: {stats['iot_devices']}")
    print(f"⚠️ Dispositivos de alto riesgo: {stats['high_risk_devices']}")
    
    if resultados['combined_hosts']:
        print("\n" + "=" * 70)
        print("🎯 DISPOSITIVOS ENCONTRADOS")
        print("=" * 70)
        
        for host in resultados['combined_hosts']:
            print(f"\n📍 {host['ip']}")
            print(f"   🔍 Detectado por: {', '.join(host['detected_by'])}")
            print(f"   🏷️ Tipo: {host['device_type']} (Confianza: {host['confidence']}%)")
            
            if host['open_ports']:
                print(f"   🔓 Puertos abiertos: {host['open_ports']}")
            
            if host['services']:
                print(f"   🛠️ Servicios: {', '.join(host['services'])}")
            
            if 'nmap_detailed_ports' in host and host['nmap_detailed_ports']:
                print(f"   🔧 Detalles Nmap:")
                for port_info in host['nmap_detailed_ports']:
                    print(f"      - {port_info['port']}/tcp {port_info['service']}")
            
            # Indicador de riesgo
            risk_emoji = {
                'LOW': '🟢',
                'MEDIUM': '🟡', 
                'HIGH': '🟠',
                'CRITICAL': '🔴'
            }
            print(f"   {risk_emoji.get(host['risk_assessment'], '⚪')} Riesgo: {host['risk_assessment']}")

def main():
    """Función principal"""
    print("🔍 SMARTCAM AUDITOR - ESCANEO HÍBRIDO CON NMAP")
    print("Combinando SmartCam Auditor + Nmap para escaneo completo")
    print()
    
    # Verificar disponibilidad de nmap
    nmap_scanner = NmapScanner()
    
    if nmap_scanner.is_available():
        print("✅ Nmap disponible y listo")
        version = nmap_scanner.get_version()
        if version:
            print(f"📋 {version.split('(')[0].strip()}")
    else:
        print("⚠️ Nmap no disponible - continuando solo con SmartCam")
    
    print()
    
    # Configurar red a escanear
    network_range = input("🌐 Ingresa el rango de red a escanear (o Enter para 192.168.1.0/24): ").strip()
    if not network_range:
        network_range = "192.168.1.0/24"
    
    print(f"\n🚀 Iniciando escaneo híbrido de {network_range}...")
    
    # Realizar escaneo
    start_time = time.time()
    resultados = escaneo_hibrido_red(network_range)
    total_time = time.time() - start_time
    
    # Mostrar resultados
    mostrar_resumen_escaneo(resultados)
    
    print(f"\n⏱️ Tiempo total de escaneo: {total_time:.2f} segundos")
    print("\n🎉 Escaneo híbrido completado")

if __name__ == "__main__":
    main()
