"""
SmartCam Auditor - Módulo de Pruebas de Credenciales
Prueba credenciales comunes en dispositivos HTTP y RTSP
"""

import requests
import socket
import base64
from typing import List, Tuple, Optional
import time

# Credenciales comunes en dispositivos IoT y cámaras IP
COMMON_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "1234"),
    ("admin", "12345"),
    ("admin", "password"),
    ("admin", ""),
    ("root", "root"),
    ("root", "admin"),
    ("root", ""),
    ("user", "user"),
    ("user", "1234"),
    ("guest", "guest"),
    ("guest", ""),
    ("", "admin"),
    ("", "1234"),
    ("", ""),
    # Credenciales específicas de cámaras
    ("admin", "admin123"),
    ("admin", "888888"),
    ("admin", "666666"),
    ("supervisor", "supervisor"),
    ("viewer", "viewer"),
    ("operator", "operator"),
    # Credenciales de fabricantes comunes
    ("ubnt", "ubnt"),  # Ubiquiti
    ("admin", "smcadmin"),  # SMC
    ("admin", "epicrouter"),  # Epic
    ("admin", "motorola"),  # Motorola
]

TIMEOUT = 5
REQUEST_DELAY = 0.5  # Pausa entre intentos para evitar sobrecarga

def probar_http(ip: str, port: int = 80) -> Optional[str]:
    """
    Prueba credenciales HTTP básicas en un dispositivo
    
    Args:
        ip: Dirección IP del dispositivo
        port: Puerto HTTP (por defecto 80)
        
    Returns:
        Mensaje de vulnerabilidad encontrada o None
    """
    url = f"http://{ip}:{port}"
    
    for usuario, clave in COMMON_CREDENTIALS:
        try:
            print(f"🧪 Probando HTTP {ip}:{port} con {usuario}:{clave}")
            
            # Intentar con autenticación básica
            resp = requests.get(
                url, 
                auth=(usuario, clave), 
                timeout=TIMEOUT,
                headers={'User-Agent': 'SmartCam-Auditor/2.0'}
            )
            
            if resp.status_code == 200:
                return f"🚨 {ip}:{port} - HTTP login débil: {usuario}:{clave}"
                
            # También verificar otros códigos que indican acceso
            if resp.status_code in [302, 301] and 'admin' in resp.text.lower():
                return f"🚨 {ip}:{port} - HTTP posible acceso: {usuario}:{clave} (redirect)"
                
        except requests.RequestException as e:
            # Continuar con la siguiente credencial
            continue
        
        # Pausa para evitar sobrecarga del dispositivo
        time.sleep(REQUEST_DELAY)
    
    return None

def probar_rtsp(ip: str, port: int = 554) -> Optional[str]:
    """
    Prueba credenciales RTSP en cámaras IP
    
    Args:
        ip: Dirección IP de la cámara
        port: Puerto RTSP (por defecto 554)
        
    Returns:
        Mensaje de vulnerabilidad encontrada o None
    """
    for usuario, clave in COMMON_CREDENTIALS:
        try:
            print(f"🧪 Probando RTSP {ip}:{port} con {usuario}:{clave}")
            
            # Crear conexión socket
            sock = socket.create_connection((ip, port), timeout=TIMEOUT)
            
            # Crear autenticación básica
            if usuario and clave:
                credentials = base64.b64encode(f"{usuario}:{clave}".encode()).decode()
                auth_header = f"Authorization: Basic {credentials}\r\n"
            else:
                auth_header = ""
            
            # Enviar petición RTSP OPTIONS
            request = (
                f"OPTIONS rtsp://{ip}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"{auth_header}"
                f"User-Agent: SmartCam-Auditor/2.0\r\n"
                f"\r\n"
            )
            
            sock.send(request.encode())
            resp = sock.recv(1024).decode()
            sock.close()
            
            # Verificar respuesta exitosa
            if "200 OK" in resp or "RTSP/1.0 200" in resp:
                return f"🚨 {ip}:{port} - RTSP accesible con {usuario}:{clave}"
                
        except Exception as e:
            # Continuar con la siguiente credencial
            continue
        
        # Pausa para evitar sobrecarga
        time.sleep(REQUEST_DELAY)
    
    return None

def probar_ssh(ip: str, port: int = 22) -> Optional[str]:
    """
    Prueba credenciales SSH básicas (requiere paramiko)
    
    Args:
        ip: Dirección IP del dispositivo
        port: Puerto SSH (por defecto 22)
        
    Returns:
        Mensaje de vulnerabilidad encontrada o None
    """
    try:
        import paramiko
    except ImportError:
        print("⚠️ Paramiko no disponible, saltando pruebas SSH")
        return None
    
    for usuario, clave in COMMON_CREDENTIALS:
        try:
            print(f"🧪 Probando SSH {ip}:{port} con {usuario}:{clave}")
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=ip,
                port=port,
                username=usuario,
                password=clave,
                timeout=TIMEOUT
            )
            
            ssh.close()
            return f"🚨 {ip}:{port} - SSH accesible con {usuario}:{clave}"
            
        except Exception:
            continue
        
        time.sleep(REQUEST_DELAY)
    
    return None

