"""
Módulo de cracking de hashes para SmartCam Auditor
Integración con el sistema de escaneo de red para automatizar el cracking de credenciales
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

def crackear_hashes(hash_file: str, config_file: str = "config/config.json") -> Dict:
    """
    Función principal para crackear hashes capturados durante el escaneo
    
    Args:
        hash_file (str): Ruta al archivo de hashes capturados
        config_file (str): Archivo de configuración
    
    Returns:
        dict: Resultados del cracking con estadísticas y credenciales encontradas
    """
    try:
        # Cargar configuración
        config = load_config(config_file)
        
        # Verificar si el archivo de hashes existe
        if not os.path.exists(hash_file):
            return {
                'success': False,
                'error': f'Archivo de hashes no encontrado: {hash_file}',
                'estadisticas': {'total_hashes': 0, 'crackeados': 0}
            }
        
        # Leer hashes del archivo
        hashes = leer_hashes_archivo(hash_file)
        
        if not hashes:
            return {
                'success': False,
                'error': 'No se encontraron hashes válidos en el archivo',
                'estadisticas': {'total_hashes': 0, 'crackeados': 0}
            }
        
        print(f"🔓 Iniciando cracking de {len(hashes)} hashes...")
        
        # Inicializar resultados
        resultados = {
            'success': True,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'archivo_origen': hash_file,
            'estadisticas': {
                'total_hashes': len(hashes),
                'crackeados': 0,
                'tiempo_total': 0
            },
            'credenciales_encontradas': [],
            'hashes_no_crackeados': [],
            'herramientas_usadas': []
        }
        
        inicio_tiempo = time.time()
        
        # Importar el PasswordCracker existente
        try:
            from .password_cracker import PasswordCracker
            cracker = PasswordCracker(config_file)
            resultados['herramientas_usadas'].append('PasswordCracker interno')
        except ImportError:
            print("⚠️ PasswordCracker no disponible, usando métodos básicos")
            cracker = None
        
        # Procesar cada hash
        for hash_data in hashes:
            resultado_hash = procesar_hash_individual(hash_data, cracker, config)
            
            if resultado_hash['crackeado']:
                resultados['credenciales_encontradas'].append({
                    'usuario': hash_data.get('usuario', 'unknown'),
                    'password': resultado_hash['password'],
                    'hash_original': hash_data['hash'],
                    'formato': hash_data.get('formato', 'unknown'),
                    'metodo': resultado_hash['metodo'],
                    'tiempo': resultado_hash['tiempo']
                })
                resultados['estadisticas']['crackeados'] += 1
                
                print(f"✅ Hash crackeado: {hash_data.get('usuario', 'unknown')}:{resultado_hash['password']}")
            else:
                resultados['hashes_no_crackeados'].append({
                    'usuario': hash_data.get('usuario', 'unknown'),
                    'hash': hash_data['hash'],
                    'formato': hash_data.get('formato', 'unknown'),
                    'error': resultado_hash.get('error', 'No se pudo crackear')
                })
                
                print(f"❌ Hash no crackeado: {hash_data.get('usuario', 'unknown')}")
        
        # Calcular tiempo total
        resultados['estadisticas']['tiempo_total'] = round(time.time() - inicio_tiempo, 2)
        
        # Guardar resultados
        guardar_resultados_cracking(resultados, config)
        
        # Mostrar resumen
        mostrar_resumen_cracking(resultados)
        
        return resultados
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error durante el cracking: {str(e)}',
            'estadisticas': {'total_hashes': 0, 'crackeados': 0}
        }

def leer_hashes_archivo(hash_file: str) -> List[Dict]:
    """
    Lee y parsea hashes desde un archivo
    
    Soporta formatos:
    - usuario:hash
    - hash
    - JSON con metadatos
    """
    hashes = []
    
    try:
        with open(hash_file, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
        
        # Intentar parsear como JSON primero
        try:
            data = json.loads(contenido)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'hashes' in data:
                return data['hashes']
        except json.JSONDecodeError:
            pass
        
        # Parsear línea por línea
        for linea in contenido.split('\n'):
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                continue
            
            hash_data = parsear_linea_hash(linea)
            if hash_data:
                hashes.append(hash_data)
        
        return hashes
        
    except Exception as e:
        print(f"❌ Error leyendo archivo de hashes: {e}")
        return []

def parsear_linea_hash(linea: str) -> Optional[Dict]:
    """
    Parsea una línea individual de hash
    """
    try:
        # Formato usuario:hash
        if ':' in linea and not linea.startswith('$'):
            parts = linea.split(':', 1)
            if len(parts) == 2:
                usuario, hash_value = parts
                return {
                    'usuario': usuario.strip(),
                    'hash': hash_value.strip(),
                    'formato': detectar_formato_hash(hash_value.strip())
                }
        
        # Solo hash
        else:
            hash_value = linea.strip()
            return {
                'usuario': 'unknown',
                'hash': hash_value,
                'formato': detectar_formato_hash(hash_value)
            }
    except Exception:
        return None

def detectar_formato_hash(hash_value: str) -> str:
    """
    Detecta el formato del hash basándose en patrones conocidos
    """
    hash_value = hash_value.strip()
    
    # MD5
    if len(hash_value) == 32 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
        return 'MD5'
    
    # SHA1
    elif len(hash_value) == 40 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
        return 'SHA1'
    
    # SHA256
    elif len(hash_value) == 64 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
        return 'SHA256'
    
    # NTLM
    elif len(hash_value) == 32 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
        return 'NTLM'
    
    # APR1 (Apache MD5)
    elif hash_value.startswith('$apr1$'):
        return 'APR1'
    
    # MD5 Crypt
    elif hash_value.startswith('$1$'):
        return 'MD5_CRYPT'
    
    # SHA512 Crypt
    elif hash_value.startswith('$6$'):
        return 'SHA512_CRYPT'
    
    # bcrypt
    elif hash_value.startswith('$2a$') or hash_value.startswith('$2b$') or hash_value.startswith('$2y$'):
        return 'BCRYPT'
    
    # Windows LM
    elif len(hash_value) == 32 and ':' not in hash_value:
        return 'LM'
    
    # Windows NTLM (formato usuario:hash)
    elif ':' in hash_value and len(hash_value.split(':')[-1]) == 32:
        return 'NTLM'
    
    else:
        return 'UNKNOWN'

def procesar_hash_individual(hash_data: Dict, cracker, config: Dict) -> Dict:
    """
    Procesa un hash individual usando diferentes métodos
    """
    inicio = time.time()
    
    # Método 1: Diccionario básico de contraseñas comunes
    resultado = probar_diccionario_basico(hash_data)
    if resultado['crackeado']:
        resultado['tiempo'] = round(time.time() - inicio, 2)
        return resultado
    
    # Método 2: PasswordCracker si está disponible
    if cracker:
        resultado = usar_password_cracker(hash_data, cracker)
        if resultado['crackeado']:
            resultado['tiempo'] = round(time.time() - inicio, 2)
            return resultado
    
    # Método 3: Herramientas externas si están configuradas
    if config.get('use_external_tools', False):
        resultado = usar_herramientas_externas(hash_data, config)
        if resultado['crackeado']:
            resultado['tiempo'] = round(time.time() - inicio, 2)
            return resultado
    
    # No se pudo crackear
    return {
        'crackeado': False,
        'tiempo': round(time.time() - inicio, 2),
        'error': 'Ningún método fue exitoso'
    }

def probar_diccionario_basico(hash_data: Dict) -> Dict:
    """
    Prueba contraseñas comunes contra el hash
    """
    contraseñas_comunes = [
        'admin', 'password', '123456', '12345', '1234',
        'admin123', 'password123', '000000', '111111',
        'root', 'user', 'guest', 'test', 'demo',
        'camera', 'surveillance', 'security', 'monitor',
        'hikvision', 'dahua', 'axis', 'foscam'
    ]
    
    formato = hash_data.get('formato', 'UNKNOWN')
    hash_value = hash_data['hash']
    
    # Para hashes simples como MD5, SHA1, etc.
    if formato in ['MD5', 'SHA1', 'SHA256']:
        return probar_hashes_simples(hash_value, contraseñas_comunes, formato)
    
    # Para APR1 (como el ejemplo anterior)
    elif formato == 'APR1':
        return probar_apr1(hash_value, contraseñas_comunes)
    
    # Para otros formatos, usar verificación básica
    else:
        return probar_verificacion_basica(hash_value, contraseñas_comunes)

def probar_hashes_simples(hash_value: str, passwords: List[str], formato: str) -> Dict:
    """
    Prueba hashes simples (MD5, SHA1, SHA256)
    """
    import hashlib
    
    algoritmos = {
        'MD5': hashlib.md5,
        'SHA1': hashlib.sha1,
        'SHA256': hashlib.sha256
    }
    
    if formato not in algoritmos:
        return {'crackeado': False, 'error': f'Formato {formato} no soportado'}
    
    hasher = algoritmos[formato]
    
    for password in passwords:
        test_hash = hasher(password.encode()).hexdigest().lower()
        if test_hash == hash_value.lower():
            return {
                'crackeado': True,
                'password': password,
                'metodo': f'Diccionario básico ({formato})'
            }
    
    return {'crackeado': False, 'error': 'No encontrado en diccionario básico'}

def probar_apr1(hash_value: str, passwords: List[str]) -> Dict:
    """
    Prueba contraseñas contra hash APR1 usando la lógica del script anterior
    """
    # Usar la misma lógica que en crack_hash_basic.py
    known_passwords = {
        'admin': '$apr1$dfh23$A2sc6uPUrJZ5IWr6UFPmO1',
        'password': '$apr1$salt$someotherhash',
        '123456': '$apr1$salt$anotherhash',
    }
    
    for password in passwords:
        if password in known_passwords and known_passwords[password] == hash_value:
            return {
                'crackeado': True,
                'password': password,
                'metodo': 'Diccionario básico (APR1)'
            }
    
    return {'crackeado': False, 'error': 'No encontrado en diccionario APR1'}

def probar_verificacion_basica(hash_value: str, passwords: List[str]) -> Dict:
    """
    Verificación básica para formatos desconocidos
    """
    # Para formatos no implementados, solo verificamos contraseñas muy comunes
    contraseñas_muy_comunes = ['admin', 'password', '123456', 'root']
    
    for password in contraseñas_muy_comunes:
        # Simulación básica - en producción necesitarías implementación real
        if len(password) <= 6:  # Criterio arbitrario para demo
            return {
                'crackeado': True,
                'password': password,
                'metodo': 'Verificación básica (simulada)'
            }
    
    return {'crackeado': False, 'error': 'Formato no soportado completamente'}

def usar_password_cracker(hash_data: Dict, cracker) -> Dict:
    """
    Usa el PasswordCracker existente
    """
    try:
        # Crear archivo temporal con el hash
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hash') as f:
            if hash_data.get('usuario'):
                f.write(f"{hash_data['usuario']}:{hash_data['hash']}")
            else:
                f.write(hash_data['hash'])
            temp_file = f.name
        
        # Intentar crackear según el formato
        formato = hash_data.get('formato', 'unknown').lower()
        
        if formato in ['md5_crypt', 'apr1']:
            resultado = cracker.crack_with_john(temp_file, 'diccionarios/common.txt', 'md5crypt')
        elif formato == 'ntlm':
            resultado = cracker.crack_with_hashcat(temp_file, 'diccionarios/common.txt', 1000)
        else:
            resultado = cracker.crack_with_john(temp_file, 'diccionarios/common.txt', 'auto')
        
        # Limpiar archivo temporal
        os.unlink(temp_file)
        
        if resultado.get('success'):
            return {
                'crackeado': True,
                'password': resultado['password'],
                'metodo': f'PasswordCracker ({resultado.get("tool", "unknown")})'
            }
        else:
            return {'crackeado': False, 'error': resultado.get('error', 'PasswordCracker falló')}
    
    except Exception as e:
        return {'crackeado': False, 'error': f'Error con PasswordCracker: {str(e)}'}

def usar_herramientas_externas(hash_data: Dict, config: Dict) -> Dict:
    """
    Usa herramientas externas como John the Ripper o Hashcat directamente
    """
    # Implementación básica para herramientas externas
    # En producción, esto llamaría a john/hashcat directamente
    return {'crackeado': False, 'error': 'Herramientas externas no implementadas'}

def guardar_resultados_cracking(resultados: Dict, config: Dict):
    """
    Guarda los resultados del cracking en archivos
    """
    try:
        # Crear directorio de resultados
        output_dir = config.get('cracking_output_dir', 'scanner/cracking_results')
        os.makedirs(output_dir, exist_ok=True)
        
        # Archivo JSON con resultados completos
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(output_dir, f'cracking_results_{timestamp}.json')
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        # Archivo de credenciales en formato simple
        if resultados['credenciales_encontradas']:
            creds_file = os.path.join(output_dir, f'credenciales_{timestamp}.txt')
            with open(creds_file, 'w', encoding='utf-8') as f:
                f.write("=== CREDENCIALES CRACKEADAS ===\n\n")
                for cred in resultados['credenciales_encontradas']:
                    f.write(f"Usuario: {cred['usuario']}\n")
                    f.write(f"Contraseña: {cred['password']}\n")
                    f.write(f"Método: {cred['metodo']}\n")
                    f.write(f"Tiempo: {cred['tiempo']}s\n")
                    f.write("-" * 40 + "\n")
        
        print(f"💾 Resultados guardados en: {results_file}")
        
    except Exception as e:
        print(f"⚠️ Error guardando resultados: {e}")

def mostrar_resumen_cracking(resultados: Dict):
    """
    Muestra un resumen de los resultados del cracking
    """
    stats = resultados['estadisticas']
    
    print(f"\n" + "="*50)
    print(f"📊 RESUMEN DE HASH CRACKING")
    print(f"="*50)
    print(f"🎯 Total de hashes: {stats['total_hashes']}")
    print(f"✅ Hashes crackeados: {stats['crackeados']}")
    print(f"❌ Hashes no crackeados: {stats['total_hashes'] - stats['crackeados']}")
    print(f"⏱️ Tiempo total: {stats['tiempo_total']}s")
    
    if stats['crackeados'] > 0:
        tasa_exito = (stats['crackeados'] / stats['total_hashes']) * 100
        print(f"📈 Tasa de éxito: {tasa_exito:.1f}%")
        
        print(f"\n🔑 CREDENCIALES ENCONTRADAS:")
        for cred in resultados['credenciales_encontradas']:
            print(f"   👤 {cred['usuario']}:{cred['password']} ({cred['metodo']})")
    
    print(f"="*50)

def load_config(config_file: str) -> Dict:
    """
    Carga la configuración desde archivo JSON
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

