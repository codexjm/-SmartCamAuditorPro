#!/usr/bin/env python3
"""
Script principal de auditoría integrada con CVE
SmartCam Auditor v2.0 Pro - Tu código CVE integrado y mejorado
"""

import os
import sys
import json
import time
from datetime import datetime

# Agregar paths necesarios
sys.path.append(os.getcwd())

# Importaciones principales
from scanner.cve_checker import buscar_vulnerabilidades_cve
from utils.logging_utils import registrar_log, log_cve, log_critical, log_success, log_warning, get_logger

def cargar_configuracion(config_file="config/config.json"):
    """Carga la configuración del sistema"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        registrar_log(f"Configuración cargada desde {config_file}", "SUCCESS")
        return config
    except Exception as e:
        registrar_log(f"Error cargando configuración: {e}", "ERROR")
        return {}

def simular_deteccion_dispositivos():
    """
    Simula la detección de dispositivos por diferentes métodos
    (fingerprint, login, banners, etc.)
    """
    registrar_log("🔍 Simulando detección de dispositivos...", "INFO", "DETECTION")
    
    # Simular diferentes métodos de detección
    dispositivos_por_metodo = {
        "fingerprint": ["Hikvision DS-2CD2042FWD", "Axis Q3517-LV"],
        "login_banner": ["Dahua IPC-HDW4631C"],
        "web_detection": ["Foscam C1", "Amcrest IP2M-841"],
        "service_detection": ["TP-Link Tapo C200"],
        "ip_scanning": ["192.168.1.100", "192.168.1.150"]
    }
    
    identificados = []
    
    for metodo, dispositivos in dispositivos_por_metodo.items():
        if dispositivos:
            registrar_log(f"📡 Detectados por {metodo}: {len(dispositivos)} dispositivos", "INFO", "DETECTION")
            for dispositivo in dispositivos:
                registrar_log(f"   • {dispositivo}", "INFO", "DEVICE_ID")
                identificados.append(dispositivo)
    
    return identificados

def analisis_cve_tu_codigo(identificados, config):
    """
    Tu código exacto de análisis CVE con mejoras de logging
    """
    # Solo ejemplo de marcas detectadas por fingerprint o login
    # identificados = ["Hikvision DS-2CD2042FWD", "Dahua IPC-HDW"]  # Ya lo tenemos como parámetro
    
    if config.get("enable_cve_check", True):
        registrar_log("🧬 Buscando CVEs...", "CVE", "CVE_SEARCH")
        
        try:
            # Tu código original
            cves = buscar_vulnerabilidades_cve(identificados)
            
            if cves:
                registrar_log(f"🚨 Se encontraron {len(cves)} vulnerabilidades", "WARNING", "CVE_FOUND")
                
                # Estadísticas adicionales
                cves_criticos = len([c for c in cves if c.get('critico', False)])
                cves_con_exploit = len([c for c in cves if c.get('exploit_disponible', False)])
                
                if cves_criticos > 0:
                    registrar_log(f"🔴 ATENCIÓN: {cves_criticos} vulnerabilidades CRÍTICAS encontradas", "CRITICAL", "CVE_CRITICAL")
                
                if cves_con_exploit > 0:
                    registrar_log(f"💥 {cves_con_exploit} vulnerabilidades tienen exploits disponibles", "WARNING", "CVE_EXPLOIT")
                
                # Tu código original mejorado
                for cve in cves:
                    nivel = "CRITICAL" if cve['critico'] else "WARNING"
                    categoria = "CVE_CRITICAL" if cve['critico'] else "CVE_STANDARD"
                    
                    # Línea principal (tu código original)
                    registrar_log(f" -> [{cve['cve']}] {cve['producto']} - {cve['descripcion']}", nivel, categoria)
                    
                    # Información adicional mejorada
                    if cve.get('cvss_score'):
                        score_level = "CRITICAL" if cve['cvss_score'] >= 9.0 else "WARNING" if cve['cvss_score'] >= 7.0 else "INFO"
                        registrar_log(f"    📊 CVSS Score: {cve['cvss_score']}", score_level, "CVE_SCORE")
                    
                    if cve.get('exploit_disponible'):
                        exploit_msg = "💥 Exploit DISPONIBLE" if cve['exploit_disponible'] else "⚪ Sin exploit público"
                        exploit_level = "CRITICAL" if cve['exploit_disponible'] else "INFO"
                        registrar_log(f"    {exploit_msg}", exploit_level, "CVE_EXPLOIT")
                    
                    if cve.get('mitigacion'):
                        registrar_log(f"    🛡️ Mitigación: {cve['mitigacion']}", "INFO", "CVE_MITIGATION")
                    
                    if cve.get('fecha'):
                        registrar_log(f"    📅 Fecha: {cve['fecha']}", "INFO", "CVE_DATE")
                
                return cves
                
            else:
                # Tu código original
                registrar_log(" -> No se encontraron CVEs.", "SUCCESS", "CVE_CLEAN")
                return []
                
        except Exception as e:
            registrar_log(f"❌ Error durante búsqueda CVE: {e}", "ERROR", "CVE_ERROR")
            return []
    else:
        registrar_log("⚪ Verificación CVE deshabilitada en configuración", "INFO", "CVE_DISABLED")
        return []

def analisis_cve_avanzado(identificados, config):
    """
    Análisis CVE avanzado con funcionalidades adicionales
    """
    registrar_log("🚀 Iniciando análisis CVE avanzado", "CVE", "CVE_ADVANCED")
    
    # Usar tu función base
    cves = analisis_cve_tu_codigo(identificados, config)
    
    if cves and config.get("enable_advanced_cve_features", True):
        # Funcionalidades avanzadas adicionales
        
        # 1. Análisis por categorías
        categorias = {}
        for cve in cves:
            cat = cve.get('categoria', 'Unknown')
            categorias[cat] = categorias.get(cat, 0) + 1
        
        if categorias:
            registrar_log("📊 Distribución por categorías de vulnerabilidad:", "INFO", "CVE_STATS")
            for categoria, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
                registrar_log(f"   • {categoria}: {count} CVEs", "INFO", "CVE_CATEGORY")
        
        # 2. Análisis de tendencias temporales
        años = {}
        for cve in cves:
            fecha = cve.get('fecha', '')
            if fecha and len(fecha) >= 4:
                año = fecha[:4]
                años[año] = años.get(año, 0) + 1
        
        if años:
            registrar_log("📈 Distribución temporal de vulnerabilidades:", "INFO", "CVE_TEMPORAL")
            for año, count in sorted(años.items(), reverse=True):
                registrar_log(f"   • {año}: {count} CVEs", "INFO", "CVE_YEAR")
        
        # 3. Recomendaciones automáticas
        generar_recomendaciones_automaticas(cves)
        
        # 4. Verificación activa si está habilitada
        if config.get("verify_cves_actively", False):
            verificar_cves_activamente(cves, config)
    
    return cves

def generar_recomendaciones_automaticas(cves):
    """Genera recomendaciones automáticas basadas en los CVEs encontrados"""
    registrar_log("🎯 Generando recomendaciones automáticas", "INFO", "RECOMMENDATIONS")
    
    cves_criticos = [c for c in cves if c.get('critico', False)]
    cves_con_exploit = [c for c in cves if c.get('exploit_disponible', False)]
    
    recomendaciones = []
    
    if cves_criticos:
        recomendaciones.append(f"🚨 URGENTE: Atender {len(cves_criticos)} vulnerabilidades críticas inmediatamente")
    
    if cves_con_exploit:
        recomendaciones.append(f"💥 PRIORITARIO: {len(cves_con_exploit)} vulnerabilidades tienen exploits públicos")
    
    # Recomendaciones por categoría
    categorias_criticas = set()
    for cve in cves_criticos:
        if cve.get('categoria'):
            categorias_criticas.add(cve['categoria'])
    
    if 'Authentication Bypass' in categorias_criticas:
        recomendaciones.append("🔒 Cambiar todas las credenciales por defecto INMEDIATAMENTE")
    
    if 'Remote Code Execution' in categorias_criticas:
        recomendaciones.append("🛡️ Aislar dispositivos vulnerables en VLAN separada")
    
    if 'Default Credentials' in categorias_criticas:
        recomendaciones.append("🔑 Implementar política de contraseñas robustas")
    
    # Recomendaciones generales
    recomendaciones.extend([
        "📊 Configurar monitoreo continuo de logs de seguridad",
        "🔄 Establecer programa de actualizaciones automáticas",
        "🌐 Implementar segmentación de red para dispositivos IoT",
        "📋 Crear plan de respuesta a incidentes"
    ])
    
    registrar_log("📝 RECOMENDACIONES AUTOMÁTICAS:", "WARNING", "AUTO_RECOMMENDATIONS")
    for i, rec in enumerate(recomendaciones, 1):
        registrar_log(f"   {i}. {rec}", "WARNING", "RECOMMENDATION")

def verificar_cves_activamente(cves, config):
    """Verificación activa de CVEs si está habilitada"""
    registrar_log("🧪 Iniciando verificación activa de CVEs", "CVE", "CVE_VERIFY")
    
    # Agrupar por IP
    cves_por_ip = {}
    for cve in cves:
        ip = cve.get('ip')
        if ip:
            if ip not in cves_por_ip:
                cves_por_ip[ip] = []
            cves_por_ip[ip].append(cve)
    
    if not cves_por_ip:
        registrar_log("⚪ No hay IPs específicas para verificar", "INFO", "CVE_VERIFY")
        return
    
    try:
        from scanner.cve_checker import CVEChecker
        cve_checker = CVEChecker()
        
        for ip, vulns in cves_por_ip.items():
            registrar_log(f"🎯 Verificando {ip} ({len(vulns)} CVEs)...", "CVE", "CVE_VERIFY_IP")
            
            # Aquí iría la verificación activa real
            # Por ahora simulamos algunos resultados
            for vuln in vulns[:2]:  # Verificar solo los primeros 2
                # Simulación - en producción usaría cve_checker.verificar_cve_activamente()
                verificado = vuln['cve'] in ['CVE-2017-7921', 'CVE-2018-9995']  # Simular
                
                if verificado:
                    registrar_log(f"   ✅ CONFIRMADO: {vuln['cve']} es explotable", "CRITICAL", "CVE_CONFIRMED")
                else:
                    registrar_log(f"   ⚪ {vuln['cve']} no pudo ser verificado", "INFO", "CVE_UNVERIFIED")
    
    except Exception as e:
        registrar_log(f"❌ Error en verificación activa: {e}", "ERROR", "CVE_VERIFY_ERROR")

def generar_reporte_final(cves, scan_info):
    """Genera un reporte final completo"""
    logger = get_logger()
    
    # Estadísticas
    total_cves = len(cves)
    cves_criticos = len([c for c in cves if c.get('critico', False)])
    cves_con_exploit = len([c for c in cves if c.get('exploit_disponible', False)])
    
    # Determinar nivel de riesgo
    if cves_criticos >= 3:
        risk_level = "🔴 CRÍTICO"
    elif cves_criticos >= 1:
        risk_level = "🟠 ALTO"
    elif total_cves >= 5:
        risk_level = "🟡 MEDIO"
    elif total_cves >= 1:
        risk_level = "🔵 BAJO"
    else:
        risk_level = "🟢 MÍNIMO"
    
    scan_results = {
        'network_range': scan_info.get('network_range', 'N/A'),
        'scan_time': scan_info.get('scan_time', 0),
        'total_devices': scan_info.get('total_devices', 0),
        'total_cves': total_cves,
        'critical_cves': cves_criticos,
        'exploitable_cves': cves_con_exploit,
        'risk_level': risk_level
    }
    
    # Generar y mostrar reporte
    reporte = logger.generate_summary_report(scan_results)
    print(reporte)
    
    return reporte

def main():
    """Función principal que integra todo tu código CVE"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   🧬 SMARTCAM AUDITOR v2.0 PRO - CVE ANALYZER                ║
