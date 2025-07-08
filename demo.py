#!/usr/bin/env python3
"""
SmartCam Auditor v2.0 Pro - Script de Demostración
Muestra las capacidades del sistema con datos de ejemplo
"""

import os
import json
import time
from datetime import datetime

def create_demo_logs():
    """Crear logs de demostración para mostrar las funcionalidades"""
    
    # Crear directorio de logs si no existe
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Log de auditoría de ejemplo 1
    demo_log_1 = f"""
========================================
🔒 SmartCam Auditor v2.0 Pro
========================================
📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Auditoría: Red Corporativa Principal
🌐 Redes: 192.168.1.0/24
========================================

[INFO] Iniciando escaneo de seguridad...
[INFO] Red objetivo: 192.168.1.0/24
[INFO] Dispositivos encontrados: 5

📱 DISPOSITIVO: 192.168.1.101
   🏷️ Tipo: Cámara IP Hikvision DS-2CD2032-I
   🔌 Puertos abiertos: 80, 443, 554, 8000
   🔑 Credenciales: ❌ admin/admin (VULNERABLE)
   ⚠️ Vulnerabilidades: 
      - [CRÍTICA] Credenciales por defecto
      - [ALTA] Puerto Telnet expuesto (23)
      - [MEDIA] Firmware desactualizado (v5.2.0)

📱 DISPOSITIVO: 192.168.1.102  
   🏷️ Tipo: Cámara IP Dahua IPC-HFW1230S
   🔌 Puertos abiertos: 80, 443, 37777
   🔑 Credenciales: ✅ Protegidas
   ⚠️ Vulnerabilidades:
      - [BAJA] HTTP sin HTTPS forzado

📱 DISPOSITIVO: 192.168.1.103
   🏷️ Tipo: DVR Hikvision DS-7608NI-K2
   🔌 Puertos abiertos: 80, 8000, 554
   🔑 Credenciales: ❌ admin/12345 (VULNERABLE)
   ⚠️ Vulnerabilidades:
      - [CRÍTICA] Credenciales débiles  
      - [ALTA] Interfaz web sin autenticación 2FA

📱 DISPOSITIVO: 192.168.1.104
   🏷️ Tipo: Cámara IP TP-Link Tapo C200
   🔌 Puertos abiertos: 443, 1935
   🔑 Credenciales: ✅ Protegidas
   ⚠️ Vulnerabilidades: Sin vulnerabilidades críticas

📱 DISPOSITIVO: 192.168.1.105
   🏷️ Tipo: Sistema NVR Synology VS960HD
   🔌 Puertos abiertos: 80, 443, 5000, 5001
   🔑 Credenciales: ✅ Protegidas
   ⚠️ Vulnerabilidades:
      - [MEDIA] Puerto de gestión expuesto

========================================
📊 RESUMEN DE SEGURIDAD
========================================
✅ Dispositivos encontrados: 5
❌ Vulnerabilidades críticas: 2
⚠️ Vulnerabilidades totales: 6
🔑 Credenciales comprometidas: 2
📈 Nivel de riesgo: ALTO

========================================
💡 RECOMENDACIONES
========================================
1. Cambiar inmediatamente credenciales por defecto
2. Actualizar firmware de dispositivos Hikvision
3. Implementar segmentación de red para cámaras
4. Configurar autenticación de dos factores
5. Cerrar puertos innecesarios (Telnet, gestión)
6. Implementar monitoreo continuo de seguridad

========================================
[INFO] Auditoría completada exitosamente
[INFO] Tiempo total: 3 minutos 45 segundos
[INFO] Reporte guardado en: logs/audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt
========================================
    """
    
    # Guardar log de demostración 1
    with open(f"{log_dir}/demo_audit_corporate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w', encoding='utf-8') as f:
        f.write(demo_log_1.strip())
    
    # Log de auditoría de ejemplo 2 (auditoría rápida)
    demo_log_2 = f"""
========================================
🔒 SmartCam Auditor v2.0 Pro - Escaneo Rápido
========================================
📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Auditoría: Red de Invitados
🌐 Redes: 10.0.0.0/24
========================================

[INFO] Modo escaneo rápido activado
[INFO] Red objetivo: 10.0.0.0/24
[INFO] Dispositivos encontrados: 2

📱 DISPOSITIVO: 10.0.0.50
   🏷️ Tipo: Cámara IP Xiaomi Mi Home Security 360°
   🔌 Puertos abiertos: 80, 443, 8080
   🔑 Credenciales: ✅ Protegidas
   ⚠️ Vulnerabilidades: Sin vulnerabilidades críticas

📱 DISPOSITIVO: 10.0.0.51
   🏷️ Tipo: Ring Video Doorbell Pro
   🔌 Puertos abiertos: 443, 1935
   🔑 Credenciales: ✅ Protegidas (Cloud)
   ⚠️ Vulnerabilidades: Sin vulnerabilidades críticas

========================================
📊 RESUMEN DE SEGURIDAD
========================================
✅ Dispositivos encontrados: 2
❌ Vulnerabilidades críticas: 0
⚠️ Vulnerabilidades totales: 0
🔑 Credenciales comprometidas: 0
📈 Nivel de riesgo: BAJO

========================================
💡 RECOMENDACIONES
========================================
1. Red de invitados configurada correctamente
2. Dispositivos con buenas prácticas de seguridad
3. Mantener firmware actualizado
4. Revisar periódicamente configuraciones

========================================
[INFO] Escaneo rápido completado
[INFO] Tiempo total: 45 segundos
========================================
    """
    
    # Guardar log de demostración 2
    with open(f"{log_dir}/demo_quick_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w', encoding='utf-8') as f:
        f.write(demo_log_2.strip())
    
    # Log de diagnóstico del sistema
    demo_log_3 = f"""
========================================
🔧 SmartCam Auditor - Diagnóstico del Sistema
========================================
📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🖥️ Sistema: Información de diagnóstico
========================================

[INFO] Iniciando diagnóstico del sistema...

🔧 CONFIGURACIÓN DEL SISTEMA
- Python: 3.10.6
- SmartCam Auditor: v2.0.0 Pro
- Flask: 2.3.2
- psutil: 7.0.0

🌐 CONFIGURACIÓN DE RED
- Interfaz principal: WiFi (192.168.1.156)
- Conectividad: ✅ Online
- DNS: 8.8.8.8, 1.1.1.1
- Latencia promedio: 15ms

📁 ARCHIVOS DE CONFIGURACIÓN
- config/config.json: ✅ Cargado correctamente
- config/networks.txt: ✅ 3 redes configuradas
- config/credentials.json: ✅ 15 credenciales de prueba

💾 RECURSOS DEL SISTEMA
- CPU: Intel Core i7 (8 cores) - Uso: 25%
- RAM: 16GB total, 12GB disponible
- Disco: 512GB SSD - 75% libre
- Red: 1Gbps Ethernet

📊 ESTADÍSTICAS DE USO
- Auditorías ejecutadas: 8
- Dispositivos analizados: 23
- Vulnerabilidades encontradas: 12
- Logs generados: 15 archivos

🔐 ESTADO DE SEGURIDAD
- Panel web: ✅ Activo (puerto 5000)
- Rutas API: ✅ Protegidas
- Validación de archivos: ✅ Activa
- Logs de seguridad: ✅ Habilitados

========================================
[INFO] Diagnóstico completado exitosamente
[INFO] Sistema operando normalmente
========================================
    """
    
    # Guardar log de diagnóstico
    with open(f"{log_dir}/system_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w', encoding='utf-8') as f:
        f.write(demo_log_3.strip())
    
    print("✅ Logs de demostración creados exitosamente")
    return True

def show_demo_info():
    """Mostrar información sobre la demostración"""
    print("=" * 60)
    print("🔒 SmartCam Auditor v2.0 Pro - Demostración")
    print("=" * 60)
    print()
    print("📋 Esta demostración incluye:")
    print("   • Logs de auditoría de ejemplo")
    print("   • Datos de dispositivos simulados") 
    print("   • Vulnerabilidades de ejemplo")
    print("   • Reportes de diagnóstico")
    print()
    print("🌐 Panel Web disponible en:")
    print("   • Local: http://localhost:5000")
    print("   • Red: http://192.168.1.156:5000")
    print()
    print("🎯 Funcionalidades a probar:")
    print("   • Dashboard con estadísticas")
    print("   • Visualización de logs")
    print("   • Descarga de archivos")
    print("   • Eliminación de logs")
    print("   • Información del sistema")
    print("   • Exportación de reportes")
    print()
    print("⚠️ NOTA: Los datos mostrados son de demostración")
    print("   Para auditorías reales, configure redes en config/networks.txt")
    print()
    print("=" * 60)

def main():
    """Función principal de demostración"""
    show_demo_info()
    print("\n📄 Creando logs de demostración...")
    
    if create_demo_logs():
        print("\n🎉 Demostración preparada exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   1. Accede al panel web: http://localhost:5000")
        print("   2. Explora la sección 'Archivos de Logs'") 
        print("   3. Prueba las funciones de visualización y descarga")
        print("   4. Haz clic en 'Info Sistema' para ver detalles")
        print("   5. Ejecuta una auditoría real configurando redes")
        print("\n🔄 Para actualizar logs: python demo.py")
    else:
        print("\n❌ Error creando logs de demostración")

if __name__ == "__main__":
    main()
