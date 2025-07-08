#!/usr/bin/env python3
"""
Script que implementa exactamente el código que proporcionaste
"""

import json
from scanner.network_scanner import obtener_ips_dispositivos

def main():
    print("🔒 SmartCam Auditor - Escaneo con Configuración JSON")
    print("=" * 55)
    
    try:
        # Tu código exacto:
        with open("config/config.json") as f:
            config = json.load(f)

        rango_red = config.get("network_range", "192.168.1.0/24")
        print(f"📡 Rango de red desde configuración: {rango_red}")
        
        ips_detectadas = obtener_ips_dispositivos(rango_red)
        
        # Mostrar resultados
        print(f"\n✅ Escaneo completado")
        print(f"📍 IPs detectadas: {ips_detectadas}")
        print(f"📊 Total de dispositivos: {len(ips_detectadas)}")
        
        # Mostrar configuración adicional disponible
        print(f"\n🔧 Configuración adicional disponible:")
        puertos_config = config.get("camera_ports", [])
        print(f"   🔌 Puertos configurados: {puertos_config}")
        
        telegram_token = config.get("telegram_bot_token", "No configurado")
        telegram_status = "✅ Configurado" if telegram_token != "TU_TOKEN" else "❌ No configurado"
        print(f"   📱 Telegram: {telegram_status}")
        
        return ips_detectadas
        
    except FileNotFoundError:
        print("❌ Error: No se encontró config/config.json")
        print("💡 Asegúrate de que el archivo existe")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    ips_encontradas = main()
