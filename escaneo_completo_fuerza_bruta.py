#!/usr/bin/env python3
"""
Script completo que integra escaneo de red + fuerza bruta
Usando tu código exacto
"""

import json
import datetime
import os
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.fuerza_bruta import iniciar_fuerza_bruta

def main():
    print("🔒 SmartCam Auditor v2.0 Pro - Escaneo + Fuerza Bruta")
    print("⚠️  ADVERTENCIA: Solo usar en redes propias o con autorización explícita")
    print("=" * 70)
    
    # Crear directorio de logs si no existe
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Archivo de log con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/escaneo_fuerza_bruta_{timestamp}.log"
    
    print(f"📝 Archivo de log: {log_path}")
    print()
    
    try:
        # Cargar configuración
        with open("config/config.json") as f:
            config = json.load(f)

        rango_red = config.get("network_range", "192.168.1.0/24")
        
        # Escribir cabecera del log
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"🔒 SmartCam Auditor v2.0 Pro - Log de Escaneo + Fuerza Bruta\n")
            f.write(f"📅 Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📡 Red objetivo: {rango_red}\n")
            f.write("=" * 60 + "\n\n")
        
        # Detectar IPs de dispositivos
        print(f"🔍 Detectando dispositivos en {rango_red}...")
        ips_detectadas = obtener_ips_dispositivos(rango_red)
        
        # Log del escaneo
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[🔎 Escaneo de red completado]\n")
            f.write(f"Red escaneada: {rango_red}\n")
            f.write(f"IPs detectadas: {len(ips_detectadas)}\n")
            f.write(f"Dispositivos encontrados: {ips_detectadas}\n\n")
        
        if not ips_detectadas:
            print("⚠️  No se encontraron dispositivos activos en la red.")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("[⚠️ No se encontraron dispositivos para atacar]\n")
            return
        
        print(f"✅ Encontrados {len(ips_detectadas)} dispositivos activos")
        print(f"📍 IPs detectadas: {ips_detectadas}")
        
        # Confirmar antes de fuerza bruta
        print(f"\n⚠️  ¿Proceder con fuerza bruta en {len(ips_detectadas)} dispositivos?")
        print("⚠️  SOLO PROCEDE SI TIENES AUTORIZACIÓN PARA ESTAS IPs")
        
        confirmar = input("Escriba 'SI' para continuar: ")
        if confirmar.upper() != 'SI':
            print("❌ Fuerza bruta cancelada por el usuario")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("[❌ Fuerza bruta cancelada por el usuario]\n")
            return
        
        # Tu código exacto de fuerza bruta:
        print("\n💣 Iniciando fuerza bruta avanzada...")
        brute_results = iniciar_fuerza_bruta(ips_detectadas)

        # Tu código exacto para escribir en log:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n[💣 Fuerza bruta avanzada:]\n")
            if brute_results:
                for r in brute_results:
                    f.write(" -> " + r + "\n")
            else:
                f.write(" -> No se logró acceso con diccionario.\n")
        
        # Mostrar resultados finales
        print(f"\n📊 RESULTADOS FINALES:")
        print("-" * 50)
        print(f"🎯 Dispositivos escaneados: {len(ips_detectadas)}")
        print(f"💣 Credenciales comprometidas: {len(brute_results)}")
        
        if brute_results:
            print(f"\n🚨 CREDENCIALES DÉBILES ENCONTRADAS:")
            for resultado in brute_results:
                print(f"   ⚠️  {resultado}")
            print(f"\n⚠️  ACCIÓN REQUERIDA: Cambiar estas credenciales INMEDIATAMENTE")
        else:
            print("✅ No se encontraron credenciales débiles con el diccionario")
            print("🛡️  Los dispositivos resistieron el ataque de diccionario")
        
        print(f"\n📄 Log completo guardado en: {log_path}")
        print("🔒 ¡Proceso completado!")
        
    except FileNotFoundError:
        print("❌ Error: config/config.json no encontrado")
    except KeyboardInterrupt:
        print("\n\n⏹️  Proceso interrumpido por el usuario.")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[⏹️ Proceso interrumpido por el usuario]\n")
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[❌ Error: {e}]\n")

if __name__ == "__main__":
    main()
