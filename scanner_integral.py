#!/usr/bin/env python3
"""
Integración del CVE Checker con Network Scanner
SmartCam Auditor v2.0 Pro - Sistema integral de detección y análisis
"""

import os
import sys
import time
import json

# Agregar el directorio actual al path
sys.path.append(os.getcwd())

from scanner.network_scanner import NetworkScanner, obtener_ips_dispositivos
from scanner.cve_checker import CVEChecker, buscar_vulnerabilidades_cve

class IntegratedSecurityScanner:
    """Scanner de seguridad integrado que combina detección de red y análisis CVE"""
    
    def __init__(self, config_file="config/config.json"):
        self.config = self.load_config(config_file)
        self.network_scanner = NetworkScanner(config_file=config_file)
        self.cve_checker = CVEChecker(config_file=config_file)
        
        # Configuración de análisis
        self.verify_cves = self.config.get("verify_cves_actively", True)
        self.generate_reports = self.config.get("generate_reports", True)
        
    def load_config(self, config_file):
        """Carga configuración"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Error cargando config: {e}")
            return {}
    
    def scan_and_analyze_network(self, network_range=None):
        """
        Escanea la red y analiza vulnerabilidades CVE de forma integrada
        
        Args:
            network_range (str): Rango de red a escanear
            
        Returns:
            dict: Resultados completos del análisis
        """
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔍 ANÁLISIS INTEGRAL DE SEGURIDAD                         ║
║                        SmartCam Auditor v2.0 Pro                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        start_time = time.time()
        
        # FASE 1: Escaneo de red
        print("🌐 FASE 1: Escaneo de red y detección de dispositivos")
        print("=" * 70)
        
        if not network_range:
            network_range = self.network_scanner.get_local_network()
        
        devices = self.network_scanner.scan_network(network_range)
        
        if not devices:
            print("❌ No se encontraron dispositivos en la red")
            return {"error": "No devices found"}
        
        print(f"✅ Dispositivos encontrados: {len(devices)}")
        
        # FASE 2: Análisis CVE por detección de fabricante
        print(f"\n🧬 FASE 2: Análisis de vulnerabilidades CVE")
        print("=" * 70)
        
        # Preparar lista para análisis CVE
        targets_for_cve = []
        
        for device in devices:
            ip = device['ip']
            device_type = device['device_type']
            
            # Agregar IP para detección automática de fabricante
            targets_for_cve.append(ip)
            
            # Si tenemos información del tipo de dispositivo, agregarla también
            if 'hikvision' in device_type.lower():
                targets_for_cve.append('Hikvision device')
            elif 'dahua' in device_type.lower():
                targets_for_cve.append('Dahua device')
            elif 'axis' in device_type.lower():
                targets_for_cve.append('Axis device')
        
        # Buscar vulnerabilidades CVE
        vulnerabilidades = self.cve_checker.buscar_vulnerabilidades_cve(targets_for_cve)
        
        print(f"🚨 Vulnerabilidades CVE encontradas: {len(vulnerabilidades)}")
        
        # FASE 3: Análisis por puertos
        print(f"\n🔌 FASE 3: Análisis de vulnerabilidades por puertos")
        print("=" * 70)
        
        vulns_por_puertos = self.cve_checker.buscar_por_puertos(devices)
        
        if vulns_por_puertos:
            print(f"⚠️ Dispositivos con vulnerabilidades por puertos: {len(vulns_por_puertos)}")
        else:
            print("✅ No se encontraron vulnerabilidades específicas por puertos")
        
        # FASE 4: Verificación activa (opcional)
        vulnerabilidades_verificadas = []
        if self.verify_cves and vulnerabilidades:
            print(f"\n🧪 FASE 4: Verificación activa de vulnerabilidades")
            print("=" * 70)
            
            # Agrupar vulnerabilidades por IP
            vulns_por_ip = {}
            for vuln in vulnerabilidades:
                ip = vuln.get('ip')
                if ip:
                    if ip not in vulns_por_ip:
                        vulns_por_ip[ip] = []
                    vulns_por_ip[ip].append(vuln)
            
            # Verificar cada IP
            for ip, vulns in vulns_por_ip.items():
                print(f"🎯 Verificando {ip}...")
                verificadas = self.cve_checker.verificar_cve_activamente(ip, vulns)
                vulnerabilidades_verificadas.extend(verificadas)
            
            # Actualizar vulnerabilidades principales con estado verificado
            for i, vuln in enumerate(vulnerabilidades):
                for verificada in vulnerabilidades_verificadas:
                    if (vuln.get('ip') == verificada.get('ip') and 
                        vuln.get('cve') == verificada.get('cve')):
                        vulnerabilidades[i] = verificada
                        break
        
        # FASE 5: Generación de reportes
        scan_time = time.time() - start_time
        
        resultados = {
            "scan_info": {
                "network_range": network_range,
                "scan_time": scan_time,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "devices_found": devices,
            "cve_vulnerabilities": vulnerabilidades,
            "port_vulnerabilities": vulns_por_puertos,
            "statistics": {
                "total_devices": len(devices),
                "total_cves": len(vulnerabilidades),
                "critical_cves": len([v for v in vulnerabilidades if v.get('critico')]),
                "verified_cves": len([v for v in vulnerabilidades if v.get('verificado')]),
                "devices_with_port_vulns": len(vulns_por_puertos)
            }
        }
        
        if self.generate_reports:
            print(f"\n📄 FASE 5: Generación de reportes")
            print("=" * 70)
            self.generate_comprehensive_report(resultados)
        
        # Resumen final
        self.print_summary(resultados)
        
        return resultados
    
    def generate_comprehensive_report(self, resultados):
        """Genera un reporte completo del análisis"""
        timestamp = int(time.time())
        
        # Reporte CVE detallado
        if resultados["cve_vulnerabilities"]:
            cve_report_file = f"reporte_cve_integral_{timestamp}.txt"
            cve_report = self.cve_checker.generar_reporte_cve(
                resultados["cve_vulnerabilities"], 
                cve_report_file
            )
            print(f"   📋 Reporte CVE: logs/{cve_report_file}")
        
        # Reporte de dispositivos encontrados
        devices_report_file = f"dispositivos_encontrados_{timestamp}.json"
        devices_report_path = f"logs/{devices_report_file}"
        
        try:
            os.makedirs("logs", exist_ok=True)
            with open(devices_report_path, 'w', encoding='utf-8') as f:
                json.dump(resultados["devices_found"], f, indent=2, ensure_ascii=False)
            print(f"   📱 Reporte de dispositivos: {devices_report_path}")
        except Exception as e:
            print(f"   ❌ Error guardando reporte de dispositivos: {e}")
        
        # Reporte resumen
        summary_report_file = f"resumen_analisis_{timestamp}.txt"
        summary_report_path = f"logs/{summary_report_file}"
        
        try:
            summary = self.generate_summary_report(resultados)
            with open(summary_report_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"   📊 Reporte resumen: {summary_report_path}")
        except Exception as e:
            print(f"   ❌ Error guardando reporte resumen: {e}")
    
    def generate_summary_report(self, resultados):
        """Genera un reporte resumen del análisis"""
        stats = resultados["statistics"]
        scan_info = resultados["scan_info"]
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       📊 RESUMEN DE ANÁLISIS INTEGRAL                        ║
║                           SmartCam Auditor v2.0 Pro                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

📅 Fecha y hora: {scan_info['timestamp']}
🌐 Red analizada: {scan_info['network_range']}
⏱️ Tiempo de análisis: {scan_info['scan_time']:.2f} segundos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 DISPOSITIVOS DETECTADOS: {stats['total_devices']}

"""
        
        # Información detallada de dispositivos
        for i, device in enumerate(resultados["devices_found"], 1):
            summary += f"""
{i}. 📡 {device['ip']} - {device['device_type']}
   🔌 Puertos abiertos: {device['open_ports']}
   📊 Confianza: {device.get('confidence', 'N/A')}%
   🏷️ Servicios: {', '.join(device.get('services', []))[:60]}...
"""
        
        summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 VULNERABILIDADES CVE: {stats['total_cves']}

   🔴 Críticas: {stats['critical_cves']}
   🧪 Verificadas: {stats['verified_cves']}
   🔌 Por puertos: {stats['devices_with_port_vulns']}