def testear_credenciales(lista_ips: List[str], puertos_http: List[int] = None, incluir_rtsp: bool = True, incluir_ssh: bool = False) -> List[str]:
    """
    Prueba credenciales débiles en una lista de IPs
    
    Args:
        lista_ips: Lista de direcciones IP a probar
        puertos_http: Lista de puertos HTTP a probar (por defecto [80, 8080, 443])
        incluir_rtsp: Si probar RTSP en puerto 554
        incluir_ssh: Si probar SSH en puerto 22
        
    Returns:
        Lista de vulnerabilidades encontradas
    """
    if puertos_http is None:
        puertos_http = [80, 8080, 443, 8000, 8081, 9000]
    
    resultados = []
    total_ips = len(lista_ips)
    
    for i, ip in enumerate(lista_ips, 1):
        print(f"\n🔍 Analizando {ip} ({i}/{total_ips})...")
        
        # Probar HTTP en múltiples puertos
        for puerto in puertos_http:
            resultado_http = probar_http(ip, puerto)
            if resultado_http:
                resultados.append(resultado_http)
                print(f"✅ {resultado_http}")
                break  # No seguir probando puertos si ya encontró vulnerabilidad
        
        # Probar RTSP si está habilitado
        if incluir_rtsp:
            resultado_rtsp = probar_rtsp(ip)
            if resultado_rtsp:
                resultados.append(resultado_rtsp)
                print(f"✅ {resultado_rtsp}")
        
        # Probar SSH si está habilitado
        if incluir_ssh:
            resultado_ssh = probar_ssh(ip)
            if resultado_ssh:
                resultados.append(resultado_ssh)
                print(f"✅ {resultado_ssh}")
    
    return resultados

def generar_reporte_credenciales(resultados: List[str], archivo_salida: str = None) -> str:
    """
    Genera un reporte detallado de las vulnerabilidades encontradas
    
    Args:
        resultados: Lista de vulnerabilidades encontradas
        archivo_salida: Archivo donde guardar el reporte (opcional)
        
    Returns:
        Contenido del reporte como string
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    reporte = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                          🔒 SMARTCAM AUDITOR - REPORTE DE CREDENCIALES                  ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║ Fecha: {timestamp}                                                           ║
║ Vulnerabilidades encontradas: {len(resultados)}                                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

"""
    
    if resultados:
        reporte += "🚨 VULNERABILIDADES CRÍTICAS DETECTADAS:\n"
        reporte += "=" * 60 + "\n\n"
        
        for i, resultado in enumerate(resultados, 1):
            reporte += f"{i}. {resultado}\n"
        
        reporte += "\n" + "=" * 60 + "\n"
        reporte += "⚠️  RECOMENDACIONES DE SEGURIDAD:\n"
        reporte += "   • Cambiar todas las credenciales por defecto inmediatamente\n"
        reporte += "   • Usar contraseñas fuertes (mínimo 12 caracteres)\n"
        reporte += "   • Implementar autenticación de dos factores cuando sea posible\n"
        reporte += "   • Restringir acceso mediante firewall o VPN\n"
        reporte += "   • Revisar logs de acceso regularmente\n"
        reporte += "   • Actualizar firmware de los dispositivos\n"
    else:
        reporte += "✅ BUENAS NOTICIAS: No se encontraron credenciales débiles\n"
        reporte += "=" * 60 + "\n"
        reporte += "Los dispositivos analizados no presentan vulnerabilidades\n"
        reporte += "obvias de credenciales por defecto.\n"
    
    reporte += f"\n\n📊 Análisis completado - SmartCam Auditor v2.0\n"
    reporte += "⚠️  Solo para uso en redes propias y con autorización explícita\n"
    
    # Guardar archivo si se especifica
    if archivo_salida:
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(reporte)
            print(f"📁 Reporte guardado en: {archivo_salida}")
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
    
    return reporte

if __name__ == "__main__":
    # Ejemplo de uso
    ips_ejemplo = ["192.168.1.100", "192.168.1.101"]
    print("🚀 Iniciando pruebas de credenciales...")
    
    vulnerabilidades = testear_credenciales(ips_ejemplo)
    reporte = generar_reporte_credenciales(vulnerabilidades, "logs/credential_test.txt")
    
    print("\n" + "=" * 60)
    print(reporte)
