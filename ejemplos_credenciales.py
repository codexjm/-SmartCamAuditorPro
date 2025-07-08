#!/usr/bin/env python3
"""
SmartCam Auditor - Ejemplo de Uso del Probador de Credenciales
Demuestra cómo integrar las pruebas de credenciales en scripts personalizados
"""

import os
import sys
from datetime import datetime

# Añadir el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ejemplo_basico():
    """Ejemplo básico de uso del probador de credenciales"""
    print("🔐 Ejemplo básico de pruebas de credenciales")
    print("=" * 50)
    
    try:
        from scanner.credential_tester import testear_credenciales, generar_reporte_credenciales
        
        # Lista de IPs detectadas (ejemplo)
        ips_detectadas = ["192.168.1.10", "192.168.1.15", "192.168.1.22"]  # Cámaras IP detectadas
        
        print(f"📡 Dispositivos a probar: {len(ips_detectadas)}")
        for ip in ips_detectadas:
            print(f"  • {ip}")
        
        print("\n🔍 Iniciando pruebas de credenciales...")
        
        # Ejecutar pruebas
        resultados_credenciales = testear_credenciales(
            ips_detectadas,
            puertos_http=[80, 8080, 443],  # Puertos web comunes
            incluir_rtsp=True,             # Incluir pruebas RTSP
            incluir_ssh=False              # No incluir SSH (puede ser lento)
        )
        
        print(f"\n📊 Resultados:")
        print(f"   Vulnerabilidades encontradas: {len(resultados_credenciales)}")
        
        if resultados_credenciales:
            print("\n🚨 Credenciales débiles detectadas:")
            for i, resultado in enumerate(resultados_credenciales, 1):
                print(f"   {i}. {resultado}")
        else:
            print("\n✅ No se encontraron credenciales débiles")
        
        # Generar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_reporte = f"logs/ejemplo_credenciales_{timestamp}.txt"
        
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        reporte = generar_reporte_credenciales(resultados_credenciales, archivo_reporte)
        print(f"\n📄 Reporte guardado en: {archivo_reporte}")
        
        return resultados_credenciales
        
    except ImportError as e:
        print(f"❌ Error: Módulo de credenciales no disponible: {e}")
        print("💡 Instala las dependencias: pip install requests paramiko")
        return []

def ejemplo_integracion_log():
    """Ejemplo de cómo integrar en un log de auditoría existente"""
    print("\n🔐 Ejemplo de integración en log de auditoría")
    print("=" * 50)
    
    # Simular un archivo de log existente
    log_path = "logs/ejemplo_auditoria_con_credenciales.txt"
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Crear log inicial
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("🔒 REPORTE DE AUDITORÍA DE SEGURIDAD\n")
        f.write("=" * 50 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("[📡 Escaneo de red completado]\n")
        f.write("Dispositivos encontrados: 3\n")
        f.write("  • 192.168.1.10 (Cámara IP)\n")
        f.write("  • 192.168.1.15 (Cámara IP)\n")
        f.write("  • 192.168.1.22 (DVR)\n\n")
    
    try:
        from scanner.credential_tester import testear_credenciales
        
        # IPs detectadas en el escaneo anterior
        ips_detectadas = ["192.168.1.10", "192.168.1.15", "192.168.1.22"]
        
        print(f"🔍 Probando credenciales en {len(ips_detectadas)} dispositivos...")
        
        # Ejecutar pruebas de credenciales
        resultados_credenciales = testear_credenciales(ips_detectadas)
        
        # Agregar resultados al log existente
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[🔐 Resultado de pruebas de credenciales débiles:]\n")
            if resultados_credenciales:
                f.write(f"Vulnerabilidades críticas encontradas: {len(resultados_credenciales)}\n")
                for r in resultados_credenciales:
                    f.write(" -> " + r + "\n")
                f.write("\n⚠️ ACCIÓN URGENTE REQUERIDA:\n")
                f.write("   • Cambiar todas las credenciales por defecto\n")
                f.write("   • Implementar contraseñas fuertes\n")
                f.write("   • Revisar logs de acceso\n")
            else:
                f.write(" -> No se encontraron credenciales débiles.\n")
                f.write(" -> ✅ Configuración de credenciales segura\n")
            f.write("\n")
        
        print(f"✅ Resultados integrados en: {log_path}")
        
        # Mostrar contenido final del log
        print(f"\n📄 Contenido del log generado:")
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(content)
            
    except ImportError as e:
        print(f"❌ Error: {e}")
        # Fallback sin el módulo real
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("[🔐 Pruebas de credenciales (simulación):]\n")
            f.write(" -> Módulo no disponible, ejecutando simulación\n")
            f.write(" -> Para pruebas reales: pip install requests paramiko\n\n")

def ejemplo_personalizado():
    """Ejemplo de configuración personalizada"""
    print("\n🔐 Ejemplo de configuración personalizada")
    print("=" * 50)
    
    try:
        from scanner.credential_tester import testear_credenciales
        
        # Configuración personalizada para diferentes tipos de dispositivos
        cámaras_ip = ["192.168.1.100", "192.168.1.101"]
        routers = ["192.168.1.1", "192.168.1.254"]
        
        print("📹 Probando credenciales en cámaras IP...")
        resultados_camaras = testear_credenciales(
            cámaras_ip,
            puertos_http=[80, 8080, 443],
            incluir_rtsp=True,    # Importante para cámaras
            incluir_ssh=False
        )
        
        print("🌐 Probando credenciales en routers...")
        resultados_routers = testear_credenciales(
            routers,
            puertos_http=[80, 443, 8080],
            incluir_rtsp=False,   # Routers no tienen RTSP
            incluir_ssh=True      # Routers pueden tener SSH
        )
        
        print(f"\n📊 Resultados:")
        print(f"   Cámaras vulnerables: {len(resultados_camaras)}")
        print(f"   Routers vulnerables: {len(resultados_routers)}")
        
        return resultados_camaras + resultados_routers
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        return []

def main():
    """Función principal de ejemplos"""
    print("🚀 SmartCam Auditor - Ejemplos de Uso del Probador de Credenciales")
    print("⚠️ Solo para uso en redes propias o con autorización explícita")
    print()
    
    # Ejecutar ejemplos
    ejemplo_basico()
    ejemplo_integracion_log()
    ejemplo_personalizado()
    
    print("\n✅ Ejemplos completados")
    print("💡 Revisa los archivos generados en el directorio 'logs/'")

if __name__ == "__main__":
    main()
