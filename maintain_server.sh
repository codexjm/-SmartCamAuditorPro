#!/bin/bash
#
# SmartCam Auditor Pro - Script de Mantenimiento del Servidor
# Script para administrar y mantener la instalación
#

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_USER="smartcam"
PROJECT_DIR="/home/$PROJECT_USER/SmartCamAuditorPro"
SERVICE_NAME="smartcam-auditor"

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

show_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    SmartCam Auditor Pro - Maintenance Script"
    echo "=================================================="
    echo -e "${NC}"
}

show_status() {
    echo -e "\n${BLUE}=== ESTADO DEL SISTEMA ===${NC}"
    
    # Estado del servicio
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Servicio $SERVICE_NAME: ACTIVO"
    else
        print_error "Servicio $SERVICE_NAME: INACTIVO"
    fi
    
    # Estado de Nginx
    if systemctl is-active --quiet nginx; then
        print_success "Nginx: ACTIVO"
    else
        print_error "Nginx: INACTIVO"
    fi
    
    # Uso de disco
    echo -e "\n${BLUE}Uso de disco:${NC}"
    df -h $PROJECT_DIR
    
    # Memoria
    echo -e "\n${BLUE}Uso de memoria:${NC}"
    free -h
    
    # Últimos logs
    echo -e "\n${BLUE}Últimos 5 logs del servicio:${NC}"
    journalctl -u $SERVICE_NAME -n 5 --no-pager
    
    # Archivos de log
    echo -e "\n${BLUE}Archivos de log:${NC}"
    ls -lah $PROJECT_DIR/logs/ 2>/dev/null || echo "No hay archivos de log"
}

start_service() {
    print_status "Iniciando servicio $SERVICE_NAME..."
    systemctl start $SERVICE_NAME
    sleep 2
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Servicio iniciado correctamente"
    else
        print_error "Error al iniciar el servicio"
        systemctl status $SERVICE_NAME
    fi
}

stop_service() {
    print_status "Deteniendo servicio $SERVICE_NAME..."
    systemctl stop $SERVICE_NAME
    print_success "Servicio detenido"
}

restart_service() {
    print_status "Reiniciando servicio $SERVICE_NAME..."
    systemctl restart $SERVICE_NAME
    sleep 2
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Servicio reiniciado correctamente"
    else
        print_error "Error al reiniciar el servicio"
        systemctl status $SERVICE_NAME
    fi
}

update_project() {
    print_status "Actualizando proyecto..."
    
    # Detener servicio
    systemctl stop $SERVICE_NAME
    
    # Actualizar código
    sudo -u $PROJECT_USER bash << 'EOF'
cd /home/smartcam/SmartCamAuditorPro
git pull origin main 2>/dev/null || echo "No se pudo actualizar desde Git"

# Actualizar dependencias
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF
    
    # Reiniciar servicio
    systemctl start $SERVICE_NAME
    print_success "Proyecto actualizado"
}

backup_now() {
    print_status "Ejecutando backup manual..."
    sudo -u $PROJECT_USER /home/$PROJECT_USER/backup_smartcam.sh
    print_success "Backup completado"
}

clean_logs() {
    read -p "¿Eliminar logs antiguos? (s/n): " confirm
    if [[ $confirm == "s" || $confirm == "S" ]]; then
        print_status "Limpiando logs antiguos..."
        
        # Limpiar logs de la aplicación (más de 30 días)
        find $PROJECT_DIR/logs -name "*.log" -mtime +30 -delete 2>/dev/null || true
        
        # Limpiar logs del journal (más de 30 días)
        journalctl --vacuum-time=30d
        
        print_success "Logs limpiados"
    fi
}

