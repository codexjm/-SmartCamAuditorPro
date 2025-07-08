"""
Módulo de análisis de diferencias y comparación de logs de auditoría
Funciones para detectar cambios entre auditorías consecutivas
"""

import os
import re
import difflib
import datetime

# =========================================================================
# FUNCIONES DE COMPARACIÓN DE LOGS DE AUDITORÍA
# =========================================================================

def obtener_logs_ordenados(log_dir="logs"):
    """
    Obtiene la lista de archivos de log de auditoría ordenados por fecha
    
    Args:
        log_dir (str): Directorio donde se almacenan los logs
    
    Returns:
        list: Lista de rutas completas a los archivos de log ordenados
    """
    if not os.path.exists(log_dir):
        return []
    
    archivos = [
        f for f in os.listdir(log_dir)
        if f.startswith("audit_") and f.endswith(".txt")
    ]
    archivos.sort()
    return [os.path.join(log_dir, f) for f in archivos]

def comparar_logs_actual_vs_anterior(log_dir="logs"):
    """
    Compara la auditoría más reciente con la anterior para detectar cambios
    
    Args:
        log_dir (str): Directorio donde se almacenan los logs
    
    Returns:
        str: Resumen de las diferencias encontradas
    """
    logs = obtener_logs_ordenados(log_dir)
    if len(logs) < 2:
        return "❌ No hay suficientes auditorías para comparar."

    log_anterior = logs[-2]
    log_actual = logs[-1]

    try:
        with open(log_anterior, "r", encoding="utf-8") as f1, \
             open(log_actual, "r", encoding="utf-8") as f2:
            anterior = f1.readlines()
            actual = f2.readlines()

        diferencias = list(difflib.unified_diff(anterior, actual, lineterm=""))
        if not diferencias:
            return "✅ No hay diferencias entre auditorías."

        resumen = ["🔄 Diferencias encontradas entre auditorías:"]
        for linea in diferencias:
            if linea.startswith("+ ") or linea.startswith("- "):
                resumen.append(linea)
        return "\n".join(resumen)
    
    except Exception as e:
        return f"❌ Error al comparar logs: {str(e)}"

def analizar_cambios_dispositivos(log_dir="logs"):
    """
    Analiza específicamente los cambios en dispositivos detectados entre auditorías
    
    Args:
        log_dir (str): Directorio donde se almacenan los logs
    
    Returns:
        dict: Resumen estructurado de cambios en dispositivos
    """
    logs = obtener_logs_ordenados(log_dir)
    if len(logs) < 2:
        return {"error": "No hay suficientes auditorías para comparar"}

    def extraer_dispositivos_de_log(log_path):
        """Extrae información de dispositivos de un archivo de log"""
        dispositivos = {}
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                contenido = f.read()
                
            # Buscar patrones de dispositivos detectados
            patron_ip = r"(\d+\.\d+\.\d+\.\d+)"
            ips_encontradas = re.findall(patron_ip, contenido)
            
            for ip in ips_encontradas:
                # Buscar información adicional para cada IP
                if ip in contenido:
                    dispositivos[ip] = {
                        "detectado": True,
                        "info": "Dispositivo detectado en auditoría"
                    }
            
            return dispositivos
        except Exception:
            return {}

    dispositivos_anterior = extraer_dispositivos_de_log(logs[-2])
    dispositivos_actual = extraer_dispositivos_de_log(logs[-1])

    # Analizar cambios
    dispositivos_nuevos = set(dispositivos_actual.keys()) - set(dispositivos_anterior.keys())
    dispositivos_perdidos = set(dispositivos_anterior.keys()) - set(dispositivos_actual.keys())
    dispositivos_comunes = set(dispositivos_actual.keys()) & set(dispositivos_anterior.keys())

    return {
        "dispositivos_nuevos": list(dispositivos_nuevos),
        "dispositivos_perdidos": list(dispositivos_perdidos),
        "dispositivos_mantenidos": list(dispositivos_comunes),
        "total_anterior": len(dispositivos_anterior),
        "total_actual": len(dispositivos_actual),
        "cambio_neto": len(dispositivos_actual) - len(dispositivos_anterior)
    }

