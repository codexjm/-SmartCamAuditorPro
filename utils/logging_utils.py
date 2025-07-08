#!/usr/bin/env python3
"""
Utilidades de logging y registro para SmartCam Auditor v2.0 Pro
Proporciona funciones mejoradas de logging con diferentes niveles y formateo
"""

import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

class AuditorLogger:
    """Logger avanzado para SmartCam Auditor"""
    
    def __init__(self, config_file="config/config.json"):
        self.config = self.load_config(config_file)
        self.log_levels = {
            "DEBUG": {"icono": "🔍", "color": "\033[90m"},    # Gris
            "INFO": {"icono": "ℹ️", "color": "\033[94m"},     # Azul
            "WARNING": {"icono": "⚠️", "color": "\033[93m"},   # Amarillo
            "ERROR": {"icono": "❌", "color": "\033[91m"},     # Rojo
            "CVE": {"icono": "🧬", "color": "\033[95m"},       # Magenta
            "CRITICAL": {"icono": "🔴", "color": "\033[91m"},  # Rojo brillante
            "SUCCESS": {"icono": "✅", "color": "\033[92m"},   # Verde
            "SCAN": {"icono": "🔍", "color": "\033[96m"},      # Cian
            "VULN": {"icono": "🚨", "color": "\033[91m"},      # Rojo
            "SECURE": {"icono": "🛡️", "color": "\033[92m"}    # Verde
        }
        self.reset_color = "\033[0m"
        
        # Configuración de logging
        self.enable_colors = self.config.get("enable_color_logs", True)
        self.log_to_file = self.config.get("log_to_file", True)
        self.log_level = self.config.get("log_level", "INFO")
        
        # Crear directorio de logs
        if self.log_to_file:
            os.makedirs("logs", exist_ok=True)
    
    def load_config(self, config_file):
        """Carga configuración"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def registrar_log(self, mensaje: str, nivel: str = "INFO", categoria: str = None):
        """
        Función principal de logging mejorada
        
        Args:
            mensaje (str): Mensaje a registrar
            nivel (str): Nivel del log (DEBUG, INFO, WARNING, ERROR, etc.)
            categoria (str): Categoría opcional para el log
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Obtener información del nivel
        level_info = self.log_levels.get(nivel, {"icono": "📝", "color": ""})
        icono = level_info["icono"]
        color = level_info["color"] if self.enable_colors else ""
        
        # Formatear mensaje
        if categoria:
            log_entry = f"[{timestamp}] {icono} [{categoria}] {mensaje}"
        else:
            log_entry = f"[{timestamp}] {icono} {mensaje}"
        
        # Imprimir en consola con colores
        if self.enable_colors:
            print(f"{color}{log_entry}{self.reset_color}")
        else:
            print(log_entry)
        
        # Guardar en archivo
        if self.log_to_file:
            self._write_to_file(log_entry, nivel)
    
    def _write_to_file(self, log_entry: str, nivel: str):
        """Escribe al archivo de log"""
        try:
            # Archivo principal
            log_file = f"logs/audit_{datetime.now().strftime('%Y%m%d')}.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
            
            # Archivo específico para CVEs si es necesario
            if nivel in ["CVE", "CRITICAL", "VULN"]:
                cve_log_file = f"logs/cve_{datetime.now().strftime('%Y%m%d')}.log"
                with open(cve_log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + "\n")
                    
        except Exception as e:
            print(f"[ERROR] No se pudo escribir al log: {e}")
    
    def log_cve_analysis(self, identificadores: list, cves_found: list):
        """Logging especializado para análisis CVE"""
        self.registrar_log(f"Iniciando análisis CVE para {len(identificadores)} objetivos", "CVE", "CVE_ANALYSIS")
        
        for i, objetivo in enumerate(identificadores, 1):
            self.registrar_log(f"  {i}. {objetivo}", "INFO", "CVE_TARGET")
        
        if cves_found:
            # Estadísticas
            total = len(cves_found)
            criticos = len([c for c in cves_found if c.get('critico', False)])
            con_exploit = len([c for c in cves_found if c.get('exploit_disponible', False)])
            
            self.registrar_log(f"RESULTADO: {total} vulnerabilidades | {criticos} críticas | {con_exploit} con exploits", 
                             "VULN", "CVE_SUMMARY")
            
            # Detallar vulnerabilidades críticas
            for cve in cves_found:
                if cve.get('critico', False):
                    self.registrar_log(f"CRÍTICO: [{cve['cve']}] {cve['producto']} - {cve['descripcion'][:60]}...", 
                                     "CRITICAL", "CVE_CRITICAL")
        else:
            self.registrar_log("No se encontraron vulnerabilidades CVE", "SUCCESS", "CVE_CLEAN")
    
    def log_network_scan(self, network_range: str, devices_found: list):
        """Logging especializado para escaneo de red"""
        self.registrar_log(f"Escaneo de red iniciado: {network_range}", "SCAN", "NETWORK_SCAN")
        
        if devices_found:
            self.registrar_log(f"Dispositivos encontrados: {len(devices_found)}", "SUCCESS", "NETWORK_RESULT")
            
            for device in devices_found:
                self.registrar_log(f"Dispositivo: {device['ip']} - {device.get('device_type', 'Unknown')}", 
                                 "INFO", "DEVICE_FOUND")
                
                # Log de vulnerabilidades si existen
                if device.get('cve_count', 0) > 0:
                    self.registrar_log(f"  ⚠️ {device['cve_count']} CVEs encontrados ({device.get('critical_cves', 0)} críticos)", 
                                     "VULN", "DEVICE_VULN")
        else:
            self.registrar_log("No se encontraron dispositivos", "WARNING", "NETWORK_EMPTY")
    
    def log_credential_test(self, ip: str, resultado: dict):
        """Logging para pruebas de credenciales"""
        if resultado.get('success', False):
            self.registrar_log(f"Credenciales encontradas en {ip}: {resultado.get('credentials', 'N/A')}", 
                             "VULN", "CRED_FOUND")
        else:
            self.registrar_log(f"No se encontraron credenciales por defecto en {ip}", 
                             "SECURE", "CRED_SECURE")
    
    def log_system_status(self, status_info: dict):
        """Log del estado del sistema"""
        self.registrar_log("Estado del sistema SmartCam Auditor v2.0 Pro", "INFO", "SYSTEM")
        
        for key, value in status_info.items():
            self.registrar_log(f"  {key}: {value}", "INFO", "SYSTEM_INFO")
    
    def generate_summary_report(self, scan_results: dict) -> str:
        """Genera un reporte resumen y lo registra"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      📊 RESUMEN DE AUDITORÍA COMPLETA                        ║
║                        SmartCam Auditor v2.0 Pro                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

📅 Fecha: {timestamp}
🌐 Red analizada: {scan_results.get('network_range', 'N/A')}
⏱️ Tiempo total: {scan_results.get('scan_time', 'N/A')} segundos

📱 DISPOSITIVOS:
   • Total encontrados: {scan_results.get('total_devices', 0)}
   • Con vulnerabilidades: {scan_results.get('vulnerable_devices', 0)}
   • Seguros: {scan_results.get('secure_devices', 0)}

🚨 VULNERABILIDADES:
   • Total CVEs: {scan_results.get('total_cves', 0)}
   • Críticas: {scan_results.get('critical_cves', 0)}
   • Con exploits: {scan_results.get('exploitable_cves', 0)}
   • Verificadas: {scan_results.get('verified_cves', 0)}

🔐 CREDENCIALES:
   • Dispositivos con creds por defecto: {scan_results.get('default_creds_found', 0)}
   • Dispositivos seguros: {scan_results.get('secure_creds', 0)}

📈 NIVEL DE RIESGO: {scan_results.get('risk_level', 'DESCONOCIDO')}

═══════════════════════════════════════════════════════════════════════════════
"""
        
        # Guardar reporte
        if self.log_to_file:
            report_file = f"logs/summary_report_{int(time.time())}.txt"
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                self.registrar_log(f"Reporte resumen guardado: {report_file}", "SUCCESS", "REPORT")
            except Exception as e:
                self.registrar_log(f"Error guardando reporte: {e}", "ERROR", "REPORT")
        
        return summary

