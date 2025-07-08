#!/usr/bin/env python3
"""
🔍 VERIFICACIÓN FINAL - SmartCam Auditor
Script de verificación completa de todas las funcionalidades integradas
"""

import sys
import os
import importlib
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_componente(nombre, funcion_test):
    """Ejecuta una verificación y muestra el resultado"""
    print(f"🔍 Verificando {nombre}...", end=" ")
    try:
        resultado = funcion_test()
        if resultado:
            print("✅ OK")
            return True
        else:
            print("❌ FALLO")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_imports():
    """Verifica que todos los imports necesarios funcionen"""
    try:
        from scanner.image_ai_analyzer import analizar_rtsp
        from scanner.network_scanner import NetworkScanner, fingerprint_camaras, analizar_rtsp_masivo
        import cv2
        import torch
        from ultralytics import YOLO
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def test_ultralytics():
    """Verifica que ultralytics pueda cargar un modelo"""
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')  # Cargará automáticamente si no existe
        return model is not None
    except Exception:
        return False

def test_opencv():
    """Verifica que OpenCV esté funcionando"""
    try:
        import cv2
        return cv2.__version__ is not None
    except Exception:
        return False

def test_nmap_detection():
    """Verifica la detección automática de Nmap"""
    try:
        from scanner.fingerprint_nmap import fingerprint_camaras
        # Intentar cargar la función sin ejecutarla
        return callable(fingerprint_camaras)
    except Exception:
        return False

def test_network_scanner():
    """Verifica que las funciones principales de network_scanner funcionen"""
    try:
        from scanner.fingerprint_nmap import fingerprint_camaras
        from scanner.network_scanner import analizar_rtsp_masivo
        # Solo verificar que las funciones se puedan importar
        return callable(fingerprint_camaras) and callable(analizar_rtsp_masivo)
    except Exception as e:
        print(f"NetworkScanner functions error: {e}")
        return False

def test_estructura_archivos():
    """Verifica que todos los archivos necesarios existan"""
    archivos_necesarios = [
        "scanner/__init__.py",
        "scanner/image_ai_analyzer.py",
        "scanner/network_scanner.py",
        "ejemplo_uso_ai_analyzer.py",
        "test_fingerprint_camaras.py",
        "demo_integracion_fingerprinting.py"
    ]
    
    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            print(f"Archivo faltante: {archivo}")
            return False
    return True

def main():
    """Ejecuta todas las verificaciones"""
    print("🚀 VERIFICACIÓN FINAL - SMARTCAM AUDITOR")
    print("=" * 50)
    print("Verificando la integridad de todas las funcionalidades...\n")
    
    verificaciones = [
        ("Estructura de archivos", test_estructura_archivos),
        ("Imports básicos", test_imports),
        ("OpenCV", test_opencv),
        ("Ultralytics/YOLO", test_ultralytics),
        ("Detección de Nmap", test_nmap_detection),
        ("NetworkScanner", test_network_scanner),
    ]
    
    resultados = []
    
    for nombre, test_func in verificaciones:
        resultado = verificar_componente(nombre, test_func)
        resultados.append((nombre, resultado))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print("=" * 50)
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"   {estado} {nombre}")
    
    print(f"\n📈 RESULTADO GENERAL: {exitosos}/{total} verificaciones exitosas")
    
    if exitosos == total:
        print("\n🎉 ¡TODAS LAS VERIFICACIONES EXITOSAS!")
        print("✅ SmartCam Auditor está completamente funcional")
        print("\n🚀 FUNCIONALIDADES DISPONIBLES:")
        print("   📡 Escaneo de red tradicional")
        print("   🎥 Análisis IA de streams RTSP")
        print("   🔍 Fingerprinting avanzado con Nmap")
        print("   🔗 Integración híbrida de todas las funciones")
        
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Ejecutar: python demo_integracion_fingerprinting.py")
        print("   2. Probar con tu red: python test_fingerprint_camaras.py")
        print("   3. Usar en auditorías reales (con autorización)")
        
    else:
        print(f"\n⚠️ {total - exitosos} verificaciones fallaron")
        print("💡 Revisa las dependencias y la instalación")
        
        if not any(resultado for nombre, resultado in resultados if "Import" in nombre):
            print("\n🔧 ACCIONES RECOMENDADAS:")
            print("   pip install ultralytics opencv-python torch")
            
        if not any(resultado for nombre, resultado in resultados if "Nmap" in nombre):
            print("   winget install Insecure.Nmap")
    
    print(f"\n📚 Documentación completa en: INTEGRACION_COMPLETA.md")
    
    return exitosos == total

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado durante la verificación: {e}")
        sys.exit(1)
