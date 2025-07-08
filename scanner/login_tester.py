"""
Módulo para probar credenciales comunes en dispositivos encontrados
"""

import requests
import json
import warnings

# Suprimir advertencias SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Cargar credenciales desde archivo JSON
def load_credentials():
    """Carga las credenciales desde el archivo de configuración"""
    try:
        with open("config/credentials.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] No se encontró el archivo config/credentials.json")
        return []
    except Exception as e:
        print(f"[ERROR] Error al cargar credenciales: {e}")
        return []

# Cargar credenciales globalmente
CREDENTIALS = load_credentials()

def test_logins(ip, ports):
    """
    Prueba credenciales comunes en los puertos HTTP de un dispositivo (versión simplificada)
    
    Args:
        ip (str): Dirección IP del dispositivo
        ports (list): Lista de puertos abiertos (números)
    
    Returns:
        list: Lista de credenciales exitosas encontradas (strings)
    """
    print(f"        [*] Probando credenciales HTTP en {ip}")
    
    results = []
    
    # Solo probar en puertos HTTP
    http_ports = [port for port in ports if port in [80, 8080, 85, 9999, 443, 8443]]
    
    if not http_ports:
        print(f"        [-] No hay puertos HTTP disponibles en {ip}")
        return results
    
    for port in http_ports:
        protocol = "https" if port in [443, 8443] else "http"
        print(f"        [*] Probando credenciales en {protocol}://{ip}:{port}")
        
        for cred in CREDENTIALS:
            try:
                url = f"{protocol}://{ip}:{port}/"
                r = requests.get(
                    url, 
                    auth=(cred["user"], cred["pass"]), 
                    timeout=2,
                    verify=False,  # Para HTTPS sin certificado válido
                    allow_redirects=True
                )
                
                if r.status_code == 200:
                    credential_string = f"{cred['user']}:{cred['pass']}"
                    results.append(credential_string)
                    print(f"        [!] CREDENCIALES ENCONTRADAS: {credential_string} en {protocol}:{port}")
                    break  # No probar más credenciales en este puerto si ya encontramos una
                    
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                break  # Si no podemos conectar, no seguir probando en este puerto
            except Exception:
                continue
    
    if results:
        print(f"        [!] {len(results)} credenciales exitosas encontradas en {ip}")
    else:
        print(f"        [-] No se encontraron credenciales válidas en {ip}")
    
    return results

# Función de compatibilidad con el nombre original del usuario
def testear_credenciales(ips, puertos_http=None, incluir_rtsp=True, incluir_ssh=False):
    """
    Función de compatibilidad - mantiene el nombre original del usuario
    
    Args:
        ips (list): Lista de IPs a probar
        puertos_http (list): Puertos HTTP a probar (default: [80, 8080])
        incluir_rtsp (bool): Si incluir pruebas RTSP
        incluir_ssh (bool): Si incluir pruebas SSH
    
    Returns:
        list: Lista de vulnerabilidades encontradas
    """
    # Importar la función principal del credential_tester
    try:
        from .credential_tester import testear_credenciales as test_creds_original
        
        # Usar valores por defecto si no se especifican
        if puertos_http is None:
            puertos_http = [80, 8080]
        
        # Llamar a la función original con el nombre de parámetro correcto
        return test_creds_original(
            lista_ips=ips,  # Usar lista_ips en lugar de ips
            puertos_http=puertos_http,
            incluir_rtsp=incluir_rtsp,
            incluir_ssh=incluir_ssh
        )
    except ImportError:
        print("⚠️ Módulo credential_tester no disponible")
        return []

# Alias adicionales para compatibilidad
probar_credenciales = testear_credenciales
test_login = testear_credenciales