def generar_reporte_cambios(log_dir="logs", output_file=None):
    """
    Genera un reporte completo de cambios entre auditorías
    
    Args:
        log_dir (str): Directorio donde se almacenan los logs
        output_file (str): Archivo donde guardar el reporte (opcional)
    
    Returns:
        str: Reporte completo de cambios
    """
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs = obtener_logs_ordenados(log_dir)
    
    if len(logs) < 2:
        reporte = f"""
🔍 REPORTE DE CAMBIOS - SMARTCAM AUDITOR
Fecha: {timestamp}
❌ No hay suficientes auditorías para generar reporte de cambios.
Ejecuta al menos 2 auditorías para comparar resultados.
"""
        return reporte

    # Obtener nombres de archivos para el reporte
    log_anterior_nombre = os.path.basename(logs[-2])
    log_actual_nombre = os.path.basename(logs[-1])

    # Comparación general
    diferencias_generales = comparar_logs_actual_vs_anterior(log_dir)
    
    # Análisis específico de dispositivos
    cambios_dispositivos = analizar_cambios_dispositivos(log_dir)

    reporte = f"""
🔍 REPORTE DE CAMBIOS - SMARTCAM AUDITOR
========================================
Fecha: {timestamp}
Auditoría anterior: {log_anterior_nombre}
Auditoría actual: {log_actual_nombre}

📊 RESUMEN DE DISPOSITIVOS:
• Total anterior: {cambios_dispositivos.get('total_anterior', 0)}
• Total actual: {cambios_dispositivos.get('total_actual', 0)}
• Cambio neto: {cambios_dispositivos.get('cambio_neto', 0):+d}

🆕 DISPOSITIVOS NUEVOS ({len(cambios_dispositivos.get('dispositivos_nuevos', []))}):
"""
    
    for ip in cambios_dispositivos.get('dispositivos_nuevos', []):
        reporte += f"   + {ip}\n"
    
    if not cambios_dispositivos.get('dispositivos_nuevos'):
        reporte += "   (Ninguno)\n"

    reporte += f"""
❌ DISPOSITIVOS PERDIDOS ({len(cambios_dispositivos.get('dispositivos_perdidos', []))}):
"""
    
    for ip in cambios_dispositivos.get('dispositivos_perdidos', []):
        reporte += f"   - {ip}\n"
    
    if not cambios_dispositivos.get('dispositivos_perdidos'):
        reporte += "   (Ninguno)\n"

    reporte += f"""
✅ DISPOSITIVOS MANTENIDOS ({len(cambios_dispositivos.get('dispositivos_mantenidos', []))}):
"""
    
    for ip in cambios_dispositivos.get('dispositivos_mantenidos', [])[:5]:  # Mostrar solo los primeros 5
        reporte += f"   = {ip}\n"
    
    if len(cambios_dispositivos.get('dispositivos_mantenidos', [])) > 5:
        reporte += f"   ... y {len(cambios_dispositivos.get('dispositivos_mantenidos', [])) - 5} más\n"
    
    if not cambios_dispositivos.get('dispositivos_mantenidos'):
        reporte += "   (Ninguno)\n"

    reporte += f"""
🔄 DIFERENCIAS DETALLADAS:
{diferencias_generales}

📋 RECOMENDACIONES:
"""
    
    if cambios_dispositivos.get('dispositivos_nuevos'):
        reporte += "• Investigar dispositivos nuevos para verificar si son legítimos\n"
    
    if cambios_dispositivos.get('dispositivos_perdidos'):
        reporte += "• Verificar por qué algunos dispositivos ya no responden\n"
    
    if cambios_dispositivos.get('cambio_neto', 0) > 0:
        reporte += "• Aumento en dispositivos detectados - revisar seguridad de red\n"
    elif cambios_dispositivos.get('cambio_neto', 0) < 0:
        reporte += "• Disminución en dispositivos - verificar conectividad de red\n"
    else:
        reporte += "• Red estable - mantener monitoreo regular\n"

    reporte += "\n" + "="*50

    # Guardar reporte si se especifica archivo
    if output_file:
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(reporte)
            print(f"📄 Reporte guardado en: {output_file}")
        except Exception as e:
            print(f"❌ Error al guardar reporte: {e}")

    return reporte

