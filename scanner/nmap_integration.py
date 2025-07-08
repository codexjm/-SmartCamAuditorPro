#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración de Nmap para SmartCam Auditor

Este módulo proporciona funciones para usar Nmap desde el proyecto SmartCam Auditor,
manejando automáticamente la ruta de instalación en Windows.
"""

import subprocess
import platform
import os
import json

class NmapScanner:
    """Wrapper para Nmap que funciona tanto en Windows como en Linux"""
    
    def __init__(self):
        self.nmap_path = self._find_nmap()
        
    def _find_nmap(self):
        """Encuentra la ruta de nmap según el sistema operativo"""
        system = platform.system().lower()
        
        if system == 'windows':
            # Rutas comunes de nmap en Windows
            possible_paths = [
                r"C:\Program Files (x86)\Nmap\nmap.exe",
                r"C:\Program Files\Nmap\nmap.exe",
                r"C:\nmap\nmap.exe"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            
            # Buscar en PATH
            try:
                result = subprocess.run(['where', 'nmap'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            except:
                pass
                
        else:  # Linux/Unix
            # Buscar en PATH
            try:
                result = subprocess.run(['which', 'nmap'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
        
        return None
    
    def is_available(self):
        """Verifica si nmap está disponible"""
        return self.nmap_path is not None
    
    def get_version(self):
        """Obtiene la versión de nmap"""
        if not self.is_available():
            return None
            
        try:
            result = subprocess.run([self.nmap_path, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"Error obteniendo versión de nmap: {e}")
        
        return None
    
    def scan_network(self, network_range, scan_type='-sn'):
        """
        Escanea una red usando nmap
        
        Args:
            network_range (str): Rango de red (ej: 192.168.1.0/24)
            scan_type (str): Tipo de escaneo (-sn para ping scan)
        
        Returns:
            dict: Resultados del escaneo
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Nmap no está disponible',
                'hosts': []
            }
        
        try:
            cmd = [self.nmap_path, scan_type, network_range]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                hosts = self._parse_nmap_output(result.stdout)
                return {
                    'success': True,
                    'hosts': hosts,
                    'raw_output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'hosts': []
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout en el escaneo de nmap',
                'hosts': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error ejecutando nmap: {str(e)}',
                'hosts': []
            }
    
    def scan_ports(self, target, ports='1-1000'):
        """
        Escanea puertos específicos de un target
        
        Args:
            target (str): IP o hostname objetivo
            ports (str): Rango de puertos (ej: '1-1000', '80,443,554')
        
        Returns:
            dict: Resultados del escaneo de puertos
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Nmap no está disponible',
                'open_ports': []
            }
        
        try:
            cmd = [self.nmap_path, '-p', ports, target]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                open_ports = self._parse_port_scan(result.stdout)
                return {
                    'success': True,
                    'target': target,
                    'open_ports': open_ports,
                    'raw_output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'open_ports': []
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout en el escaneo de puertos',
                'open_ports': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en escaneo de puertos: {str(e)}',
                'open_ports': []
            }
    
    def _parse_nmap_output(self, output):
        """Parsea la salida de nmap para extraer hosts activos"""
        hosts = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'Nmap scan report for' in line:
                # Extraer IP de la línea
                parts = line.split()
                if len(parts) >= 5:
                    ip = parts[4]
                    # Limpiar IP de paréntesis si existe
                    ip = ip.replace('(', '').replace(')', '')
                    hosts.append(ip)
        
        return hosts
    
    def _parse_port_scan(self, output):
        """Parsea la salida de escaneo de puertos de nmap"""
        open_ports = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if '/tcp' in line and 'open' in line:
                # Extraer número de puerto
                port_info = line.split('/tcp')[0].strip()
                try:
                    port = int(port_info)
                    service = line.split()[-1] if len(line.split()) > 2 else 'unknown'
                    open_ports.append({
                        'port': port,
                        'protocol': 'tcp',
                        'service': service
                    })
                except ValueError:
                    continue
        
        return open_ports

def test_nmap_integration():
    """Test de integración de nmap"""
    print("🔍 SMARTCAM AUDITOR - INTEGRACIÓN NMAP")
    print("=" * 50)
    
    scanner = NmapScanner()
    
    print(f"📍 Nmap disponible: {'✅' if scanner.is_available() else '❌'}")
    
    if scanner.is_available():
        print(f"📁 Ruta de nmap: {scanner.nmap_path}")
        
        version = scanner.get_version()
        if version:
            print(f"📋 Versión:")
            for line in version.split('\n')[:2]:
                print(f"   {line}")
        
        print("\n🧪 Probando escaneo básico...")
        
        # Test de escaneo local
        result = scanner.scan_network('127.0.0.1/32')
        
        if result['success']:
            print(f"✅ Test de escaneo exitoso")
            print(f"   Hosts encontrados: {len(result['hosts'])}")
        else:
            print(f"❌ Error en test: {result['error']}")
    
    else:
        print("❌ Nmap no está disponible")
        print("💡 Para instalar:")
        if platform.system().lower() == 'windows':
            print("   winget install Insecure.Nmap")
        else:
            print("   sudo apt install nmap")

if __name__ == "__main__":
    test_nmap_integration()
