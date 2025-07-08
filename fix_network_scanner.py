#!/usr/bin/env python3
"""
Script para limpiar el archivo network_scanner.py
Remueve contenido corrupto al final del archivo
"""

def limpiar_network_scanner():
    archivo = "scanner/network_scanner.py"
    
    try:
        # Leer el archivo
        with open(archivo, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📄 Archivo original: {len(lines)} líneas")
        
        # Encontrar donde debería terminar el archivo
        # Buscar la línea con el comentario final
        linea_final = -1
        for i, line in enumerate(lines):
            if "# Para usar fingerprinting" in line:
                linea_final = i + 1  # Incluir esta línea
                break
        
        if linea_final > 0:
            # Truncar el archivo en la línea correcta
            lines_limpias = lines[:linea_final]
            
            # Escribir el archivo limpio
            with open(archivo, 'w', encoding='utf-8') as f:
                f.writelines(lines_limpias)
            
            print(f"✅ Archivo limpiado: {len(lines_limpias)} líneas")
            print(f"🗑️  Removidas: {len(lines) - len(lines_limpias)} líneas")
        else:
            print("❌ No se encontró la línea final esperada")
    
    except Exception as e:
        print(f"❌ Error limpiando archivo: {e}")

if __name__ == "__main__":
    limpiar_network_scanner()
