#!/usr/bin/env python3
"""
Ejemplo de uso del módulo de fuerza bruta tal como lo escribiste
SmartCam Auditor v2.0 Pro - Fuerza Bruta
"""

import json
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.fuerza_bruta import iniciar_fuerza_bruta

def main():
    print("🔒 SmartCam Auditor v2.0 Pro - Fuerza Bruta Avanzada")
    print("⚠️  ADVERTENCIA: Solo usar en redes propias o con autorización explícita")
    print("=" * 70)
    
    try:
        # Cargar configuración
        with open("config/config.json") as f:
            config = json.load(f)

        rango_red = config.get("network_range", "192.168.1.0/24")
        
        # Verificar si fuerza bruta está habilitada
        if not config.get("brute_force", {}).get("enabled", True):
            print("❌ Fuerza bruta deshabilitada en configuración")
            return
        
        print(f"📡 Escaneando red: {rango_red}")
        
        # Detectar dispositivos
        ips_detectadas = obtener_ips_dispositivos(rango_red)
        
        if not ips_detectadas:
            print("⚠️  No se encontraron dispositivos para atacar")
            return
        
        print(f"\n🎯 Dispositivos objetivo: {ips_detectadas}")
        print(f"📊 Total de objetivos: {len(ips_detectadas)}")
        
        # Confirmar antes de proceder
        print(f"\n⚠️  ¿Continuar con fuerza bruta en {len(ips_detectadas)} dispositivos?")
        print("⚠️  SOLO PROCEDE SI TIENES AUTORIZACIÓN PARA ESTAS IPs")
        
        confirmar = input("Escriba 'SI' para continuar o cualquier otra cosa para cancelar: ")
        if confirmar.upper() != 'SI':
            print("❌ Operación cancelada por el usuario")
            return
        
        # Obtener diccionario de configuración
        diccionario_path = config.get("brute_force", {}).get(
            "dictionary_path", 
            "diccionarios/credenciales_comunes.txt"
        )
        
        print(f"\n🚀 Iniciando fuerza bruta...")
        print(f"📖 Diccionario: {diccionario_path}")
        
        # Tu función exacta de fuerza bruta
        resultados = iniciar_fuerza_bruta(ips_detectadas, diccionario_path)
        
        # Mostrar resumen final
        print(f"\n📋 RESUMEN FINAL:")
        print("=" * 40)
        print(f"🎯 Dispositivos atacados: {len(ips_detectadas)}")
        print(f"🚨 Credenciales encontradas: {len(resultados)}")
        
        if resultados:
            print(f"\n🚨 CREDENCIALES COMPROMETIDAS:")
            for resultado in resultados:
                print(f"   ⚠️  {resultado}")
            print(f"\n⚠️  RECOMENDACIÓN: Cambiar estas credenciales INMEDIATAMENTE")
        else:
            print("✅ No se encontraron credenciales débiles")
            print("🛡️  Los dispositivos parecen estar bien protegidos")
            
    except FileNotFoundError:
        print("❌ Error: config/config.json no encontrado")
    except KeyboardInterrupt:
        print("\n\n⏹️  Fuerza bruta interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error durante la fuerza bruta: {e}")

if __name__ == "__main__":
    main()
