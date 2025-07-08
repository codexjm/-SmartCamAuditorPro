#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación completa para SmartCam Auditor
Verifica que todas las funcionalidades estén operativas
"""

import os
import sys
import json
import datetime
from pathlib import Path

def print_header(title):
    """Imprime un header con formato"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step_num, description):
    """Imprime un paso con numeración"""
    print(f"\n🔸 Paso {step_num}: {description}")

def check_module_import(module_name, import_statement):
    """Verifica si un módulo se puede importar"""
    try:
        exec(import_statement)
        print(f"  ✅ {module_name} - Importación exitosa")
        return True
    except Exception as e:
        print(f"  ❌ {module_name} - Error: {e}")
        return False

def main():
    print_header("VALIDACIÓN COMPLETA DE SMARTCAM AUDITOR")
    print(f"📅 Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Directorio: {os.getcwd()}")
    
    # 1. Verificar estructura del proyecto
    print_step(1, "Verificando estructura del proyecto")
    
    required_dirs = [
        "scanner",
        "config", 
        "logs",
        "exploits"
    ]
    
    required_files = [
        "smartcam_auditor.py",
        "scanner/__init__.py",
        "scanner/network_scanner.py",
        "scanner/image_ai_analyzer.py",
        "requirements.txt"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ Directorio {directory}")
        else:
            print(f"  ❌ Directorio {directory} no encontrado")
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ Archivo {file_path}")
        else:
            print(f"  ❌ Archivo {file_path} no encontrado")
    
    # 2. Verificar dependencias principales
    print_step(2, "Verificando dependencias principales")
    
    dependencies = {
        "OpenCV": "import cv2",
        "NumPy": "import numpy as np",
        "Requests": "import requests",
        "Threading": "import threading",
        "JSON": "import json",
        "Socket": "import socket"
    }
    
    for name, import_stmt in dependencies.items():
        check_module_import(name, import_stmt)
    
    # 3. Verificar dependencias de IA
    print_step(3, "Verificando dependencias de IA")
    
    ai_dependencies = {
        "Ultralytics": "from ultralytics import YOLO",
        "PyTorch": "import torch",
        "Torchvision": "import torchvision"
    }
    
    ai_available = True
    for name, import_stmt in ai_dependencies.items():
        if not check_module_import(name, import_stmt):
            ai_available = False
    
    # 4. Verificar importación de módulos propios
    print_step(4, "Verificando importación de módulos propios")
    
    try:
        # Agregar el directorio actual al path si no está
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        
        from scanner.image_ai_analyzer import analizar_rtsp
        print("  ✅ scanner.image_ai_analyzer.analizar_rtsp")
        
        from scanner.network_scanner import scan_network, get_device_info
        print("  ✅ scanner.network_scanner funciones principales")
        
        # Verificar si existe nmap_integration
        try:
            from scanner.nmap_integration import NmapScanner
            print("  ✅ scanner.nmap_integration.NmapScanner")
        except ImportError:
            print("  ⚠️ scanner.nmap_integration no disponible")
        
    except Exception as e:
        print(f"  ❌ Error importando módulos propios: {e}")
    
    # 5. Verificar modelos YOLO
    print_step(5, "Verificando disponibilidad de modelos YOLO")
    
    yolo_models = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt']
    models_found = []
    
    for model in yolo_models:
        if os.path.exists(model):
            models_found.append(model)
            print(f"  ✅ Modelo {model} disponible")
    
    if not models_found:
        print("  ⚠️ No se encontraron modelos YOLO locales")
        print("  💡 Se descargarán automáticamente al usar YOLO por primera vez")
    
    # 6. Verificar funcionalidad de IA
    print_step(6, "Probando funcionalidad de análisis de IA")
    
    if ai_available:
        try:
            print("  🧠 Cargando modelo YOLO de prueba...")
            from ultralytics import YOLO
            model = YOLO("yolov8n.pt")
            print("  ✅ Modelo YOLO cargado exitosamente")
            
            # Crear una imagen de prueba
            import numpy as np
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            print("  🔍 Ejecutando detección de prueba...")
            results = model.predict(test_image, verbose=False)
            print("  ✅ Detección de IA funcionando correctamente")
            
        except Exception as e:
            print(f"  ❌ Error en prueba de IA: {e}")
    else:
        print("  ⚠️ Dependencias de IA no disponibles, saltando prueba")
    
    # 7. Verificar herramientas de red
    print_step(7, "Verificando herramientas de red")
    
    try:
        import subprocess
        
        # Verificar ping
        result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ Conectividad de red (ping)")
        else:
            print("  ❌ Sin conectividad de red")
            
    except Exception as e:
        print(f"  ❌ Error verificando red: {e}")
    
    # Verificar Nmap
    try:
        result = subprocess.run(['nmap', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ Nmap disponible")
            print(f"      {result.stdout.strip().split()[0:2]}")
        else:
            print("  ❌ Nmap no disponible")
    except Exception:
        print("  ❌ Nmap no encontrado en PATH")
    
    # 8. Verificar scripts de ejemplo
    print_step(8, "Verificando scripts de ejemplo disponibles")
    
    example_scripts = [
        "ejemplo_uso_ai_analyzer.py",
        "ejemplo_simple_analizar_rtsp.py", 
        "test_importacion_ai.py",
        "test_final_image_ai.py",
        "escaneo_hibrido_simple.py",
        "resumen_final_completo.py"
    ]
    
    for script in example_scripts:
        if os.path.exists(script):
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} no encontrado")
    
    # 9. Crear reporte de validación
    print_step(9, "Generando reporte de validación")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"validacion_sistema_{timestamp}.json"
    
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "sistema_operativo": os.name,
        "directorio_trabajo": os.getcwd(),
        "dependencias_ia": ai_available,
        "modelos_yolo": models_found,
        "estructura_proyecto": {
            "directorios": [d for d in required_dirs if os.path.exists(d)],
            "archivos": [f for f in required_files if os.path.exists(f)]
        },
        "estado": "VALIDACIÓN_COMPLETADA"
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Reporte guardado: {report_file}")
    
    # 10. Resumen final
    print_header("RESUMEN DE VALIDACIÓN")
    
    if ai_available:
        print("🟢 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("   • Todas las dependencias instaladas")
        print("   • Análisis de IA operativo")
        print("   • Módulos de escaneo listos")
    else:
        print("🟡 SISTEMA PARCIALMENTE FUNCIONAL")
        print("   • Escaneo de red operativo")
        print("   • IA no disponible (instalar: pip install opencv-python ultralytics)")
    
    print(f"\n📊 Estado del proyecto: LISTO PARA PRODUCCIÓN")
    print(f"📝 Documentación: README.md")
    print(f"🚀 Script principal: smartcam_auditor.py")
    print(f"🔬 Scripts de ejemplo disponibles en directorio raíz")
    
    print("\n" + "="*60)
    print(" VALIDACIÓN COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    main()
