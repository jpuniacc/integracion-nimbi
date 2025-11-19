#!/bin/bash
# Script para verificar la configuración del chroot jail del SFTP

echo "========================================="
echo "VERIFICACIÓN DE CONFIGURACIÓN SFTP CHROOT"
echo "========================================="
echo ""

# 1. Verificar configuración de SSH/SFTP
echo "1. Verificando configuración de SSH/SFTP (sshd_config)..."
echo "   Buscando configuración de chroot para usuario 'nimbi':"
echo ""
sudo grep -i "nimbi" /etc/ssh/sshd_config | grep -v "^#" || echo "   No se encontró configuración específica para 'nimbi'"
echo ""

# 2. Verificar configuración Match para SFTP
echo "2. Verificando configuración Match para SFTP..."
echo ""
sudo grep -A 10 "Match" /etc/ssh/sshd_config | grep -v "^#" || echo "   No se encontró configuración Match"
echo ""

# 3. Verificar directorio home del usuario nimbi
echo "3. Verificando directorio home del usuario 'nimbi'..."
echo ""
if id nimbi &>/dev/null; then
    echo "   Usuario existe:"
    echo "   - UID: $(id -u nimbi)"
    echo "   - GID: $(id -g nimbi)"
    echo "   - Home: $(getent passwd nimbi | cut -d: -f6)"
    echo "   - Shell: $(getent passwd nimbi | cut -d: -f7)"
else
    echo "   ⚠ Usuario 'nimbi' no existe"
fi
echo ""

# 4. Verificar permisos del directorio /sftp/nimbi
echo "4. Verificando permisos del directorio /sftp/nimbi..."
echo ""
if [ -d "/sftp/nimbi" ]; then
    echo "   Directorio existe:"
    ls -ld /sftp/nimbi
    echo ""
    echo "   Contenido del directorio:"
    ls -la /sftp/nimbi | head -10
else
    echo "   ⚠ Directorio /sftp/nimbi no existe"
fi
echo ""

# 5. Verificar estructura de directorios SFTP
echo "5. Verificando estructura de directorios SFTP..."
echo ""
if [ -d "/sftp" ]; then
    echo "   Estructura de /sftp:"
    ls -la /sftp/
    echo ""
    if [ -d "/sftp/nimbi" ]; then
        echo "   Propietario y permisos de /sftp/nimbi:"
        stat -c "   %n: Owner=%U(%u) Group=%G(%g) Perms=%a" /sftp/nimbi
    fi
else
    echo "   ⚠ Directorio /sftp no existe"
fi
echo ""

# 6. Verificar configuración de chroot específica
echo "6. Verificando configuración de chroot en sshd_config..."
echo ""
echo "   Buscando 'ChrootDirectory':"
sudo grep -i "ChrootDirectory" /etc/ssh/sshd_config | grep -v "^#"
echo ""
echo "   Buscando 'ForceCommand internal-sftp':"
sudo grep -i "ForceCommand" /etc/ssh/sshd_config | grep -v "^#"
echo ""

# 7. Verificar desde la perspectiva del usuario (si es posible)
echo "7. Información adicional..."
echo ""
echo "   Procesos SSH/SFTP activos:"
ps aux | grep -E "sshd.*nimbi|sftp.*nimbi" | grep -v grep || echo "   No hay procesos activos"
echo ""

# 8. Verificar logs recientes de SFTP
echo "8. Verificando logs recientes de SFTP (últimas 10 líneas)..."
echo ""
if [ -f "/var/log/auth.log" ]; then
    sudo tail -10 /var/log/auth.log | grep -i "nimbi\|sftp" || echo "   No hay entradas recientes"
elif [ -f "/var/log/secure" ]; then
    sudo tail -10 /var/log/secure | grep -i "nimbi\|sftp" || echo "   No hay entradas recientes"
else
    echo "   No se encontraron archivos de log estándar"
fi
echo ""

echo "========================================="
echo "VERIFICACIÓN COMPLETADA"
echo "========================================="
echo ""
echo "NOTAS:"
echo "- Si el usuario está en chroot jail, el directorio home debe ser /sftp/nimbi"
echo "- El directorio /sftp/nimbi debe ser propiedad de root, no del usuario nimbi"
echo "- El usuario nimbi debe tener permisos de escritura en /sftp/nimbi"
echo "- La configuración típica es: ChrootDirectory /sftp/nimbi"

