#!/usr/bin/env python3
"""
Tu código exacto de importación y uso de fuerza bruta
"""

from scanner.fuerza_bruta import iniciar_fuerza_bruta
from scanner.network_scanner import obtener_ips_dispositivos
import datetime
import json
import os

# Cargar configuración como en tus ejemplos anteriores
with open("config/config.json") as f:
    config = json.load(f)

rango_red = config.get("network_range", "192.168.1.0/24")

# Detectar IPs
ips_detectadas = obtener_ips_dispositivos(rango_red)

# Crear archivo de log
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = f"logs/tu_codigo_fuerza_bruta_{timestamp}.log"

# Asegurar que existe el directorio
if not os.path.exists("logs"):
    os.makedirs("logs")

# Tu código exacto:
brute_results = iniciar_fuerza_bruta(ips_detectadas)

with open(log_path, "a", encoding="utf-8") as f:
    f.write("\n[💣 Fuerza bruta avanzada:]\n")
    if brute_results:
        for r in brute_results:
            f.write(" -> " + r + "\n")
    else:
        f.write(" -> No se logró acceso con diccionario.\n")

# Mostrar resultados
print(f"\n🎯 IPs atacadas: {ips_detectadas}")
print(f"💣 Resultados de fuerza bruta: {brute_results}")
print(f"📄 Log guardado en: {log_path}")

# Mostrar contenido del log
print(f"\n📖 Contenido del log:")
with open(log_path, "r", encoding="utf-8") as f:
    print(f.read())
