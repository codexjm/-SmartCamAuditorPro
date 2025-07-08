# 🚀 Guía Completa de Despliegue en Servidor - SmartCam Auditor Pro

Esta guía te ayudará a desplegar SmartCam Auditor Pro en un servidor Linux de forma profesional.

## 📋 Índice

1. [Preparación del Servidor](#preparación-del-servidor)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Configuración del Proyecto](#configuración-del-proyecto)
4. [Configuración de Seguridad](#configuración-de-seguridad)
5. [Despliegue con Systemd](#despliegue-con-systemd)
6. [Configuración de Nginx](#configuración-de-nginx)
7. [Monitoreo y Logs](#monitoreo-y-logs)
8. [Backup y Mantenimiento](#backup-y-mantenimiento)

## 🔧 Preparación del Servidor

### Requisitos Mínimos
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: 4GB mínimo (8GB recomendado)
- **CPU**: 2 cores mínimo (4 cores recomendado)
- **Disco**: 20GB mínimo (50GB recomendado)
- **Red**: Acceso a internet y redes objetivo

### Actualización del Sistema

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# o para versiones más nuevas
sudo dnf update -y
```

## 📦 Instalación de Dependencias

### Paso 1: Python y Herramientas Básicas

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv git curl wget nmap

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl wget nmap
# o
sudo dnf install -y python3 python3-pip git curl wget nmap
```

### Paso 2: John the Ripper (para cracking de hashes)

```bash
# Ubuntu/Debian
sudo apt install -y john

# CentOS/RHEL - Compilar desde fuente
cd /tmp
wget https://www.openwall.com/john/k/john-1.9.0-jumbo-1.tar.gz
tar xzf john-1.9.0-jumbo-1.tar.gz
cd john-1.9.0-jumbo-1/src
./configure && make
sudo make install
```

### Paso 3: Hashcat (opcional, para cracking avanzado)

```bash
# Ubuntu/Debian
sudo apt install -y hashcat

# CentOS/RHEL
sudo yum install -y hashcat
# o compilar desde fuente si no está disponible
```

### Paso 4: Nginx (para proxy reverso)

```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 🚀 Configuración del Proyecto

### Paso 1: Crear Usuario del Sistema

```bash
# Crear usuario dedicado para la aplicación
sudo useradd -m -s /bin/bash smartcam
sudo usermod -aG sudo smartcam

# Cambiar al usuario
sudo su - smartcam
```

### Paso 2: Clonar el Proyecto

```bash
# En el directorio home del usuario smartcam
cd /home/smartcam
git clone https://github.com/codexjm/-SmartCamAuditorPro.git
cd -SmartCamAuditorPro

# Alternativamente, si tienes el proyecto local
# scp -r /ruta/local/smartcam_auditor usuario@servidor:/home/smartcam/
```

### Paso 3: Configurar Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar Permisos

```bash
# Volver al usuario root temporalmente
sudo chown -R smartcam:smartcam /home/smartcam/-SmartCamAuditorPro
sudo chmod +x /home/smartcam/-SmartCamAuditorPro/main_auditor.py
sudo chmod +x /home/smartcam/-SmartCamAuditorPro/web_panel.py

# Crear directorios necesarios
mkdir -p logs reports scanner/cracking_results scanner/hashes
```

## 🔐 Configuración de Seguridad

### Paso 1: Configurar Firewall

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp  # Puerto de la aplicación (temporal)
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### Paso 2: Configurar Variables de Entorno

```bash
# Crear archivo de variables de entorno
sudo nano /etc/environment

# Agregar:
SMARTCAM_SECRET_KEY="tu_clave_secreta_muy_segura_aqui"
SMARTCAM_CONFIG_PATH="/home/smartcam/-SmartCamAuditorPro/config"
SMARTCAM_LOG_PATH="/home/smartcam/-SmartCamAuditorPro/logs"
```

### Paso 3: Configurar Sudoers para Nmap

```bash
# Permitir que el usuario smartcam ejecute nmap sin sudo
sudo visudo

# Agregar esta línea:
smartcam ALL=(ALL) NOPASSWD: /usr/bin/nmap
```

## ⚙️ Despliegue con Systemd

### Paso 1: Crear Servicio Systemd

```bash
sudo nano /etc/systemd/system/smartcam-auditor.service
```

Contenido del archivo:

```ini
[Unit]
Description=SmartCam Auditor Pro
After=network.target

[Service]
Type=simple
User=smartcam
Group=smartcam
WorkingDirectory=/home/smartcam/-SmartCamAuditorPro
Environment=PATH=/home/smartcam/-SmartCamAuditorPro/venv/bin
ExecStart=/home/smartcam/-SmartCamAuditorPro/venv/bin/python web_panel.py
Restart=always
RestartSec=10

# Configuración de logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=smartcam-auditor

# Configuración de seguridad
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### Paso 2: Habilitar e Iniciar el Servicio

```bash
# Recargar configuración de systemd
sudo systemctl daemon-reload

# Habilitar el servicio para inicio automático
sudo systemctl enable smartcam-auditor

# Iniciar el servicio
sudo systemctl start smartcam-auditor

# Verificar el estado
sudo systemctl status smartcam-auditor
```

## 🌐 Configuración de Nginx

### Paso 1: Crear Configuración de Nginx

```bash
sudo nano /etc/nginx/sites-available/smartcam-auditor
```

Contenido:

```nginx
server {
    listen 80;
    server_name tu_dominio.com;  # Cambiar por tu dominio o IP

    # Redirigir HTTP a HTTPS (opcional)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Para WebSockets (si se implementan en el futuro)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Configuración de logs
    access_log /var/log/nginx/smartcam-auditor.access.log;
    error_log /var/log/nginx/smartcam-auditor.error.log;

    # Configuración de seguridad
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

### Paso 2: Habilitar el Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/smartcam-auditor /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

### Paso 3: Configurar SSL (Opcional pero Recomendado)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu_dominio.com

# El certificado se renovará automáticamente
```

## 📊 Monitoreo y Logs

### Visualizar Logs en Tiempo Real

```bash
# Logs del servicio
sudo journalctl -u smartcam-auditor -f

# Logs de Nginx
sudo tail -f /var/log/nginx/smartcam-auditor.access.log
sudo tail -f /var/log/nginx/smartcam-auditor.error.log

# Logs de la aplicación
tail -f /home/smartcam/-SmartCamAuditorPro/logs/*.log
```

### Configurar Monitoreo con Logrotate

```bash
sudo nano /etc/logrotate.d/smartcam-auditor
```

Contenido:

```
/home/smartcam/-SmartCamAuditorPro/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 smartcam smartcam
    postrotate
        systemctl reload smartcam-auditor
    endscript
}
```

## 💾 Backup y Mantenimiento

### Script de Backup Automático

```bash
nano /home/smartcam/backup_smartcam.sh
```

Contenido:

```bash
#!/bin/bash
BACKUP_DIR="/backup/smartcam"
PROJECT_DIR="/home/smartcam/-SmartCamAuditorPro"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de configuración y logs
tar -czf $BACKUP_DIR/smartcam_backup_$DATE.tar.gz \
    $PROJECT_DIR/config \
    $PROJECT_DIR/logs \
    $PROJECT_DIR/reports

# Mantener solo los últimos 7 backups
find $BACKUP_DIR -name "smartcam_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completado: smartcam_backup_$DATE.tar.gz"
```

### Configurar Cron para Backups

```bash
crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * /home/smartcam/backup_smartcam.sh
```

## 🚀 Comandos de Control del Servicio

```bash
# Iniciar el servicio
sudo systemctl start smartcam-auditor

# Parar el servicio
sudo systemctl stop smartcam-auditor

# Reiniciar el servicio
sudo systemctl restart smartcam-auditor

# Ver estado del servicio
sudo systemctl status smartcam-auditor

# Ver logs en tiempo real
sudo journalctl -u smartcam-auditor -f

# Recargar configuración
sudo systemctl daemon-reload
```

## 🌍 Acceso a la Aplicación

Una vez desplegado, puedes acceder a:

- **Panel Web**: `http://tu_servidor_ip` o `http://tu_dominio.com`
- **CLI**: Conectarse por SSH y usar `python main_auditor.py`

## 🔍 Solución de Problemas

### Verificar que todo funciona:

```bash
# Verificar servicios
sudo systemctl status smartcam-auditor
sudo systemctl status nginx

# Verificar puertos
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :80

# Verificar logs
sudo journalctl -u smartcam-auditor --no-pager -l
```

### Problemas Comunes:

1. **Puerto 5000 en uso**: Cambiar el puerto en `web_panel.py`
2. **Permisos de Nmap**: Verificar configuración de sudoers
3. **Dependencias faltantes**: Reinstalar con `pip install -r requirements.txt`

---

¡Con esta guía tendrás SmartCam Auditor Pro funcionando profesionalmente en tu servidor! 🎉
