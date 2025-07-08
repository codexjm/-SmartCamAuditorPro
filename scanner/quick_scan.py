#!/usr/bin/env python3
"""
SmartCam Auditor - Script de Escaneo Rápido
Ejecuta un escaneo básico y rápido de dispositivos IoT
"""

import os
import sys
import time
import socket
from datetime import datetime

# Añadir el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos
try:
    from scanner.credential_tester import testear_credenciales
    CREDENTIAL_TESTER_AVAILABLE = True
    print("✅ Módulo de pruebas de credenciales cargado")
except ImportError as e:
    CREDENTIAL_TESTER_AVAILABLE = False
    print(f"⚠️ Módulo de credenciales no disponible: {e}")

try:
    from scanner.network_scanner import NetworkScanner
    ADVANCED_SCANNER_AVAILABLE = True
    print("✅ Escáner de red avanzado cargado")
except ImportError as e:
    ADVANCED_SCANNER_AVAILABLE = False
    print(f"⚠️ Escáner avanzado no disponible: {e}")

def log_message(message):
    """Imprime mensaje con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def quick_scan_advanced():
    """Escaneo rápido usando el escáner avanzado"""
    log_message("⚡ Iniciando escaneo rápido avanzado...")
    
    if ADVANCED_SCANNER_AVAILABLE:
        try:
            # Configuración más rápida para escaneo rápido
            scanner = NetworkScanner(timeout=0.8, max_threads=100)
            network = scanner.get_local_network()
            
            # Limitar el escaneo para que sea realmente rápido
            log_message(f"📡 Escaneo rápido en: {network}")
            devices = scanner.scan_network(network)
            
            # Filtrar solo dispositivos de alta confianza para escaneo rápido
            high_confidence_devices = [d for d in devices if d['confidence'] >= 70]
            
            if high_confidence_devices:
                log_message(f"✅ {len(high_confidence_devices)} dispositivos IoT/cámaras de alta confianza")
                return high_confidence_devices
            else:
                log_message("ℹ️ No se encontraron dispositivos IoT/cámaras de alta confianza")
                return devices
                
        except Exception as e:
            log_message(f"❌ Error en escaneo avanzado: {e}")
            return quick_ping_sweep_basic()
    else:
        return quick_ping_sweep_basic()

def quick_ping_sweep_basic():
    """Escaneo rápido básico (fallback)"""
    log_message("⚡ Iniciando ping sweep rápido básico...")
    
    devices = []
    base_ip = "192.168.1."
    
    # Solo escanear IPs comunes para dispositivos IoT
    common_ips = [1, 100, 101, 102, 200, 201, 254]
    
    for ip_end in common_ips:
        ip = base_ip + str(ip_end)
        try:
            # Ping muy rápido
            sock = socket.create_connection((ip, 80), timeout=0.1)
            sock.close()
            device_info = {
                'ip': ip,
                'device_type': 'Web Device (Quick)',
                'confidence': 50,
                'open_ports': [80],
                'services': ['80/HTTP Web Interface']
            }
            devices.append(device_info)
            log_message(f"  📱 Dispositivo IoT: {ip}")
        except:
            pass
    
    return devices

# Función principal de escaneo rápido
def quick_ping_sweep():
    """Función principal de escaneo rápido"""
    if ADVANCED_SCANNER_AVAILABLE:
        return quick_scan_advanced()
    else:
        return quick_ping_sweep_basic()
    return devices

def quick_port_check(devices):
    """Verificación rápida de puertos críticos"""
    log_message("🔍 Verificando puertos críticos...")
    
    critical_ports = [80, 443, 22, 23, 554, 8080]
    open_ports = {}
    vulnerable_credentials = []
    
    for device in devices:
        device_ip = device['ip'] if isinstance(device, dict) else device
        device_info = device if isinstance(device, dict) else {'ip': device}
        
        # Si ya tenemos información de puertos del escáner avanzado, usarla
        if 'open_ports' in device_info:
            open_ports[device_ip] = device_info['open_ports']
            log_message(f"    📋 Puertos conocidos para {device_ip}: {device_info['open_ports']}")
        else:
            # Verificación básica de puertos
            open_ports[device_ip] = []
            for port in critical_ports:
                try:
                    sock = socket.create_connection((device_ip, port), timeout=0.1)
                    sock.close()
                    open_ports[device_ip].append(port)
                    log_message(f"    🚪 Puerto abierto: {device_ip}:{port}")
                except:
                    pass
    
    # Pruebas rápidas de credenciales en dispositivos con puertos web
    devices_with_web = []
    for device in devices:
        device_ip = device['ip'] if isinstance(device, dict) else device
        if any(port in [80, 443, 8080] for port in open_ports.get(device_ip, [])):
            devices_with_web.append(device_ip)
    
    if devices_with_web and CREDENTIAL_TESTER_AVAILABLE:
        log_message("🔐 Pruebas rápidas de credenciales...")
        try:
            # Solo probar los primeros 3 dispositivos para mantener velocidad
            test_devices = devices_with_web[:3]
            resultados_credenciales = testear_credenciales(
                test_devices,
                puertos_http=[80, 8080],  # Solo HTTP básico
                incluir_rtsp=False,       # Sin RTSP para ser más rápido
                incluir_ssh=False         # Sin SSH para ser más rápido
            )
            
            for resultado in resultados_credenciales:
                vulnerable_credentials.append(resultado)
                log_message(f"    🚨 Credencial débil encontrada")
                
        except Exception as e:
            log_message(f"    ❌ Error en pruebas de credenciales: {e}")
    
    return open_ports, vulnerable_credentials

def generate_quick_report(devices, open_ports, vulnerable_credentials):
    """Genera reporte de escaneo rápido"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    report_path = os.path.join(log_dir, f"quick_scan_{timestamp}.txt")
    
    total_open_ports = sum(len(ports) for ports in open_ports.values())
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"⚡ REPORTE DE ESCANEO RÁPIDO\n")
        f.write(f"=" * 40 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tipo: Escaneo Rápido Avanzado con Detección IoT\n")
        f.write(f"SmartCam Auditor v2.0 Pro\n\n")
        
        f.write(f"📊 RESUMEN\n")
        f.write(f"-" * 20 + "\n")
        f.write(f"Dispositivos activos: {len(devices)}\n")
        f.write(f"Puertos abiertos: {total_open_ports}\n")
        f.write(f"Credenciales débiles: {len(vulnerable_credentials)}\n")
        
        # Análisis de tipos de dispositivos (si está disponible)
        if devices and isinstance(devices[0], dict):
            device_types = {}
            high_confidence = 0
            for device in devices:
                device_type = device.get('device_type', 'Unknown')
                confidence = device.get('confidence', 0)
                
                if device_type not in device_types:
                    device_types[device_type] = 0
                device_types[device_type] += 1
                
                if confidence >= 75:
                    high_confidence += 1
            
            f.write(f"Dispositivos alta confianza (≥75%): {high_confidence}\n")
            
            if device_types:
                f.write(f"\nTipos de dispositivos:\n")
                for device_type, count in device_types.items():
                    f.write(f"  - {device_type}: {count}\n")
        
        # Determinar estado
        if vulnerable_credentials:
            status = "🚨 Crítico"
        elif total_open_ports > 8:
            status = "⚠️ Revisar"
        elif total_open_ports > 0:
            status = "📋 Monitorear"
        else:
            status = "✅ Normal"
        
        f.write(f"\nEstado general: {status}\n\n")
        
        if devices:
            f.write(f"📱 DISPOSITIVOS IoT/CÁMARAS DETECTADOS\n")
            f.write(f"-" * 40 + "\n")
            for i, device in enumerate(devices, 1):
                if isinstance(device, dict):
                    f.write(f"{i}. IP: {device['ip']}\n")
                    f.write(f"   Tipo: {device.get('device_type', 'Unknown')}\n")
                    f.write(f"   Confianza: {device.get('confidence', 'N/A')}%\n")
                    f.write(f"   Puertos: {device.get('open_ports', [])}\n")
                    if device.get('services'):
                        f.write(f"   Servicios: {', '.join(device['services'])}\n")
                else:
                    f.write(f"{i}. IP: {device}\n")
                    device_ports = open_ports.get(device, [])
                    f.write(f"   Puertos abiertos: {device_ports}\n")
            for device in devices:
                ports = open_ports.get(device, [])
                f.write(f"  • {device}")
                if ports:
                    f.write(f" - Puertos: {', '.join(map(str, ports))}")
                f.write("\n")
        
        # Agregar sección de credenciales débiles
        if vulnerable_credentials:
            f.write(f"\n🔐 CREDENCIALES DÉBILES DETECTADAS\n")
            f.write(f"-" * 35 + "\n")
            for i, cred in enumerate(vulnerable_credentials, 1):
                f.write(f"{i}. {cred}\n")
            
            f.write(f"\n⚠️ ACCIÓN URGENTE REQUERIDA:\n")
            f.write(f"   • Cambiar credenciales inmediatamente\n")
            f.write(f"   • Revisar accesos no autorizados\n")
            f.write(f"   • Implementar contraseñas fuertes\n")
        
        f.write(f"\n⚡ FIN DEL ESCANEO RÁPIDO\n")
        f.write(f"⚠️ Para análisis completo, ejecutar auditoría completa\n")
    
    log_message(f"📄 Reporte guardado en: {report_path}")
    return report_path

def main():
    """Función principal"""
    log_message("⚡ Iniciando SmartCam Auditor - Escaneo Rápido")
    
    try:
        # Paso 1: Ping sweep rápido
        devices = quick_ping_sweep()
        
        if not devices:
            log_message("ℹ️ No se encontraron dispositivos activos")
            devices = []
        
        # Paso 2: Verificación de puertos y credenciales rápidas
        open_ports, vulnerable_credentials = quick_port_check(devices)
        
        # Paso 3: Generar reporte
        report_path = generate_quick_report(devices, open_ports, vulnerable_credentials)
        
        log_message("✅ Escaneo rápido completado")
        log_message(f"📊 Dispositivos: {len(devices)}")
        if vulnerable_credentials:
            log_message(f"🚨 Credenciales débiles: {len(vulnerable_credentials)}")
        
        return 0
        
    except Exception as e:
        log_message(f"❌ Error durante el escaneo: {e}")
        return 1
        
    except Exception as e:
        log_message(f"❌ Error durante el escaneo: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
