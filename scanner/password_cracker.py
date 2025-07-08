"""
Módulo de cracking de contraseñas para SmartCam Auditor
Soporte para John the Ripper, Hashcat y ataques de diccionario
"""

import subprocess
import os
import platform
import json
import time
from pathlib import Path

class PasswordCracker:
    def __init__(self, config_file="config/config.json"):
        self.config = self.load_config(config_file)
        self.john_path = self.config.get('john_path', 'john')
        self.hashcat_path = self.config.get('hashcat_path', 'hashcat')
        self.dictionaries_dir = self.config.get('dictionaries_dir', 'diccionarios')
        
        # Crear directorio de diccionarios si no existe
        os.makedirs(self.dictionaries_dir, exist_ok=True)
        
        # Verificar herramientas disponibles
        self.john_available = self.check_tool_availability('john')
        self.hashcat_available = self.check_tool_availability('hashcat')
        
        print(f"🔧 Password Cracker inicializado:")
        print(f"   📁 Diccionarios: {self.dictionaries_dir}")
        print(f"   🔓 John the Ripper: {'✅' if self.john_available else '❌'}")
        print(f"   🔥 Hashcat: {'✅' if self.hashcat_available else '❌'}")
    
    def load_config(self, config_file):
        """Carga la configuración desde archivo JSON"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"[WARNING] Error cargando configuración: {e}")
            return {}
    
    def check_tool_availability(self, tool_name):
        """Verifica si una herramienta está disponible"""
        try:
            result = subprocess.run([tool_name, '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def check_tools(self):
        """Verifica el estado de todas las herramientas disponibles"""
        return {
            'john': self.john_available,
            'hashcat': self.hashcat_available
        }
    
    def crackear_hashes(self, archivo_hashes, diccionario=None, formato="raw-md5"):
        """
        Crackea hashes usando John the Ripper
        
        Args:
            archivo_hashes (str): Ruta al archivo con hashes
            diccionario (str): Ruta al diccionario (opcional)
            formato (str): Formato de hash (raw-md5, raw-sha1, etc.)
        
        Returns:
            dict: Resultado del cracking con información detallada
        """
        if not self.john_available:
            return {
                'success': False,
                'error': 'John the Ripper no está disponible',
                'suggestion': 'Instalar John the Ripper o configurar la ruta en config.json'
            }
        
        if not os.path.exists(archivo_hashes):
            return {
                'success': False,
                'error': f"Archivo {archivo_hashes} no encontrado"
            }
        
        # Usar diccionario por defecto si no se especifica
        if not diccionario:
            diccionario = os.path.join(self.dictionaries_dir, "rockyou.txt")
        
        if not os.path.exists(diccionario):
            # Intentar descargar rockyou.txt si no existe
            self._download_rockyou_if_needed()
            if not os.path.exists(diccionario):
                return {
                    'success': False,
                    'error': f"Diccionario {diccionario} no encontrado",
                    'suggestion': 'Descargar rockyou.txt o especificar otro diccionario'
                }
        
        print(f"🔓 Crackeando hashes en {archivo_hashes}...")
        print(f"   📖 Diccionario: {diccionario}")
        print(f"   🔢 Formato: {formato}")
        
        start_time = time.time()
        
        try:
            # Comando John the Ripper
            cmd = [
                self.john_path,
                f"--wordlist={diccionario}",
                f"--format={formato}",
                archivo_hashes
            ]
            
            print(f"🚀 Ejecutando: {' '.join(cmd)}")
            
            # Ejecutar John
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Obtener resultados
            show_cmd = [self.john_path, "--show", archivo_hashes]
            show_process = subprocess.run(show_cmd, capture_output=True, text=True)
            
            crack_time = time.time() - start_time
            
            # Parsear resultados
            results = self._parse_john_results(show_process.stdout)
            
            return {
                'success': True,
                'archivo_hashes': archivo_hashes,
                'diccionario': diccionario,
                'formato': formato,
                'tiempo_ejecucion': round(crack_time, 2),
                'hashes_crackeados': len(results),
                'resultados': results,
                'output': process.stdout + process.stderr,
                'john_output': show_process.stdout
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout - El proceso tomó más de 5 minutos',
                'suggestion': 'Usar un diccionario más pequeño o aumentar timeout'
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f"Error ejecutando John: {e}",
                'stderr': e.stderr if hasattr(e, 'stderr') else ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error inesperado: {str(e)}"
            }
    
    def crackear_con_hashcat(self, archivo_hashes, diccionario=None, modo_hash=0):
        """
        Crackea hashes usando Hashcat
        
        Args:
            archivo_hashes (str): Ruta al archivo con hashes
            diccionario (str): Ruta al diccionario
            modo_hash (int): Modo de hash de Hashcat (0=MD5, 100=SHA1, etc.)
        
        Returns:
            dict: Resultado del cracking
        """
        if not self.hashcat_available:
            return {
                'success': False,
                'error': 'Hashcat no está disponible',
                'suggestion': 'Instalar Hashcat o configurar la ruta en config.json'
            }
        
        if not os.path.exists(archivo_hashes):
            return {
                'success': False,
                'error': f"Archivo {archivo_hashes} no encontrado"
            }
        
        if not diccionario:
            diccionario = os.path.join(self.dictionaries_dir, "rockyou.txt")
        
        if not os.path.exists(diccionario):
            return {
                'success': False,
                'error': f"Diccionario {diccionario} no encontrado"
            }
        
        print(f"🔥 Crackeando con Hashcat...")
        print(f"   📁 Hashes: {archivo_hashes}")
        print(f"   📖 Diccionario: {diccionario}")
        print(f"   🔢 Modo: {modo_hash}")
        
        try:
            # Comando Hashcat
            cmd = [
                self.hashcat_path,
                "-m", str(modo_hash),
                "-a", "0",  # Ataque de diccionario
                archivo_hashes,
                diccionario,
                "--show"
            ]
            
            start_time = time.time()
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            crack_time = time.time() - start_time
            
            # Parsear resultados
            results = self._parse_hashcat_results(process.stdout)
            
            return {
                'success': True,
                'herramienta': 'hashcat',
                'archivo_hashes': archivo_hashes,
                'diccionario': diccionario,
                'modo_hash': modo_hash,
                'tiempo_ejecucion': round(crack_time, 2),
                'hashes_crackeados': len(results),
                'resultados': results,
                'output': process.stdout
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout - Hashcat tomó más de 10 minutos'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error ejecutando Hashcat: {str(e)}"
            }
    
    def _parse_john_results(self, output):
        """Parsea la salida de John the Ripper --show"""
        results = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if ':' in line and not line.startswith('#'):
                parts = line.split(':')
                if len(parts) >= 2:
                    usuario = parts[0]
                    password = parts[1]
                    results.append({
                        'usuario': usuario,
                        'password': password,
                        'hash': parts[2] if len(parts) > 2 else ''
                    })
        
        return results
    
    def _parse_hashcat_results(self, output):
        """Parsea la salida de Hashcat"""
        results = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    hash_value = parts[0]
                    password = parts[1]
                    results.append({
                        'hash': hash_value,
                        'password': password
                    })
        
        return results
    
    def _download_rockyou_if_needed(self):
        """Intenta descargar rockyou.txt si no existe"""
        rockyou_path = os.path.join(self.dictionaries_dir, "rockyou.txt")
        
        if os.path.exists(rockyou_path):
            return
        
        print("📥 Rockyou.txt no encontrado. Intentando descargar...")
        
        # URLs comunes para rockyou.txt
        urls = [
            "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt",
            "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Leaked-Databases/rockyou.txt.tar.gz"
        ]
        
        for url in urls:
            try:
                print(f"   🌐 Intentando descargar desde: {url}")
                
                # Usar curl o wget en Windows
                if platform.system().lower() == 'windows':
                    # Intentar con curl (disponible en Windows 10+)
                    result = subprocess.run([
                        'curl', '-L', '-o', rockyou_path, url
                    ], capture_output=True, timeout=60)
                    
                    if result.returncode == 0 and os.path.exists(rockyou_path):
                        print(f"   ✅ Rockyou.txt descargado exitosamente")
                        return
                else:
                    # Linux/Mac - usar wget
                    result = subprocess.run([
                        'wget', '-O', rockyou_path, url
                    ], capture_output=True, timeout=60)
                    
                    if result.returncode == 0 and os.path.exists(rockyou_path):
                        print(f"   ✅ Rockyou.txt descargado exitosamente")
                        return
                        
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        print("   ⚠️ No se pudo descargar rockyou.txt automáticamente")
        print("   💡 Descargar manualmente desde: https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt")
    
    def crear_diccionario_personalizado(self, dispositivos_info, output_file=None):
        """
        Crea un diccionario personalizado basado en información de dispositivos
        
        Args:
            dispositivos_info (list): Lista de dispositivos con información
            output_file (str): Archivo de salida (opcional)
        
        Returns:
            str: Ruta del diccionario creado
        """
        if not output_file:
            output_file = os.path.join(self.dictionaries_dir, "smartcam_custom.txt")
        
        passwords = set()
        
        # Contraseñas comunes de cámaras IP
        common_passwords = [
            "admin", "password", "123456", "12345", "1234", "123",
            "password123", "admin123", "root", "user", "guest",
            "camera", "ipcam", "hikvision", "dahua", "axis",
            "default", "support", "service", "ubnt", "public",
            "private", "system", "operator", "supervisor",
            "888888", "666666", "000000", "111111", "888",
            "pass", "passwd", "qwerty", "abc123", "welcome"
        ]
        
        passwords.update(common_passwords)
        
        # Generar contraseñas basadas en información de dispositivos
        for device in dispositivos_info:
            ip = device.get('ip', '')
            device_type = device.get('device_type', '')
            fabricante = device.get('fabricante', '')
            
            # Agregar variaciones de IP
            if ip:
                ip_parts = ip.split('.')
                passwords.add(ip.replace('.', ''))
                passwords.add(''.join(ip_parts[-2:]))  # Últimos dos octetos
                passwords.add(ip_parts[-1])  # Último octeto
            
            # Agregar fabricante en minúsculas
            if fabricante:
                passwords.add(fabricante.lower())
                passwords.add(fabricante.lower() + "123")
                passwords.add(fabricante.lower() + "admin")
            
            # Patrones comunes por tipo de dispositivo
            if 'hikvision' in device_type.lower():
                passwords.update(['hik12345', 'hikuser', 'hik123'])
            elif 'dahua' in device_type.lower():
                passwords.update(['dahua123', 'dahuauser', 'dh123'])
            elif 'axis' in device_type.lower():
                passwords.update(['axis123', 'axisuser', 'pass'])
        
        # Escribir diccionario
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for password in sorted(passwords):
                    f.write(password + '\n')
            
            print(f"📝 Diccionario personalizado creado: {output_file}")
            print(f"   📊 Total contraseñas: {len(passwords)}")
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error creando diccionario: {e}")
            return None
    
    def generar_hashes_test(self, passwords, output_file=None, hash_type="md5"):
        """
        Genera archivo de hashes para pruebas
        
        Args:
            passwords (list): Lista de contraseñas
            output_file (str): Archivo de salida
            hash_type (str): Tipo de hash (md5, sha1, sha256)
        
        Returns:
            str: Ruta del archivo de hashes generado
        """
        import hashlib
        
        if not output_file:
            output_file = f"test_hashes_{hash_type}.txt"
        
        try:
            with open(output_file, 'w') as f:
                for password in passwords:
                    if hash_type.lower() == "md5":
                        hash_value = hashlib.md5(password.encode()).hexdigest()
                    elif hash_type.lower() == "sha1":
                        hash_value = hashlib.sha1(password.encode()).hexdigest()
                    elif hash_type.lower() == "sha256":
                        hash_value = hashlib.sha256(password.encode()).hexdigest()
                    else:
                        hash_value = hashlib.md5(password.encode()).hexdigest()
                    
                    f.write(f"{hash_value}\n")
            
            print(f"🔢 Archivo de hashes generado: {output_file}")
            print(f"   📊 Total hashes: {len(passwords)}")
            print(f"   🔐 Tipo: {hash_type.upper()}")
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error generando hashes: {e}")
            return None


# Función de compatibilidad con el código original del usuario
def crackear_hashes(archivo_hashes, diccionario="diccionarios/rockyou.txt"):
    """
    Función original del usuario mejorada
    
    Args:
        archivo_hashes (str): Archivo con hashes
        diccionario (str): Diccionario a usar
    
    Returns:
        str: Resultado del cracking
    """
    cracker = PasswordCracker()
    resultado = cracker.crackear_hashes(archivo_hashes, diccionario)
    
    if resultado['success']:
        output = f"🔓 Cracking completado exitosamente!\n"
        output += f"📁 Archivo: {resultado['archivo_hashes']}\n"
        output += f"📖 Diccionario: {resultado['diccionario']}\n"
        output += f"⏱️ Tiempo: {resultado['tiempo_ejecucion']} segundos\n"
        output += f"✅ Hashes crackeados: {resultado['hashes_crackeados']}\n\n"
        
        if resultado['resultados']:
            output += "🔑 CONTRASEÑAS ENCONTRADAS:\n"
            output += "=" * 50 + "\n"
            for i, result in enumerate(resultado['resultados'], 1):
                output += f"{i}. Usuario: {result['usuario']} | Password: {result['password']}\n"
        else:
            output += "❌ No se encontraron contraseñas\n"
        
        return output
    else:
        return f"❌ Error: {resultado['error']}"


# Función de conveniencia para SmartCam Auditor
def crackear_hashes_smartcam(dispositivos_detectados, archivo_hashes=None):
    """
    Función específica para SmartCam Auditor que integra el cracking
    con la información de dispositivos detectados
    
    Args:
        dispositivos_detectados (list): Lista de dispositivos detectados
        archivo_hashes (str): Archivo de hashes (opcional)
    
    Returns:
        dict: Resultados del cracking integrado
    """
    cracker = PasswordCracker()
    
    # Crear diccionario personalizado basado en dispositivos
    diccionario_custom = cracker.crear_diccionario_personalizado(dispositivos_detectados)
    
    if not archivo_hashes:
        # Generar hashes de prueba si no se proporciona archivo
        test_passwords = ["admin", "password", "123456", "admin123"]
        archivo_hashes = cracker.generar_hashes_test(test_passwords)
    
    # Intentar cracking con diccionario personalizado
    resultado_custom = cracker.crackear_hashes(archivo_hashes, diccionario_custom)
    
    # Si no se encontraron resultados, probar con rockyou.txt
    resultado_rockyou = None
    if resultado_custom['success'] and resultado_custom['hashes_crackeados'] == 0:
        rockyou_path = os.path.join(cracker.dictionaries_dir, "rockyou.txt")
        if os.path.exists(rockyou_path):
            resultado_rockyou = cracker.crackear_hashes(archivo_hashes, rockyou_path)
    
    return {
        'custom_dict_result': resultado_custom,
        'rockyou_result': resultado_rockyou,
        'devices_analyzed': len(dispositivos_detectados),
        'custom_dictionary': diccionario_custom
    }
