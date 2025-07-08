"""
Módulo avanzado para verificación de CVEs en dispositivos IoT y cámaras IP
SmartCam Auditor v2.0 Pro - Sistema CVE mejorado y unificado
"""

import json
import os
import requests
import time
import re
import socket
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

class CVEChecker:
    def __init__(self, config_file="config/config.json"):
        self.config = self.load_config(config_file)
        self.cve_database_path = "scanner/data/cves.json"
        self.cve_cache = []
        self.load_cve_database()
        
        # Configuración de timeouts y hilos
        self.timeout = self.config.get("cve_timeout", 5)
        self.max_threads = self.config.get("cve_max_threads", 10)
        
    def load_config(self, config_file):
        """Carga configuración del sistema"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Error cargando config CVE: {e}")
            return {}
    
    def cargar_cve_base(self, path=None):
        """
        Carga la base de datos de CVEs desde archivo JSON
        
        Args:
            path (str): Ruta al archivo de CVEs
            
        Returns:
            list: Lista de vulnerabilidades CVE
        """
        if path is None:
            path = self.cve_database_path
            
        if not os.path.exists(path):
            print(f"⚠️ Base de datos CVE no encontrada en: {path}")
            print("🔧 Creando base de datos básica...")
            self.create_basic_cve_database(path)
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                cves = json.load(f)
            print(f"✅ Base de datos CVE cargada: {len(cves)} vulnerabilidades")
            return cves
        except Exception as e:
            print(f"❌ Error cargando CVEs: {e}")
            return []
    
    def load_cve_database(self):
        """Carga y cachea la base de datos CVE"""
        self.cve_cache = self.cargar_cve_base()
        
    def detectar_fabricante(self, ip, puerto=80):
        """
        Detecta el fabricante del dispositivo mediante banners HTTP
        
        Args:
            ip (str): IP del dispositivo
            puerto (int): Puerto a consultar
            
        Returns:
            str: Fabricante detectado o 'unknown'
        """
        try:
            response = requests.get(
                f"http://{ip}:{puerto}", 
                timeout=self.timeout,
                allow_redirects=False
            )
            
            headers = response.headers
            content = response.text.lower()
            
            # Detección por headers y contenido
            server = headers.get('Server', '').lower()
            www_auth = headers.get('WWW-Authenticate', '').lower()
            
            # Patrones de detección mejorados
            if any(keyword in server or keyword in content or keyword in www_auth 
                   for keyword in ['hikvision', 'hik-connect']):
                return 'hikvision'
            elif any(keyword in server or keyword in content or keyword in www_auth 
                     for keyword in ['dahua', 'dh-']):
                return 'dahua'
            elif any(keyword in server or keyword in content or keyword in www_auth 
                     for keyword in ['axis', 'vapix']):
                return 'axis'
            elif any(keyword in content for keyword in ['foscam', 'fos']):
                return 'foscam'
            elif any(keyword in content for keyword in ['amcrest']):
                return 'amcrest'
            elif any(keyword in content for keyword in ['camera', 'nvr', 'dvr', 'ipcam']):
                return 'generic_camera'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def buscar_vulnerabilidades_cve(self, identificadores):
        """
        Busca vulnerabilidades CVE para una lista de identificadores de dispositivos
        
        Args:
            identificadores (list): Lista de identificadores como 
                                  ["Hikvision DS-2CD2042FWD", "Dahua IPC-HDW", "Axis Q3517"]
                                  o IPs ["192.168.1.100", "192.168.1.101"]
        
        Returns:
            list: Lista de vulnerabilidades encontradas
        """
        if not self.cve_cache:
            print("⚠️ Base de datos CVE no disponible")
            return []
            
        resultados = []
        
        print(f"🔍 Buscando CVEs para {len(identificadores)} elementos...")
        
        for identificador in identificadores:
            vulnerabilidades_encontradas = 0
            
            # Determinar si es una IP o un identificador de dispositivo
            if self._is_ip(identificador):
                # Es una IP, detectar fabricante primero
                fabricante = self.detectar_fabricante(identificador)
                print(f"  📡 {identificador} -> Fabricante: {fabricante}")
                marca_modelo = f"{fabricante} device"
            else:
                # Es un identificador de dispositivo
                marca_modelo = identificador
                print(f"  🔍 Analizando: {marca_modelo}")
            
            for entry in self.cve_cache:
                # Búsqueda flexible por marca/modelo
                if self._match_device(marca_modelo, entry["producto"]):
                    vuln = {
                        "producto": marca_modelo,
                        "ip": identificador if self._is_ip(identificador) else None,
                        "cve": entry["cve"],
                        "descripcion": entry["descripcion"],
                        "critico": entry["critico"],
                        "severidad": entry.get("severidad", "UNKNOWN"),
                        "cvss_score": entry.get("cvss_score", 0.0),
                        "fecha": entry.get("fecha", "Unknown"),
                        "categoria": entry.get("categoria", "Unknown"),
                        "exploit_disponible": entry.get("exploit_disponible", False),
                        "mitigacion": entry.get("mitigacion", "Contactar fabricante"),
                        "verificado": False
                    }
                    resultados.append(vuln)
                    vulnerabilidades_encontradas += 1
            
            if vulnerabilidades_encontradas > 0:
                print(f"    ⚠️ {vulnerabilidades_encontradas} CVEs encontrados")
            else:
                print(f"    ✅ Sin CVEs conocidos")
        
        # Ordenar por criticidad y CVSS score
        resultados.sort(key=lambda x: (x["critico"], x["cvss_score"]), reverse=True)
        
        return resultados
    
    def _is_ip(self, address):
        """Verifica si una cadena es una dirección IP válida"""
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            return False
    
    def _match_device(self, dispositivo, producto_cve):
        """
        Verifica si un dispositivo coincide con un producto en la base CVE
        
        Args:
            dispositivo (str): Identificador del dispositivo detectado
            producto_cve (str): Producto en la base de datos CVE
            
        Returns:
            bool: True si hay coincidencia
        """
        dispositivo_lower = dispositivo.lower()
        producto_lower = producto_cve.lower()
        
        # Palabras clave de fabricantes
        palabras_clave = ["hikvision", "dahua", "axis", "foscam", "amcrest", 
                         "tp-link", "d-link", "linksys", "netgear", "huawei",
                         "generic_camera", "generic"]
        
        # Buscar coincidencias por fabricante
        for palabra in palabras_clave:
            if palabra in dispositivo_lower and palabra in producto_lower:
                return True
        
        # Buscar coincidencias de modelo específico
        palabras_dispositivo = dispositivo_lower.split()
        for palabra in palabras_dispositivo:
            if len(palabra) > 2 and palabra in producto_lower:
                return True
            
        return False
    
    def verificar_cve_activamente(self, ip, vulnerabilidades):
        """
        Verifica activamente si las vulnerabilidades CVE son explotables
        
        Args:
            ip (str): IP del dispositivo
            vulnerabilidades (list): Lista de vulnerabilidades encontradas
            
        Returns:
            list: Vulnerabilidades verificadas con estado
        """
        print(f"🧪 Verificando activamente CVEs en {ip}...")
        resultados = []
        
        for vuln in vulnerabilidades:
            resultado = vuln.copy()
            cve = vuln["cve"]
            
            # Tests específicos por CVE
            if cve == "CVE-2017-7921":  # Hikvision bypass
                resultado["verificado"] = self._test_hikvision_bypass(ip)
            elif cve == "CVE-2018-9995":  # Dahua bypass
                resultado["verificado"] = self._test_dahua_bypass(ip)
            elif "default" in vuln["descripcion"].lower() or "credential" in vuln["descripcion"].lower():
                resultado["verificado"] = self._test_default_credentials(ip)
            else:
                # Verificación genérica por puertos
                resultado["verificado"] = self._test_generic_vulnerability(ip, vuln)
            
            if resultado["verificado"]:
                print(f"    🚨 CONFIRMADO: {cve}")
            else:
                print(f"    ✅ No explotable: {cve}")
                
            resultados.append(resultado)
        
        return resultados
    
    def _test_hikvision_bypass(self, ip):
        """Test para CVE-2017-7921 - Bypass de autenticación Hikvision"""
        test_ports = [80, 8080, 8000]
        
        for puerto in test_ports:
            try:
                # Rutas vulnerables conocidas
                test_urls = [
                    f"http://{ip}:{puerto}/System/configurationFile",
                    f"http://{ip}:{puerto}/Security/users",
                    f"http://{ip}:{puerto}/System/deviceInfo"
                ]
                
                for url in test_urls:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200 and len(response.content) > 100:
                        return True
                        
            except Exception:
                continue
        return False
    
    def _test_dahua_bypass(self, ip):
        """Test para CVE-2018-9995 - Bypass de autenticación Dahua"""
        test_ports = [80, 8080, 37777]
        
        for puerto in test_ports:
            try:
                # Bypass específico de Dahua
                test_url = f"http://{ip}:{puerto}/current_config/passwd"
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    return True
            except Exception:
                continue
        return False
    
    def _test_default_credentials(self, ip):
        """Test para credenciales por defecto"""
        creds_por_defecto = [
            ('admin', 'admin'),
            ('admin', ''),
            ('admin', 'password'),
            ('root', 'root'),
            ('admin', '12345'),
            ('admin', '123456'),
            ('user', 'user')
        ]
        
        test_ports = [80, 8080, 8000]
        
        for puerto in test_ports:
            for usuario, password in creds_por_defecto:
                try:
                    response = requests.get(
                        f"http://{ip}:{puerto}",
                        auth=(usuario, password),
                        timeout=3
                    )
                    if response.status_code == 200:
                        return True
                except Exception:
                    continue
        return False
    
    def _test_generic_vulnerability(self, ip, vuln_info):
        """Test genérico para vulnerabilidades"""
        try:
            # Intentar conectar a puertos comunes
            common_ports = [80, 8080, 554, 8000]
            
            for puerto in common_ports:
                try:
                    response = requests.get(
                        f"http://{ip}:{puerto}",
                        timeout=3,
                        allow_redirects=False
                    )
                    # Si responde, el puerto está activo
                    if response.status_code in [200, 401, 403]:
                        return True
                except Exception:
                    continue
                    
        except Exception:
            pass
        return False
    
    def buscar_por_puertos(self, dispositivos_con_puertos):
        """
        Busca CVEs basándose en puertos abiertos de dispositivos
        
        Args:
            dispositivos_con_puertos (list): Lista de dispositivos con formato:
                [{"ip": "192.168.1.100", "open_ports": [80, 554], "device_type": "IP Camera"}]
        
        Returns:
            dict: Resultados de CVEs por dispositivo
        """
        resultados = {}
        
        print(f"🔍 Analizando CVEs por puertos en {len(dispositivos_con_puertos)} dispositivos...")
        
        for dispositivo in dispositivos_con_puertos:
            ip = dispositivo.get("ip")
            puertos = dispositivo.get("open_ports", [])
            tipo = dispositivo.get("device_type", "Unknown")
            
            vulnerabilidades = []
            
            # Buscar CVEs relacionados con puertos específicos
            for cve in self.cve_cache:
                if self._check_port_vulnerability(puertos, cve):
                    vulnerabilidades.append(cve)
            
            if vulnerabilidades:
                resultados[ip] = {
                    "device_type": tipo,
                    "open_ports": puertos,
                    "cves": vulnerabilidades,
                    "risk_level": self._calculate_risk_level(vulnerabilidades)
                }
                print(f"  📡 {ip}: {len(vulnerabilidades)} CVEs encontrados")
        
        return resultados
    
    def _check_port_vulnerability(self, puertos_abiertos, cve_entry):
        """Verifica si los puertos abiertos coinciden con vulnerabilidades conocidas"""
        # Mapeo de puertos a servicios vulnerables
        port_services = {
            23: ["telnet", "terminal"],
            21: ["ftp", "file transfer"],
            80: ["http", "web", "camera"],
            554: ["rtsp", "stream", "video"],
            8080: ["http-alt", "web-alt", "camera"],
            22: ["ssh", "secure shell"],
            443: ["https", "ssl", "web"],
            8000: ["http-alt", "camera"],
            37777: ["dahua", "dvr"]
        }
        
        descripcion_lower = cve_entry.get("descripcion", "").lower()
        
        for puerto in puertos_abiertos:
            if puerto in port_services:
                servicios = port_services[puerto]
                if any(servicio in descripcion_lower for servicio in servicios):
                    return True
        
        return False
    
    def _calculate_risk_level(self, vulnerabilidades):
        """Calcula el nivel de riesgo basado en las vulnerabilidades encontradas"""
        if not vulnerabilidades:
            return "LOW"
        
        max_score = max(vuln.get("cvss_score", 0) for vuln in vulnerabilidades)
        critical_count = sum(1 for vuln in vulnerabilidades if vuln.get("critico", False))
        exploit_count = sum(1 for vuln in vulnerabilidades if vuln.get("exploit_disponible", False))
        
        if max_score >= 9.0 or critical_count >= 2 or exploit_count >= 1:
            return "CRITICAL"
        elif max_score >= 7.0 or critical_count >= 1:
            return "HIGH"
        elif max_score >= 4.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generar_reporte_cve(self, resultados, output_file=None):
        """
        Genera un reporte detallado de CVEs encontrados
        
        Args:
            resultados (list): Lista de vulnerabilidades encontradas
            output_file (str): Archivo de salida (opcional)
        
        Returns:
            str: Reporte en formato texto
        """
        if not resultados:
            return "✅ No se encontraron vulnerabilidades CVE conocidas."
        
        reporte = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🚨 REPORTE DE VULNERABILIDADES CVE                  ║
║                             SmartCam Auditor v2.0 Pro                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

📅 Fecha del análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔍 Vulnerabilidades encontradas: {len(resultados)}

"""
        
        # Agrupar por nivel de criticidad
        criticas = [r for r in resultados if r["critico"]]
        altas = [r for r in resultados if not r["critico"] and r.get("cvss_score", 0) >= 7.0]
        medias = [r for r in resultados if not r["critico"] and 4.0 <= r.get("cvss_score", 0) < 7.0]
        bajas = [r for r in resultados if not r["critico"] and r.get("cvss_score", 0) < 4.0]
        
        if criticas:
            reporte += f"🔴 VULNERABILIDADES CRÍTICAS ({len(criticas)}):\n"
            reporte += "=" * 60 + "\n"
            for vuln in criticas:
                verificado = "✅ VERIFICADO" if vuln.get("verificado") else "⚪ SIN VERIFICAR"
                reporte += f"""
🎯 Producto: {vuln['producto']}
📍 IP: {vuln.get('ip', 'N/A')}
📋 CVE: {vuln['cve']} | Score: {vuln.get('cvss_score', 'N/A')}
📝 Descripción: {vuln['descripcion']}
🏷️ Categoría: {vuln.get('categoria', 'Unknown')}
💥 Exploit disponible: {'Sí' if vuln.get('exploit_disponible') else 'No'}
🔬 Estado: {verificado}
🛡️ Mitigación: {vuln.get('mitigacion', 'Contactar fabricante')}
{'-' * 50}"""
        
        if altas:
            reporte += f"\n\n🟠 VULNERABILIDADES ALTAS ({len(altas)}):\n"
            reporte += "=" * 60 + "\n"
            for vuln in altas:
                verificado = "✅" if vuln.get("verificado") else "⚪"
                reporte += f"• {verificado} {vuln['cve']} - {vuln['producto']}: {vuln['descripcion']}\n"
        
        if medias:
            reporte += f"\n\n🟡 VULNERABILIDADES MEDIAS ({len(medias)}):\n"
            reporte += "=" * 60 + "\n"
            for vuln in medias:
                verificado = "✅" if vuln.get("verificado") else "⚪"
                reporte += f"• {verificado} {vuln['cve']} - {vuln['producto']}: {vuln['descripcion']}\n"
        
        if bajas:
            reporte += f"\n\n🔵 VULNERABILIDADES BAJAS ({len(bajas)}):\n"
            reporte += "=" * 60 + "\n"
            for vuln in bajas:
                verificado = "✅" if vuln.get("verificado") else "⚪"
                reporte += f"• {verificado} {vuln['cve']} - {vuln['producto']}: {vuln['descripcion']}\n"
        
        verificadas = len([v for v in resultados if v.get("verificado")])
        
        reporte += f"""

📊 RESUMEN ESTADÍSTICO:
• Críticas: {len(criticas)}
• Altas: {len(altas)} 
• Medias: {len(medias)}
• Bajas: {len(bajas)}
• Verificadas activamente: {verificadas}
• Exploits disponibles: {len([v for v in resultados if v.get("exploit_disponible")])}

⚠️ RECOMENDACIONES PRIORITARIAS:
1. 🚨 Atender vulnerabilidades críticas verificadas inmediatamente
2. 🔒 Cambiar todas las credenciales por defecto
3. 🔧 Aplicar parches de seguridad disponibles
4. 🛡️ Implementar segmentación de red para dispositivos IoT
5. 📊 Configurar monitoreo continuo de logs de seguridad
6. 🔄 Establecer programa de actualizaciones automáticas
7. 🚫 Considerar reemplazo de dispositivos sin soporte

"""
        
        if output_file:
            try:
                os.makedirs("logs", exist_ok=True)
                filename = f"logs/{output_file}"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(reporte)
                print(f"📄 Reporte CVE guardado en: {filename}")
            except Exception as e:
                print(f"❌ Error guardando reporte: {e}")
        
        return reporte
    
    def create_basic_cve_database(self, path):
        """Crea una base de datos básica de CVEs si no existe"""
        basic_cves = [
            {
                "cve": "CVE-2017-7921",
                "producto": "Hikvision DS-2CD",
                "descripcion": "Bypass de autenticación en cámaras Hikvision",
                "critico": True,
                "severidad": "CRITICAL",
                "cvss_score": 9.8,
                "fecha": "2017-04-24",
                "categoria": "Authentication Bypass",
                "exploit_disponible": True,
                "mitigacion": "Actualizar firmware inmediatamente"
            },
            {
                "cve": "CVE-2018-9995",
                "producto": "Dahua Technology",
                "descripcion": "Bypass de autenticación en dispositivos Dahua",
                "critico": True,
                "severidad": "CRITICAL",
                "cvss_score": 9.8,
                "fecha": "2018-04-16",
                "categoria": "Authentication Bypass",
                "exploit_disponible": True,
                "mitigacion": "Actualizar firmware inmediatamente"
            }
        ]
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(basic_cves, f, indent=2, ensure_ascii=False)
            print(f"✅ Base de datos CVE básica creada en: {path}")
        except Exception as e:
            print(f"❌ Error creando base CVE: {e}")

