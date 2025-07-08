#!/usr/bin/env python3
"""
Verificación completa de la integración del módulo fingerprint_nmap
Este script verifica que la función fingerprint_camaras funciona correctamente
desde su módulo dedicado y se integra bien con el sistema principal.
"""

import sys
import os
import json

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import_fingerprint():
    """Verifica que se puede importar la función desde el módulo correcto"""
    print("🔍 Test 1: Verificando importación desde scanner.fingerprint_nmap")
    try:
        from scanner.fingerprint_nmap import fingerprint_camaras, resumen_fingerprinting, fingerprint_dispositivo_unico
        print("   ✅ Importación exitosa")
        print(f"   📦 fingerprint_camaras: {callable(fingerprint_camaras)}")
        print(f"   📦 resumen_fingerprinting: {callable(resumen_fingerprinting)}")
        print(f"   📦 fingerprint_dispositivo_unico: {callable(fingerprint_dispositivo_unico)}")
        return True
    except Exception as e:
        print(f"   ❌ Error en importación: {e}")
        return False

def test_function_signature():
    """Verifica que la función tenga la signatura correcta"""
    print("\n🔍 Test 2: Verificando signatura de función")
    try:
        from scanner.fingerprint_nmap import fingerprint_camaras
        import inspect
        
        sig = inspect.signature(fingerprint_camaras)
        params = list(sig.parameters.keys())
        
        print(f"   📋 Parámetros: {params}")
        
        if 'lista_ips' in params:
            print("   ✅ Signatura correcta")
            return True
        else:
            print("   ❌ Signatura incorrecta - falta 'lista_ips'")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando signatura: {e}")
        return False

def test_function_mock():
    """Prueba la función con datos mock para verificar formato de salida"""
    print("\n🔍 Test 3: Verificando formato de salida con mock")
    try:
        from scanner.fingerprint_nmap import fingerprint_camaras
        
        # Usar IPs que probablemente no existan para evitar escaneos reales
        mock_ips = ["10.255.255.1", "10.255.255.2"]
        
        print(f"   📡 Ejecutando fingerprinting en IPs mock: {mock_ips}")
        results = fingerprint_camaras(mock_ips)
        
        print(f"   📊 Resultados obtenidos: {len(results)} elementos")
        
        # Verificar estructura de salida
        if isinstance(results, list):
            print("   ✅ Salida es una lista")
            
            if results:
                primer_resultado = results[0]
                campos_esperados = ['ip', 'sistema', 'servicios', 'posible_marca']
                
                for campo in campos_esperados:
                    if campo in primer_resultado:
                        print(f"   ✅ Campo '{campo}' presente")
                    else:
                        print(f"   ❌ Campo '{campo}' faltante")
                        return False
                
                print("   ✅ Estructura de salida correcta")
                return True
            else:
                print("   ⚠️  Lista vacía (esperado para IPs mock)")
                return True
        else:
            print(f"   ❌ Salida no es lista: {type(results)}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en test de función: {e}")
        return False

def test_integration_smartcam():
    """Verifica que se pueda importar desde el script principal"""
    print("\n🔍 Test 4: Verificando integración con smartcam_auditor.py")
    try:
        # Leer el contenido del script principal
        with open("smartcam_auditor.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verificar que contiene la importación correcta
        if "from scanner.fingerprint_nmap import fingerprint_camaras" in content:
            print("   ✅ smartcam_auditor.py contiene la importación correcta")
            
            # Verificar que no tiene importación incorrecta
            if "from scanner.network_scanner import fingerprint_camaras" not in content:
                print("   ✅ No hay importaciones duplicadas")
                return True
            else:
                print("   ❌ Importación duplicada encontrada")
                return False
        else:
            print("   ❌ smartcam_auditor.py no contiene la importación correcta")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando integración: {e}")
        return False

def test_helper_functions():
    """Verifica las funciones auxiliares del módulo"""
    print("\n🔍 Test 5: Verificando funciones auxiliares")
    try:
        from scanner.fingerprint_nmap import resumen_fingerprinting
        
        # Datos mock para el resumen
        mock_results = [
            {"ip": "192.168.1.1", "posible_marca": "Hikvision", "sistema": "Linux"},
            {"ip": "192.168.1.2", "posible_marca": "Dahua", "sistema": "Linux"},
            {"ip": "192.168.1.3", "error": "timeout"},
        ]
        
        resumen = resumen_fingerprinting(mock_results)
        
        campos_esperados = ['total_analizado', 'exitosos', 'con_marca', 'distribución_marcas', 'tasa_exito']
        
        for campo in campos_esperados:
            if campo in resumen:
                print(f"   ✅ Campo '{campo}' presente en resumen")
            else:
                print(f"   ❌ Campo '{campo}' faltante en resumen")
                return False
        
        print(f"   📊 Resumen generado: {resumen}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en funciones auxiliares: {e}")
        return False

def test_no_duplication():
    """Verifica que no hay duplicación de código"""
    print("\n🔍 Test 6: Verificando ausencia de duplicación")
    try:
        # Verificar que network_scanner.py no contiene fingerprint_camaras
        with open("scanner/network_scanner.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "def fingerprint_camaras(" not in content:
            print("   ✅ network_scanner.py no contiene duplicación de fingerprint_camaras")
            return True
        else:
            print("   ❌ network_scanner.py aún contiene fingerprint_camaras duplicado")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando duplicación: {e}")
        return False

def main():
    """Ejecuta todos los tests de verificación"""
    print("🚀 VERIFICACIÓN COMPLETA - INTEGRACIÓN FINGERPRINT_NMAP")
    print("=" * 60)
    
    tests = [
        test_import_fingerprint,
        test_function_signature,
        test_function_mock,
        test_integration_smartcam,
        test_helper_functions,
        test_no_duplication
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Error inesperado en test: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 RESULTADOS: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡VERIFICACIÓN COMPLETADA EXITOSAMENTE!")
        print("✅ El módulo scanner.fingerprint_nmap está correctamente integrado")
        print("\n📋 RESUMEN DE CAPACIDADES:")
        print("   • fingerprint_camaras(lista_ips) - Función principal")
        print("   • fingerprint_dispositivo_unico(ip) - Análisis individual")
        print("   • resumen_fingerprinting(resultados) - Estadísticas")
        print("   • Integración completa con smartcam_auditor.py")
        print("   • Sin duplicación de código")
        
        print("\n💡 EJEMPLO DE USO:")
        print("   from scanner.fingerprint_nmap import fingerprint_camaras")
        print("   resultados = fingerprint_camaras(['192.168.1.100'])")
        print("   for cam in resultados:")
        print("       print(f'IP: {cam[\"ip\"]} - Marca: {cam[\"posible_marca\"]}')")
        
    else:
        print("❌ Algunos tests fallaron - revisar errores arriba")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
