#!/usr/bin/env python3
"""
SmartCam Auditor - Herramienta de auditoría de seguridad para cámaras inteligentes
Autor: SmartCam Security Team
Fecha: 7 de julio de 2025
"""

import json
from scanner.network_scanner import scan_network
from scanner.port_checker import check_ports
from scanner.login_tester import test_logins
from scanner.log_manager import save_log
from scanner.advanced_testing import advanced_camera_testing, generate_professional_report
from scanner.fingerprint_nmap import fingerprint_camaras, resumen_fingerprinting
# Importar funciones de comparación de logs desde el nuevo módulo diff_analyzer
from scanner.diff_analyzer import (
    comparar_logs_actual_vs_anterior,
    analizar_cambios_dispositivos,
    generar_reporte_cambios,
    monitorear_cambios_automatico
)

def load_config():
    """Carga la configuración desde config.json"""
    try:
        with open("config/config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[WARNING] No se encontró config/config.json, usando valores por defecto")
        return {"alert_mode": "console", "log_folder": "logs"}
    except Exception as e:
        print(f"[ERROR] Error al leer configuración: {e}")
        return {"alert_mode": "console", "log_folder": "logs"}

def show_alert(message, config):
    """Muestra alertas según el modo configurado"""
    if config["alert_mode"] == "console":
        print(f"[!] ALERTA: {message}")
    # Aquí se pueden agregar otros modos como "file", "email", etc.

