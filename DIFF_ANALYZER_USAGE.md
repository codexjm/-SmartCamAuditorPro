# Módulo diff_analyzer - Documentación de Uso

## Resumen

El módulo `scanner.diff_analyzer` contiene todas las funciones para comparar auditorías y analizar cambios entre logs de SmartCam Auditor. Este módulo ha sido refactorizado desde `scanner.network_scanner` para mantener la separación de responsabilidades.

## Importación

```python
# Importar funciones específicas
from scanner.diff_analyzer import (
    obtener_logs_ordenados,
    comparar_logs_actual_vs_anterior,
    analizar_cambios_dispositivos,
    generar_reporte_cambios,
    monitorear_cambios_automatico
)

# O importar el módulo completo
import scanner.diff_analyzer as diff_analyzer
```

## Funciones Disponibles

### 1. `obtener_logs_ordenados(log_dir="logs")`
Obtiene la lista de archivos de log ordenados por fecha.

**Parámetros:**
- `log_dir` (str): Directorio donde se almacenan los logs

**Retorna:**
- `list`: Lista de rutas completas a los archivos de log

### 2. `comparar_logs_actual_vs_anterior(log_dir="logs")`
Compara la auditoría más reciente con la anterior.

**Parámetros:**
- `log_dir` (str): Directorio donde se almacenan los logs

**Retorna:**
- `str`: Resumen de las diferencias encontradas

### 3. `analizar_cambios_dispositivos(log_dir="logs")`
Analiza específicamente cambios en dispositivos detectados.

**Parámetros:**
- `log_dir` (str): Directorio donde se almacenan los logs

**Retorna:**
- `dict`: Resumen estructurado con claves:
  - `dispositivos_nuevos`: Lista de IPs nuevas
  - `dispositivos_perdidos`: Lista de IPs que ya no responden
  - `dispositivos_mantenidos`: Lista de IPs que persisten
  - `total_anterior`: Número total de dispositivos en auditoría anterior
  - `total_actual`: Número total de dispositivos en auditoría actual
  - `cambio_neto`: Diferencia entre totales

### 4. `generar_reporte_cambios(log_dir="logs", output_file=None)`
Genera un reporte completo de cambios entre auditorías.

**Parámetros:**
- `log_dir` (str): Directorio donde se almacenan los logs
- `output_file` (str, opcional): Archivo donde guardar el reporte

**Retorna:**
- `str`: Reporte completo de cambios

### 5. `monitorear_cambios_automatico(log_dir="logs", umbral_cambios=3)`
Monitorea automáticamente cambios significativos.

**Parámetros:**
- `log_dir` (str): Directorio donde se almacenan los logs
- `umbral_cambios` (int): Número mínimo de cambios para generar alerta

**Retorna:**
- `dict`: Estado del monitoreo con claves:
  - `estado`: "ok" o "error"
  - `total_cambios`: Número total de cambios detectados
  - `alerta`: Boolean indicando si hay alertas
  - `alertas`: Lista de mensajes de alerta

## Ejemplo de Uso Básico

```python
from scanner.diff_analyzer import comparar_logs_actual_vs_anterior

# Comparación simple
resultado = comparar_logs_actual_vs_anterior()
print(resultado)
```

## Ejemplo de Uso con Configuración

```python
import json
from scanner.diff_analyzer import (
    comparar_logs_actual_vs_anterior,
    monitorear_cambios_automatico
)

# Cargar configuración
with open("config/config.json") as f:
    config = json.load(f)

# Usar funciones con configuración
if config.get("enable_diff_analyzer", True):
    print("🔍 Comparando con auditoría anterior...")
    resultado_diff = comparar_logs_actual_vs_anterior()
    print(resultado_diff)
    
    # Monitoreo automático con umbral personalizado
    umbral = config.get("umbral_cambios", 3)
    estado = monitorear_cambios_automatico(umbral_cambios=umbral)
    
    if estado.get("alerta"):
        print("🚨 ¡Alertas detectadas!")
        for alerta in estado["alertas"]:
            print(f"   - {alerta}")
```

## Integración con el Flujo Principal

```python
# En smartcam_auditor.py
from scanner.diff_analyzer import comparar_logs_actual_vs_anterior
from scanner.log_manager import save_log

def registrar_log(mensaje):
    """Función auxiliar para logging"""
    print(f"[{datetime.now()}] {mensaje}")
    save_log(mensaje)

# Uso en el flujo principal
config = load_config()

if config.get("enable_diff_analyzer", True):
    registrar_log("🔍 Comparando con auditoría anterior...")
    resultado_diff = comparar_logs_actual_vs_anterior()
    registrar_log(resultado_diff)
```

## Configuración Recomendada (config/config.json)

```json
{
    "enable_diff_analyzer": true,
    "umbral_cambios": 3,
    "generar_reportes_automaticos": true,
    "log_folder": "logs",
    "alert_mode": "console"
}
```

## Archivos de Salida

El módulo puede generar los siguientes archivos:

1. **Logs de actividad**: `logs/diff_analyzer_YYYYMMDD.log`
2. **Reportes de cambios**: `logs/reporte_cambios_YYYYMMDD_HHMMSS.txt`

## Notas Importantes

- ⚠️ Las funciones han sido **removidas** de `scanner.network_scanner` para evitar duplicación
- ✅ Todas las importaciones deben hacerse desde `scanner.diff_analyzer`
- 🔄 La funcionalidad permanece exactamente igual, solo cambió la ubicación
- 📊 Compatible con la configuración existente del proyecto

## Scripts de Demostración

- `demo_diff_analyzer_modular.py`: Demo completo con configuración
- `test_diff_analyzer_modular.py`: Tests de verificación del módulo

## Migración desde Versiones Anteriores

Si tenías código que importaba desde `network_scanner`:

```python
# ❌ Antes (ya no funciona)
from scanner.network_scanner import comparar_logs_actual_vs_anterior

# ✅ Ahora (correcto)
from scanner.diff_analyzer import comparar_logs_actual_vs_anterior
```

---

**Autor**: SmartCam Security Team  
**Fecha**: 8 de julio de 2025  
**Versión**: 2.0 (Modularizado)