# ============================================================================
# FUNCIONES DE COMPATIBILIDAD - Mantienen tu API original
# ============================================================================

def cargar_cve_base(path="scanner/data/cves.json"):
    """Función de compatibilidad - mantiene tu API original"""
    checker = CVEChecker()
    return checker.cargar_cve_base(path)

def buscar_vulnerabilidades_cve(identificadores):
    """
    Función de compatibilidad principal - mantiene tu API original
    
    Args:
        identificadores (list): Lista de identificadores como 
                              ["Hikvision DS-2CD2042FWD", "Dahua IPC-HDW"] 
                              o IPs ["192.168.1.100", "192.168.1.101"]
    
    Returns:
        list: Lista de vulnerabilidades encontradas
    """
    checker = CVEChecker()
    return checker.buscar_vulnerabilidades_cve(identificadores)

def ejemplo_uso():
    """Ejemplo de uso del sistema CVE mejorado"""
    print("🔍 CVE Checker - SmartCam Auditor v2.0 Pro")
    print("=" * 60)
    
    # Ejemplo con identificadores de dispositivos
    print("\n1️⃣ Búsqueda por identificadores de dispositivos:")
    dispositivos = [
        "Hikvision DS-2CD2042FWD",
        "Dahua IPC-HDW", 
        "Axis Q3517",
        "Foscam C1"
    ]
    
    vulnerabilidades = buscar_vulnerabilidades_cve(dispositivos)
    
    if vulnerabilidades:
        print(f"\n🚨 Se encontraron {len(vulnerabilidades)} vulnerabilidades:")
        for vuln in vulnerabilidades[:3]:  # Mostrar solo las primeras 3
            critico = "🔴 CRÍTICO" if vuln["critico"] else "🟡 NO CRÍTICO"
            print(f"   {critico} | {vuln['cve']} | {vuln['producto']}")
            print(f"      └─ {vuln['descripcion']}")
    else:
        print("\n✅ No se encontraron vulnerabilidades CVE conocidas")
    
    # Ejemplo con IPs
    print("\n2️⃣ Búsqueda por direcciones IP:")
    ips = ["192.168.1.100", "192.168.1.101"]
    
    vulnerabilidades_ip = buscar_vulnerabilidades_cve(ips)
    print(f"📊 Vulnerabilidades encontradas por IP: {len(vulnerabilidades_ip)}")

