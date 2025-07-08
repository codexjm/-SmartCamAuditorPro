#!/bin/bash
#
# SmartCam Auditor Pro - Script de Despliegue Automático para Servidor
# Este script automatiza la instalación completa en un servidor Linux
#

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Variables de configuración
PROJECT_USER="smartcam"
PROJECT_DIR="/home/$PROJECT_USER/SmartCamAuditorPro"
SERVICE_NAME="smartcam-auditor"
DOMAIN=""  # Se solicitará al usuario

# Banner
echo -e "${BLUE}"
echo "=================================================="
echo "    SmartCam Auditor Pro - Auto Deploy Script"
echo "=================================================="
echo -e "${NC}"

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script debe ejecutarse como root (sudo)"
   exit 1
fi

# Detectar distribución
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    DISTRO=$ID
else
    print_error "No se puede detectar la distribución del sistema"
    exit 1
fi

print_status "Distribución detectada: $OS"

# Solicitar información al usuario
read -p "Ingresa el dominio o IP del servidor (ejemplo: ejemplo.com o 192.168.1.100): " DOMAIN
if [[ -z "$DOMAIN" ]]; then
    print_error "Debe especificar un dominio o IP"
    exit 1
fi

read -p "¿Instalar SSL con Let's Encrypt? (s/n): " INSTALL_SSL
read -p "¿Instalar Hashcat para cracking avanzado? (s/n): " INSTALL_HASHCAT

print_status "Iniciando instalación..."

# Función para instalar paquetes según la distribución
install_packages() {
    case $DISTRO in
        ubuntu|debian)
            apt update
            apt install -y python3 python3-pip python3-venv git curl wget nmap nginx john
            if [[ $INSTALL_HASHCAT == "s" || $INSTALL_HASHCAT == "S" ]]; then
                apt install -y hashcat
            fi
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf update -y
                dnf install -y python3 python3-pip git curl wget nmap nginx john
            else
                yum update -y
                yum install -y python3 python3-pip git curl wget nmap nginx john
            fi
            systemctl enable nginx
            systemctl start nginx
            ;;
        *)
            print_error "Distribución no soportada: $DISTRO"
            exit 1
            ;;
    esac
}

# Paso 1: Instalar paquetes del sistema
print_status "Instalando paquetes del sistema..."
install_packages
print_success "Paquetes del sistema instalados"

# Paso 2: Crear usuario del sistema
print_status "Creando usuario del sistema..."
if ! id "$PROJECT_USER" &>/dev/null; then
    useradd -m -s /bin/bash $PROJECT_USER
    usermod -aG sudo $PROJECT_USER
    print_success "Usuario $PROJECT_USER creado"
else
    print_warning "Usuario $PROJECT_USER ya existe"
fi

# Paso 3: Configurar proyecto
print_status "Configurando proyecto..."

# Crear directorio del proyecto si no existe
mkdir -p $PROJECT_DIR
chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR

# Ejecutar como usuario smartcam
sudo -u $PROJECT_USER bash << EOF
cd $PROJECT_DIR

# Clonar o copiar proyecto (aquí asumimos que ya está en el directorio)
if [ ! -f "main_auditor.py" ]; then
    echo "NOTA: Debe copiar manualmente los archivos del proyecto a $PROJECT_DIR"
    echo "O clonar desde: git clone https://github.com/codexjm/-SmartCamAuditorPro.git ."
fi

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias si existe requirements.txt
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Crear directorios necesarios
mkdir -p logs reports scanner/cracking_results scanner/hashes config

# Hacer scripts ejecutables
chmod +x *.py 2>/dev/null || true
EOF

print_success "Proyecto configurado"

# Paso 4: Configurar sudoers para nmap
print_status "Configurando permisos para nmap..."
echo "$PROJECT_USER ALL=(ALL) NOPASSWD: /usr/bin/nmap" >> /etc/sudoers.d/smartcam-nmap
print_success "Permisos de nmap configurados"

# Paso 5: Crear servicio systemd
print_status "Configurando servicio systemd..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=SmartCam Auditor Pro
After=network.target

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python web_panel.py
Restart=always
RestartSec=10

# Configuración de logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Configuración de seguridad
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE_NAME
print_success "Servicio systemd configurado"

