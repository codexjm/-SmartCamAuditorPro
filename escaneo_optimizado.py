#!/usr/bin/env python3
"""
Implementación directa del código de escaneo proporcionado por el usuario
Integrado con el sistema SmartCam Auditor
"""

import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import time

# Puertos típicos de cámaras IP
PUERTOS_OBJETIVO = [80, 554, 8000, 8080]
TIMEOUT = 1.5

def escanear_puerto(ip, puerto):
    """Escanea un puerto específico en una IP"""
    try:
        with socket.create_connection((ip, puerto), timeout=TIMEOUT):
            print(f"[+] {ip}:{puerto} está abierto")
            return True
    except:
        return False

def escanear_ip(ip):
    """Escanea una IP específica en todos los puertos objetivo"""
    for puerto in PUERTOS_OBJETIVO:
        if escanear_puerto(str(ip), puerto):
            return str(ip)
    return None

def obtener_ips_dispositivos(rango_red):
    """
    Función principal del escáner optimizado
    
    Args:
        rango_red (str): Rango de red en formato CIDR (ej: 192.168.1.0/24)
    
    Returns:
        list: Lista de IPs de dispositivos encontrados
    """
    print(f"[SCAN] Escaneando red {rango_red}...")
    ips_detectadas = []

    red = ipaddress.IPv4Network(rango_red, strict=False)
    with ThreadPoolExecutor(max_workers=50) as executor:
        resultados = list(executor.map(escanear_ip, red.hosts()))

    for ip in resultados:
        if ip:
            ips_detectadas.append(ip)

    print(f"[RESULTS] IPs activas encontradas: {ips_detectadas}")
    return ips_detectadas

def demo_escaneo_optimizado():
    """Demostración del escáner optimizado"""
    print("SMARTCAM AUDITOR - ESCÁNER OPTIMIZADO")
    print("=" * 50)
    
    # Detectar red local automáticamente
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        
        # Construir rango de red
        ip_parts = local_ip.split('.')
        rango_red = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        print(f"[INFO] Red local detectada: {rango_red}")
        
    except:
        rango_red = "192.168.1.0/24"
        print(f"[INFO] Usando red por defecto: {rango_red}")
    
    # Ejecutar escaneo
    inicio = time.time()
    dispositivos = obtener_ips_dispositivos(rango_red)
    tiempo_total = time.time() - inicio
    
    # Mostrar resultados
    print(f"\n[SUMMARY] RESULTADOS DEL ESCANEO")
    print(f"[TIME] Tiempo total: {tiempo_total:.2f} segundos")
    print(f"[DEVICES] Dispositivos encontrados: {len(dispositivos)}")
    
    if dispositivos:
        print(f"\n[CAMERAS] DISPOSITIVOS CON PUERTOS DE CAMARAS IP:")
        for i, ip in enumerate(dispositivos, 1):
            print(f"  {i}. {ip}")
            
            # Mostrar detalles de puertos abiertos para cada dispositivo
            print(f"     Puertos abiertos:")
            for puerto in PUERTOS_OBJETIVO:
                if escanear_puerto(ip, puerto):
                    servicio = {
                        80: "HTTP Web Interface",
                        554: "RTSP Stream",
                        8000: "HTTP Streaming",
                        8080: "HTTP Alternative"
                    }.get(puerto, f"Puerto {puerto}")
                    print(f"       • {puerto} - {servicio}")
    else:
        print("[INFO] No se encontraron dispositivos con puertos de camaras IP en la red.")
    
    return dispositivos

def integracion_con_smartcam():
    """Integración con el sistema SmartCam Auditor existente"""
    print(f"\n[INTEGRATION] INTEGRACION CON SMARTCAM AUDITOR")
    print("=" * 50)
    
    dispositivos = demo_escaneo_optimizado()
    
    if dispositivos:
        print(f"\n[CREDS] Iniciando pruebas de credenciales en dispositivos encontrados...")
        
        # Intentar cargar el módulo de pruebas de credenciales
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            from scanner.credential_tester import testear_credenciales
            
            # Probar credenciales solo en los primeros 3 dispositivos
            dispositivos_limitados = dispositivos[:3]
            print(f"[TEST] Probando credenciales en: {dispositivos_limitados}")
            
            vulnerabilidades = testear_credenciales(
                dispositivos_limitados,
                puertos_http=[80, 8080],
                incluir_rtsp=True,
                incluir_ssh=False
            )
            
            if vulnerabilidades:
                print(f"\n[ALERT] Se encontraron {len(vulnerabilidades)} vulnerabilidades de credenciales:")
                for vuln in vulnerabilidades[:5]:  # Mostrar solo las primeras 5
                    print(f"  • {vuln}")
            else:
                print(f"[OK] No se encontraron credenciales débiles en los dispositivos probados.")
                
        except ImportError:
            print(f"[WARN] Módulo de pruebas de credenciales no disponible.")
            print(f"[INFO] Para habilitar esta funcionalidad, ejecute: pip install requests")
        except Exception as e:
            print(f"[ERROR] Error en pruebas de credenciales: {e}")
    
    print(f"\n[LOGS] Para ver reportes detallados, revise la carpeta 'logs'")
    print(f"[WEB] Para acceso visual, use el panel web: http://localhost:5000")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--solo-escaneo":
        demo_escaneo_optimizado()
    else:
        integracion_con_smartcam()