def monitorear_cambios_automatico(log_dir="logs", umbral_cambios=3):
    """
    Monitorea automáticamente cambios significativos entre auditorías
    
    Args:
        log_dir (str): Directorio donde se almacenan los logs
        umbral_cambios (int): Número mínimo de cambios para generar alerta
    
    Returns:
        dict: Estado del monitoreo y alertas
    """
    cambios = analizar_cambios_dispositivos(log_dir)
    
    if "error" in cambios:
        return {
            "estado": "error",
            "mensaje": cambios["error"],
            "alerta": False
        }

    total_cambios = len(cambios.get('dispositivos_nuevos', [])) + len(cambios.get('dispositivos_perdidos', []))
    
    alertas = []
    
    if total_cambios >= umbral_cambios:
        alertas.append(f"🚨 {total_cambios} cambios detectados (umbral: {umbral_cambios})")
    
    if len(cambios.get('dispositivos_nuevos', [])) > 0:
        alertas.append(f"🆕 {len(cambios['dispositivos_nuevos'])} dispositivos nuevos")
    
    if len(cambios.get('dispositivos_perdidos', [])) > 0:
        alertas.append(f"❌ {len(cambios['dispositivos_perdidos'])} dispositivos perdidos")
    
    cambio_neto_abs = abs(cambios.get('cambio_neto', 0))
    if cambio_neto_abs > umbral_cambios:
        alertas.append(f"📊 Cambio neto significativo: {cambios.get('cambio_neto', 0):+d}")

    return {
        "estado": "ok",
        "total_cambios": total_cambios,
        "umbral": umbral_cambios,
        "alerta": len(alertas) > 0,
        "alertas": alertas,
        "cambios_detallados": cambios
    }

# =========================================================================
# FUNCIONES DE ANÁLISIS AVANZADO DE DIFERENCIAS
# =========================================================================

def comparar_auditorias_especificas(log_file1, log_file2):
    """
    Compara dos archivos de auditoría específicos
    
    Args:
        log_file1 (str): Ruta al primer archivo de log
        log_file2 (str): Ruta al segundo archivo de log
    
    Returns:
        dict: Análisis detallado de diferencias
    """
    try:
        with open(log_file1, "r", encoding="utf-8") as f1, \
             open(log_file2, "r", encoding="utf-8") as f2:
            contenido1 = f1.read()
            contenido2 = f2.read()
        
        # Extraer IPs de ambos logs
        patron_ip = r"(\d+\.\d+\.\d+\.\d+)"
        ips1 = set(re.findall(patron_ip, contenido1))
        ips2 = set(re.findall(patron_ip, contenido2))
        
        return {
            "archivo1": os.path.basename(log_file1),
            "archivo2": os.path.basename(log_file2),
            "ips_solo_archivo1": list(ips1 - ips2),
            "ips_solo_archivo2": list(ips2 - ips1),
            "ips_comunes": list(ips1 & ips2),
            "total_archivo1": len(ips1),
            "total_archivo2": len(ips2)
        }
        
    except Exception as e:
        return {"error": f"Error comparando archivos: {str(e)}"}

def generar_historial_cambios(log_dir="logs", ultimas_n_auditorias=5):
    """
    Genera un historial de cambios para las últimas N auditorías
    
    Args:
        log_dir (str): Directorio de logs
        ultimas_n_auditorias (int): Número de auditorías a analizar
    
    Returns:
        dict: Historial detallado de cambios
    """
    logs = obtener_logs_ordenados(log_dir)
    
    if len(logs) < 2:
        return {"error": "Insuficientes auditorías para generar historial"}
    
    # Tomar las últimas N auditorías
    logs_analizar = logs[-ultimas_n_auditorias:] if len(logs) >= ultimas_n_auditorias else logs
    
    historial = {
        "auditorias_analizadas": len(logs_analizar),
        "periodo": {
            "inicio": os.path.basename(logs_analizar[0]),
            "fin": os.path.basename(logs_analizar[-1])
        },
        "cambios_por_auditoria": []
    }
    
    # Analizar cambios entre auditorías consecutivas
    for i in range(1, len(logs_analizar)):
        cambio = comparar_auditorias_especificas(logs_analizar[i-1], logs_analizar[i])
        if "error" not in cambio:
            historial["cambios_por_auditoria"].append({
                "transicion": f"{cambio['archivo1']} → {cambio['archivo2']}",
                "dispositivos_añadidos": len(cambio["ips_solo_archivo2"]),
                "dispositivos_perdidos": len(cambio["ips_solo_archivo1"]),
                "dispositivos_estables": len(cambio["ips_comunes"]),
                "cambio_neto": len(cambio["ips_solo_archivo2"]) - len(cambio["ips_solo_archivo1"])
            })
    
    return historial