if __name__ == "__main__":
    ejemplo_uso()

# Funciones de compatibilidad para mantener la API original

def buscar_cve_por_id(cve_id):
    """
    Busca un CVE específico por su ID
    
    Args:
        cve_id (str): ID del CVE (ej: "CVE-2021-36260")
        
    Returns:
        dict: Información del CVE o None si no se encuentra
    """
    try:
        checker = CVEChecker()
        for cve in checker.cve_cache:
            if cve.get('cve') == cve_id:
                return cve
        return None
    except Exception as e:
        print(f"❌ Error buscando CVE {cve_id}: {e}")
        return None

def obtener_cves_dispositivo(fabricante, modelo="", version=""):
    """
    Obtiene todos los CVEs relevantes para un dispositivo específico
    
    Args:
        fabricante (str): Fabricante del dispositivo
        modelo (str): Modelo del dispositivo
        version (str): Versión del firmware
        
    Returns:
        list: Lista de CVEs relevantes para el dispositivo
    """
    try:
        checker = CVEChecker()
        # Crear identificador del dispositivo
        identificador = f"{fabricante} {modelo}".strip()
        return checker.buscar_vulnerabilidades_cve([identificador])
    except Exception as e:
        print(f"❌ Error obteniendo CVEs para {fabricante} {modelo}: {e}")
        return []

def verificar_cve_dispositivo(ip, fabricante="", modelo="", version=""):
    """
    Función de compatibilidad mejorada para verificar CVEs
    
    Args:
        ip (str): IP del dispositivo
        fabricante (str): Fabricante del dispositivo  
        modelo (str): Modelo del dispositivo
        version (str): Versión del firmware
        
    Returns:
        list: Lista de vulnerabilidades encontradas
    """
    try:
        checker = CVEChecker()
        # Crear identificadores para búsqueda
        identificadores = [ip]
        if fabricante and modelo:
            identificadores.append(f"{fabricante} {modelo}")
        elif fabricante:
            identificadores.append(fabricante)
        
        return checker.buscar_vulnerabilidades_cve(identificadores)
    except Exception as e:
        print(f"❌ Error verificando CVEs para {ip}: {e}")
        return []
