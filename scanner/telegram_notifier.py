"""
Módulo de notificaciones por Telegram para SmartCam Auditor
"""

import requests
import json
import time
from datetime import datetime

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None, config_file="config/config.json"):
        """
        Inicializa el notificador de Telegram
        
        Args:
            bot_token (str): Token del bot de Telegram
            chat_id (str): ID del chat donde enviar notificaciones
            config_file (str): Archivo de configuración
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.config = {}
        
        # Cargar configuración si no se proporcionan parámetros
        if not bot_token or not chat_id:
            self.load_config(config_file)
    
    def load_config(self, config_file):
        """Carga la configuración desde archivo"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            if not self.bot_token:
                self.bot_token = self.config.get('telegram_bot_token')
            if not self.chat_id:
                self.chat_id = self.config.get('telegram_chat_id')
                
        except Exception as e:
            print(f"[WARNING] No se pudo cargar la configuración de Telegram: {e}")
            self.config = {}
    
    def is_enabled(self):
        """Verifica si las notificaciones están habilitadas"""
        return (
            self.bot_token and 
            self.chat_id and 
            self.bot_token != "TU_TOKEN" and 
            self.chat_id != "TU_CHAT_ID" and
            self.config.get('notification_settings', {}).get('enable_telegram', False)
        )
    
    def send_message(self, message, parse_mode='HTML'):
        """
        Envía un mensaje por Telegram
        
        Args:
            message (str): Mensaje a enviar
            parse_mode (str): Modo de parseo (HTML, Markdown)
        
        Returns:
            bool: True si se envió correctamente
        """
        if not self.is_enabled():
            print(f"[INFO] Telegram no configurado, mensaje: {message}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"[✓] Notificación enviada por Telegram")
                return True
            else:
                print(f"[ERROR] Error enviando notificación: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error de conexión con Telegram: {e}")
            return False
    
    def notify_scan_start(self, network_range):
        """Notifica el inicio de un escaneo"""
        if not self.config.get('notification_settings', {}).get('notify_on_scan_complete', True):
            return False
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"""
🔍 <b>SmartCam Auditor - Escaneo Iniciado</b>

📅 <b>Fecha:</b> {timestamp}
🌐 <b>Red objetivo:</b> <code>{network_range}</code>
🎯 <b>Estado:</b> Escaneando dispositivos IoT/Cámaras IP

⏳ El escaneo está en progreso...
        """
        return self.send_message(message)
    
    def notify_device_found(self, device_info):
        """Notifica cuando se encuentra un dispositivo"""
        if not self.config.get('notification_settings', {}).get('notify_on_device_found', True):
            return False
            
        message = f"""
📱 <b>Dispositivo Detectado</b>

🔗 <b>IP:</b> <code>{device_info['ip']}</code>
🏷️ <b>Tipo:</b> {device_info['device_type']}
📊 <b>Confianza:</b> {device_info['confidence']}%
🔌 <b>Puertos:</b> {', '.join(map(str, device_info['open_ports']))}
        """
        return self.send_message(message)
    
    def notify_vulnerability_found(self, ip, vulnerability_type, details):
        """Notifica cuando se encuentra una vulnerabilidad"""
        if not self.config.get('notification_settings', {}).get('notify_on_vulnerability', True):
            return False
            
        message = f"""
🚨 <b>VULNERABILIDAD DETECTADA</b>

🔗 <b>IP:</b> <code>{ip}</code>
⚠️ <b>Tipo:</b> {vulnerability_type}
📋 <b>Detalles:</b> {details}

🛡️ <b>Acción recomendada:</b> Revisar y corregir inmediatamente
        """
        return self.send_message(message)
    
    def notify_scan_complete(self, results_summary):
        """Notifica cuando se completa un escaneo"""
        if not self.config.get('notification_settings', {}).get('notify_on_scan_complete', True):
            return False
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        devices_count = results_summary.get('devices_found', 0)
        vulnerabilities_count = results_summary.get('vulnerabilities_found', 0)
        scan_time = results_summary.get('scan_time', 'N/A')
        
        status_emoji = "✅" if vulnerabilities_count == 0 else "⚠️"
        
        message = f"""
{status_emoji} <b>SmartCam Auditor - Escaneo Completado</b>

📅 <b>Fecha:</b> {timestamp}
⏱️ <b>Duración:</b> {scan_time}
📱 <b>Dispositivos encontrados:</b> {devices_count}
🚨 <b>Vulnerabilidades:</b> {vulnerabilities_count}

📊 <b>Estado de seguridad:</b> {'SEGURO' if vulnerabilities_count == 0 else 'REQUIERE ATENCIÓN'}
        """
        
        return self.send_message(message)
    
    def notify_credentials_found(self, ip, credentials, service_type):
        """Notifica cuando se encuentran credenciales débiles"""
        message = f"""
🔑 <b>CREDENCIALES DÉBILES ENCONTRADAS</b>

🔗 <b>IP:</b> <code>{ip}</code>
🌐 <b>Servicio:</b> {service_type}
👤 <b>Credenciales:</b> <code>{credentials}</code>

⚠️ <b>RIESGO ALTO:</b> Cambiar credenciales inmediatamente
        """
        return self.send_message(message)

# Función de conveniencia para uso fácil
def send_telegram_notification(message, config_file="config/config.json"):
    """
    Envía una notificación rápida por Telegram
    
    Args:
        message (str): Mensaje a enviar
        config_file (str): Archivo de configuración
    
    Returns:
        bool: True si se envió correctamente
    """
    notifier = TelegramNotifier(config_file=config_file)
    return notifier.send_message(message)
