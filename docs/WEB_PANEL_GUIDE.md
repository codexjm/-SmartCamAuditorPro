# SmartCam Auditor v2.0 Pro - Guía de Uso del Panel Web

## 🚀 Introducción

El panel web de SmartCam Auditor v2.0 Pro proporciona una interfaz moderna y profesional para ejecutar auditorías de seguridad en cámaras inteligentes y dispositivos IoT desde el navegador.

## 🔐 Acceso al Sistema

### Login
1. Accede a `http://localhost:5000`
2. **Interfaz moderna**: Disfruta del nuevo diseño profesional con efectos visuales
3. Ingresa las credenciales:
   - **Usuario**: `admin`
   - **Contraseña**: `smartcam2025`
4. Haz clic en "🚀 Iniciar Sesión"

### Características del Login
- **Diseño responsivo**: Compatible con dispositivos móviles y desktop
- **Animaciones suaves**: Efectos visuales profesionales
- **Validación en tiempo real**: Retroalimentación inmediata
- **Seguridad visual**: Indicadores de estado y loading
- **Credenciales mostradas**: Hint con las credenciales por defecto

### Logout
- Haz clic en el botón "🚪 Cerrar Sesión" en la esquina superior derecha

## 🎯 Tipos de Auditoría

### 1. Ejecución Directa 🚀
- **Descripción**: Ejecuta una auditoría completa usando el archivo `smartcam_auditor.py`
- **Uso**: Haz clic en "🚀 Ejecutar Auditoría"
- **Duración**: 5-10 minutos aproximadamente
- **Redes**: Utiliza la configuración de `config/networks.txt`

### 2. Auditoría Rápida ⚡
- **Descripción**: Escaneo optimizado de la red `192.168.1.0/24`
- **Uso**: Haz clic en "⚡ Ejecutar Rápido"
- **Duración**: 2-3 minutos aproximadamente
- **Ideal para**: Pruebas rápidas y validación inicial

### 3. Auditoría Personalizada 🎯
- **Descripción**: Permite especificar manualmente la red objetivo
- **Uso**: 
  1. Haz clic en "🎯 Auditoría Personalizada"
  2. Ingresa la red en formato CIDR (ej: `192.168.1.0/24`)
  3. Haz clic en "🚀 Ejecutar"
- **Duración**: Variable según el tamaño de la red
- **Formatos válidos**: 
  - `192.168.1.0/24` (256 hosts)
  - `10.0.0.0/8` (16.7M hosts)
  - `172.16.0.0/16` (65K hosts)

## 📊 Monitoreo en Tiempo Real

### Barra de Progreso
- **Ubicación**: Centro del dashboard
- **Información**: Muestra el porcentaje de completado
- **Efecto visual**: Animación de brillo durante la ejecución

### Estados de la Auditoría
- 🟢 **Listo**: Sistema disponible para nueva auditoría
- 🔍 **Ejecutando**: Auditoría en progreso
- ✅ **Completada**: Auditoría finalizada exitosamente
- ❌ **Error**: Error durante la ejecución

### Indicador de Conexión
- **Ubicación**: Esquina inferior izquierda
- 🟢 **Conectado**: Comunicación normal con el servidor
- 🔴 **Desconectado**: Problemas de conectividad

## 📈 Dashboard de Gráficos

### Visualización de Analytics
- **Descripción**: Dashboard simplificado con gráficos de seguridad interactivos
- **Acceso**: Haz clic en "� Ver Gráficos" desde el dashboard principal
- **URL directa**: `http://localhost:5000/graficos`

### Características Principales
- **Estadísticas en tiempo real**: Tarjetas con métricas principales
- **Gráfico principal**: Visualización de barras de vulnerabilidades detectadas
- **Interactividad**: Botones para actualizar y exportar datos
- **Diseño responsivo**: Compatible con dispositivos móviles

### Datos Visualizados
- **Credenciales débiles**: Número de credenciales inseguras encontradas
- **Puertos inseguros**: Cantidad de puertos vulnerables detectados
- **Cámaras sin cifrado**: Dispositivos sin protección de cifrado
- **Gráfico de barras**: Distribución visual de todas las vulnerabilidades

### Funcionalidades Interactivas
- **🔄 Actualizar Gráfico**: Recarga los datos con simulación de nuevas métricas
- **📥 Exportar Datos**: Descarga un archivo JSON con los datos del gráfico
- **📊 Volver al Dashboard**: Navegación rápida al panel principal
- **Notificaciones**: Sistema de alertas visuales para acciones del usuario

## 🔔 Sistema de Notificaciones

### Tipos de Notificaciones
- ✅ **Éxito**: Operaciones completadas
- ⚠️ **Advertencia**: Validaciones y precauciones
- ❌ **Error**: Problemas y errores
- ℹ️ **Información**: Estados y procesos

