"""
Módulo para verificar puertos abiertos en dispositivos detectados
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# Puertos comunes en cámaras IP y dispositivos IoT (versión simplificada)
COMMON_PORTS = [80, 554, 8080, 21, 23, 22]

# Puertos extendidos para escaneo completo (opcional)
EXTENDED_CAMERA_PORTS = [
    21,    # FTP
    22,    # SSH
    23,    # Telnet
    25,    # SMTP
    53,    # DNS
    80,    # HTTP
    110,   # POP3
    143,   # IMAP
    443,   # HTTPS
    554,   # RTSP (streaming)
    993,   # IMAPS
    995,   # POP3S
    1935,  # RTMP
    8080,  # HTTP alternativo
    8443,  # HTTPS alternativo
    8554,  # RTSP alternativo
    9999,  # Puerto común en cámaras chinas
    37777, # Puerto común en DVR/NVR
    34567, # Puerto común en cámaras Dahua
    85,    # Puerto alternativo HTTP
]

def check_port_simple(ip, port, timeout=0.5):
    """
    Verifica si un puerto específico está abierto (versión simplificada)
    
    Args:
        ip (str): Dirección IP del dispositivo
        port (int): Puerto a verificar
        timeout (float): Timeout en segundos
    
    Returns:
        bool: True si el puerto está abierto
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
        return True
    except:
        return False
    finally:
        sock.close()

def check_port(ip, port, timeout=1):
    """
    Verifica si un puerto específico está abierto (versión detallada)
    
    Args:
        ip (str): Dirección IP del dispositivo
        port (int): Puerto a verificar
        timeout (int): Timeout en segundos
    
    Returns:
        dict: Información del puerto si está abierto, None si está cerrado
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            return {
                'port': port,
                'status': 'abierto',
                'service': get_service_name(port)
            }
    except Exception:
        pass
    
    return None

def check_ports(ip, extended=False):
    """
    Verifica puertos abiertos en un dispositivo (versión simplificada y rápida)
    
    Args:
        ip (str): Dirección IP del dispositivo
        extended (bool): Si usar lista extendida de puertos
    
    Returns:
        list: Lista de puertos abiertos (números simples)
    """
    ports_to_check = EXTENDED_CAMERA_PORTS if extended else COMMON_PORTS
    print(f"      [*] Verificando {len(ports_to_check)} puertos en {ip}")
    
    open_ports = []
    for port in ports_to_check:
        if check_port_simple(ip, port):
            open_ports.append(port)
            service_name = get_service_name(port)
            print(f"      [+] Puerto abierto: {port} ({service_name})")
    
    print(f"      [*] {len(open_ports)} puertos abiertos encontrados en {ip}")
    return open_ports

def check_ports_detailed(ip, custom_ports=None):
    """
    Verifica múltiples puertos en un dispositivo (versión detallada con paralelismo)
    
    Args:
        ip (str): Dirección IP del dispositivo
        custom_ports (list): Lista personalizada de puertos (opcional)
    
    Returns:
        list: Lista de diccionarios con información detallada de puertos
    """
    ports_to_check = custom_ports if custom_ports else EXTENDED_CAMERA_PORTS
    print(f"      [*] Verificando {len(ports_to_check)} puertos en {ip} (modo detallado)")
    
    open_ports = []
    
    # Verificación paralela de puertos
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_port = {
            executor.submit(check_port, ip, port): port 
            for port in ports_to_check
        }
        
        for future in as_completed(future_to_port):
            result = future.result()
            if result:
                open_ports.append(result)
                print(f"      [+] Puerto abierto: {result['port']} ({result['service']})")
    
    print(f"      [*] {len(open_ports)} puertos abiertos encontrados en {ip}")
    return open_ports

def get_service_name(port):
    """Obtiene el nombre del servicio común para un puerto"""
    services = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        554: 'RTSP',
        993: 'IMAPS',
        995: 'POP3S',
        1935: 'RTMP',
        8080: 'HTTP-Alt',
        8443: 'HTTPS-Alt',
        8554: 'RTSP-Alt',
        9999: 'Camera-Web',
        37777: 'DVR/NVR',
        34567: 'Dahua-Camera',
        85: 'HTTP-Alt2',
    }
    return services.get(port, f'Puerto-{port}')
