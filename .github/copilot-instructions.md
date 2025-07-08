<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# SmartCam Auditor - Instrucciones para Copilot

Este es un proyecto de auditoría de seguridad para cámaras inteligentes y dispositivos IoT.

## Contexto del Proyecto
- **Propósito**: Herramienta de pentesting para identificar vulnerabilidades en cámaras IP
- **Lenguaje**: Python 3.7+
- **Arquitectura**: Modular con scanner independientes

## Estructura del Proyecto
- `smartcam_auditor.py`: Script principal
- `scanner/`: Módulos de escaneo
  - `network_scanner.py`: Detección de dispositivos en red
  - `port_checker.py`: Verificación de puertos abiertos
  - `login_tester.py`: Pruebas de credenciales por defecto
  - `log_manager.py`: Gestión de logs y reportes
- `config/`: Archivos de configuración
- `logs/`: Salidas de auditoría

## Guías de Desarrollo
- Usar programación defensiva con manejo de excepciones
- Implementar timeouts en todas las conexiones de red
- Priorizar la seguridad y el uso ético
- Mantener logs detallados de todas las operaciones
- Optimizar rendimiento con threading/async cuando sea apropiado

## Consideraciones de Seguridad
- Esta herramienta debe usarse SOLO en redes propias o con autorización explícita
- Implementar mecanismos de throttling para evitar saturar la red
- No almacenar credenciales en texto plano en logs públicos
- Incluir advertencias legales en la documentación
