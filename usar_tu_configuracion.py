#!/usr/bin/env python3
"""
Script que usa exactamente tu configuración JSON proporcionada
"""

import json
from datetime import datetime
import os
from scanner.network_scanner import obtener_ips_dispositivos
from scanner.login_tester import testear_credenciales
from scanner.fuerza_bruta import iniciar_fuerza_bruta
from telegram_alert import enviar_alerta

def cargar_tu_configuracion():
    """Carga tu configuración específica"""
    # Tu configuración exacta
    tu_config = {
        "network_range": "192.168.1.0/24",
        "camera_ports": [80, 554, 8000, 8080],
        "enable_network_scan": True,
        "enable_login_test": True,
        "enable_brute_force": True,
        "enable_cve_check": False,
        "enable_telegram": True,
        "brute_dict_path": "diccionarios/rockyou.txt",
        "telegram_bot_token": "TU_TOKEN",
        "telegram_chat_id": "TU_CHAT_ID"
    }
    
    return tu_config

def main():
    print("🔒 SmartCam Auditor - Usando Tu Configuración Específica")
    print("=" * 60)
    
    # Cargar tu configuración
    config = cargar_tu_configuracion()
    
    # Crear directorio de logs
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join("logs", f"audit_tu_config_{timestamp}.txt")
    
    def registrar_log(texto):
        print(texto)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    
    registrar_log(f"🧠 SmartCam Auditor - Tu Configuración - {timestamp}")
    registrar_log("=" * 50)
    registrar_log(f"📡 Red objetivo: {config['network_range']}")
    registrar_log(f"🔌 Puertos: {config['camera_ports']}")
    registrar_log(f"📖 Diccionario: {config['brute_dict_path']}")
    registrar_log("")
    
    # 1. Escaneo de red
    if config["enable_network_scan"]:
        registrar_log("🔍 Escaneando red...")
        ips = obtener_ips_dispositivos(config["network_range"])
        registrar_log(f" -> IPs encontradas: {ips}")
    else:
        ips = []
        registrar_log("⚪ Escaneo de red deshabilitado")
    
    if not ips:
        registrar_log("❌ No se encontraron dispositivos. Fin de auditoría.")
        return
    
    # 2. Pruebas de credenciales
    if config["enable_login_test"]:
        registrar_log("🔐 Probando credenciales comunes...")
        cred_results = testear_credenciales(ips)
        if cred_results:
            for r in cred_results:
                registrar_log(f" -> {r}")
        else:
            registrar_log(" -> No se encontraron credenciales débiles")
    
    # 3. Fuerza bruta
    if config["enable_brute_force"]:
        registrar_log("💣 Ejecutando fuerza bruta...")
        brute_results = iniciar_fuerza_bruta(ips, config["brute_dict_path"])
        if brute_results:
            for r in brute_results:
                registrar_log(f" -> {r}")
        else:
            registrar_log(" -> No se logró acceso con diccionario")
    
    # 4. CVE check (deshabilitado en tu config)
    if config["enable_cve_check"]:
        registrar_log("🧬 CVE check habilitado pero no implementado en esta demo")
    
    # 5. Alertas Telegram
    if config["enable_telegram"]:
        registrar_log("📱 Intentando enviar alerta Telegram...")
        try:
            # Actualizar configuración temporal para Telegram
            temp_config = {
                "enable_telegram": True,
                "telegram_bot_token": config["telegram_bot_token"],
                "telegram_chat_id": config["telegram_chat_id"]
            }
            
            # Guardar configuración temporal
            with open("temp_config.json", "w", encoding="utf-8") as f:
                json.dump(temp_config, f, indent=2)
            
            mensaje = f"✅ Auditoría completada\n📁 Log: {log_path}\n🎯 Dispositivos: {len(ips)}"
            resultado = enviar_alerta(mensaje, "temp_config.json")
            
            if resultado:
                registrar_log(" -> ✅ Alerta Telegram enviada")
            else:
                registrar_log(" -> ❌ Error enviando alerta (verificar token/chat_id)")
            
            # Limpiar archivo temporal
            if os.path.exists("temp_config.json"):
                os.remove("temp_config.json")
                
        except Exception as e:
            registrar_log(f" -> ❌ Error Telegram: {e}")
    
    registrar_log("")
    registrar_log("✅ Auditoría completada")
    registrar_log(f"📄 Log guardado en: {log_path}")
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DE TU CONFIGURACIÓN:")
    print(f"   📡 Red escaneada: {config['network_range']}")
    print(f"   🎯 Dispositivos encontrados: {len(ips) if 'ips' in locals() else 0}")
    print(f"   🔌 Puertos configurados: {config['camera_ports']}")
    print(f"   📖 Diccionario usado: {config['brute_dict_path']}")
    print(f"   📱 Telegram: {'✅' if config['enable_telegram'] else '❌'}")
    print(f"   📄 Log: {log_path}")

if __name__ == "__main__":
    main()
