"""
Generador de reportes HTML para SmartCam Auditor
"""

import json
import os
from datetime import datetime

def generate_html_report(results_list, config):
    """Genera un reporte HTML profesional"""
    
    html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCam Auditor - Reporte de Seguridad</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #007bff; margin: 0; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .metric { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .metric h3 { margin: 0; color: #495057; }
        .metric .number { font-size: 2em; font-weight: bold; color: #007bff; }
        .device { margin: 30px 0; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; }
        .device h3 { color: #495057; margin-top: 0; }
        .vulnerability { margin: 15px 0; padding: 15px; border-radius: 5px; }
        .critical { background-color: #f8d7da; border-left: 4px solid #dc3545; }
        .high { background-color: #fff3cd; border-left: 4px solid #ffc107; }
        .medium { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
        .low { background-color: #d4edda; border-left: 4px solid #28a745; }
        .severity { font-weight: bold; text-transform: uppercase; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 SmartCam Auditor</h1>
            <h2>Reporte de Evaluación de Seguridad</h2>
            <p>Generado el: {timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <h3>Dispositivos Analizados</h3>
                <div class="number">{total_devices}</div>
            </div>
            <div class="metric">
                <h3>Vulnerabilidades Críticas</h3>
                <div class="number" style="color: #dc3545;">{critical_count}</div>
            </div>
            <div class="metric">
                <h3>Vulnerabilidades Altas</h3>
                <div class="number" style="color: #ffc107;">{high_count}</div>
            </div>
            <div class="metric">
                <h3>Total de Hallazgos</h3>
                <div class="number">{total_findings}</div>
            </div>
        </div>
        
        {devices_html}
        
        <div class="footer">
            <p>SmartCam Auditor v1.0 - Para uso en redes autorizadas únicamente</p>
            <p>© 2025 Security Solutions Corp. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>"""
    
    # Calcular métricas
    total_devices = len(results_list)
    critical_count = 0
    high_count = 0
    total_findings = 0
    
    devices_html = ""
    
    for result in results_list:
        device_html = f'<div class="device"><h3>📹 Dispositivo: {result["ip"]}</h3>'
        
        vulnerabilities = result.get("vulnerabilities", [])
        if vulnerabilities:
            device_html += "<h4>Vulnerabilidades Encontradas:</h4>"
            for vuln in vulnerabilities:
                severity = vuln["severity"].lower()
                if severity == "critical":
                    critical_count += 1
                elif severity == "high":
                    high_count += 1
                total_findings += 1
                
                device_html += f"""
                <div class="vulnerability {severity}">
                    <span class="severity">{vuln["severity"]}</span>: {vuln["type"]}<br>
                    <small>{vuln["description"]}</small>
                </div>
                """
        else:
            device_html += "<p style='color: #28a745;'>✅ No se encontraron vulnerabilidades críticas</p>"
        
        device_html += "</div>"
        devices_html += device_html
    
    # Generar HTML final
    html_content = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_devices=total_devices,
        critical_count=critical_count,
        high_count=high_count,
        total_findings=total_findings,
        devices_html=devices_html
    )
    
    # Guardar archivo
    report_folder = config.get("log_folder", "logs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = f"{report_folder}/security_report_{timestamp}.html"
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[+] Reporte HTML generado: {html_file}")
    return html_file
