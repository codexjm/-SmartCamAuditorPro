# 🚀 Instrucciones Rápidas de Despliegue - SmartCam Auditor Pro

## 📋 Resumen Ejecutivo

Tu proyecto **SmartCam Auditor Pro** está listo para ser desplegado en un servidor Linux. He creado todos los scripts y guías necesarias para un despliegue profesional.

## 🎯 Pasos Inmediatos

### 1. Finalizar Commits en Local

```powershell
# En tu máquina Windows
cd c:\Users\codex\smartcam_auditor
git add .
git commit -m "Add server deployment scripts and guides"
git push origin main
```

### 2. Preparar el Servidor

**Opción A: Servidor en la Nube (Recomendado)**
- AWS EC2, Google Cloud, DigitalOcean, etc.
- Mínimo: 2 CPU, 4GB RAM, 20GB disco
- Ubuntu 20.04+ o CentOS 8+

**Opción B: Servidor Local**
- VPS local o máquina dedicada
- Acceso SSH configurado
- IP estática o dominio

### 3. Despliegue Automático

```bash
# Conectar al servidor por SSH
ssh usuario@tu_servidor

# Descargar y ejecutar el script de despliegue
wget https://raw.githubusercontent.com/codexjm/-SmartCamAuditorPro/main/deploy_server.sh
chmod +x deploy_server.sh
sudo ./deploy_server.sh
```

**O manualmente:**

```bash
# Clonar el proyecto
git clone https://github.com/codexjm/-SmartCamAuditorPro.git
cd -SmartCamAuditorPro
chmod +x deploy_server.sh
sudo ./deploy_server.sh
```

### 4. Acceder a la Aplicación

- **Panel Web**: `http://tu_servidor_ip` 
- **HTTPS**: `https://tu_servidor_ip` (si configuraste SSL)
- **SSH**: Para usar CLI directamente

## 📁 Archivos Creados para Despliegue

| Archivo | Descripción |
|---------|-------------|
| `DEPLOY_SERVER_GUIDE.md` | Guía completa paso a paso |
| `deploy_server.sh` | Script automático de instalación |
| `maintain_server.sh` | Script de mantenimiento del servidor |
| `check_deployment.py` | Verificador pre-despliegue |

## ⚡ Comandos Rápidos Post-Despliegue

```bash
# Ver estado del servicio
sudo systemctl status smartcam-auditor

# Ver logs en tiempo real
sudo journalctl -u smartcam-auditor -f

# Ejecutar mantenimiento
sudo ./maintain_server.sh

# Backup manual
sudo -u smartcam /home/smartcam/backup_smartcam.sh
```

## 🔧 Configuración Inicial

1. **Editar redes objetivo**:
   ```bash
   sudo nano /home/smartcam/SmartCamAuditorPro/config/networks.txt
   ```

2. **Configurar parámetros**:
   ```bash
   sudo nano /home/smartcam/SmartCamAuditorPro/config/config.json
   ```

3. **Reiniciar servicio**:
   ```bash
   sudo systemctl restart smartcam-auditor
   ```

## 🌐 Ejemplo de URLs

- **Panel Principal**: `http://192.168.1.100`
- **Logs**: `http://192.168.1.100/logs`
- **Configuración**: `http://192.168.1.100/config`
- **API**: `http://192.168.1.100/api/status`

## 🔒 Consideraciones de Seguridad

✅ **Configurado Automáticamente:**
- Firewall (UFW/firewalld)
- Usuario dedicado (`smartcam`)
- Permisos restrictivos
- Logs de auditoría
- Backup automático

⚠️ **Configurar Manualmente:**
- Cambiar passwords por defecto
- Configurar SSH keys
- Certificado SSL para HTTPS
- Monitoreo adicional (opcional)

## 📊 Monitoreo

El script de mantenimiento incluye:
- Estado del sistema en tiempo real
- Monitoreo de recursos
- Gestión de logs
- Backup automatizado
- Verificaciones de seguridad

## 🆘 Soporte Rápido

### Problemas Comunes:

1. **Servicio no inicia:**
   ```bash
   sudo journalctl -u smartcam-auditor --no-pager -l
   ```

2. **Error de permisos:**
   ```bash
   sudo chown -R smartcam:smartcam /home/smartcam/SmartCamAuditorPro
   ```

3. **Puerto 5000 ocupado:**
   ```bash
   sudo netstat -tulpn | grep :5000
   ```

### Contacto:
- **Logs**: Siempre incluir logs en reportes de errores
- **GitHub**: Issues en el repositorio del proyecto
- **Documentación**: `DEPLOY_SERVER_GUIDE.md` para detalles completos

---

## 🎉 ¡Listo para Producción!

Tu **SmartCam Auditor Pro** incluye:

✅ **Frontend Web Completo**  
✅ **API REST**  
✅ **Scanner Avanzado**  
✅ **Cracking de Hashes**  
✅ **Análisis CVE**  
✅ **Base de Datos Local**  
✅ **Notificaciones**  
✅ **Reportes Detallados**  
✅ **Despliegue Automatizado**  
✅ **Monitoreo y Mantenimiento**  

**¡El proyecto está completamente listo para ser usado en entornos profesionales!** 🚀
