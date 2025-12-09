#!/bin/bash
# Script de diagnóstico para verificar por qué el cron no está funcionando

echo "========================================="
echo "DIAGNÓSTICO DE CRON"
echo "========================================="
echo ""

# Colores para salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que el servicio cron está corriendo
echo "1. Verificando servicio cron..."
if systemctl is-active --quiet cron || systemctl is-active --quiet crond; then
    echo -e "${GREEN}✓${NC} Servicio cron está corriendo"
else
    echo -e "${RED}✗${NC} Servicio cron NO está corriendo"
    echo "   Intenta: sudo systemctl start cron"
fi
echo ""

# 2. Verificar el crontab del usuario
echo "2. Verificando crontab del usuario actual ($USER)..."
if crontab -l > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Crontab encontrado:"
    echo "   ---"
    crontab -l | grep -v "^#" | grep -v "^$" || echo "   (Sin entradas activas)"
    echo "   ---"
else
    echo -e "${RED}✗${NC} No se encontró crontab para el usuario $USER"
    echo "   Verifica con: crontab -l"
fi
echo ""

# 3. Verificar permisos del script
SCRIPT_PATH="/home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh"
echo "3. Verificando script principal..."
if [ -f "$SCRIPT_PATH" ]; then
    echo -e "${GREEN}✓${NC} Script existe: $SCRIPT_PATH"
    
    # Verificar permisos
    if [ -x "$SCRIPT_PATH" ]; then
        echo -e "${GREEN}✓${NC} Script tiene permisos de ejecución"
    else
        echo -e "${YELLOW}⚠${NC} Script NO tiene permisos de ejecución"
        echo "   Ejecuta: chmod +x $SCRIPT_PATH"
    fi
    
    # Mostrar permisos
    ls -l "$SCRIPT_PATH"
else
    echo -e "${RED}✗${NC} Script NO existe: $SCRIPT_PATH"
fi
echo ""

# 4. Verificar entorno virtual
VENV_PATH="/home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/.venv-crm"
echo "4. Verificando entorno virtual..."
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}✓${NC} Entorno virtual encontrado: $VENV_PATH"
    
    if [ -f "$VENV_PATH/bin/activate" ]; then
        echo -e "${GREEN}✓${NC} Script de activación existe"
    else
        echo -e "${RED}✗${NC} Script de activación NO existe"
    fi
else
    echo -e "${YELLOW}⚠${NC} Entorno virtual NO encontrado en: $VENV_PATH"
    echo "   Buscando en otras ubicaciones..."
    if [ -d "/home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/.venv" ]; then
        echo -e "${GREEN}✓${NC} Encontrado en: /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/.venv"
    fi
fi
echo ""

# 5. Verificar logs del sistema (últimas ejecuciones de cron)
echo "5. Verificando logs del sistema cron..."
echo "   Últimas entradas de cron en syslog (últimas 10):"
echo "   ---"
if [ -f /var/log/syslog ]; then
    sudo grep CRON /var/log/syslog | tail -10 || echo "   No se encontraron entradas"
elif [ -f /var/log/messages ]; then
    sudo grep CRON /var/log/messages | tail -10 || echo "   No se encontraron entradas"
else
    echo "   Intentando con journalctl..."
    sudo journalctl -u cron -n 10 --no-pager 2>/dev/null || echo "   No se pudo acceder a los logs"
fi
echo "   ---"
echo ""

# 6. Verificar logs de ejecución del script
LOG_DIR="/home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/logs"
echo "6. Verificando logs de ejecución del script..."
if [ -d "$LOG_DIR" ]; then
    echo -e "${GREEN}✓${NC} Directorio de logs existe: $LOG_DIR"
    
    # Buscar el log más reciente
    LATEST_LOG=$(ls -t "$LOG_DIR"/actualizaciones_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "   Log más reciente: $(basename "$LATEST_LOG")"
        echo "   Tamaño: $(du -h "$LATEST_LOG" | cut -f1)"
        echo "   Última modificación: $(stat -c %y "$LATEST_LOG" | cut -d'.' -f1)"
        echo ""
        echo "   Últimas 5 líneas del log:"
        echo "   ---"
        tail -5 "$LATEST_LOG" | sed 's/^/   /'
        echo "   ---"
    else
        echo -e "${YELLOW}⚠${NC} No se encontraron logs de actualizaciones"
    fi
else
    echo -e "${RED}✗${NC} Directorio de logs NO existe: $LOG_DIR"
fi
echo ""

# 7. Verificar variables de entorno necesarias
echo "7. Verificando variables de entorno..."
echo "   PATH: $PATH"
echo "   HOME: $HOME"
echo "   USER: $USER"
echo "   SHELL: $SHELL"
echo ""

# 8. Intentar ejecutar el script manualmente (solo si se solicita)
if [ "$1" == "--test" ]; then
    echo "8. Ejecutando prueba del script (modo test)..."
    echo "   (Esto puede tardar un momento)"
    echo ""
    if [ -f "$SCRIPT_PATH" ]; then
        bash "$SCRIPT_PATH" 2>&1 | head -20
        echo "..."
        echo "   (Mostrando solo las primeras 20 líneas)"
    fi
    echo ""
fi

# 9. Resumen y recomendaciones
echo "========================================="
echo "RESUMEN Y RECOMENDACIONES"
echo "========================================="
echo ""
echo "Para ver más detalles, ejecuta:"
echo "  - Ver crontab: crontab -l"
echo "  - Ver logs del sistema: sudo tail -f /var/log/syslog | grep CRON"
echo "  - Ver logs del script: tail -f $LOG_DIR/actualizaciones_\$(date +%Y%m%d).log"
echo "  - Probar script manualmente: bash $SCRIPT_PATH"
echo ""
echo "Para verificar si cron intentó ejecutar algo hoy:"
echo "  sudo grep \"$USER\" /var/log/syslog | grep CRON | grep \"$(date +%b\ %d)\""
echo ""
echo "Para agregar logging adicional al crontab, usa:"
echo "  0 5 * * 1-5 $SCRIPT_PATH >> $LOG_DIR/cron.log 2>&1"
echo ""

