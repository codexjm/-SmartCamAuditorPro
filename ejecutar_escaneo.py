#!/usr/bin/env python3
"""
Script para ejecutar escaneo de red y pruebas de credenciales
SmartCam Auditor v2.0 Pro
"""

import os
import datetime
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.login_tester import testear_credenciales

def main():
    print("🔒 SmartCam Auditor v2.0 Pro - Escaneo y Pruebas de Credenciales")
    print("=" * 60)
    
    # Crear directorio de logs si no existe
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Archivo de log con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/escaneo_credenciales_{timestamp}.log"
    
    print(f"📝 Archivo de log: {log_path}")
    print()
    
    # Escribir cabecera del log
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"🔒 SmartCam Auditor v2.0 Pro - Log de Escaneo\n")
        f.write(f"📅 Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
    
    try:
        # Detectar IPs de cámaras
        print("🔍 Detectando dispositivos en la red...")
        ips_detectadas = obtener_ips_dispositivos("192.168.1.0/24")  # Cambia a tu red local
        
        # Escribir resultados del escaneo al log
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[🔎 Escaneo de red completado]\n")
            f.write(f"Red escaneada: 192.168.1.0/24\n")
            f.write(f"IPs detectadas: {len(ips_detectadas)}\n")
            f.write(f"Dispositivos encontrados: {ips_detectadas}\n\n")
        
        if not ips_detectadas:
            print("⚠️  No se encontraron dispositivos activos en la red.")
            print("💡 Verifica que estés conectado a la red correcta.")
            print("💡 Puedes cambiar el rango de red en el código (línea con '192.168.1.0/24').")
            return
        
        print(f"✅ Encontrados {len(ips_detectadas)} dispositivos activos")
        print(f"📍 IPs detectadas: {ips_detectadas}")
        print()
        
        # Probar credenciales débiles
        print("🔐 Probando credenciales débiles...")
        resultados_credenciales = testear_credenciales(ips_detectadas)
        
        # Escribir en el log
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[🔐 Resultado de pruebas de credenciales débiles:]\n")
            if resultados_credenciales:
                for r in resultados_credenciales:
                    f.write(" -> " + str(r) + "\n")
            else:
                f.write(" -> No se encontraron credenciales débiles.\n")
            f.write("\n")
        
        # Mostrar resultados en consola
        print("\n📊 RESULTADOS:")
        print("-" * 40)
        if resultados_credenciales:
            print("🚨 CREDENCIALES DÉBILES ENCONTRADAS:")
            for resultado in resultados_credenciales:
                print(f"  ⚠️  {resultado}")
        else:
            print("✅ No se encontraron credenciales débiles.")
            print("🛡️  Los dispositivos parecen estar bien protegidos.")
        
        print()
        print(f"📄 Log completo guardado en: {log_path}")
        print("🔒 ¡Escaneo completado!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Escaneo interrumpido por el usuario.")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[⏹️ Escaneo interrumpido por el usuario]\n")
    except Exception as e:
        print(f"\n❌ Error durante el escaneo: {e}")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[❌ Error: {e}]\n")

if __name__ == "__main__":
    main()
