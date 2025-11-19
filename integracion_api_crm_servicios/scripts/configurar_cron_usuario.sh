#!/bin/bash
# Script para configurar el cron job para el usuario cl159906175

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_SCRIPT="${SCRIPT_DIR}/ejecutar_actualizaciones_diarias.sh"
CRON_USER="cl159906175"
HORA=${1:-5}
DIAS_SEMANA=${2:-"1-5"}  # Por defecto: lunes a viernes (1=lunes, 5=viernes)

# Validar que la hora sea un número entre 0 y 23
if ! [[ "$HORA" =~ ^[0-9]+$ ]] || [ "$HORA" -lt 0 ] || [ "$HORA" -gt 23 ]; then
    echo "ERROR: La hora debe ser un número entre 0 y 23"
    exit 1
fi

# Validar días de la semana (0-7, donde 0 y 7 = domingo)
# Formatos aceptados: 1-5, 1,2,3, 0-6, etc.
if ! [[ "$DIAS_SEMANA" =~ ^[0-7,-]+$ ]]; then
    echo "ERROR: Formato de días de la semana inválido"
    echo "  Ejemplos válidos: 1-5 (lun-vie), 0-6 (dom-sab), 1,3,5 (lun,mié,vie)"
    exit 1
fi

# Verificar que el script existe
if [ ! -f "$CRON_SCRIPT" ]; then
    echo "ERROR: No se encuentra el script: $CRON_SCRIPT"
    exit 1
fi

# Dar permisos de ejecución al script si no los tiene
if [ ! -x "$CRON_SCRIPT" ]; then
    echo "Otorgando permisos de ejecución al script..."
    chmod +x "$CRON_SCRIPT"
fi

# Verificar que el usuario existe
if ! id "$CRON_USER" &>/dev/null; then
    echo "ERROR: El usuario $CRON_USER no existe"
    exit 1
fi

# Crear la entrada de cron
# Formato: minuto hora día_mes mes día_semana comando
CRON_ENTRY="0 ${HORA} * * ${DIAS_SEMANA} ${CRON_SCRIPT}"

echo "Configurando cron job para el usuario: $CRON_USER"
echo "Hora de ejecución: ${HORA}:00"
echo "Días de la semana: ${DIAS_SEMANA}"
echo "  (0=domingo, 1=lunes, 2=martes, 3=miércoles, 4=jueves, 5=viernes, 6=sábado, 7=domingo)"
echo "Script: $CRON_SCRIPT"
echo ""

# Verificar si ya existe una entrada similar
# Crear archivo temporal en un lugar accesible
CRON_TEMP=$(mktemp /tmp/crontab_${CRON_USER}_XXXXXX 2>/dev/null || echo "/tmp/crontab_${CRON_USER}_$$")
sudo -u "$CRON_USER" crontab -l 2>/dev/null > "$CRON_TEMP" 2>/dev/null || touch "$CRON_TEMP"
sudo chown "$CRON_USER:$CRON_USER" "$CRON_TEMP" 2>/dev/null || true

# Buscar si ya existe una entrada para este script
if grep -q "$CRON_SCRIPT" "$CRON_TEMP"; then
    echo "⚠ Ya existe una entrada de cron para este script."
    echo ""
    echo "Entrada actual:"
    grep "$CRON_SCRIPT" "$CRON_TEMP"
    echo ""
    read -p "¿Deseas reemplazarla? (s/n): " respuesta
    if [ "$respuesta" != "s" ] && [ "$respuesta" != "S" ]; then
        echo "Operación cancelada."
        rm "$CRON_TEMP"
        exit 0
    fi
    # Eliminar la entrada antigua
    grep -v "$CRON_SCRIPT" "$CRON_TEMP" > "${CRON_TEMP}.new"
    mv "${CRON_TEMP}.new" "$CRON_TEMP"
fi

# Agregar la nueva entrada
echo "$CRON_ENTRY" >> "$CRON_TEMP"

# Instalar el nuevo crontab para el usuario
sudo -u "$CRON_USER" crontab "$CRON_TEMP"
EXIT_CODE=$?
rm -f "$CRON_TEMP"

if [ $EXIT_CODE -ne 0 ]; then
    echo "✗ Error al instalar el crontab. Intentando método alternativo..."
    # Método alternativo: crear archivo directamente
    CRON_TEMP_ALT="/tmp/crontab_${CRON_USER}_alt_$$"
    sudo -u "$CRON_USER" crontab -l 2>/dev/null > "$CRON_TEMP_ALT" 2>/dev/null || true
    grep -v "$CRON_SCRIPT" "$CRON_TEMP_ALT" 2>/dev/null > "${CRON_TEMP_ALT}.new" || true
    echo "$CRON_ENTRY" >> "${CRON_TEMP_ALT}.new"
    sudo -u "$CRON_USER" crontab "${CRON_TEMP_ALT}.new"
    rm -f "$CRON_TEMP_ALT" "${CRON_TEMP_ALT}.new"
fi

# Verificar que el usuario tiene configuración de msmtp
if [ ! -f "/home/${CRON_USER}/.msmtprc" ]; then
    echo ""
    echo "⚠ ADVERTENCIA: No se encuentra ~/.msmtprc para el usuario $CRON_USER"
    echo "  Los emails no se enviarán correctamente."
    echo ""
    read -p "¿Deseas crear la configuración de msmtp para este usuario? (s/n): " crear_msmtp
    if [ "$crear_msmtp" = "s" ] || [ "$crear_msmtp" = "S" ]; then
        # Crear configuración de msmtp
        sudo tee "/home/${CRON_USER}/.msmtprc" > /dev/null << 'EOF'
# Configuración global de msmtp
defaults
# Sin autenticación
auth           off
# Sin TLS
tls            off
# Logs
logfile        /var/log/msmtp.log

# Cuenta SMTP
account        uniacc
host           172.16.0.170
port           25
from           integracion_nimbi@uniacc.local
protocol       smtp

# Usar esta cuenta por defecto
account default : uniacc
EOF
        sudo chmod 600 "/home/${CRON_USER}/.msmtprc"
        sudo chown ${CRON_USER}:${CRON_USER} "/home/${CRON_USER}/.msmtprc"
        echo "✓ Configuración de msmtp creada para $CRON_USER"
    fi
fi

echo ""
echo "✓ Cron job configurado exitosamente para el usuario: $CRON_USER"
echo ""
echo "Configuración:"
echo "  Usuario: $CRON_USER"
echo "  Hora de ejecución: ${HORA}:00"
echo "  Días de la semana: ${DIAS_SEMANA} (lunes a viernes)"
echo "  Script: $CRON_SCRIPT"
echo ""
echo "Para ver los cron jobs del usuario:"
echo "  sudo -u $CRON_USER crontab -l"
echo ""
echo "Para editar manualmente:"
echo "  sudo -u $CRON_USER crontab -e"
echo ""
echo "Los logs se guardarán en:"
echo "  ${SCRIPT_DIR}/logs/actualizaciones_YYYYMMDD.log"
echo ""