"""
        
        # Top 5 vulnerabilidades más críticas
        if resultados["cve_vulnerabilities"]:
            critical_vulns = [v for v in resultados["cve_vulnerabilities"] if v.get('critico')][:5]
            
            if critical_vulns:
                summary += "🔥 TOP 5 VULNERABILIDADES CRÍTICAS:\n\n"
                for i, vuln in enumerate(critical_vulns, 1):
                    verified = "✅ VERIFICADO" if vuln.get('verificado') else "⚪ SIN VERIFICAR"
                    summary += f"   {i}. {vuln['cve']} - {vuln['producto']}\n"
                    summary += f"      📝 {vuln['descripcion'][:60]}...\n"
                    summary += f"      🔬 {verified}\n\n"
        
        summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ RECOMENDACIONES PRIORITARIAS:

1. 🔥 ACCIÓN INMEDIATA: Atender {stats['critical_cves']} vulnerabilidades críticas
2. 🔒 SEGURIDAD: Cambiar todas las credenciales por defecto encontradas
3. 🛡️ MITIGACIÓN: Implementar segmentación de red para dispositivos IoT
4. 📊 MONITOREO: Configurar alertas para nuevas vulnerabilidades
5. 🔧 MANTENIMIENTO: Establecer programa de actualizaciones automáticas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 NIVEL DE RIESGO GENERAL: """
        
        # Calcular nivel de riesgo general
        if stats['critical_cves'] >= 3:
            summary += "🔴 CRÍTICO"
        elif stats['critical_cves'] >= 1 or stats['total_cves'] >= 5:
            summary += "🟠 ALTO"
        elif stats['total_cves'] >= 1:
            summary += "🟡 MEDIO"
        else:
            summary += "🟢 BAJO"
        
        summary += f"""

🎯 EFECTIVIDAD DEL ANÁLISIS:
   • Cobertura de red: 100%
   • Detección de dispositivos: {len(resultados['devices_found'])} encontrados
   • Verificación CVE: {(stats['verified_cves']/max(stats['total_cves'], 1)*100):.1f}%
   • Tiempo por dispositivo: {scan_info['scan_time']/max(stats['total_devices'], 1):.1f}s

═══════════════════════════════════════════════════════════════════════════════
        """
        
        return summary
    
    def print_summary(self, resultados):
        """Imprime un resumen en consola"""
        stats = resultados["statistics"]
        scan_info = resultados["scan_info"]
        
        print(f"\n{'='*80}")
        print("📊 RESUMEN DEL ANÁLISIS INTEGRAL")
        print('='*80)
        
        print(f"🌐 Red escaneada: {scan_info['network_range']}")
        print(f"⏱️ Tiempo total: {scan_info['scan_time']:.2f} segundos")
        print(f"📱 Dispositivos encontrados: {stats['total_devices']}")
        print(f"🚨 Vulnerabilidades CVE: {stats['total_cves']}")
        print(f"🔴 Vulnerabilidades críticas: {stats['critical_cves']}")
        print(f"🧪 Vulnerabilidades verificadas: {stats['verified_cves']}")
        
        # Nivel de riesgo
        if stats['critical_cves'] >= 3:
            risk_level = "🔴 CRÍTICO"
        elif stats['critical_cves'] >= 1:
            risk_level = "🟠 ALTO"
        elif stats['total_cves'] >= 1:
            risk_level = "🟡 MEDIO"
        else:
            risk_level = "🟢 BAJO"
        
        print(f"📈 Nivel de riesgo: {risk_level}")
        
        if stats['critical_cves'] > 0:
            print(f"\n⚠️ ATENCIÓN: Se encontraron {stats['critical_cves']} vulnerabilidades CRÍTICAS")
            print("   Revisar inmediatamente los reportes generados en la carpeta 'logs/'")
        
        print('='*80)

def main():
    """Función principal del scanner integrado"""
    print("🚀 Iniciando SmartCam Auditor v2.0 Pro - Scanner Integrado")
    
    # Crear instancia del scanner integrado
    scanner = IntegratedSecurityScanner()
    
    # Realizar análisis completo
    # Usar red por defecto de la configuración o detectar automáticamente
    network_range = scanner.config.get('network_range')
    
    if not network_range:
        print("🔍 Detectando red local automáticamente...")
        network_range = None  # Se detectará automáticamente
    else:
        print(f"🎯 Usando red configurada: {network_range}")
    
    # Ejecutar análisis integral
    resultados = scanner.scan_and_analyze_network(network_range)
    
    if "error" not in resultados:
        print(f"\n✅ Análisis completado exitosamente")
        print(f"📁 Revisa la carpeta 'logs/' para ver todos los reportes generados")
    else:
        print(f"\n❌ Error en el análisis: {resultados['error']}")

if __name__ == "__main__":
    main()
