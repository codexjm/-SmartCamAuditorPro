# 🔒 SmartCam Auditor Pro v2.0

## 📋 Descripción

**SmartCam Auditor Pro** es una herramienta profesional de auditoría de seguridad diseñada específicamente para identificar vulnerabilidades en cámaras inteligentes y dispositivos IoT. Esta versión Pro incluye funcionalidades avanzadas como cracking de hashes, análisis CVE automatizado, fingerprinting con Nmap, análisis de diferencias y un panel web completo para gestión empresarial.

## ⚠️ Aviso Legal

**IMPORTANTE**: Esta herramienta está destinada únicamente para uso en redes propias o con autorización explícita del propietario de la red. El uso no autorizado puede violar leyes locales e internacionales. Los autores no se hacen responsables del mal uso de esta herramienta.

## 🌟 Características Principales

### 🔍 Auditoría de Seguridad Avanzada
- **Escaneo de Red**: Detección automática de dispositivos IoT en múltiples redes
- **Análisis CVE**: Verificación automática de vulnerabilidades conocidas
- **Cracking de Hashes**: Integración con John the Ripper y Hashcat
- **Análisis de Puertos**: Identificación de servicios activos y vulnerables  
- **Pruebas de Credenciales**: Testing de credenciales por defecto y débiles
- **Fingerprinting**: Identificación de marcas y modelos con Nmap
- **Análisis de Diferencias**: Comparación entre escaneos para detectar cambios
- **Base de Datos Local**: Almacenamiento SQLite para historial de auditorías
- **Análisis IA**: Detección de objetos en streams RTSP con YOLO
- **Notificaciones**: Alertas por Telegram integradas
- **Reportes Detallados**: Generación de informes completos en múltiples formatos

### 🌐 Panel Web Empresarial
- **Dashboard Intuitivo**: Interfaz moderna y responsiva
- **Control de Auditorías**: Inicio, parada y monitoreo en tiempo real
- **Visualización de Resultados**: Tablas interactivas con estadísticas
- **Gestión de Logs**: Visualización, descarga y eliminación de archivos
- **Información del Sistema**: Monitoreo de recursos y configuración
- **Exportación de Reportes**: Descarga de informes en formato JSON

### 🛡️ Módulos Especializados
- **Hash Cracker**: Cracking automático con detección de formatos
- **Diff Analyzer**: Análisis de cambios entre auditorías
- **Shodan Local**: Base de datos local para gestión de dispositivos
- **CVE Checker**: Verificación de vulnerabilidades específicas
- **Exploit Launcher**: Lanzamiento controlado de exploits
- **Image AI Analyzer**: Análisis inteligente de imágenes
- **Telegram Notifier**: Sistema de notificaciones en tiempo real

## Instalación

### Prerrequisitos
- Python 3.7 o superior
- Acceso a la red que se desea auditar

### Pasos de Instalación

1. Clona o descarga este repositorio:
```bash
git clone <url-del-repositorio>
cd smartcam_auditor
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las redes a escanear editando `config/networks.txt`

## Uso

### Configuración Básica

1. **Edita el archivo de configuración**:
   ```
   config/networks.txt
   ```
   Agrega las redes que deseas escanear en formato CIDR:
   ```
   192.168.1.0/24
   10.0.0.0/24
   ```

2. **Ejecuta la auditoría**:
   ```bash
   python smartcam_auditor.py
   ```

### Ejemplo de Salida

```
=== SmartCam Auditor - Iniciando auditoría ===

[+] Escaneando red: 192.168.1.0/24
    [*] Iniciando escaneo de red 192.168.1.0/24
    [*] Escaneando 254 hosts...
    [+] Dispositivo encontrado: 192.168.1.100
    [+] Dispositivo encontrado: 192.168.1.101

  [+] Analizando dispositivo: 192.168.1.100
      [*] Verificando 21 puertos en 192.168.1.100
      [+] Puerto abierto: 80 (HTTP)
      [+] Puerto abierto: 554 (RTSP)
        [*] Probando credenciales comunes en 192.168.1.100
        [!] CREDENCIALES ENCONTRADAS: admin:admin en HTTP:80

      ═══ RESUMEN DE AUDITORÍA - 192.168.1.100 ═══
      Puertos abiertos: 2
      Credenciales encontradas: 1
      Nivel de riesgo: ALTO
      ⚠️  VULNERABILIDAD DETECTADA: Credenciales por defecto activas
```

## Estructura del Proyecto

```
smartcam_auditor/
├── smartcam_auditor.py      # Script principal
├── requirements.txt         # Dependencias Python
├── README.md               # Este archivo
├── config/
│   └── networks.txt        # Configuración de redes
├── scanner/
│   ├── __init__.py
│   ├── network_scanner.py  # Escaneo de red
│   ├── port_checker.py     # Verificación de puertos
│   ├── login_tester.py     # Pruebas de login
│   └── log_manager.py      # Gestión de logs
└── logs/                   # Reportes generados
    ├── smartcam_audit_current.json
    └── smartcam_audit_current.csv
```

## Reportes

La herramienta genera dos tipos de reportes:

### JSON (Detallado)
- Información completa de cada dispositivo
- Análisis de riesgo
- Recomendaciones de seguridad
- Metadatos de auditoría

### CSV (Resumen)
- Formato tabular para análisis rápido
- Compatible con Excel y herramientas de BI
- Ideal para reportes ejecutivos

## Credenciales Probadas

La herramienta verifica estas combinaciones comunes:
- admin/admin
- admin/(vacío)
- root/root
- admin/123456
- Y muchas más específicas de fabricantes

## Puertos Escaneados

Puertos comunes en cámaras IP y dispositivos IoT:
- 80, 443 (HTTP/HTTPS)
- 554, 8554 (RTSP)
- 21 (FTP)
- 22 (SSH)
- 23 (Telnet)
- 8080, 8443 (HTTP alternativo)
- 9999, 37777, 34567 (Puertos específicos de cámaras)

## Evaluación de Riesgo

La herramienta asigna niveles de riesgo basados en:
- Número de puertos abiertos
- Tipos de servicios expuestos
- Credenciales por defecto encontradas

**Niveles de Riesgo**:
- 🟢 **BAJO**: Configuración básica de seguridad
- 🟡 **MEDIO**: Algunos servicios expuestos
- 🟠 **ALTO**: Multiple servicios y/o credenciales débiles
- 🔴 **CRÍTICO**: Vulnerabilidades graves detectadas

## Consideraciones Éticas y Legales

- ✅ Usar solo en redes propias
- ✅ Obtener autorización escrita antes de auditar redes de terceros
- ✅ Respetar los términos de servicio y políticas de uso
- ❌ No usar para actividades maliciosas
- ❌ No comprometer sistemas sin autorización

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para reportar bugs o solicitar features, por favor abre un issue en el repositorio.

---

**Desarrollado por el SmartCam Security Team**  
*Versión 1.0.0 - Julio 2025*
