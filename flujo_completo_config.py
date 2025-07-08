#!/usr/bin/env python3
"""
Flujo completo usando tu código + pruebas de credenciales
"""

import json
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.login_tester import testear_credenciales

print("🔒 SmartCam Auditor - Flujo Completo con Configuración")
print("=" * 60)

# Tu código exacto:
with open("config/config.json") as f:
    config = json.load(f)

rango_red = config.get("network_range", "192.168.1.0/24")
ips_detectadas = obtener_ips_dispositivos(rango_red)

print(f"\n📊 RESULTADOS DEL ESCANEO:")
print(f"   📡 Red escaneada: {rango_red}")
print(f"   🎯 IPs detectadas: {ips_detectadas}")
print(f"   📈 Total: {len(ips_detectadas)} dispositivos")

# Continuar con pruebas de credenciales si hay dispositivos
if ips_detectadas:
    print(f"\n🔐 Probando credenciales en {len(ips_detectadas)} dispositivos...")
    resultados_credenciales = testear_credenciales(ips_detectadas)
    
    print(f"\n🎯 RESULTADOS DE CREDENCIALES:")
    if resultados_credenciales:
        print("🚨 VULNERABILIDADES ENCONTRADAS:")
        for resultado in resultados_credenciales:
            print(f"   ⚠️  {resultado}")
    else:
        print("✅ No se encontraron credenciales débiles")
        
    # Mostrar configuración de puertos usada
    puertos_config = config.get("camera_ports", [])
    print(f"\n🔧 Configuración utilizada:")
    print(f"   🔌 Puertos escaneados: {puertos_config}")
    print(f"   ⏱️  Timeout: {config.get('scan_settings', {}).get('timeout', 'Por defecto')}")
    
else:
    print("\n⚠️  No se encontraron dispositivos para probar credenciales")

print("\n✅ Proceso completado")
