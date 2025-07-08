"""
Módulo de testing avanzado para empresas de seguridad
Incluye pruebas más profundas para productos propios
"""

import requests
import json
from urllib.parse import urljoin
import ssl
import socket
from datetime import datetime

# Base de datos de vulnerabilidades conocidas por marca/modelo
KNOWN_VULNERABILITIES = {
    "hikvision": [
        {"cve": "CVE-2021-36260", "path": "/SDK/webLanguage", "description": "Command injection"},
        {"cve": "CVE-2017-7921", "path": "/System/configurationFile", "description": "Info disclosure"}
    ],
    "dahua": [
        {"cve": "CVE-2021-33044", "path": "/cgi-bin/snapshot.cgi", "description": "Auth bypass"},
        {"cve": "CVE-2020-9473", "path": "/cgi-bin/main-cgi", "description": "Buffer overflow"}
    ],
    "axis": [
        {"cve": "CVE-2022-31199", "path": "/axis-cgi/param.cgi", "description": "Directory traversal"}
    ]
}

# Rutas comunes de administración y configuración
ADMIN_PATHS = [
    "/admin", "/config", "/setup", "/system", "/maintenance",
    "/cgi-bin/main-cgi", "/ISAPI/System/deviceInfo", 
    "/onvif/device_service", "/axis-cgi/param.cgi",
    "/SDK/webLanguage", "/System/configurationFile"
]

# Headers inseguros comunes
SECURITY_HEADERS_CHECK = [
    "X-Frame-Options", "X-Content-Type-Options", 
    "X-XSS-Protection", "Strict-Transport-Security"
]

def advanced_camera_testing(ip, ports, config):
    """
    Realiza testing avanzado específico para cámaras IP
    Para uso en productos propios de la empresa
    """
    results = {
        "ip": ip,
        "timestamp": datetime.now().isoformat(),
        "vulnerabilities": [],
        "misconfigurations": [],
        "security_issues": []
    }
    
    print(f"        [*] Iniciando testing avanzado en {ip}")
    
    # Testing en puertos HTTP/HTTPS
    web_ports = [p for p in ports if p in [80, 443, 8080, 8443]]
    
    for port in web_ports:
        protocol = "https" if port in [443, 8443] else "http"
        base_url = f"{protocol}://{ip}:{port}"
        
        # 1. Verificar rutas de administración expuestas
        check_admin_paths(base_url, results)
        
        # 2. Análisis de headers de seguridad
        check_security_headers(base_url, results)
        
        # 3. Verificar vulnerabilidades conocidas
        check_known_vulnerabilities(base_url, results)
        
        # 4. Testing de autenticación débil
        check_weak_authentication(base_url, results)
        
        # 5. Verificar certificados SSL (si es HTTPS)
        if protocol == "https":
            check_ssl_configuration(ip, port, results)
    
    return results

def check_admin_paths(base_url, results):
    """Verifica si rutas administrativas están expuestas"""
    print(f"          [*] Verificando rutas administrativas...")
    
    for path in ADMIN_PATHS:
        try:
            url = urljoin(base_url, path)
            response = requests.get(url, timeout=3, verify=False, allow_redirects=False)
            
            if response.status_code == 200:
                results["vulnerabilities"].append({
                    "type": "Exposed Admin Interface",
                    "severity": "HIGH",
                    "url": url,
                    "description": f"Interfaz administrativa accesible en {path}"
                })
                print(f"          [!] Ruta administrativa expuesta: {path}")
                
        except requests.exceptions.RequestException:
            continue

def check_security_headers(base_url, results):
    """Analiza headers de seguridad HTTP"""
    print(f"          [*] Analizando headers de seguridad...")
    
    try:
        response = requests.get(base_url, timeout=3, verify=False)
        headers = response.headers
        
        missing_headers = []
        for header in SECURITY_HEADERS_CHECK:
            if header not in headers:
                missing_headers.append(header)
        
        if missing_headers:
            results["security_issues"].append({
                "type": "Missing Security Headers",
                "severity": "MEDIUM",
                "missing_headers": missing_headers,
                "description": "Headers de seguridad faltantes"
            })
            print(f"          [!] Headers de seguridad faltantes: {missing_headers}")
            
        # Verificar versión del servidor expuesta
        if "Server" in headers:
            server_info = headers["Server"]
            results["misconfigurations"].append({
                "type": "Server Version Disclosure",
                "severity": "LOW",
                "server_info": server_info,
                "description": "Información del servidor expuesta"
            })
            
    except requests.exceptions.RequestException:
        pass

def check_known_vulnerabilities(base_url, results):
    """Verifica vulnerabilidades conocidas basadas en fingerprinting"""
    print(f"          [*] Verificando vulnerabilidades conocidas...")
    
    # Intentar identificar marca/modelo
    brand = identify_camera_brand(base_url)
    
    if brand and brand.lower() in KNOWN_VULNERABILITIES:
        vulns = KNOWN_VULNERABILITIES[brand.lower()]
        
        for vuln in vulns:
            test_url = urljoin(base_url, vuln["path"])
            try:
                response = requests.get(test_url, timeout=3, verify=False)
                
                # Si responde, podría ser vulnerable
                if response.status_code in [200, 401, 403]:
                    results["vulnerabilities"].append({
                        "type": "Known Vulnerability",
                        "severity": "CRITICAL",
                        "cve": vuln["cve"],
                        "url": test_url,
                        "description": vuln["description"],
                        "brand": brand
                    })
                    print(f"          [!] Posible vulnerabilidad {vuln['cve']}: {vuln['description']}")
                    
            except requests.exceptions.RequestException:
                continue

