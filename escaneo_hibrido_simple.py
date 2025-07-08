#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartCam Auditor - Escaneo Híbrido Simplificado

Combinación de escaneo básico + Nmap sin dependencias problemáticas
"""

import os
import sys
import time
import socket
import threading
import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor

# Agregar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SimpleScanner:
    """Escáner simplificado sin dependencias externas"""
    
    def __init__(self, timeout=1.0, max_threads=50):
        self.timeout = timeout
        self.max_threads = max_threads
        self.found_devices = []
        self.lock = threading.Lock()
        
        # Puertos comunes de cámaras/IoT
        self.camera_ports = [80, 443, 554, 8080, 8554, 8000, 8081, 9999, 10001]
        
        # Servicios típicos
        self.port_services = {
            80: "HTTP",
            443: "HTTPS", 
            554: "RTSP",
            8080: "HTTP-Alt",
            8554: "RTSP-Alt",
            8000: "HTTP-Stream",
            8081: "HTTP-Mgmt",
            9999: "IoT-Mgmt",
            10001: "Camera-Ctrl"
        }
    
    def scan_port(self, ip, port):
        """Escanea un puerto específico"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def identify_device_type(self, ip, open_ports):
        """Identifica el tipo de dispositivo"""
        if 554 in open_ports or 8554 in open_ports:
            return "IP Camera (RTSP)", 85
        elif 80 in open_ports and any(p in open_ports for p in [8080, 8000]):
            return "IP Camera (HTTP)", 75
        elif 80 in open_ports or 443 in open_ports:
            return "Web Device", 60
        elif any(p in open_ports for p in [8000, 9999, 10001]):
            return "IoT Device", 65
        else:
            return "Unknown Device", 30
    
    def scan_device(self, ip):
        """Escanea un dispositivo específico"""
        ip_str = str(ip)
        open_ports = []
        
        # Escanear puertos
        for port in self.camera_ports:
            if self.scan_port(ip_str, port):
                open_ports.append(port)
        
        if open_ports:
            device_type, confidence = self.identify_device_type(ip_str, open_ports)
            services = [f"{port}/{self.port_services.get(port, 'unknown')}" for port in open_ports]
            
            device_info = {
                'ip': ip_str,
                'open_ports': open_ports,
                'device_type': device_type,
                'confidence': confidence,
                'services': services,
                'scan_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with self.lock:
                self.found_devices.append(device_info)
                print(f"    [+] {ip_str} - {device_type} ({confidence}%) - Puertos: {open_ports}")
            
            return device_info
        
        return None
    
    def scan_network(self, network_range):
        """Escanea una red completa"""
        print(f"[*] Escaneando red: {network_range}")
        
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
        except ValueError as e:
            print(f"[ERROR] Red inválida: {e}")
            return []
        
        hosts = list(network.hosts())
        if len(hosts) > 254:
            hosts = hosts[:254]
        
        print(f"[*] Escaneando {len(hosts)} hosts...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            executor.map(self.scan_device, hosts)
        
        scan_time = time.time() - start_time
        print(f"[*] Escaneo completado en {scan_time:.2f}s")
        print(f"[*] Dispositivos encontrados: {len(self.found_devices)}")
        
        return self.found_devices

def nmap_scan(network_range):
    """Ejecuta escaneo con nmap si está disponible"""
    try:
        # Verificar si nmap está disponible
        result = subprocess.run(['nmap', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return None
    except:
        return None
    
    print(f"[*] Ejecutando nmap en {network_range}...")
    
    try:
        # Escaneo de descubrimiento
        cmd = ['nmap', '-sn', network_range]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            hosts = []
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        ip = parts[4].replace('(', '').replace(')', '')
                        hosts.append(ip)
            
            print(f"[*] Nmap encontró {len(hosts)} hosts activos")
            return hosts
        else:
            print(f"[ERROR] Nmap falló: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en nmap")
        return None
    except Exception as e:
        print(f"[ERROR] Error ejecutando nmap: {e}")
        return None

def escaneo_hibrido_simple(network_range):
    """Escaneo híbrido simplificado"""
    print("🚀 ESCANEO HÍBRIDO SIMPLIFICADO")
    print("=" * 50)
    
    resultados = {
        'network_range': network_range,
        'nmap_hosts': [],
        'smartcam_devices': [],
        'combined_analysis': {}
    }
    
    # Fase 1: Nmap para descubrimiento rápido
    print("\n📡 Fase 1: Descubrimiento con Nmap...")
    nmap_hosts = nmap_scan(network_range)
    
    if nmap_hosts:
        resultados['nmap_hosts'] = nmap_hosts
        print(f"✅ Nmap: {len(nmap_hosts)} hosts activos")
    else:
        print("⚠️ Nmap no disponible o falló")
    
    # Fase 2: SmartCam para análisis detallado
    print("\n🤖 Fase 2: Análisis detallado con SmartCam...")
    scanner = SimpleScanner()
    devices = scanner.scan_network(network_range)
    resultados['smartcam_devices'] = devices
    
    # Fase 3: Análisis combinado
    print("\n📊 Fase 3: Análisis combinado...")
    
    all_ips = set()
    if nmap_hosts:
        all_ips.update(nmap_hosts)
    
    device_ips = [d['ip'] for d in devices]
    all_ips.update(device_ips)
    
    combined = []
    for ip in sorted(all_ips):
        info = {
            'ip': ip,
            'detected_by': [],
            'device_info': None
        }
        
        if nmap_hosts and ip in nmap_hosts:
            info['detected_by'].append('nmap')
        
        device_info = next((d for d in devices if d['ip'] == ip), None)
        if device_info:
            info['detected_by'].append('smartcam')
            info['device_info'] = device_info
        
        combined.append(info)
    
    resultados['combined_analysis'] = combined
    
    return resultados

def mostrar_resultados(resultados):
    """Muestra los resultados del escaneo"""
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DEL ESCANEO HÍBRIDO")
    print("=" * 60)
    
    print(f"🎯 Red escaneada: {resultados['network_range']}")
    print(f"📡 Hosts Nmap: {len(resultados['nmap_hosts'])}")
    print(f"🤖 Dispositivos SmartCam: {len(resultados['smartcam_devices'])}")
    print(f"🔗 Total único: {len(resultados['combined_analysis'])}")
    
    if resultados['combined_analysis']:
        print("\n" + "=" * 60)
        print("🎯 DISPOSITIVOS ENCONTRADOS")
        print("=" * 60)
        
        for item in resultados['combined_analysis']:
            ip = item['ip']
            detected_by = ', '.join(item['detected_by'])
            
            print(f"\n📍 {ip}")
            print(f"   🔍 Detectado por: {detected_by}")
            
            if item['device_info']:
                device = item['device_info']
                print(f"   🏷️ Tipo: {device['device_type']} (Confianza: {device['confidence']}%)")
                print(f"   🔓 Puertos: {device['open_ports']}")
                print(f"   🛠️ Servicios: {', '.join(device['services'])}")
            else:
                print(f"   📡 Solo detectado por Nmap (host activo)")

def test_ia_analyzer():
    """Test rápido del analizador de IA"""
    print("\n🧠 TEST: Analizador de IA")
    print("-" * 30)
    
    try:
        from scanner.image_ai_analyzer import verificar_disponibilidad_ia
        
        estado = verificar_disponibilidad_ia()
        
        if estado['ai_disponible']:
            print("✅ Sistema de IA disponible")
            print(f"   📷 OpenCV: {estado['version_opencv']}")
            print(f"   🧠 Modelos YOLO: {len(estado['modelos_yolo_disponibles'])}")
            
            print("\n💡 Para usar:")
            print("   from scanner.image_ai_analyzer import analizar_rtsp")
            print("   imagen = analizar_rtsp('rtsp://admin:admin@IP:554')")
        else:
            print("❌ Sistema de IA no disponible")
            print("💡 Instalar: pip install opencv-python ultralytics")
            
    except Exception as e:
        print(f"❌ Error verificando IA: {e}")

def main():
    """Función principal"""
    print("🔍 SMARTCAM AUDITOR - ESCANEO HÍBRIDO SIMPLIFICADO")
    print("Nmap + SmartCam sin dependencias problemáticas")
    print()
    
    # Verificar nmap
    try:
        result = subprocess.run(['nmap', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Nmap disponible")
            version_line = result.stdout.split('\n')[0]
            print(f"📋 {version_line}")
        else:
            print("❌ Nmap no funciona correctamente")
    except:
        print("⚠️ Nmap no encontrado")
        print("💡 Instalar: winget install Insecure.Nmap")
    
    print()
    
    # Solicitar red a escanear
    network = input("🌐 Red a escanear (Enter para 192.168.1.0/24): ").strip()
    if not network:
        network = "192.168.1.0/24"
    
    print(f"\n🚀 Iniciando escaneo de {network}...")
    
    # Ejecutar escaneo
    start_time = time.time()
    resultados = escaneo_hibrido_simple(network)
    total_time = time.time() - start_time
    
    # Mostrar resultados
    mostrar_resultados(resultados)
    
    # Test de IA
    test_ia_analyzer()
    
    # Resumen final
    print(f"\n⏱️ Tiempo total: {total_time:.2f} segundos")
    print("\n🎉 Escaneo completado")
    
    # Guardar resultados si hay dispositivos
    if resultados['smartcam_devices']:
        try:
            import json
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"escaneo_hibrido_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Resultados guardados en: {filename}")
        except Exception as e:
            print(f"⚠️ No se pudieron guardar los resultados: {e}")

if __name__ == "__main__":
    main()
