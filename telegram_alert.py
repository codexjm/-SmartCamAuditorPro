"""
Módulo para enviar alertas por Telegram
SmartCam Auditor v2.0 Pro
"""

import json
import requests
import os

def cargar_config_telegram(config_file="config/config.json"):
    """Carga la configuración de Telegram desde JSON"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        return {}
    except Exception as e:
        print(f"[ERROR] Error cargando configuración Telegram: {e}")
        return {}

def enviar_alerta(mensaje, config_file="config/config.json"):
    """
    Envía una alerta por Telegram
    
    Args:
        mensaje (str): Mensaje a enviar
        config_file (str): Ruta al archivo de configuración
    
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        config = cargar_config_telegram(config_file)
        
        # Verificar si Telegram está habilitado
        if not config.get("enable_telegram", False):
            print("[INFO] Telegram deshabilitado en configuración")
            return False
        
        # Obtener credenciales
        bot_token = config.get("telegram_bot_token", "")
        chat_id = config.get("telegram_chat_id", "")
        
        # Verificar credenciales
        if bot_token == "TU_TOKEN" or not bot_token:
            print("[WARNING] Token de Telegram no configurado")
            return False
            
        if chat_id == "TU_CHAT_ID" or not chat_id:
            print("[WARNING] Chat ID de Telegram no configurado")
            return False
        
        # Preparar mensaje
        mensaje_formateado = f"🔒 SmartCam Auditor v2.0 Pro\n\n{mensaje}"
        
        # URL de la API de Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Parámetros
        params = {
            'chat_id': chat_id,
            'text': mensaje_formateado,
            'parse_mode': 'HTML'
        }
        
        # Enviar mensaje
        response = requests.post(url, data=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ Alerta Telegram enviada correctamente")
            return True
        else:
            print(f"❌ Error enviando Telegram: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout enviando alerta Telegram")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión enviando alerta Telegram")
        return False
    except Exception as e:
        print(f"❌ Error inesperado enviando Telegram: {e}")
        return False

def enviar_alerta_vulnerabilidades(vulnerabilidades, config_file="config/config.json"):
    """
    Envía alerta específica de vulnerabilidades encontradas
    
    Args:
        vulnerabilidades (list): Lista de vulnerabilidades encontradas
        config_file (str): Ruta al archivo de configuración
    """
    if not vulnerabilidades:
        return
    
    mensaje = "🚨 <b>VULNERABILIDADES ENCONTRADAS</b>\n\n"
    
    for i, vuln in enumerate(vulnerabilidades, 1):
        mensaje += f"{i}. {vuln}\n"
    
    mensaje += f"\n⚠️ <b>ACCIÓN REQUERIDA:</b> Revisar y corregir inmediatamente"
    
    return enviar_alerta(mensaje, config_file)

def enviar_alerta_escaneo_completo(stats, config_file="config/config.json"):
    """
    Envía alerta de escaneo completo con estadísticas
    
    Args:
        stats (dict): Estadísticas del escaneo
        config_file (str): Ruta al archivo de configuración
    """
    dispositivos = stats.get('dispositivos_encontrados', 0)
    vulnerabilidades = stats.get('vulnerabilidades_encontradas', 0)
    tiempo = stats.get('tiempo_total', 'N/A')
    
    mensaje = f"""📊 <b>ESCANEO COMPLETADO</b>

🎯 Dispositivos encontrados: {dispositivos}
🚨 Vulnerabilidades: {vulnerabilidades}
⏱️ Tiempo total: {tiempo}

Status: {'🚨 CRÍTICO' if vulnerabilidades > 0 else '✅ SEGURO'}"""
    
    return enviar_alerta(mensaje, config_file)

def test_telegram(config_file="config/config.json"):
    """
    Prueba la configuración de Telegram
    
    Args:
        config_file (str): Ruta al archivo de configuración
    """
    print("🧪 Probando configuración de Telegram...")
    
    resultado = enviar_alerta("🧪 Mensaje de prueba desde SmartCam Auditor", config_file)
    
    if resultado:
        print("✅ Telegram configurado correctamente")
    else:
        print("❌ Error en configuración de Telegram")
        print("💡 Verifica bot_token y chat_id en config/config.json")
    
    return resultado

if __name__ == "__main__":
    # Prueba la configuración
    test_telegram()