def save_fingerprint_log(fingerprint_results, config):
    """Guarda los resultados de fingerprinting en un archivo de log"""
    import os
    import datetime
    
    try:
        log_folder = config.get("log_folder", "logs")
        os.makedirs(log_folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fingerprint_file = os.path.join(log_folder, f"fingerprint_{timestamp}.json")
        
        with open(fingerprint_file, 'w', encoding='utf-8') as f:
            json.dump(fingerprint_results, f, indent=2, ensure_ascii=False)
        
        print(f"  [📄] Resultados de fingerprinting guardados en: {fingerprint_file}")
        
    except Exception as e:
        print(f"  [!] Error al guardar log de fingerprinting: {e}")

def main():
    """Función principal del auditor de cámaras inteligentes"""
    print("=== SmartCam Auditor - Iniciando auditoría ===")
    print("*** PARA USO EN REDES PROPIAS Y PRODUCTOS DE LA EMPRESA ***\n")
    
    # Cargar configuración
    config = load_config()
    print(f"[*] Configuración cargada - Modo alertas: {config['alert_mode']}, Logs: {config['log_folder']}")
    
    advanced_results = []  # Para el reporte profesional
    
    try:
        with open("config/networks.txt") as f:
            networks = [
                line.strip() for line in f.readlines() 
                if line.strip() and not line.strip().startswith('#')
            ]
    except FileNotFoundError:
        print("[ERROR] No se encontró el archivo config/networks.txt")
        return
    except Exception as e:
        print(f"[ERROR] Error al leer configuración: {e}")
        return

    for net in networks:
        print(f"\n[+] Escaneando red: {net}")
        try:
            devices = scan_network(net)

            if not devices:
                print(f"  [-] No se encontraron dispositivos en {net}")
                continue

            # Extraer IPs para fingerprinting
            device_ips = [device['ip'] for device in devices]
            
            # Verificar si el fingerprinting está habilitado en la configuración
            enable_fingerprint = config.get("enable_fingerprint", True)
            
            if enable_fingerprint:
                print(f"  [🔍] Ejecutando fingerprinting avanzado en {len(device_ips)} dispositivos...")
                try:
                    fingerprint_results = fingerprint_camaras(device_ips)
                    
                    # Mostrar resumen del fingerprinting
                    resumen = resumen_fingerprinting(fingerprint_results)
                    print(f"  [📊] Fingerprinting completado: {resumen['exitosos']}/{resumen['total_analizado']} exitosos")
                    
                    if resumen['con_marca'] > 0:
                        print(f"  [🎯] Marcas detectadas: {', '.join(resumen['distribución_marcas'].keys())}")
                    
                    # Guardar resultados de fingerprinting en logs
                    save_fingerprint_log(fingerprint_results, config)
                    
                except Exception as e:
                    print(f"  [!] Error en fingerprinting: {e}")
                    fingerprint_results = []
            else:
                print(f"  [⏩] Fingerprinting deshabilitado en configuración")
                fingerprint_results = []

            for device in devices:
                ip = device['ip']
                print(f"  [+] Analizando dispositivo: {ip}")
                ports = check_ports(ip)
                logins = test_logins(ip, ports)
                
                # Buscar información de fingerprinting para este dispositivo
                fingerprint_info = None
                if enable_fingerprint:
                    for fp in fingerprint_results:
                        if fp['ip'] == ip:
                            fingerprint_info = fp
                            break
                
                # Testing avanzado para empresas de cámaras
                advanced_result = advanced_camera_testing(ip, ports, config)
                if fingerprint_info:
                    advanced_result['fingerprint'] = fingerprint_info
                
                advanced_results.append(advanced_result)
                
                # Mostrar información de fingerprinting si está disponible
                if fingerprint_info and fingerprint_info.get('posible_marca'):
                    print(f"    [📱] Marca detectada: {fingerprint_info['posible_marca']}")
                    if fingerprint_info.get('sistema'):
                        print(f"    [💻] Sistema: {fingerprint_info['sistema']}")
                
                # Mostrar alerta si se encuentran vulnerabilidades
                if logins:
                    show_alert(f"Credenciales vulnerables encontradas en {ip}: {logins}", config)
                
                # Mostrar alertas de vulnerabilidades avanzadas
                vulns = advanced_result.get("vulnerabilities", [])
                for vuln in vulns:
                    if vuln["severity"] in ["CRITICAL", "HIGH"]:
                        show_alert(f"{vuln['severity']}: {vuln['type']} en {ip}", config)
                
                save_log(ip, ports, logins, config)
                
        except Exception as e:
            print(f"[ERROR] Error al escanear red {net}: {e}")
    
    print("\n[+] Auditoría completada. Revisa los logs generados.")
    
    # Análisis de cambios automático
    if config.get("enable_change_tracking", True):
        print("\n[🔍] Analizando cambios respecto a auditoría anterior...")
        try:
            # Monitorear cambios automáticamente
            umbral_cambios = config.get("change_alert_threshold", 3)
            monitor_result = monitorear_cambios_automatico(umbral_cambios=umbral_cambios)
            
            if monitor_result['estado'] == 'ok':
                if monitor_result['alerta']:
                    print(f"🚨 CAMBIOS SIGNIFICATIVOS DETECTADOS!")
                    print(f"   📊 Total cambios: {monitor_result['total_cambios']}")
                    
                    for alerta in monitor_result['alertas']:
                        print(f"   {alerta}")
                    
                    # Generar reporte automático de cambios
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    reporte_file = f"logs/cambios_automatico_{timestamp}.txt"
                    
                    print(f"   📄 Generando reporte de cambios...")
                    generar_reporte_cambios(output_file=reporte_file)
                    
                    # Mostrar resumen rápido
                    cambios_detallados = monitor_result['cambios_detallados']
                    if cambios_detallados.get('dispositivos_nuevos'):
                        print(f"   🆕 Dispositivos nuevos: {', '.join(cambios_detallados['dispositivos_nuevos'])}")
                    if cambios_detallados.get('dispositivos_perdidos'):
                        print(f"   ❌ Dispositivos perdidos: {', '.join(cambios_detallados['dispositivos_perdidos'])}")
                    
                else:
                    print("✅ No hay cambios significativos desde la última auditoría")
                    
                    # Mostrar comparación simple
                    comparacion = comparar_logs_actual_vs_anterior()
                    if "No hay diferencias" not in comparacion:
                        print("   🔄 Diferencias menores detectadas - ver logs para detalles")
            else:
                print(f"   ⚠️ {monitor_result['mensaje']}")
                
        except Exception as e:
            print(f"   ❌ Error en análisis de cambios: {e}")
    
    # Generar reporte profesional
    if advanced_results:
        print("[+] Generando reporte profesional de seguridad...")
        generate_professional_report(advanced_results, config)

if __name__ == "__main__":
    main()
