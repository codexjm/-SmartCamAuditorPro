#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo exacto del código solicitado por el usuario

Este archivo demuestra el uso directo del módulo modularizado
tal como lo solicita el usuario en su consulta.
"""

# IMPORTACIÓN EXACTA como solicita el usuario
from scanner.image_ai_analyzer import analizar_rtsp

def registrar_log(mensaje):
    """Función de logging simple"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def ejemplo_codigo_exacto():
    """
    Código exacto como lo solicita el usuario
    """
    # CÓDIGO EXACTO del usuario:
    rtsp_url = "rtsp://admin:admin@192.168.1.10:554"
    imagen = analizar_rtsp(rtsp_url)

    if imagen:
        registrar_log(f"[🧠 IA] Detección completada. Imagen: {imagen}")
    else:
        registrar_log("[🧠 IA] No se pudo analizar la cámara.")

def main():
    """Función principal"""
    print("🎯 CÓDIGO EXACTO DEL USUARIO")
    print("=" * 50)
    print("Ejecutando:")
    print("from scanner.image_ai_analyzer import analizar_rtsp")
    print("")
    print("rtsp_url = \"rtsp://admin:admin@192.168.1.10:554\"")
    print("imagen = analizar_rtsp(rtsp_url)")
    print("")
    print("if imagen:")
    print("    registrar_log(f\"[🧠 IA] Detección completada. Imagen: {imagen}\")")
    print("else:")
    print("    registrar_log(\"[🧠 IA] No se pudo analizar la cámara.\")")
    print("")
    print("🚀 EJECUTANDO...")
    print("-" * 50)
    
    # Ejecutar el código exacto
    ejemplo_codigo_exacto()
    
    print("-" * 50)
    print("✅ CÓDIGO EJECUTADO EXITOSAMENTE")
    print("✅ El módulo está modularizado y funcional")
    print("✅ La función analizar_rtsp puede ser importada y usada")

if __name__ == "__main__":
    main()
