#!/bin/bash
# Script para instalar y configurar msmtp (alternativa ligera a Postfix)
# Servidor SMTP: 172.16.0.170:25 (sin autenticación)

echo "Instalando msmtp..."

# Instalar msmtp
sudo apt-get update
sudo apt-get install -y msmtp msmtp-mta

echo ""
echo "Configurando msmtp..."

# Crear directorio de configuración si no existe
sudo mkdir -p /etc/msmtp

# Crear archivo de configuración
sudo tee /etc/msmtprc > /dev/null << 'EOF'
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

# Dar permisos correctos
sudo chmod 600 /etc/msmtprc
sudo chown root:root /etc/msmtprc

# Crear configuración en el home del usuario (necesario para que funcione con mail)
# Obtener el usuario actual
USER_HOME=$(eval echo ~$SUDO_USER)
if [ -z "$USER_HOME" ] || [ "$USER_HOME" = "~$SUDO_USER" ]; then
    USER_HOME=$HOME
fi

# Crear archivo de configuración en el home del usuario
sudo tee "$USER_HOME/.msmtprc" > /dev/null << 'EOFUSER'
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
EOFUSER

# Dar permisos correctos al archivo del usuario
sudo chmod 600 "$USER_HOME/.msmtprc"
if [ -n "$SUDO_USER" ]; then
    sudo chown $SUDO_USER:$SUDO_USER "$USER_HOME/.msmtprc"
fi

# Crear directorio de log si no existe y dar permisos
sudo touch /var/log/msmtp.log
sudo chmod 666 /var/log/msmtp.log

# Crear link simbólico para que 'mail' use msmtp
sudo update-alternatives --install /usr/bin/sendmail sendmail /usr/bin/msmtp 1

echo "✓ msmtp configurado exitosamente"
echo ""
echo "Configuración creada en:"
echo "  - /etc/msmtprc (global, root)"
if [ -n "$USER_HOME" ]; then
    echo "  - $USER_HOME/.msmtprc (usuario)"
fi
echo ""
echo "Para probar el envío, ejecuta:"
echo "  echo 'Test de email' | mail -s 'Test' -r 'integracion_nimbi@uniacc.local' juan.silva@uniacc.cl"
echo ""
echo "Para ver los logs:"
echo "  sudo tail -f /var/log/msmtp.log"
echo ""
echo "NOTA: Si ejecutas el cron con otro usuario, necesitarás crear ~/.msmtprc para ese usuario también."

