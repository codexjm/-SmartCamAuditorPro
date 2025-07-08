#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 GUÍA DE LOCALIZACIÓN - SmartCam Auditor v2.0 Pro
Cómo encontrar y acceder al proyecto mañana

UBICACIÓN PRINCIPAL DEL PROYECTO:
📁 c:\\Users\\codex\\smartcam_auditor\\

FECHA GUARDADO: 8 de julio de 2025
"""

import os
import json
from datetime import datetime

def mostrar_ubicaciones():
    """Muestra todas las ubicaciones importantes del proyecto"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔍 GUÍA DE LOCALIZACIÓN DEL PROYECTO                      ║
║                         SmartCam Auditor v2.0 Pro                           ║
║                         Guardado: 8 de julio 2025                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 UBICACIÓN PRINCIPAL:
===============================================================================
📁 DIRECTORIO BASE: c:\\Users\\codex\\smartcam_auditor\\

🚀 COMANDOS PARA ACCEDER RÁPIDAMENTE:
===============================================================================
""")
    
    print("💻 DESDE LÍNEA DE COMANDOS (Windows PowerShell/CMD):")
    print("   cd c:\\\\Users\\\\codex\\\\smartcam_auditor")
    print("   dir                                    # Ver contenido")
    print("   python verificar_configuracion.py     # Verificar estado")
    print()
    
    print("📂 DESDE EXPLORADOR DE ARCHIVOS:")
    print("   1. Abrir Explorador de Windows")
    print("   2. Ir a: C:\\\\Users\\\\codex\\\\smartcam_auditor")
    print("   3. O pegar en barra de direcciones: c:\\\\Users\\\\codex\\\\smartcam_auditor")
    print()
    
    print("🔧 DESDE VS CODE:")
    print("   1. File → Open Folder")
    print("   2. Navegar a: C:\\\\Users\\\\codex\\\\smartcam_auditor")
    print("   3. O usar: Ctrl+K, Ctrl+O → seleccionar carpeta")
    print()

def mostrar_archivos_clave():
    """Muestra los archivos más importantes y dónde encontrarlos"""
    
    print("""
📋 ARCHIVOS CLAVE Y SUS UBICACIONES:
===============================================================================""")
    
    archivos = {
        "DOCUMENTACIÓN PRINCIPAL": [
            ("CHECKLIST_PARA_MAÑANA.md", "Pasos exactos para retomar"),
            ("ESTADO_ACTUAL_PROYECTO.md", "Resumen completo del estado"),
            ("IMPLEMENTACION_COMPLETADA.md", "Funcionalidades completadas"),
            ("README.md", "Documentación general")
        ],
        
        "CONFIGURACIÓN": [
            ("config/config.json", "Tu configuración personalizada (75 threads, modo agresivo)"),
            ("verificar_configuracion.py", "Script para verificar que todo funciona"),
            ("demo_configuracion_personalizada.py", "Demostración de tu config")
        ],
        
        "SCRIPTS PRINCIPALES": [
            ("run_web.py", "Iniciar interfaz web moderna"),
            ("audit_master.py", "Auditoría completa con todos los módulos"),
            ("app.py", "Aplicación Flask principal")
        ],
        
        "MÓDULOS DE ESCANEO": [
            ("scanner/network_scanner.py", "Escaneo de red avanzado (tu archivo actual)"),
            ("scanner/fuerza_bruta.py", "Ataques de fuerza bruta multi-protocolo"),
            ("scanner/cve_checker.py", "Verificación de vulnerabilidades CVE"),
            ("scanner/credential_tester.py", "Pruebas de credenciales automáticas")
        ],
        
        "INTERFAZ WEB": [
            ("web_panel/templates/", "Plantillas HTML con tema cyberpunk"),
            ("web_panel/static/style_new.css", "CSS moderno con animaciones"),
            ("web_panel/routes.py", "Rutas y lógica web")
        ],
        
        "RESPALDOS": [
            ("backups/", "Respaldos automáticos con timestamp"),
            ("guardar_proyecto.py", "Script que usamos para guardar todo")
        ]
    }
    
    for categoria, items in archivos.items():
        print(f"\n🔸 {categoria}:")
        for archivo, descripcion in items:
            ruta_completa = f"c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\{archivo}"
            print(f"   📄 {archivo}")
            print(f"      └─ {descripcion}")
            print(f"      └─ Ruta: {ruta_completa}")

def crear_accesos_directos():
    """Crea scripts de acceso directo para Windows"""
    
    print("""
⚡ CREANDO ACCESOS DIRECTOS:
===============================================================================""")
    
    # Script BAT para abrir el proyecto rápidamente
    bat_content = f"""@echo off
