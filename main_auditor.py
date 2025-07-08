#!/usr/bin/env python3
"""
SmartCam Auditor Pro - Herramienta de Auditoría de Seguridad para Dispositivos IoT
Versión: 2.0 Pro

Características principales:
- Escaneo avanzado de red con detección de dispositivos IoT
- Análisis de vulnerabilidades CVE automatizado
- Cracking de contraseñas con John the Ripper/Hashcat
- Fingerprinting con Nmap
- Análisis de diferencias (diff_analyzer)
- Base de datos local (shodan_local)
- Lanzamiento automático de exploits
- Panel web integrado
- Análisis de imágenes con IA
- Notificaciones por Telegram
"""

import sys
import os
import argparse
import json
import time
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos del scanner
from scanner.network_scanner import NetworkScanner
from scanner.hash_cracker import crackear_hashes
from scanner.diff_analyzer import comparar_logs_actual_vs_anterior
from scanner.shodan_local import ShodanLocal

class SmartCamAuditorPro:
    """Clase principal de SmartCam Auditor Pro"""
    
    def __init__(self, config_file="config/config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.scanner = NetworkScanner(config_file=config_file)
        self.db = ShodanLocal()
        
        # Banner
        self.show_banner()
        
    def load_config(self):
        """Carga la configuración desde archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ Archivo de configuración no encontrado: {self.config_file}")
                return self.create_default_config()
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return {}
    
    def create_default_config(self):
        """Crea configuración por defecto"""
        default_config = {
            "network_range": "192.168.1.0/24",
            "camera_ports": [80, 81, 82, 83, 554, 8000, 8080, 8081, 8090, 9000],
            "scan_settings": {
                "timeout": 1.5,
                "max_threads": 75
            },
            "enable_cve_check": True,
            "enable_hash_cracker": True,
            "enable_fingerprint": True,
            "enable_diff_analyzer": True,
            "enable_web_panel": False,
            "web_panel_port": 5000
        }
        
        # Crear directorio de configuración si no existe
        os.makedirs("config", exist_ok=True)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            print(f"✅ Configuración por defecto creada: {self.config_file}")
        except Exception as e:
            print(f"❌ Error creando configuración: {e}")
        
        return default_config
    
    def show_banner(self):
        """Muestra el banner de la aplicación"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                    SmartCam Auditor Pro v2.0                 ║
║               Herramienta de Auditoría IoT Avanzada          ║
╠═══════════════════════════════════════════════════════════════╣
║  🔍 Network Scanning    🧬 CVE Analysis    🔓 Hash Cracking  ║
║  🚀 Exploit Launcher    📊 Diff Analyzer   💾 Local Database ║
║  🎯 Fingerprinting     🌐 Web Panel       📱 Telegram Alerts ║
║  🤖 AI Image Analysis  📋 Report Generation                  ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"📅 Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Directorio de trabajo: {os.getcwd()}")
        print()
    
    def run_network_scan(self, network_range=None):
        """Ejecuta escaneo completo de red"""
        print("🔍 INICIANDO ESCANEO COMPLETO DE RED")
        print("=" * 50)
        
        if not network_range:
            network_range = self.config.get('network_range', '192.168.1.0/24')
        
        print(f"🎯 Rango objetivo: {network_range}")
        
        # Ejecutar escaneo
        devices = self.scanner.scan_network(network_range)
        
        if devices:
            print(f"\n✅ Escaneo completado: {len(devices)} dispositivos encontrados")
            
            # Guardar dispositivos en base de datos local
            self.save_devices_to_db(devices)
            
            # Mostrar resumen
            self.show_scan_summary(devices)
            
            return devices
        else:
            print("❌ No se encontraron dispositivos")
            return []
    
    def save_devices_to_db(self, devices):
        """Guarda dispositivos en la base de datos local"""
        print("\n💾 Guardando dispositivos en base de datos local...")
        
        for device in devices:
            try:
                device_data = {
                    'hostname': device.get('hostname', ''),
                    'device_type': device.get('device_type', 'Unknown'),
                    'open_ports': device.get('open_ports', []),
                    'services': device.get('services', []),
                    'confidence': device.get('confidence', 0),
                    'scan_time': device.get('scan_time', ''),
                    'cves_found': device.get('cves_found', []),
                    'cracked_credentials': device.get('cracked_credentials', []),
                    'risk_level': device.get('risk_level', 'LOW')
                }
                
                self.db.agregar_dispositivo(device['ip'], device_data)
                
            except Exception as e:
                print(f"⚠️ Error guardando dispositivo {device['ip']}: {e}")
        
        print("✅ Dispositivos guardados en base de datos")
    
    def show_scan_summary(self, devices):
        """Muestra resumen del escaneo"""
        print(f"\n📊 RESUMEN DEL ESCANEO")
        print("=" * 30)
        
        # Estadísticas básicas
        total_devices = len(devices)
        cameras = len([d for d in devices if 'camera' in d.get('device_type', '').lower()])
        high_risk = len([d for d in devices if d.get('risk_level') in ['HIGH', 'CRITICAL']])
        with_creds = len([d for d in devices if d.get('cracked_credentials', [])])
        
        print(f"📱 Total dispositivos: {total_devices}")
        print(f"📷 Cámaras detectadas: {cameras}")
        print(f"⚠️ Dispositivos alto riesgo: {high_risk}")
        print(f"🔑 Con credenciales crackeadas: {with_creds}")
        
        # Top dispositivos por riesgo
        if high_risk > 0:
            print(f"\n🚨 DISPOSITIVOS DE ALTO RIESGO:")
            high_risk_devices = [d for d in devices if d.get('risk_level') in ['HIGH', 'CRITICAL']]
            for device in high_risk_devices[:5]:  # Top 5
                print(f"   🔴 {device['ip']} - {device['device_type']} ({device['risk_level']})")
        
        print()
    
    def run_hash_cracking(self, hash_file=None):
        """Ejecuta cracking de hashes"""
        print("🔓 INICIANDO CRACKING DE HASHES")
        print("=" * 40)
        
        if not hash_file:
            hash_file = "scanner/hashes/capturados.hash"
        
        if not os.path.exists(hash_file):
            print(f"❌ Archivo de hashes no encontrado: {hash_file}")
            return None
        
        resultado = crackear_hashes(hash_file)
        
        if resultado['success']:
            stats = resultado['estadisticas']
            print(f"✅ Cracking completado: {stats['crackeados']}/{stats['total_hashes']} crackeados")
            
            if resultado['credenciales_encontradas']:
                print(f"\n🔑 CREDENCIALES ENCONTRADAS:")
                for cred in resultado['credenciales_encontradas']:
                    print(f"   👤 {cred['usuario']}:{cred['password']} ({cred['metodo']})")
        else:
            print(f"❌ Error en cracking: {resultado['error']}")
        
        return resultado
    
    def run_diff_analysis(self):
        """Ejecuta análisis de diferencias"""
        print("📊 INICIANDO ANÁLISIS DE DIFERENCIAS")
        print("=" * 40)
        
        try:
            from scanner.diff_analyzer import obtener_logs_ordenados, comparar_logs_actual_vs_anterior
            
            logs = obtener_logs_ordenados()
            if len(logs) >= 2:
                diff_result = comparar_logs_actual_vs_anterior()
                
                if diff_result:
                    print("✅ Análisis de diferencias completado")
                    print(f"📈 Cambios detectados: {len(diff_result.get('cambios', []))}")
                else:
                    print("ℹ️ No se detectaron cambios significativos")
            else:
                print("⚠️ Se necesitan al menos 2 logs para comparar")
                
        except Exception as e:
            print(f"❌ Error en análisis de diferencias: {e}")
    
    def run_web_panel(self):
        """Inicia el panel web"""
        if not self.config.get('enable_web_panel', False):
            print("⚠️ Panel web deshabilitado en configuración")
            return
        
        print("🌐 INICIANDO PANEL WEB")
        print("=" * 30)
        
        try:
            from web_panel.routes import create_app
            
            app = create_app()
            port = self.config.get('web_panel_port', 5000)
            
            print(f"🚀 Panel web iniciado en http://localhost:{port}")
            print("💡 Presiona Ctrl+C para detener")
            
            app.run(host='0.0.0.0', port=port, debug=False)
            
        except ImportError:
            print("❌ Módulo de panel web no disponible")
        except Exception as e:
            print(f"❌ Error iniciando panel web: {e}")
    
    def run_full_audit(self, network_range=None):
        """Ejecuta auditoría completa"""
        print("🎯 INICIANDO AUDITORÍA COMPLETA")
        print("=" * 50)
        
        start_time = time.time()
        
        # 1. Escaneo de red
        devices = self.run_network_scan(network_range)
        
        if not devices:
            print("❌ No se encontraron dispositivos. Terminando auditoría.")
            return
        
        # 2. Cracking de hashes si está habilitado
        if self.config.get('enable_hash_cracker', True):
            print("\n" + "="*50)
            self.run_hash_cracking()
        
        # 3. Análisis de diferencias si está habilitado
        if self.config.get('enable_diff_analyzer', True):
            print("\n" + "="*50)
            self.run_diff_analysis()
        
        # 4. Generar reporte final
        self.generate_final_report(devices, start_time)
    
    def generate_final_report(self, devices, start_time):
        """Genera reporte final de auditoría"""
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📋 REPORTE FINAL DE AUDITORÍA")
        print("=" * 50)
        
        # Crear reporte
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': round(duration, 2),
            'auditor': 'SmartCam Auditor Pro v2.0',
            'summary': {
                'total_devices': len(devices),
                'cameras_found': len([d for d in devices if 'camera' in d.get('device_type', '').lower()]),
                'high_risk_devices': len([d for d in devices if d.get('risk_level') in ['HIGH', 'CRITICAL']]),
                'vulnerabilities_found': sum(d.get('cve_count', 0) for d in devices),
                'credentials_cracked': sum(len(d.get('cracked_credentials', [])) for d in devices)
            },
            'devices': devices
        }
        
        # Guardar reporte
        report_file = f"logs/audit_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("logs", exist_ok=True)
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Reporte guardado: {report_file}")
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
        
        # Mostrar resumen
        print(f"⏱️ Duración total: {duration:.2f} segundos")
        print(f"📱 Dispositivos analizados: {report['summary']['total_devices']}")
        print(f"🚨 Vulnerabilidades encontradas: {report['summary']['vulnerabilities_found']}")
        print(f"🔑 Credenciales crackeadas: {report['summary']['credentials_cracked']}")
        
        print(f"\n✅ AUDITORÍA COMPLETADA")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='SmartCam Auditor Pro - Herramienta de Auditoría IoT Avanzada',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main_auditor.py --scan                    # Escaneo básico
  python main_auditor.py --scan --network 192.168.1.0/24  # Escaneo de red específica
  python main_auditor.py --hash-crack               # Solo cracking de hashes
  python main_auditor.py --diff-analysis           # Solo análisis de diferencias
  python main_auditor.py --web                     # Iniciar panel web
  python main_auditor.py --full-audit              # Auditoría completa
        """)
    
    parser.add_argument('--scan', action='store_true',
                       help='Ejecutar escaneo de red')
    parser.add_argument('--network', type=str,
                       help='Rango de red a escanear (ej: 192.168.1.0/24)')
    parser.add_argument('--hash-crack', action='store_true',
                       help='Ejecutar cracking de hashes')
    parser.add_argument('--hash-file', type=str,
                       help='Archivo de hashes a crackear')
    parser.add_argument('--diff-analysis', action='store_true',
                       help='Ejecutar análisis de diferencias')
    parser.add_argument('--web', action='store_true',
                       help='Iniciar panel web')
    parser.add_argument('--full-audit', action='store_true',
                       help='Ejecutar auditoría completa')
    parser.add_argument('--config', type=str, default='config/config.json',
                       help='Archivo de configuración')
    
    args = parser.parse_args()
    
    # Crear instancia del auditor
    auditor = SmartCamAuditorPro(config_file=args.config)
    
    try:
        if args.scan:
            auditor.run_network_scan(args.network)
        elif args.hash_crack:
            auditor.run_hash_cracking(args.hash_file)
        elif args.diff_analysis:
            auditor.run_diff_analysis()
        elif args.web:
            auditor.run_web_panel()
        elif args.full_audit:
            auditor.run_full_audit(args.network)
        else:
            # Modo interactivo
            show_interactive_menu(auditor)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

def show_interactive_menu(auditor):
    """Muestra menú interactivo"""
    while True:
        print("\n" + "="*50)
        print("🎯 SMARTCAM AUDITOR PRO - MENÚ PRINCIPAL")
        print("="*50)
        print("1. 🔍 Escaneo de Red")
        print("2. 🔓 Cracking de Hashes")
        print("3. 📊 Análisis de Diferencias")
        print("4. 🌐 Panel Web")
        print("5. 🎯 Auditoría Completa")
        print("6. ⚙️ Configuración")
        print("7. 📋 Mostrar Base de Datos")
        print("0. 🚪 Salir")
        print("="*50)
        
        try:
            choice = input("Selecciona una opción: ").strip()
            
            if choice == '1':
                network = input("Rango de red (Enter para usar configuración): ").strip()
                auditor.run_network_scan(network if network else None)
            elif choice == '2':
                hash_file = input("Archivo de hashes (Enter para usar default): ").strip()
                auditor.run_hash_cracking(hash_file if hash_file else None)
            elif choice == '3':
                auditor.run_diff_analysis()
            elif choice == '4':
                auditor.run_web_panel()
            elif choice == '5':
                network = input("Rango de red (Enter para usar configuración): ").strip()
                auditor.run_full_audit(network if network else None)
            elif choice == '6':
                show_config_menu(auditor)
            elif choice == '7':
                show_database_info(auditor)
            elif choice == '0':
                print("👋 ¡Gracias por usar SmartCam Auditor Pro!")
                break
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Gracias por usar SmartCam Auditor Pro!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_config_menu(auditor):
    """Muestra menú de configuración"""
    print(f"\n⚙️ CONFIGURACIÓN ACTUAL")
    print("-" * 30)
    
    config = auditor.config
    print(f"🌐 Red objetivo: {config.get('network_range', 'No configurado')}")
    print(f"🔍 CVE Check: {'✅' if config.get('enable_cve_check', False) else '❌'}")
    print(f"🔓 Hash Cracker: {'✅' if config.get('enable_hash_cracker', False) else '❌'}")
    print(f"📊 Diff Analyzer: {'✅' if config.get('enable_diff_analyzer', False) else '❌'}")
    print(f"🌐 Panel Web: {'✅' if config.get('enable_web_panel', False) else '❌'}")

def show_database_info(auditor):
    """Muestra información de la base de datos"""
    print(f"\n💾 INFORMACIÓN DE BASE DE DATOS")
    print("-" * 30)
    
    try:
        devices = auditor.db.buscar_dispositivos()
        print(f"📱 Total dispositivos: {len(devices)}")
        
        if devices:
            print(f"📋 Últimos 5 dispositivos:")
            for device in devices[-5:]:
                print(f"   🎯 {device['ip']} - {device.get('device_type', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error accediendo a base de datos: {e}")

if __name__ == "__main__":
    main()