### Interacción
- **Auto-eliminación**: Después de 6 segundos
- **Cierre manual**: Botón "×" en cada notificación
- **Ubicación**: Esquina superior derecha

## 📋 Resultados y Reportes

### Visualización de Resultados
- **Estadísticas**: Dispositivos, vulnerabilidades, credenciales
- **Tabla detallada**: Lista de dispositivos encontrados
- **Información temporal**: Timestamp de última auditoría

### Gestión de Logs
- **Visualización**: Lista de archivos de log generados
- **Descarga**: Botón "📥 Descargar" para cada archivo
- **Eliminación**: Botón "🗑️ Eliminar" para limpiar logs antiguos
- **Información**: Tamaño y fecha de modificación

### Exportación
- **Formato JSON**: Reporte completo con metadatos
- **Botón**: "📥 Exportar Reporte"
- **Contenido**: Resultados, estadísticas y recomendaciones

## ⌨️ Atajos de Teclado

- `Ctrl + Enter`: Ejecutar auditoría rápida
- `Escape`: Cerrar modales abiertos

## 🎨 Personalización

### Tema Oscuro
- **Activación**: Botón "🌙 Tema Oscuro" en la esquina superior
- **Persistencia**: Se mantiene entre sesiones
- **Compatibilidad**: Todos los elementos del dashboard

## 🔧 Configuración Avanzada

### Archivos de Configuración
```
config/
├── networks.txt        # Redes para auditoría directa
├── temp_networks.txt   # Archivo temporal para auditorías personalizadas
└── config.json        # Configuración general
```

### Variables de Entorno
- `SMARTCAM_NETWORK_FILE`: Archivo de redes personalizado
- `PYTHONPATH`: Ruta de módulos Python

## 🚨 Seguridad y Buenas Prácticas

### Validaciones Implementadas
- **Formato CIDR**: Verificación de sintaxis de red
- **Rangos IP**: Validación de direcciones válidas (0-255)
- **Máscara de red**: Rango permitido /8 a /32
- **Path traversal**: Protección contra accesos no autorizados

### Recomendaciones
1. **Cambiar credenciales por defecto** en entornos de producción
2. **Ejecutar solo en redes autorizadas**
3. **Revisar logs regularmente** para detectar anomalías
4. **Mantener el sistema actualizado**
5. **Usar HTTPS en producción**

## 🐛 Resolución de Problemas

### Problemas Comunes

#### Error de Conexión
- **Síntoma**: Indicador rojo de desconexión
- **Solución**: Verificar que el servidor esté ejecutándose
- **Comando**: `python main.py`

#### Auditoría No Inicia
- **Síntoma**: Botón permanece habilitado
- **Solución**: Verificar permisos de ejecución de Python
- **Revisar**: Logs de consola del navegador (F12)

#### Formato de Red Inválido
- **Síntoma**: Notificación de advertencia
- **Solución**: Usar formato CIDR válido (ej: `192.168.1.0/24`)
- **Herramienta**: Calculadora CIDR online

#### Subprocess Falla
- **Síntoma**: Error durante la ejecución
- **Solución**: Verificar dependencias Python instaladas
- **Comando**: `pip install -r requirements.txt`

### Logs de Diagnóstico
```bash
# Ver logs del servidor
python main.py

# Logs de navegador
F12 > Console

# Logs de sistema
logs/smartcam_audit_*.txt
```

## 📱 Compatibilidad Mobile

### Responsive Design
- **Tablets**: Interfaz optimizada para pantallas medianas
- **Móviles**: Layout adaptativo en una columna
- **Touch**: Botones con tamaño apropiado para táctil

### Limitaciones Móviles
- Ejecución de subprocess puede ser limitada
- Recomendado usar desde desktop para auditorías completas

## 🚀 API Endpoints

### Principales Endpoints
```
GET  /                          # Panel principal
POST /login                     # Autenticación
GET  /logout                    # Cerrar sesión
GET  /dashboard                 # Dashboard (autenticado)
GET  /ejecutar                  # Ejecución directa
GET  /ejecutar_rapido          # Auditoría rápida
POST /ejecutar_personalizada   # Auditoría personalizada

# API
GET  /api/status               # Estado actual
GET  /api/results              # Resultados de auditoría
GET  /api/logs                 # Lista de logs
POST /api/clear_results        # Limpiar resultados
GET  /api/system_info          # Información del sistema
```

## 📞 Soporte

### Información de Contacto
- **Desarrollador**: Security Solutions Corp.
- **Versión**: v2.0 Pro
- **Año**: 2025
- **Licencia**: Para uso empresarial y educativo

### Contribuciones
El código está disponible para mejoras y contribuciones siguiendo las mejores prácticas de seguridad.

---

**¡Gracias por usar SmartCam Auditor v2.0 Pro!** 🛡️