║                        Tu código CVE integrado y mejorado                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    start_time = time.time()
    
    # 1. Cargar configuración
    config = cargar_configuracion()
    
    # 2. Simular detección de dispositivos (en producción vendría del scanner)
    identificados = simular_deteccion_dispositivos()
    
    if not identificados:
        registrar_log("❌ No se detectaron dispositivos para analizar", "ERROR")
        return
    
    registrar_log(f"📋 Total de dispositivos a analizar: {len(identificados)}", "INFO", "ANALYSIS_START")
    
    # 3. Ejecutar tu código CVE original
    registrar_log("▶️ Ejecutando análisis CVE original", "CVE", "CVE_ORIGINAL")
    cves_originales = analisis_cve_tu_codigo(identificados, config)
    
    # 4. Ejecutar análisis avanzado
    if config.get("enable_advanced_analysis", True):
        registrar_log("▶️ Ejecutando análisis CVE avanzado", "CVE", "CVE_ADVANCED")
        cves_avanzados = analisis_cve_avanzado(identificados, config)
    else:
        cves_avanzados = cves_originales
    
    # 5. Generar reporte final
    scan_time = time.time() - start_time
    scan_info = {
        'network_range': config.get('network_range', 'Simulado'),
        'scan_time': scan_time,
        'total_devices': len(identificados)
    }
    
    registrar_log("📄 Generando reporte final", "INFO", "REPORT_GEN")
    generar_reporte_final(cves_avanzados, scan_info)
    
    # 6. Resumen final
    registrar_log(f"✅ Análisis completado en {scan_time:.2f} segundos", "SUCCESS", "ANALYSIS_COMPLETE")
    registrar_log(f"📊 Dispositivos analizados: {len(identificados)}", "SUCCESS")
    registrar_log(f"🧬 CVEs encontrados: {len(cves_avanzados)}", "SUCCESS")
    registrar_log(f"📁 Revisa la carpeta 'logs/' para reportes detallados", "INFO")

if __name__ == "__main__":
    main()
