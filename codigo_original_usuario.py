#!/usr/bin/env python3
"""
Ejemplo directo del código original del usuario
Demuestra que las importaciones funcionan exactamente como se especificaron
"""

# Importaciones exactas como las especificaste
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.login_tester import testear_credenciales

def main():
    """Función principal usando el código original del usuario"""
    print("SMARTCAM AUDITOR - CÓDIGO ORIGINAL DEL USUARIO")
    print("=" * 60)
    
    # Tu código original de escaneo
    rango_red = "192.168.1.0/24"  # Puedes cambiar esto por tu red
    
    print(f"🌐 Escaneando red: {rango_red}")
    ips_detectadas = obtener_ips_dispositivos(rango_red)
    
    print(f"\n📊 Dispositivos encontrados: {len(ips_detectadas)}")
    
    if ips_detectadas:
        print("📱 IPs con puertos de cámaras:")
        for i, ip in enumerate(ips_detectadas, 1):
            print(f"   {i}. {ip}")
        
        # Probar credenciales en los dispositivos encontrados
        print(f"\n🔐 Probando credenciales...")
        vulnerabilidades = testear_credenciales(
            ips=ips_detectadas[:3],  # Máximo 3 para acelerar
            puertos_http=[80, 8080],
            incluir_rtsp=True,
            incluir_ssh=False
        )
        
        if vulnerabilidades:
            print(f"\n🚨 VULNERABILIDADES ENCONTRADAS:")
            for vuln in vulnerabilidades:
                print(f"   • {vuln}")
        else:
            print(f"\n✅ No se encontraron credenciales débiles")
    else:
        print("ℹ️ No se encontraron dispositivos en esta red")
    
    print(f"\n✅ Escaneo completado exitosamente")

if __name__ == "__main__":
    main()