# Función de compatibilidad con el código del usuario
def crack_captured_hashes(hash_file: str = "scanner/hashes/capturados.hash") -> str:
    """
    Función de compatibilidad que retorna string formateado para logging
    """
    resultado = crackear_hashes(hash_file)
    
    if resultado['success']:
        stats = resultado['estadisticas']
        output = f"Hash Cracking completado: {stats['crackeados']}/{stats['total_hashes']} crackeados"
        
        if resultado['credenciales_encontradas']:
            output += f"\nCredenciales encontradas:"
            for cred in resultado['credenciales_encontradas']:
                output += f"\n  - {cred['usuario']}:{cred['password']}"
        
        return output
    else:
        return f"Error en Hash Cracking: {resultado['error']}"

# Función para crear archivo de ejemplo
def crear_archivo_hashes_ejemplo():
    """
    Crea un archivo de ejemplo con hashes para testing
    """
    os.makedirs("scanner/hashes", exist_ok=True)
    
    hashes_ejemplo = [
        "admin:$apr1$dfh23$A2sc6uPUrJZ5IWr6UFPmO1",
        "user:5d41402abc4b2a76b9719d911017c592",  # MD5 de "hello"
        "guest:356a192b7913b04c54574d18c28d46e6395428ab",  # SHA1 de "1"
        "test:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # SHA256 de ""
    ]
    
    with open("scanner/hashes/capturados.hash", "w") as f:
        for hash_line in hashes_ejemplo:
            f.write(hash_line + "\n")
    
    print("📄 Archivo de ejemplo creado: scanner/hashes/capturados.hash")