show_logs() {
    echo -e "\n${BLUE}=== LOGS DISPONIBLES ===${NC}"
    echo "1. Ver logs del servicio en tiempo real"
    echo "2. Ver logs de Nginx"
    echo "3. Ver logs de la aplicación"
    echo "4. Ver logs de errores"
    echo "5. Volver al menú principal"
    
    read -p "Selecciona una opción: " log_option
    
    case $log_option in
        1)
            print_status "Presiona Ctrl+C para salir"
            journalctl -u $SERVICE_NAME -f
            ;;
        2)
            print_status "Logs de Nginx:"
            tail -n 50 /var/log/nginx/$SERVICE_NAME.access.log 2>/dev/null || echo "No hay logs de Nginx"
            ;;
        3)
            print_status "Logs de la aplicación:"
            tail -n 50 $PROJECT_DIR/logs/*.log 2>/dev/null || echo "No hay logs de aplicación"
            ;;
        4)
            print_status "Logs de errores:"
            journalctl -u $SERVICE_NAME -p err --no-pager
            ;;
        5)
            return
            ;;
        *)
            print_error "Opción inválida"
            ;;
    esac
}

monitor_system() {
    print_status "Presiona Ctrl+C para salir del monitor"
    
    while true; do
        clear
        show_banner
        show_status
        sleep 5
    done
}

configure_system() {
    echo -e "\n${BLUE}=== CONFIGURACIÓN DEL SISTEMA ===${NC}"
    echo "1. Editar configuración de la aplicación"
    echo "2. Editar redes objetivo"
    echo "3. Ver configuración actual"
    echo "4. Reiniciar servicios"
    echo "5. Volver al menú principal"
    
    read -p "Selecciona una opción: " config_option
    
    case $config_option in
        1)
            nano $PROJECT_DIR/config/config.json
            ;;
        2)
            nano $PROJECT_DIR/config/networks.txt
            ;;
        3)
            echo -e "\n${BLUE}Configuración actual:${NC}"
            cat $PROJECT_DIR/config/config.json 2>/dev/null || echo "No hay archivo de configuración"
            echo -e "\n${BLUE}Redes objetivo:${NC}"
            cat $PROJECT_DIR/config/networks.txt 2>/dev/null || echo "No hay archivo de redes"
            ;;
        4)
            restart_service
            systemctl reload nginx
            ;;
        5)
            return
            ;;
        *)
            print_error "Opción inválida"
            ;;
    esac
}

security_check() {
    echo -e "\n${BLUE}=== VERIFICACIÓN DE SEGURIDAD ===${NC}"
    
    # Verificar permisos
    print_status "Verificando permisos de archivos..."
    ls -la $PROJECT_DIR/config/ 2>/dev/null
    
    # Verificar firewall
    print_status "Estado del firewall:"
    if command -v ufw &> /dev/null; then
        ufw status
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --list-all
    else
        print_warning "No se detectó firewall configurado"
    fi
    
    # Verificar certificado SSL
    print_status "Verificando certificado SSL:"
    certbot certificates 2>/dev/null || print_warning "No se encontraron certificados SSL"
    
    # Verificar actualizaciones del sistema
    print_status "Verificando actualizaciones disponibles:"
    if command -v apt &> /dev/null; then
        apt list --upgradable 2>/dev/null | head -10
    elif command -v yum &> /dev/null; then
        yum check-update | head -10
    fi
}

show_menu() {
    echo -e "\n${BLUE}=== MENÚ PRINCIPAL ===${NC}"
    echo "1.  Ver estado del sistema"
    echo "2.  Iniciar servicio"
    echo "3.  Detener servicio"
    echo "4.  Reiniciar servicio"
    echo "5.  Ver logs"
    echo "6.  Monitor en tiempo real"
    echo "7.  Actualizar proyecto"
    echo "8.  Hacer backup"
    echo "9.  Limpiar logs antiguos"
    echo "10. Configurar sistema"
    echo "11. Verificación de seguridad"
    echo "12. Salir"
    echo
    read -p "Selecciona una opción (1-12): " choice
}

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script debe ejecutarse como root (sudo)"
   exit 1
fi

# Menú principal
show_banner

while true; do
    show_menu
    
    case $choice in
        1)
            show_status
            ;;
        2)
            start_service
            ;;
        3)
            stop_service
            ;;
        4)
            restart_service
            ;;
        5)
            show_logs
            ;;
        6)
            monitor_system
            ;;
        7)
            update_project
            ;;
        8)
            backup_now
            ;;
        9)
            clean_logs
            ;;
        10)
            configure_system
            ;;
        11)
            security_check
            ;;
        12)
            print_status "Saliendo..."
            exit 0
            ;;
        *)
            print_error "Opción inválida. Por favor selecciona un número del 1 al 12."
            ;;
    esac
    
    echo
    read -p "Presiona Enter para continuar..."
done