def detectar_patrones_dispositivos(log_dir="logs"):
    """
    Detecta patrones en la aparición y desaparición de dispositivos
    
    Args:
        log_dir (str): Directorio de logs
    
    Returns:
        dict: Patrones detectados
    """
    logs = obtener_logs_ordenados(log_dir)
    
    if len(logs) < 3:
        return {"error": "Se necesitan al menos 3 auditorías para detectar patrones"}
    
    # Extraer IPs de cada log
    ips_por_log = {}
    for log_path in logs:
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                contenido = f.read()
            patron_ip = r"(\d+\.\d+\.\d+\.\d+)"
            ips = set(re.findall(patron_ip, contenido))
            ips_por_log[os.path.basename(log_path)] = ips
        except Exception:
            continue
    
    # Analizar patrones
    todas_las_ips = set()
    for ips in ips_por_log.values():
        todas_las_ips.update(ips)
    
    patrones = {
        "dispositivos_persistentes": [],  # Aparecen en todas las auditorías
        "dispositivos_intermitentes": [], # Aparecen y desaparecen
        "dispositivos_nuevos_recientes": [], # Solo en las últimas auditorías
        "dispositivos_desaparecidos": []  # Solo en las primeras auditorías
    }
    
    nombre_logs = list(ips_por_log.keys())
    total_auditorias = len(nombre_logs)
    
    for ip in todas_las_ips:
        apariciones = [log for log, ips in ips_por_log.items() if ip in ips]
        frecuencia = len(apariciones) / total_auditorias
        
        if frecuencia == 1.0:
            patrones["dispositivos_persistentes"].append(ip)
        elif frecuencia >= 0.5:
            patrones["dispositivos_intermitentes"].append(ip)
        elif apariciones[-1] in nombre_logs[-2:]:  # Últimas 2 auditorías
            patrones["dispositivos_nuevos_recientes"].append(ip)
        elif apariciones[-1] in nombre_logs[:2]:  # Primeras 2 auditorías
            patrones["dispositivos_desaparecidos"].append(ip)
    
    return patrones

# =========================================================================
# FUNCIONES DE EXPORTACIÓN Y REPORTING
# =========================================================================

def exportar_analisis_csv(log_dir="logs", output_file="analisis_cambios.csv"):
    """
    Exporta el análisis de cambios a formato CSV
    
    Args:
        log_dir (str): Directorio de logs
        output_file (str): Archivo CSV de salida
    
    Returns:
        bool: True si se exportó exitosamente
    """
    try:
        import csv
        
        logs = obtener_logs_ordenados(log_dir)
        if len(logs) < 2:
            return False
        
        # Preparar datos para CSV
        datos_csv = []
        
        for i in range(1, len(logs)):
            cambio = comparar_auditorias_especificas(logs[i-1], logs[i])
            if "error" not in cambio:
                datos_csv.append({
                    "auditoria_anterior": cambio["archivo1"],
                    "auditoria_actual": cambio["archivo2"],
                    "dispositivos_anteriores": cambio["total_archivo1"],
                    "dispositivos_actuales": cambio["total_archivo2"],
                    "dispositivos_nuevos": len(cambio["ips_solo_archivo2"]),
                    "dispositivos_perdidos": len(cambio["ips_solo_archivo1"]),
                    "dispositivos_comunes": len(cambio["ips_comunes"]),
                    "cambio_neto": len(cambio["ips_solo_archivo2"]) - len(cambio["ips_solo_archivo1"])
                })
        
        # Escribir CSV
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            if datos_csv:
                fieldnames = datos_csv[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(datos_csv)
        
        return True
        
    except Exception as e:
        print(f"❌ Error exportando CSV: {e}")
        return False
