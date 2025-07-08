#!/usr/bin/env python3
"""
SmartCam Auditor Pro - Verificador de Despliegue
Script para verificar que el proyecto está listo para desplegar en servidor
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class DeploymentChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def print_header(self):
        print("=" * 60)
        print("    SmartCam Auditor Pro - Verificador de Despliegue")
        print("=" * 60)
        print()
        
    def check_file_exists(self, file_path, required=True):
        """Verifica si un archivo existe"""
        full_path = self.project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path} - OK")
            self.success_count += 1
            return True
        else:
            msg = f"❌ {file_path} - NO ENCONTRADO"
            if required:
                self.errors.append(msg)
            else:
                self.warnings.append(msg)
            print(msg)
            return False
            
    def check_directory_exists(self, dir_path, required=True):
        """Verifica si un directorio existe"""
        full_path = self.project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}/ - OK")
            self.success_count += 1
            return True
        else:
            msg = f"❌ {dir_path}/ - NO ENCONTRADO"
            if required:
                self.errors.append(msg)
            else:
                self.warnings.append(msg)
            print(msg)
            return False
            
    def check_python_dependencies(self):
        """Verifica las dependencias de Python"""
        print("\n📦 Verificando dependencias de Python...")
        
        if not self.check_file_exists("requirements.txt"):
            return
            
        try:
            with open(self.project_root / "requirements.txt", 'r') as f:
                requirements = f.readlines()
                
            print(f"✅ requirements.txt contiene {len(requirements)} dependencias")
            self.success_count += 1
            
            # Verificar algunas dependencias críticas
            req_text = ''.join(requirements)
            critical_deps = ['flask', 'psutil', 'python-nmap', 'requests']
            
            for dep in critical_deps:
                if dep in req_text:
                    print(f"✅ Dependencia crítica {dep} - OK")
                    self.success_count += 1
                else:
                    msg = f"⚠️  Dependencia crítica {dep} - NO ENCONTRADA"
                    self.warnings.append(msg)
                    print(msg)
                    
        except Exception as e:
            msg = f"❌ Error leyendo requirements.txt: {e}"
            self.errors.append(msg)
            print(msg)
            
    def check_config_files(self):
        """Verifica archivos de configuración"""
        print("\n⚙️  Verificando archivos de configuración...")
        
        # Verificar config.json
        if self.check_file_exists("config/config.json"):
            try:
                with open(self.project_root / "config/config.json", 'r') as f:
                    config = json.load(f)
                print("✅ config.json es válido JSON")
                self.success_count += 1
            except json.JSONDecodeError as e:
                msg = f"❌ config.json tiene errores de formato: {e}"
                self.errors.append(msg)
                print(msg)
                
        # Verificar networks.txt
        self.check_file_exists("config/networks.txt", required=False)
        
    def check_core_modules(self):
        """Verifica módulos principales"""
        print("\n🔧 Verificando módulos principales...")
        
        core_files = [
            "main_auditor.py",
            "web_panel.py",
            "scanner/__init__.py",
            "scanner/network_scanner.py",
            "scanner/hash_cracker.py",
            "scanner/diff_analyzer.py",
            "scanner/shodan_local.py",
            "scanner/password_cracker.py"
        ]
        
        for file_path in core_files:
            self.check_file_exists(file_path)
            
    def check_web_panel(self):
        """Verifica componentes del panel web"""
        print("\n🌐 Verificando panel web...")
        
        web_files = [
            "web_panel/routes.py",
            "web_panel/__init__.py",
            "web_panel/templates",
            "web_panel/static"
        ]
        
        for item in web_files:
            if item.endswith('/'):
                self.check_directory_exists(item, required=False)
            else:
                if '.' in item:
                    self.check_file_exists(item, required=False)
                else:
                    self.check_directory_exists(item, required=False)
                    
    def check_deployment_files(self):
        """Verifica archivos de despliegue"""
        print("\n🚀 Verificando archivos de despliegue...")
        
        deployment_files = [
            "deploy_server.sh",
            "maintain_server.sh",
            "DEPLOY_SERVER_GUIDE.md",
            ".gitignore",
            "README.md"
        ]
        
        for file_path in deployment_files:
            self.check_file_exists(file_path, required=False)
            
    def check_python_syntax(self):
        """Verifica sintaxis de archivos Python principales"""
        print("\n🐍 Verificando sintaxis de Python...")
        
        python_files = [
            "main_auditor.py",
            "web_panel.py"
        ]
        
        for file_path in python_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Compilar el archivo para verificar sintaxis
                    with open(full_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), str(full_path), 'exec')
                    print(f"✅ {file_path} - Sintaxis OK")
                    self.success_count += 1
                except SyntaxError as e:
                    msg = f"❌ {file_path} - Error de sintaxis: {e}"
                    self.errors.append(msg)
                    print(msg)
                except Exception as e:
                    msg = f"⚠️  {file_path} - No se pudo verificar: {e}"
                    self.warnings.append(msg)
                    print(msg)
                    
    def check_git_status(self):
        """Verifica estado del repositorio Git"""
        print("\n📋 Verificando estado de Git...")
        
        if not (self.project_root / ".git").exists():
            msg = "⚠️  No es un repositorio Git"
            self.warnings.append(msg)
            print(msg)
            return
            
        try:
            # Verificar si hay cambios sin commit
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=self.project_root,
                capture_output=True, 
                text=True
            )
            
            if result.stdout.strip():
                msg = "⚠️  Hay cambios sin commit en Git"
                self.warnings.append(msg)
                print(msg)
                print("   Archivos modificados:")
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
            else:
                print("✅ Git - Sin cambios pendientes")
                self.success_count += 1
                
            # Verificar branch actual
            result = subprocess.run(
                ["git", "branch", "--show-current"], 
                cwd=self.project_root,
                capture_output=True, 
                text=True
            )
            current_branch = result.stdout.strip()
            print(f"✅ Branch actual: {current_branch}")
            self.success_count += 1
            
        except Exception as e:
            msg = f"⚠️  Error verificando Git: {e}"
            self.warnings.append(msg)
            print(msg)
            
    def generate_deployment_checklist(self):
        """Genera una lista de verificación para el despliegue"""
        print("\n📝 Lista de verificación para despliegue:")
        print()
        
        checklist = [
            "□ Servidor Linux preparado (Ubuntu 20.04+ recomendado)",
            "□ Acceso SSH configurado al servidor",
            "□ Dominio o IP del servidor disponible",
            "□ Puertos 80 y 443 disponibles en el servidor",
            "□ Archivos del proyecto copiados o Git configurado",
            "□ Configuración de redes objetivo lista (config/networks.txt)",
            "□ Configuración general revisada (config/config.json)",
            "□ Certificado SSL planificado (Let's Encrypt recomendado)",
            "□ Estrategia de backup definida",
            "□ Monitoreo y alertas configurados"
        ]
        
        for item in checklist:
            print(f"  {item}")
            
    def run_all_checks(self):
        """Ejecuta todas las verificaciones"""
        self.print_header()
        
        print("🔍 Iniciando verificación del proyecto...")
        print()
        
        # Verificar estructura básica
        print("📁 Verificando estructura de directorios...")
        directories = ["config", "scanner", "logs", "web_panel"]
        for directory in directories:
            self.check_directory_exists(directory)
            
        # Ejecutar todas las verificaciones
        self.check_core_modules()
        self.check_config_files()
        self.check_python_dependencies()
        self.check_web_panel()
        self.check_deployment_files()
        self.check_python_syntax()
        self.check_git_status()
        
        # Mostrar resumen
        self.show_summary()
        
        # Mostrar checklist
        self.generate_deployment_checklist()
        
    def show_summary(self):
        """Muestra resumen de la verificación"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 60)
        
        print(f"✅ Verificaciones exitosas: {self.success_count}")
        print(f"⚠️  Advertencias: {len(self.warnings)}")
        print(f"❌ Errores: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in self.errors:
                print(f"   {error}")
                
        if self.warnings:
            print("\n⚠️  ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"   {warning}")
                
        if not self.errors:
            print("\n🎉 ¡El proyecto está listo para desplegar!")
            print("\nPróximos pasos:")
            print("1. Ejecutar deploy_server.sh en el servidor destino")
            print("2. Copiar archivos del proyecto al servidor")
            print("3. Configurar redes objetivo")
            print("4. Probar la instalación")
        else:
            print("\n⚠️  Corrige los errores antes de desplegar")

if __name__ == "__main__":
    checker = DeploymentChecker()
    checker.run_all_checks()
