#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 GUÍA RÁPIDA - Cómo encontrar SmartCam Auditor v2.0 Pro mañana
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔍 CÓMO ENCONTRAR TU PROYECTO MAÑANA                      ║
║                         SmartCam Auditor v2.0 Pro                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 UBICACIÓN PRINCIPAL:
   C:\\Users\\codex\\smartcam_auditor

🚀 COMANDOS PARA ACCEDER:
   1. Abrir PowerShell o CMD
   2. Escribir: cd C:\\Users\\codex\\smartcam_auditor
   3. Verificar: python verificar_configuracion.py

📂 DESDE EXPLORADOR DE WINDOWS:
   1. Abrir Explorador
   2. Ir a: C:\\Users\\codex\\smartcam_auditor
   3. Buscar archivo: CHECKLIST_PARA_MAÑANA.md

🔧 DESDE VS CODE:
   1. File → Open Folder
   2. Seleccionar: C:\\Users\\codex\\smartcam_auditor

📋 ARCHIVOS IMPORTANTES:
   ✅ CHECKLIST_PARA_MAÑANA.md (pasos para continuar)
   ✅ ESTADO_ACTUAL_PROYECTO.md (resumen completo)
   ✅ config/config.json (tu configuración personalizada)
   ✅ verificar_configuracion.py (verificar sistema)

🔍 SI NO LO ENCUENTRAS:
   En PowerShell/CMD ejecuta:
   dir C:\\ /s "CHECKLIST_PARA_MAÑANA.md"

💡 PRIMEROS PASOS MAÑANA:
   1. cd C:\\Users\\codex\\smartcam_auditor
   2. python verificar_configuracion.py
   3. python demo_configuracion_personalizada.py
   4. python run_web.py (interfaz web)

🎯 TU CONFIGURACIÓN GUARDADA:
   • Red: 192.168.1.1/24
   • Modo: Agresivo (75 threads)
   • Fuerza bruta: 30 threads
   • Puertos: 10 configurados
   • CVE checking: Habilitado

¡El proyecto te está esperando! 🚀
""")

# Crear acceso directo BAT
bat_content = '''@echo off
title SmartCam Auditor v2.0 Pro
echo 🚀 SmartCam Auditor v2.0 Pro
echo ================================
cd /d "C:\\Users\\codex\\smartcam_auditor"
echo 📁 Ubicacion actual: %CD%
echo.
echo 💡 Comandos disponibles:
echo    python verificar_configuracion.py
echo    python demo_configuracion_personalizada.py
echo    python run_web.py
echo    python audit_master.py
echo.
echo ✅ Listo para trabajar!
cmd /k
'''

try:
    with open("ABRIR_PROYECTO.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    print("✅ Creado acceso directo: ABRIR_PROYECTO.bat")
    print("   (Doble clic para abrir terminal en el proyecto)")
except Exception as e:
    print(f"⚠️ Error creando BAT: {e}")

print("\n🎉 ¡Guía de localización lista!")
print("📄 Este archivo está en: C:\\Users\\codex\\smartcam_auditor\\guia_localizacion.py")
