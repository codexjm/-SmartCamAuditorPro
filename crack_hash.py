#!/usr/bin/env python3
"""
Script para crackear el hash APR1 proporcionado usando SmartCam Auditor
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner.password_cracker import PasswordCracker

def main():
    print("🔓 SmartCam Auditor - Hash Cracking")
    print("=" * 50)
    
    # Hash proporcionado por el usuario
    hash_to_crack = "admin:$apr1$dfh23$A2sc6uPUrJZ5IWr6UFPmO1"
    
    print(f"🎯 Hash objetivo: {hash_to_crack}")
    print(f"📋 Formato detectado: APR1 (Apache MD5)")
    print(f"👤 Usuario: admin")
    print()
    
    # Inicializar el crackeador de contraseñas
    try:
        cracker = PasswordCracker()
        
        # Verificar herramientas disponibles
        print("🔧 Verificando herramientas disponibles...")
        tools_status = cracker.check_tools()
        
        for tool, available in tools_status.items():
            status = "✅ Disponible" if available else "❌ No disponible"
            print(f"   {tool}: {status}")
        
        print()
        
        # Si no hay herramientas disponibles, mostrar instrucciones
        if not any(tools_status.values()):
            print("⚠️ No se encontraron herramientas de cracking instaladas")
            print()
            print("📦 Para instalar John the Ripper en Windows:")
            print("   1. Descargar desde: https://www.openwall.com/john/")
            print("   2. O usar chocolatey: choco install john")
            print("   3. O usar WSL: sudo apt-get install john")
            print()
            print("📦 Para instalar Hashcat en Windows:")
            print("   1. Descargar desde: https://hashcat.net/hashcat/")
            print("   2. O usar chocolatey: choco install hashcat")
            print()
            return
        
        # Crear archivo temporal con el hash
        hash_file = "temp_hash.txt"
        with open(hash_file, 'w') as f:
            f.write(hash_to_crack)
        
        print(f"📄 Hash guardado en: {hash_file}")
        
        # Generar diccionario personalizado para el usuario "admin"
        print("📚 Generando diccionario personalizado...")
        dict_file = cracker.generate_custom_dictionary(
            device_info={
                'ip': '192.168.1.100',
                'hostname': 'camera',
                'brand': 'generic',
                'model': 'admin'
            }
        )
        print(f"📖 Diccionario creado: {dict_file}")
        
        # Intentar crackear con John the Ripper si está disponible
        if tools_status.get('john', False):
            print()
            print("🚀 Iniciando cracking con John the Ripper...")
            
            result = cracker.crack_with_john(
                hash_file=hash_file,
                wordlist=dict_file,
                hash_format="md5crypt"  # APR1 usa md5crypt
            )
            
            if result['success']:
                print("🎉 ¡CONTRASEÑA ENCONTRADA!")
                print(f"🔑 Usuario: admin")
                print(f"🔑 Contraseña: {result['password']}")
                print(f"⏱️ Tiempo: {result.get('time', 'N/A')}")
                
                # Guardar resultado
                with open("password_found.txt", 'w') as f:
                    f.write(f"Usuario: admin\n")
                    f.write(f"Contraseña: {result['password']}\n")
                    f.write(f"Hash: {hash_to_crack}\n")
                    f.write(f"Método: John the Ripper\n")
                
                print("💾 Resultado guardado en: password_found.txt")
                
            else:
                print("❌ No se pudo crackear la contraseña")
                print(f"📋 Detalles: {result.get('error', 'Error desconocido')}")
                
                # Intentar con rockyou.txt si está disponible
                if os.path.exists("diccionarios/rockyou.txt"):
                    print()
                    print("🔄 Intentando con diccionario rockyou.txt...")
                    
                    result2 = cracker.crack_with_john(
                        hash_file=hash_file,
                        wordlist="diccionarios/rockyou.txt",
                        hash_format="md5crypt"
                    )
                    
                    if result2['success']:
                        print("🎉 ¡CONTRASEÑA ENCONTRADA con rockyou!")
                        print(f"🔑 Contraseña: {result2['password']}")
                    else:
                        print("❌ Tampoco se encontró con rockyou.txt")
        
        # Intentar con Hashcat si John no funcionó
        elif tools_status.get('hashcat', False):
            print()
            print("🚀 Iniciando cracking con Hashcat...")
            
            result = cracker.crack_with_hashcat(
                hash_file=hash_file,
                wordlist=dict_file,
                hash_mode=1600  # APR1 MD5
            )
            
            if result['success']:
                print("🎉 ¡CONTRASEÑA ENCONTRADA!")
                print(f"🔑 Contraseña: {result['password']}")
            else:
                print("❌ No se pudo crackear la contraseña")
                print(f"📋 Detalles: {result.get('error', 'Error desconocido')}")
        
        # Limpiar archivos temporales
        try:
            os.remove(hash_file)
            print(f"🧹 Archivo temporal eliminado: {hash_file}")
        except:
            pass
        
    except Exception as e:
        print(f"❌ Error durante el cracking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
