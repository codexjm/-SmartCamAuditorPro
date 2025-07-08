import json
from datetime import datetime
import os

# Rutas a tus módulos
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.login_tester import testear_credenciales
from scanner.fuerza_bruta import iniciar_fuerza_bruta
# Módulos avanzados (por crear)
from scanner.cve_checker import buscar_vulnerabilidades_cve
# from scanner.exploit_launcher import lanzar_exploits
# from scanner.image_ai_analyzer import analizar_imagen_camara
# from scanner.fingerprint_nmap import fingerprint_camaras
# from scanner.diff_analyzer import comparar_logs
# from scanner.shodan_local import indexar_camaras
# from scanner.hash_cracker import crackear_hashes
from telegram_alert import enviar_alerta  # si lo usas

class AuditorMaestro:
    """Clase principal para gestionar auditorías completas"""
    
    def __init__(self, config_file="config/config.json"):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Crear carpeta de logs
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(self.log_dir, f"audit_full_{timestamp}.txt")
    
    def registrar_log(self, texto):
        print(texto)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {texto}\n")
    
    def ejecutar_auditoria(self):
        """Ejecuta una auditoría completa"""
        self.registrar_log("🚀 Iniciando auditoría maestra")
        return self.auditoria_completa()
    
    def auditoria_completa(self):
        """Función principal de auditoría"""
        resultados = {
            'ips_encontradas': [],
            'credenciales_encontradas': [],
            'vulnerabilidades': []
        }
        
        # Escaneo de red
        if self.config.get('audit_master', {}).get('enable_network_scan', True):
            self.registrar_log("🌐 Iniciando escaneo de red...")
            resultados['ips_encontradas'] = obtener_ips_dispositivos(self.config['network_range'])
        
        # Pruebas de credenciales
        if self.config.get('audit_master', {}).get('enable_login_test', True):
            self.registrar_log("🔐 Probando credenciales...")
            for ip in resultados['ips_encontradas']:
                creds = testear_credenciales(ip)
                if creds:
                    resultados['credenciales_encontradas'].extend(creds)
        
        return resultados

# Cargar configuración global (para compatibilidad con funciones existentes)
with open("config/config.json") as f:
    config = json.load(f)

# Crear carpeta de logs
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = os.path.join(log_dir, f"audit_full_{timestamp}.txt")

def registrar_log(texto):
    print(texto)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(texto + "\n")

def main():
    registrar_log(f"🧠 SmartCam Auditor Pro - Auditoría {timestamp}")
    registrar_log("====================================================")

    # Configuración de auditoría
    audit_config = config.get("audit_master", {})

    # 1. Escanear red
    if audit_config.get("enable_network_scan", True):
        registrar_log("🔎 Escaneando red...")
        ips = obtener_ips_dispositivos(config["network_range"])
        registrar_log(f" -> IPs encontradas: {ips}")
    else:
        ips = audit_config.get("manual_ips", [])
        registrar_log(f"📍 Usando IPs manuales: {ips}")

    if not ips:
        registrar_log("❌ No se encontraron dispositivos. Fin de auditoría.")
        return

    # 2. Probar credenciales comunes
    if audit_config.get("enable_login_test", True):
        registrar_log("🔐 Probando credenciales comunes...")
        cred_result = testear_credenciales(ips)
        if cred_result:
            for r in cred_result:
                registrar_log(" -> " + r)
        else:
            registrar_log(" -> No se encontraron credenciales débiles")

    # 3. Fuerza bruta
    if audit_config.get("enable_brute_force", True):
        registrar_log("💣 Ejecutando fuerza bruta...")
        dicc_path = audit_config.get("brute_dict_path", "diccionarios/credenciales_comunes.txt")
        brute_result = iniciar_fuerza_bruta(ips, diccionario_path=dicc_path)
        if brute_result:
            for r in brute_result:
                registrar_log(" -> " + r)
        else:
            registrar_log(" -> No se logró acceso con diccionario")

    # 4. CVE check
    if audit_config.get("enable_cve_check", False):
        registrar_log("🧬 Buscando CVEs...")
        cve_result = buscar_vulnerabilidades_cve(ips)
        if cve_result:
            for r in cve_result:
                registrar_log(" -> " + r)
        else:
            registrar_log(" -> No se encontraron CVEs conocidos")

    # 5. Enviar alerta
    if audit_config.get("enable_telegram", False):
        try:
            enviar_alerta(f"✅ Auditoría finalizada.\nLog: {log_path}")
            registrar_log("📱 Alerta Telegram enviada")
        except Exception as e:
            registrar_log(f"⚠️ Error enviando alerta Telegram: {e}")

    registrar_log("✅ Auditoría completa.")

if __name__ == "__main__":
    main()
