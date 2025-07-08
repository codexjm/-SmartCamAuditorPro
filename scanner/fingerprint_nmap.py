"""
Módulo de fingerprinting de cámaras IP usando Nmap
Extrae la función fingerprint_camaras para uso independiente
"""

import subprocess
import platform
import os
import re

def fingerprint_camaras(lista_ips):
    """
    Realiza fingerprinting avanzado de cámaras IP usando Nmap
    
    Args:
        lista_ips (list): Lista de direcciones IP a analizar
    
    Returns:
        list: Lista de diccionarios con información detallada de cada cámara
        
    Example:
        ips = ["192.168.1.100", "192.168.1.101"]
        resultados = fingerprint_camaras(ips)
        for camara in resultados:
            print(f"IP: {camara['ip']} - Marca: {camara['posible_marca']}")
    """
    resultados = []
    
    # Verificar y configurar Nmap
    nmap_cmd = "nmap"
    
    def verificar_nmap():
        try:
            subprocess.check_output([nmap_cmd, "--version"], stderr=subprocess.DEVNULL)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    # Si Nmap no está en PATH, intentar ubicaciones comunes en Windows
    if not verificar_nmap():
        if platform.system() == "Windows":
            posibles_rutas = [
                r"C:\Program Files (x86)\Nmap\nmap.exe",
                r"C:\Program Files\Nmap\nmap.exe",
                r"C:\Nmap\nmap.exe"
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    nmap_cmd = ruta
                    if verificar_nmap():
                        print(f"🔧 Nmap encontrado en: {ruta}")
                        break
            else:
                print("❌ Error: Nmap no está instalado o no está disponible")
                print("💡 Instala Nmap desde: https://nmap.org/download.html")
                return []
        else:
            print("❌ Error: Nmap no está instalado o no está disponible en PATH")
            return []
    
    print(f"🔍 Iniciando fingerprinting de {len(lista_ips)} dispositivos con Nmap...")

    for ip in lista_ips:
        print(f"📡 Fingerprinting {ip} con Nmap...")
        try:
            # Comando Nmap optimizado para cámaras IP
            output = subprocess.check_output(
                [nmap_cmd, "-sV", "-O", "--script=http-title,http-server-header", ip],
                stderr=subprocess.DEVNULL,
                timeout=30
            ).decode()

            camara = {
                "ip": ip,
                "sistema": None,
                "servicios": [],
                "posible_marca": None
            }

            # Extraer SO con mejor parsing
            so_match = re.search(r"OS details: (.+)", output)
            if so_match:
                camara["sistema"] = so_match.group(1).strip()
            else:
                # Buscar alternativas de OS
                os_guess = re.search(r"Aggressive OS guesses: (.+)", output)
                if os_guess:
                    camara["sistema"] = os_guess.group(1).split(',')[0].strip()

            # Extraer servicios y versiones
            for linea in output.splitlines():
                if "/tcp" in linea and "open" in linea:
                    camara["servicios"].append(linea.strip())

            # Detección avanzada de marcas de cámaras
            marcas_patrones = {
                "Hikvision": ["hikvision", "ds-2cd", "isapi", "webservice"],
                "Dahua": ["dahua", "dh-ipc", "netsurveillance"],
                "Axis": ["axis", "vapix", "live view"],
                "Ubiquiti": ["ubiquiti", "unifi", "unifi video"],
                "Vivotek": ["vivotek", "network camera"],
                "Foscam": ["foscam", "ipcam client"],
                "TP-Link": ["tp-link", "tapo"],
                "Amcrest": ["amcrest"]
            }

            # Buscar marcas con mejor precisión
            output_lower = output.lower()
            for marca, patrones in marcas_patrones.items():
                for patron in patrones:
                    if patron in output_lower:
                        camara["posible_marca"] = marca
                        break
                if camara["posible_marca"]:
                    break

            resultados.append(camara)

        except subprocess.TimeoutExpired:
            print(f"⏳ Tiempo agotado al escanear {ip}")
            resultados.append({
                "ip": ip,
                "error": "timeout",
                "sistema": None,
                "servicios": [],
                "posible_marca": None
            })
        except Exception as e:
            print(f"❌ Error escaneando {ip}: {e}")
            resultados.append({
                "ip": ip,
                "error": str(e),
                "sistema": None,
                "servicios": [],
                "posible_marca": None
            })

    return resultados

def fingerprint_dispositivo_unico(ip):
    """
    Analiza un único dispositivo
    
    Args:
        ip (str): Dirección IP a analizar
    
    Returns:
        dict: Información del dispositivo
    """
    resultados = fingerprint_camaras([ip])
    return resultados[0] if resultados else None

def resumen_fingerprinting(resultados):
    """
    Genera un resumen de los resultados de fingerprinting
    
    Args:
        resultados (list): Lista de resultados de fingerprint_camaras
    
    Returns:
        dict: Resumen estadístico
    """
    total = len(resultados)
    exitosos = [r for r in resultados if not r.get('error')]
    con_marca = [r for r in exitosos if r.get('posible_marca')]
    
    marcas_count = {}
    for resultado in con_marca:
        marca = resultado['posible_marca']
        marcas_count[marca] = marcas_count.get(marca, 0) + 1
    
    return {
        'total_analizado': total,
        'exitosos': len(exitosos),
        'con_marca': len(con_marca),
        'distribución_marcas': marcas_count,
        'tasa_exito': round(len(exitosos) / total * 100, 2) if total > 0 else 0
    }