def identify_camera_brand(base_url):
    """Intenta identificar la marca de la cámara"""
    
    # Indicadores comunes por marca
    brand_indicators = {
        "hikvision": ["/doc/page/login.asp", "/ISAPI/System/deviceInfo"],
        "dahua": ["/RPC2_Login", "/cgi-bin/main-cgi"],
        "axis": ["/axis-cgi/param.cgi", "/view/view.shtml"],
        "foscam": ["/cgi-bin/CGIProxy.fcgi", "/login.htm"],
        "vivotek": ["/cgi-bin/viewer/video.jpg", "/setup/config.html"]
    }
    
    for brand, paths in brand_indicators.items():
        for path in paths:
            try:
                test_url = urljoin(base_url, path)
                response = requests.get(test_url, timeout=2, verify=False)
                if response.status_code in [200, 401]:
                    return brand
            except:
                continue
    
    return None

def check_weak_authentication(base_url, results):
    """Verifica configuraciones de autenticación débiles"""
    print(f"          [*] Verificando configuraciones de autenticación...")
    
    # Verificar si hay endpoints sin autenticación
    unauth_endpoints = [
        "/cgi-bin/snapshot.cgi", "/tmpfs/auto.jpg", "/onvif/device_service",
        "/axis-cgi/mjpg/video.cgi", "/videostream.cgi"
    ]
    
    for endpoint in unauth_endpoints:
        try:
            test_url = urljoin(base_url, endpoint)
            response = requests.get(test_url, timeout=3, verify=False)
            
            if response.status_code == 200 and len(response.content) > 1000:
                results["vulnerabilities"].append({
                    "type": "Unauthenticated Access",
                    "severity": "HIGH",
                    "url": test_url,
                    "description": "Acceso sin autenticación a contenido sensible"
                })
                print(f"          [!] Acceso sin autenticación: {endpoint}")
                
        except requests.exceptions.RequestException:
            continue

def check_ssl_configuration(ip, port, results):
    """Analiza la configuración SSL/TLS"""
    print(f"          [*] Analizando configuración SSL...")
    
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((ip, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=ip) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                
                # Verificar versión SSL/TLS
                if version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                    results["vulnerabilities"].append({
                        "type": "Weak SSL/TLS Version",
                        "severity": "HIGH",
                        "version": version,
                        "description": f"Versión SSL/TLS insegura: {version}"
                    })
                    print(f"          [!] Versión SSL/TLS insegura: {version}")
                
                # Verificar algoritmos de cifrado débiles
                if cipher and "RC4" in cipher[0] or "DES" in cipher[0]:
                    results["vulnerabilities"].append({
                        "type": "Weak Cipher",
                        "severity": "MEDIUM",
                        "cipher": cipher[0],
                        "description": f"Algoritmo de cifrado débil: {cipher[0]}"
                    })
                    
    except Exception as e:
        print(f"          [*] No se pudo analizar SSL: {e}")

def generate_professional_report(results_list, config):
    """Genera un reporte profesional de las pruebas"""
    
    report_folder = config.get("log_folder", "logs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"{report_folder}/security_assessment_{timestamp}.txt"
    
    with open(report_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("         REPORTE DE EVALUACIÓN DE SEGURIDAD - CÁMARAS IP\n")
        f.write("=" * 80 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de dispositivos analizados: {len(results_list)}\n\n")
        
        critical_count = 0
        high_count = 0
        medium_count = 0
        
        for result in results_list:
            f.write(f"\n{'='*60}\n")
            f.write(f"DISPOSITIVO: {result['ip']}\n")
            f.write(f"{'='*60}\n")
            
            # Vulnerabilidades críticas
            vulns = result.get("vulnerabilities", [])
            for vuln in vulns:
                if vuln["severity"] == "CRITICAL":
                    critical_count += 1
                elif vuln["severity"] == "HIGH":
                    high_count += 1
                elif vuln["severity"] == "MEDIUM":
                    medium_count += 1
                    
                f.write(f"\n[{vuln['severity']}] {vuln['type']}\n")
                f.write(f"Descripción: {vuln['description']}\n")
                if 'url' in vuln:
                    f.write(f"URL: {vuln['url']}\n")
                if 'cve' in vuln:
                    f.write(f"CVE: {vuln['cve']}\n")
        
        f.write(f"\n{'='*80}\n")
        f.write("RESUMEN EJECUTIVO\n")
        f.write(f"{'='*80}\n")
        f.write(f"Vulnerabilidades Críticas: {critical_count}\n")
        f.write(f"Vulnerabilidades Altas: {high_count}\n")
        f.write(f"Vulnerabilidades Medias: {medium_count}\n")
        
    print(f"\n[+] Reporte profesional generado: {report_file}")
    return report_file