echo 🚀 Abriendo SmartCam Auditor v2.0 Pro...
cd /d "c:\\\\Users\\\\codex\\\\smartcam_auditor"
echo.
echo 📁 Ubicación: %CD%
echo.
echo 💡 Comandos disponibles:
echo    python verificar_configuracion.py
echo    python demo_configuracion_personalizada.py
echo    python run_web.py
echo    python audit_master.py
echo.
cmd /k
"""
    
    with open("c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\ABRIR_PROYECTO.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    print("   ✅ Creado: ABRIR_PROYECTO.bat")
    print("      └─ Doble clic para abrir terminal en el proyecto")
    
    # Script PowerShell alternativo
    ps1_content = f"""# SmartCam Auditor v2.0 Pro - Acceso Rápido
Write-Host "🚀 SmartCam Auditor v2.0 Pro" -ForegroundColor Cyan
Write-Host "📁 Cambiando al directorio del proyecto..." -ForegroundColor Yellow
Set-Location "c:\\\\Users\\\\codex\\\\smartcam_auditor"
Write-Host ""
Write-Host "✅ Listo! Ubicación actual:" -ForegroundColor Green
Get-Location
Write-Host ""
Write-Host "💡 Comandos sugeridos:" -ForegroundColor Yellow
Write-Host "   python verificar_configuracion.py" -ForegroundColor White
Write-Host "   python demo_configuracion_personalizada.py" -ForegroundColor White
Write-Host "   python run_web.py" -ForegroundColor White
Write-Host ""
"""
    
    with open("c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\abrir_proyecto.ps1", "w", encoding="utf-8") as f:
        f.write(ps1_content)
    
    print("   ✅ Creado: abrir_proyecto.ps1")
    print("      └─ Para PowerShell: Click derecho → Ejecutar con PowerShell")

def mostrar_comandos_busqueda():
    """Muestra comandos para buscar el proyecto si se olvida la ubicación"""
    
    print("""
🔍 SI OLVIDAS LA UBICACIÓN, USA ESTOS COMANDOS:
===============================================================================

📍 BUSCAR POR NOMBRE DE ARCHIVO:
   # En PowerShell/CMD:
   dir c:\\\\ /s "smartcam_auditor" 2>nul
   
   # O buscar archivo específico:
   dir c:\\\\ /s "CHECKLIST_PARA_MAÑANA.md" 2>nul

📍 BUSCAR POR CONTENIDO:
   # Buscar archivos que contengan "SmartCam Auditor":
   findstr /s /i "SmartCam Auditor" c:\\\\Users\\\\*.py c:\\\\Users\\\\*.md

📍 DESDE EXPLORADOR DE WINDOWS:
   1. Abrir Explorador
   2. En barra de búsqueda escribir: smartcam_auditor
   3. O buscar: "CHECKLIST_PARA_MAÑANA"

📍 ACCESOS RÁPIDOS CREADOS:
   ▶ Doble clic: c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\ABRIR_PROYECTO.bat
   ▶ PowerShell: c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\abrir_proyecto.ps1
""")

def verificar_existencia():
    """Verifica que los archivos principales existen"""
    
    print("""
✅ VERIFICACIÓN DE ARCHIVOS:
===============================================================================""")
    
    archivos_criticos = [
        "c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\CHECKLIST_PARA_MAÑANA.md",
        "c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\config\\\\config.json",
        "c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\scanner\\\\network_scanner.py",
        "c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\verificar_configuracion.py",
        "c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\run_web.py"
    ]
    
    todos_existen = True
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - NO ENCONTRADO")
            todos_existen = False
    
    if todos_existen:
        print("\n🎉 ¡Todos los archivos principales están en su lugar!")
    else:
        print("\n⚠️  Algunos archivos no se encontraron. Usar comandos de búsqueda.")

def main():
    """Función principal"""
    mostrar_ubicaciones()
    mostrar_archivos_clave()
    crear_accesos_directos()
    mostrar_comandos_busqueda()
    verificar_existencia()
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              📋 RESUMEN RÁPIDO                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 UBICACIÓN PRINCIPAL: c:\\\\Users\\\\codex\\\\smartcam_auditor\\\\

🚀 PARA EMPEZAR MAÑANA:
   1. cd c:\\\\Users\\\\codex\\\\smartcam_auditor
   2. python verificar_configuracion.py
   3. python demo_configuracion_personalizada.py

📋 DOCUMENTOS IMPORTANTES:
   • CHECKLIST_PARA_MAÑANA.md (pasos exactos)
   • ESTADO_ACTUAL_PROYECTO.md (resumen completo)

⚡ ACCESOS DIRECTOS:
   • ABRIR_PROYECTO.bat (doble clic)
   • abrir_proyecto.ps1 (PowerShell)

🔍 SI SE PIERDE:
   dir c:\\\\ /s "CHECKLIST_PARA_MAÑANA.md" 2>nul

¡El proyecto te está esperando! 🎉
""")

if __name__ == "__main__":
    main()
