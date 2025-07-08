"""
Módulo para gestionar logs de auditoría (versión simplificada)
"""

import os
from datetime import datetime

def save_log(ip, ports, logins, config=None):
    """
    Guarda los resultados de auditoría en un archivo de texto simple
    
    Args:
        ip (str): Dirección IP del dispositivo
        ports (list): Lista de puertos abiertos
        logins (list): Lista de credenciales exitosas
        config (dict): Configuración del sistema
    """
    if config is None:
        config = {"log_folder": "logs"}
    
    log_folder = config.get("log_folder", "logs")
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, "results.txt")
    with open(log_file, "a") as f:
        f.write(f"\n[{datetime.now()}] IP: {ip}\n")
        f.write(f"  Puertos abiertos: {ports}\n")
        if logins:
            f.write(f"  ACCESO VULNERABLE: {logins}\n")
        f.write("------------------------------------------------\n")