# Instancia global del logger
_global_logger = None

def get_logger(config_file="config/config.json") -> AuditorLogger:
    """Obtiene la instancia global del logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AuditorLogger(config_file)
    return _global_logger

def registrar_log(mensaje: str, nivel: str = "INFO", categoria: str = None):
    """Función de conveniencia para logging rápido"""
    logger = get_logger()
    logger.registrar_log(mensaje, nivel, categoria)

# Funciones de conveniencia para diferentes tipos de logs
def log_info(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "INFO", categoria)

def log_warning(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "WARNING", categoria)

def log_error(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "ERROR", categoria)

def log_cve(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "CVE", categoria)

def log_critical(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "CRITICAL", categoria)

def log_success(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "SUCCESS", categoria)

def log_vuln(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "VULN", categoria)

def log_secure(mensaje: str, categoria: str = None):
    registrar_log(mensaje, "SECURE", categoria)

if __name__ == "__main__":
    # Ejemplo de uso del logger
    print("🧪 Probando sistema de logging avanzado")
    
    # Diferentes niveles de log
    registrar_log("Sistema iniciado", "INFO")
    registrar_log("Configuración cargada", "SUCCESS")
    registrar_log("Advertencia de prueba", "WARNING")
    registrar_log("Vulnerabilidad encontrada", "CVE")
    registrar_log("Situación crítica", "CRITICAL")
    registrar_log("Error de prueba", "ERROR")
    
    # Ejemplo con categorías
    log_cve("Analizando base de datos CVE", "CVE_INIT")
    log_vuln("Credenciales por defecto encontradas", "CRED_VULN")
    log_secure("Sistema protegido correctamente", "SECURITY_OK")
    
    print("\n✅ Prueba de logging completada. Revisa logs/ para ver los archivos generados.")