# Paso 6: Configurar Nginx
print_status "Configurando Nginx..."
cat > /etc/nginx/sites-available/$SERVICE_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Para WebSockets
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Configuración de logs
    access_log /var/log/nginx/$SERVICE_NAME.access.log;
    error_log /var/log/nginx/$SERVICE_NAME.error.log;

    # Configuración de seguridad
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Habilitar sitio
ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
print_success "Nginx configurado"

# Paso 7: Configurar firewall
print_status "Configurando firewall..."
if command -v ufw &> /dev/null; then
    # Ubuntu/Debian
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    # CentOS/RHEL
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
fi
print_success "Firewall configurado"

# Paso 8: Instalar SSL si se solicitó
if [[ $INSTALL_SSL == "s" || $INSTALL_SSL == "S" ]]; then
    print_status "Instalando certificado SSL..."
    
    case $DISTRO in
        ubuntu|debian)
            apt install -y certbot python3-certbot-nginx
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y certbot python3-certbot-nginx
            else
                yum install -y certbot python3-certbot-nginx
            fi
            ;;
    esac
    
    # Obtener certificado
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    print_success "Certificado SSL configurado"
fi

# Paso 9: Crear script de backup
print_status "Configurando backup automático..."
cat > /home/$PROJECT_USER/backup_smartcam.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/smartcam"
PROJECT_DIR="/home/smartcam/SmartCamAuditorPro"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de configuración y logs
tar -czf $BACKUP_DIR/smartcam_backup_$DATE.tar.gz \
    $PROJECT_DIR/config \
    $PROJECT_DIR/logs \
    $PROJECT_DIR/reports \
    2>/dev/null || true

# Mantener solo los últimos 7 backups
find $BACKUP_DIR -name "smartcam_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true

echo "Backup completado: smartcam_backup_$DATE.tar.gz"
EOF

chmod +x /home/$PROJECT_USER/backup_smartcam.sh
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/backup_smartcam.sh

# Configurar cron para backup diario
(crontab -u $PROJECT_USER -l 2>/dev/null; echo "0 2 * * * /home/$PROJECT_USER/backup_smartcam.sh") | crontab -u $PROJECT_USER -
print_success "Backup automático configurado"

# Paso 10: Iniciar servicios
print_status "Iniciando servicios..."
systemctl start $SERVICE_NAME
sleep 3

# Verificar estado
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Servicio $SERVICE_NAME iniciado correctamente"
else
    print_error "Error al iniciar el servicio $SERVICE_NAME"
    systemctl status $SERVICE_NAME
fi

# Configurar logrotate
print_status "Configurando rotación de logs..."
cat > /etc/logrotate.d/$SERVICE_NAME << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $PROJECT_USER $PROJECT_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

print_success "Rotación de logs configurada"

# Resumen final
echo -e "\n${GREEN}=================================================="
echo "         ¡INSTALACIÓN COMPLETADA!"
echo "==================================================${NC}"
echo
echo -e "${BLUE}Información del despliegue:${NC}"
echo "• Usuario del sistema: $PROJECT_USER"
echo "• Directorio del proyecto: $PROJECT_DIR"
echo "• Servicio: $SERVICE_NAME"
echo "• URL de acceso: http://$DOMAIN"
if [[ $INSTALL_SSL == "s" || $INSTALL_SSL == "S" ]]; then
    echo "• URL segura: https://$DOMAIN"
fi
echo
echo -e "${BLUE}Comandos útiles:${NC}"
echo "• Ver estado: sudo systemctl status $SERVICE_NAME"
echo "• Ver logs: sudo journalctl -u $SERVICE_NAME -f"
echo "• Reiniciar: sudo systemctl restart $SERVICE_NAME"
echo "• Backup manual: sudo -u $PROJECT_USER /home/$PROJECT_USER/backup_smartcam.sh"
echo
echo -e "${YELLOW}IMPORTANTE:${NC}"
echo "• Asegúrate de copiar los archivos del proyecto a $PROJECT_DIR"
echo "• Configura las redes en $PROJECT_DIR/config/networks.txt"
echo "• Revisa la configuración en $PROJECT_DIR/config/config.json"
echo
print_success "¡SmartCam Auditor Pro está listo para usar!"
