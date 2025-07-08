#!/usr/bin/env python3
"""
SmartCam Auditor - Panel Web
Interfaz web para ejecutar auditorías de seguridad
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from scanner.network_scanner import scan_network
from scanner.port_checker import check_ports
from scanner.login_tester import test_logins
from scanner.advanced_testing import advanced_camera_testing

app = Flask(__name__)

# Estado global de la aplicación
audit_status = {
    "running": False,
    "progress": 0,
    "current_task": "",
    "results": [],
    "last_audit": None
}

def load_config():
    """Carga la configuración desde config.json"""
    try:
        with open("config/config.json") as f:
            return json.load(f)
    except:
        return {"alert_mode": "console", "log_folder": "logs"}

def load_networks():
    """Carga las redes configuradas"""
    try:
        with open("config/networks.txt") as f:
            return [line.strip() for line in f.readlines() 
                   if line.strip() and not line.strip().startswith('#')]
    except:
        return ["192.168.1.0/24"]

def run_audit(networks, config):
    """Ejecuta una auditoría completa"""
    global audit_status
    
    audit_status["running"] = True
    audit_status["progress"] = 0
    audit_status["results"] = []
    audit_status["current_task"] = "Iniciando auditoría..."
    
    total_networks = len(networks)
    
    for i, network in enumerate(networks):
        if not audit_status["running"]:
            break
            
        audit_status["current_task"] = f"Escaneando red: {network}"
        audit_status["progress"] = int((i / total_networks) * 100)
        
        try:
            devices = scan_network(network)
            
            for device in devices:
                if not audit_status["running"]:
                    break
                    
                ip = device['ip']
                audit_status["current_task"] = f"Analizando dispositivo: {ip}"
                
                # Escanear puertos
                ports = check_ports(ip)
                
                # Probar credenciales
                logins = test_logins(ip, ports)
                
                # Testing avanzado
                advanced_result = advanced_camera_testing(ip, ports, config)
                
                # Agregar resultado
                result = {
                    "ip": ip,
                    "network": network,
                    "ports": ports,
                    "credentials": logins,
                    "vulnerabilities": advanced_result.get("vulnerabilities", []),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                audit_status["results"].append(result)
                
        except Exception as e:
            print(f"Error escaneando {network}: {e}")
    
    audit_status["running"] = False
    audit_status["progress"] = 100
    audit_status["current_task"] = "Auditoría completada"
    audit_status["last_audit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def index():
    """Página principal del panel"""
    return render_template('index.html')

@app.route('/api/config')
def get_config():
    """Obtiene la configuración actual"""
    config = load_config()
    networks = load_networks()
    return jsonify({
        "config": config,
        "networks": networks
    })

@app.route('/api/start_audit', methods=['POST'])
def start_audit():
    """Inicia una nueva auditoría"""
    if audit_status["running"]:
        return jsonify({"error": "Ya hay una auditoría en curso"}), 400
    
    data = request.get_json()
    networks = data.get('networks', load_networks())
    config = load_config()
    
    # Ejecutar auditoría en un hilo separado
    thread = threading.Thread(target=run_audit, args=(networks, config))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Auditoría iniciada", "status": "started"})

@app.route('/api/stop_audit', methods=['POST'])
def stop_audit():
    """Detiene la auditoría actual"""
    audit_status["running"] = False
    return jsonify({"message": "Auditoría detenida", "status": "stopped"})

@app.route('/api/status')
def get_status():
    """Obtiene el estado actual de la auditoría"""
    return jsonify(audit_status)

@app.route('/api/results')
def get_results():
    """Obtiene los resultados de la última auditoría"""
    return jsonify({
        "results": audit_status["results"],
        "total_devices": len(audit_status["results"]),
        "vulnerabilities_count": sum(len(r.get("vulnerabilities", [])) for r in audit_status["results"]),
        "credentials_found": sum(len(r.get("credentials", [])) for r in audit_status["results"])
    })

@app.route('/api/export_report')
def export_report():
    """Exporta un reporte en formato JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"smartcam_report_{timestamp}.json"
    
    report = {
        "audit_info": {
            "timestamp": audit_status["last_audit"],
            "total_devices": len(audit_status["results"]),
            "vulnerabilities_count": sum(len(r.get("vulnerabilities", [])) for r in audit_status["results"])
        },
        "results": audit_status["results"]
    }
    
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/{filename}"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    print("=== SmartCam Auditor - Panel Web ===")
    print("🌐 Iniciando servidor web...")
    print("📍 Accede al panel en: http://localhost:5000")
    print("⚠️  Para uso en redes autorizadas únicamente")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
