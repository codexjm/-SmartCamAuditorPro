#!/usr/bin/env python3
"""
Ejemplo simple y directo de uso de shodan_local
Solo muestra la funcionalidad básica sin depender de NetworkScanner
"""

# Importar la función que querías usar originalmente
from scanner.shodan_local import crear_base_datos, ShodanLocal, buscar_en_base_local

def main():
    """Ejemplo directo de uso de shodan_local"""
    
    print("🔍 SHODAN LOCAL - USO DIRECTO")
    print("=" * 40)
    
    # 1. Usar crear_base_datos() como en tu solicitud original
    print("1️⃣ Ejecutando: crear_base_datos()")
    shodan_local = crear_base_datos()
    
    # 2. Agregar algunos datos de ejemplo
    print("\n2️⃣ Agregando dispositivos de ejemplo...")
    
    # Dispositivo 1: Cámara Hikvision
    device1 = {
        'device_type': 'IP Camera (RTSP)',
        'fabricante': 'Hikvision',
        'modelo': 'DS-2CD2042FWD',
        'open_ports': [80, 554, 8000],
        'confidence': 85,
        'cves_found': [
            {'cve': 'CVE-2021-36260', 'descripcion': 'Command injection vulnerability'}
        ]
    }
    shodan_local.agregar_dispositivo("192.168.1.100", device1)
    
    # Dispositivo 2: Router
    device2 = {
        'device_type': 'Router/Gateway',
        'fabricante': 'TP-Link',
        'modelo': 'Archer C7',
        'open_ports': [80, 443, 22],
        'confidence': 90,
        'cves_found': []
    }
    shodan_local.agregar_dispositivo("192.168.1.1", device2)
    
    # Dispositivo 3: Dispositivo IoT
    device3 = {
        'device_type': 'IoT Device (Telnet)',
        'fabricante': 'Unknown',
        'modelo': '',
        'open_ports': [23, 80],
        'confidence': 70,
        'cves_found': [
            {'cve': 'CVE-2020-25078', 'descripcion': 'Default credentials vulnerability'}
        ]
    }
    shodan_local.agregar_dispositivo("192.168.1.55", device3)
    
    # 3. Mostrar estadísticas
    print("\n3️⃣ Estadísticas de la base de datos:")
    stats = shodan_local.obtener_estadisticas()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   • {key}:")
            for subkey, subvalue in value.items():
                print(f"     - {subkey}: {subvalue}")
        else:
            print(f"   • {key}: {value}")
    
    # 4. Ejemplos de búsquedas usando buscar_en_base_local()
    print("\n4️⃣ Ejemplos de búsqueda:")
    
    ejemplos = [
        "192.168.1",      # Buscar por IP parcial
        "Camera",         # Buscar por tipo de dispositivo
        "Hikvision",      # Buscar por fabricante
        "80",             # Buscar por puerto
        "Router"          # Buscar por tipo de dispositivo
    ]
    
    for termino in ejemplos:
        print(f"\n🔍 Buscando: '{termino}'")
        resultados = buscar_en_base_local(termino)
        if resultados:
            for resultado in resultados:
                print(f"   ✅ {resultado['ip']} - {resultado['device_type']} ({resultado['fabricante']})")
        else:
            print("   ❌ Sin resultados")
    
    # 5. Exportar datos
    print("\n5️⃣ Exportando datos:")
    
    # Exportar a JSON
    json_data = shodan_local.exportar_datos('json')
    print(f"📄 JSON export: {len(json_data)} caracteres")
    
    # Exportar a CSV
    csv_data = shodan_local.exportar_datos('csv')
    print(f"📄 CSV export: {len(csv_data)} caracteres")
    
    # 6. Mostrar algunos dispositivos
    print("\n6️⃣ Lista de dispositivos:")
    todos_dispositivos = shodan_local.buscar_dispositivos()
    for i, device in enumerate(todos_dispositivos, 1):
        print(f"   {i}. 📍 {device['ip']} - {device['device_type']}")
        print(f"      🏭 Fabricante: {device['fabricante'] or 'Desconocido'}")
        print(f"      🔌 Puertos: {device['puertos_abiertos']}")
        print(f"      📊 Confianza: {device['confianza']}%")
        if device['vulnerabilidades']:
            print(f"      🚨 Vulnerabilidades: {len(device['vulnerabilidades'])}")
        print()
    
    print("✅ Ejemplo completado exitosamente!")
    print(f"📁 Base de datos guardada en: {shodan_local.db_path}")
    
    # Comandos útiles para seguir explorando
    print("\n💡 Para seguir explorando:")
    print("   from scanner.shodan_local import buscar_en_base_local, ShodanLocal")
    print("   db = ShodanLocal()")
    print("   resultados = buscar_en_base_local('Camera')")
    print("   stats = db.obtener_estadisticas()")

if __name__ == "__main__":
    main()
