import os
import time
from datetime import datetime

def realizar_auditoria():
    """Realiza una auditoría de seguridad simulada y genera un reporte"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f"security_assessment_{timestamp}.txt")

    contenido = [
        f"📡 Auditoría de Seguridad - {timestamp}",
        "------------------------------------------",
        "[✔️] Escaneando red local...",
        " -> Detectadas 5 cámaras IP activas.",
        "[✔️] Verificando puertos abiertos...",
        " -> 3 cámaras con puertos expuestos: 80, 554, 8000",
        "[⚠️] Verificando credenciales débiles...",
        " -> 2 cámaras usan admin:admin",
        "[❌] Cámaras sin cifrado detectadas",
        "[✔️] Reporte finalizado.",
        "------------------------------------------",
    ]

    # Simular tiempo de procesamiento para ver el indicador
    time.sleep(3)  # 3 segundos de delay para pruebas

    with open(log_path, "w", encoding="utf-8") as f:
        for linea in contenido:
            f.write(linea + "\n")

    print(f"[+] Reporte guardado en: {log_path}")
    return log_path

def realizar_auditoria_rapida():
    """Realiza una auditoría rápida con menos checks"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f"quick_scan_{timestamp}.txt")

    contenido = [
        f"⚡ Escaneo Rápido - {timestamp}",
        "------------------------------------------",
        "[✔️] Ping sweep completado",
        " -> 3 dispositivos IoT encontrados",
        "[⚠️] Puertos críticos abiertos detectados",
        "[✔️] Escaneo rápido finalizado.",
        "------------------------------------------",
    ]

    # Simular tiempo de procesamiento más corto
    time.sleep(1.5)  # 1.5 segundos de delay para pruebas

    with open(log_path, "w", encoding="utf-8") as f:
        for linea in contenido:
            f.write(linea + "\n")

    print(f"[+] Escaneo rápido guardado en: {log_path}")
    return log_path

if __name__ == "__main__":
    realizar_auditoria()
