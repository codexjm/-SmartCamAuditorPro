#!/usr/bin/env python3
"""
Tu código exacto sin modificaciones
"""

import json
from scanner.network_scanner import obtener_ips_dispositivos

# Tu código exacto:
with open("config/config.json") as f:
    config = json.load(f)

rango_red = config.get("network_range", "192.168.1.0/24")
ips_detectadas = obtener_ips_dispositivos(rango_red)

# Mostrar los resultados
print(f"\n🎯 Variable rango_red: {rango_red}")
print(f"🎯 Variable ips_detectadas: {ips_detectadas}")
print(f"🎯 Tipo de ips_detectadas: {type(ips_detectadas)}")
print(f"🎯 Cantidad de IPs: {len(ips_detectadas)}")
