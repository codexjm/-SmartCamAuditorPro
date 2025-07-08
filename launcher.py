#!/usr/bin/env python3
"""
Launcher para SmartCam Auditor con diferentes modos de operación
"""

import sys
import os
import shutil

def show_banner():
    print("="*60)
    print("         SMARTCAM AUDITOR - SECURITY SCANNER")
    print("              For Professional Use Only")
    print("="*60)
    print()

def show_menu():
    print("Selecciona el modo de operación:")
    print()
    print("1. Auditoría Empresarial (config/networks_enterprise.txt)")
    print("2. Auditoría de Laboratorio (config/networks_lab.txt)")
    print("3. Auditoría Personalizada (config/networks.txt)")
    print("4. Prueba del Sistema")
    print("5. Ver Reportes Anteriores")
    print("6. Configuración")
    print("0. Salir")
    print()

def run_audit(network_file):
    """Ejecuta auditoría con archivo de red específico"""
    
    # Backup del archivo actual
    if os.path.exists("config/networks.txt"):
        shutil.copy("config/networks.txt", "config/networks_backup.txt")
    
    # Copiar archivo seleccionado
    if os.path.exists(network_file):
        shutil.copy(network_file, "config/networks.txt")
        print(f"[*] Usando configuración: {network_file}")
        
        # Ejecutar auditoría
        os.system("python smartcam_auditor.py")
        
        # Restaurar backup si existe
        if os.path.exists("config/networks_backup.txt"):
            shutil.copy("config/networks_backup.txt", "config/networks.txt")
            os.remove("config/networks_backup.txt")
    else:
        print(f"[ERROR] No se encontró el archivo: {network_file}")

def main():
    show_banner()
    
    while True:
        show_menu()
        choice = input("Selecciona una opción (0-6): ").strip()
        
        if choice == "1":
            run_audit("config/networks_enterprise.txt")
        elif choice == "2":
            run_audit("config/networks_lab.txt")
        elif choice == "3":
            os.system("python smartcam_auditor.py")
        elif choice == "4":
            os.system("python test_system.py")
        elif choice == "5":
            print("\n[*] Reportes disponibles en la carpeta 'logs/'")
            if os.path.exists("logs"):
                files = [f for f in os.listdir("logs") if f.endswith(".txt")]
                if files:
                    for i, file in enumerate(files, 1):
                        print(f"    {i}. {file}")
                else:
                    print("    No hay reportes disponibles")
            input("\nPresiona Enter para continuar...")
        elif choice == "6":
            os.system("python setup.py")
        elif choice == "0":
            print("\n[*] Saliendo...")
            break
        else:
            print("\n[ERROR] Opción inválida")
        
        print()

if __name__ == "__main__":
    main()
