#!/bin/bash
# Script para ejecutar todas las actualizaciones diarias desde SQL Server y API a PostgreSQL
# Este script activa el entorno virtual y ejecuta todos los scripts de actualización

# =============================================================================
# CONFIGURACIÓN - AJUSTA ESTAS RUTAS SEGÚN TU ENTORNO
# =============================================================================

# Ruta base del proyecto
PROJECT_ROOT="/home/cl159906175/integracion_nimbi/integracion_api_crm_servicios"

# Ruta del entorno virtual (ajusta según tu configuración)
# Opciones comunes:
# - Si está en el proyecto: "${PROJECT_ROOT}/.venv" o "${PROJECT_ROOT}/venv"
# - Si está en el home: "${HOME}/venv" o "${HOME}/.venv"
# - Si está en otro lugar, especifica la ruta completa
VENV_PATH="${PROJECT_ROOT}/.venv-crm"

# Si el venv no está en el proyecto, intenta buscar en ubicaciones comunes
if [ ! -d "$VENV_PATH" ]; then
    # Intenta otras ubicaciones comunes
    if [ -d "${PROJECT_ROOT}/.venv-crm" ]; then
        VENV_PATH="${PROJECT_ROOT}/.venv-crm"
    elif [ -d "${HOME}/.venv" ]; then
        VENV_PATH="${HOME}/.venv-crm"
    elif [ -d "${HOME}/venv-crm" ]; then
        VENV_PATH="${HOME}/venv-crm"
    fi
fi

# Directorio de scripts
SCRIPTS_DIR="${PROJECT_ROOT}/scripts"

# Archivo de log
LOG_DIR="${SCRIPTS_DIR}/logs"
LOG_FILE="${LOG_DIR}/actualizaciones_$(date +%Y%m%d).log"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Configuración de email
# Agrega las direcciones de email separadas por espacios
# Ejemplo: EMAIL_RECIPIENTS="admin@example.com operaciones@example.com"
EMAIL_RECIPIENTS="${EMAIL_RECIPIENTS:-juan.silva@uniacc.cl hans.vidal@uniacc.cl}"
# Asunto del email (se completará automáticamente con el estado)
EMAIL_SUBJECT_PREFIX="[Integración NIMBI] Actualizaciones Diarias"
# Remitente del email (opcional, dejar vacío para usar el default del sistema)
EMAIL_FROM="${EMAIL_FROM:-integracion_nimbi@uniacc.local}"

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

log() {
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

enviar_email() {
    local estado=$1
    local asunto=""
    local cuerpo=""
    local fecha_yyyymmdd=$(date +%Y%m%d)
    
    # Determinar el asunto según el estado (incluye fecha en formato yyyymmdd)
    if [ "$estado" = "exitoso" ]; then
        asunto="${EMAIL_SUBJECT_PREFIX} ${fecha_yyyymmdd} - ✓ Completado Exitosamente"
    else
        asunto="${EMAIL_SUBJECT_PREFIX} ${fecha_yyyymmdd} - ✗ Error en la Ejecución"
    fi
    
    # Leer el log completo para el cuerpo del email
    local log_content=$(cat "$LOG_FILE" 2>/dev/null || echo "No se pudo leer el archivo de log")
    
    # Construir el cuerpo del email con el resumen
    cuerpo="RESUMEN DE EJECUCIÓN DE ACTUALIZACIONES DIARIAS
==========================================

Fecha de ejecución: $(date '+%Y-%m-%d %H:%M:%S')

Estado: ${estado}

Total de scripts ejecutados: ${total_scripts}
Scripts exitosos: ${scripts_exitosos}
Scripts fallidos: ${scripts_fallidos}
Tiempo total de ejecución: ${MINUTOS} minutos y ${SEGUNDOS} segundos

==========================================
LOG COMPLETO:
==========================================

${log_content}

==========================================
Este es un mensaje automático generado por el sistema de actualizaciones diarias.
"
    
    # Verificar si hay destinatarios configurados
    if [ -z "$EMAIL_RECIPIENTS" ]; then
        log "⚠ No hay destinatarios de email configurados. Saltando envío de email."
        return 0
    fi
    
    # Verificar si existe el comando mail
    if ! command -v mail &> /dev/null && ! command -v mailx &> /dev/null; then
        log "⚠ No se encuentra el comando 'mail' o 'mailx'. No se puede enviar email."
        log "  Instala mailx con: sudo apt-get install mailutils (o mailx según tu distribución)"
        return 1
    fi
    
    # Determinar qué comando usar
    local mail_cmd=""
    if command -v mail &> /dev/null; then
        mail_cmd="mail"
    elif command -v mailx &> /dev/null; then
        mail_cmd="mailx"
    fi
    
    log "Enviando email de notificación a: $EMAIL_RECIPIENTS"
    
    # Enviar email a cada destinatario
    for recipient in $EMAIL_RECIPIENTS; do
        if [ -n "$EMAIL_FROM" ]; then
            echo "$cuerpo" | $mail_cmd -s "$asunto" -r "$EMAIL_FROM" "$recipient" 2>&1 | tee -a "$LOG_FILE"
        else
            echo "$cuerpo" | $mail_cmd -s "$asunto" "$recipient" 2>&1 | tee -a "$LOG_FILE"
        fi
        
        if [ $? -eq 0 ]; then
            log "✓ Email enviado exitosamente a: $recipient"
        else
            log "✗ Error al enviar email a: $recipient"
        fi
    done
}

ejecutar_script() {
    local script_name=$1
    local script_path="${SCRIPTS_DIR}/${script_name}"
    
    log "=========================================="
    log "Ejecutando: $script_name"
    log "=========================================="
    
    if [ ! -f "$script_path" ]; then
        log "ERROR: No se encuentra el script: $script_path"
        return 1
    fi
    
    # Ejecutar el script con Python del venv y mostrar salida en tiempo real
    # tee -a muestra la salida en la terminal Y la guarda en el log
    echo "" | tee -a "$LOG_FILE"
    "$VENV_PATH/bin/python" "$script_path" 2>&1 | tee -a "$LOG_FILE"
    local exit_code=${PIPESTATUS[0]}
    
    echo "" | tee -a "$LOG_FILE"
    
    if [ $exit_code -eq 0 ]; then
        log "✓ $script_name completado exitosamente"
    else
        log "✗ $script_name falló con código de salida: $exit_code"
    fi
    
    log ""
    return $exit_code
}

# =============================================================================
# VERIFICACIONES INICIALES
# =============================================================================

log "=========================================="
log "INICIO DE ACTUALIZACIONES DIARIAS"
log "=========================================="
log "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
log ""

# Verificar que existe el venv
if [ ! -d "$VENV_PATH" ]; then
    log "ERROR: No se encuentra el entorno virtual en: $VENV_PATH"
    log "Por favor, ajusta la variable VENV_PATH en este script"
    exit 1
fi

# Verificar que existe el script de activación
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    log "ERROR: No se encuentra el script de activación en: $VENV_PATH/bin/activate"
    log "Verifica que el entorno virtual esté correctamente configurado"
    exit 1
fi

log "✓ Entorno virtual encontrado: $VENV_PATH"
log "✓ Directorio de scripts: $SCRIPTS_DIR"
log "✓ Archivo de log: $LOG_FILE"
log ""

# Guardar tiempo de inicio
INICIO_TIEMPO=$(date +%s)

# =============================================================================
# EJECUTAR SCRIPTS
# =============================================================================

# Contadores para el resumen final
total_scripts=0
scripts_exitosos=0
scripts_fallidos=0

# Lista de scripts a ejecutar en orden
# Nota: actualizar_solicitudes_crm.py usa API, los demás usan SQL Server
SCRIPTS=(
    "actualizar_datos_identificadores_y_data_operacional.py"
    "actualizar_datos_academicos.py"
    "actualizar_notas_y_asistencia.py"
    "actualizar_beneficios_alumnos.py"
    "actualizar_datos_moodle_operacional.py"
    "actualizar_datos_sies.py"
    "actualizar_encuesta_docente.py"
    "actualizar_informe_finanzas.py"
    "actualizar_solicitudes_crm.py"
)

# Ejecutar cada script
for script in "${SCRIPTS[@]}"; do
    total_scripts=$((total_scripts + 1))
    ejecutar_script "$script"
    if [ $? -eq 0 ]; then
        scripts_exitosos=$((scripts_exitosos + 1))
    else
        scripts_fallidos=$((scripts_fallidos + 1))
    fi
    
    # Pequeña pausa entre scripts para evitar sobrecarga
    sleep 2
done

# =============================================================================
# RESUMEN FINAL
# =============================================================================

# Calcular tiempo total transcurrido
FIN_TIEMPO=$(date +%s)
TIEMPO_TOTAL=$((FIN_TIEMPO - INICIO_TIEMPO))
MINUTOS=$((TIEMPO_TOTAL / 60))
SEGUNDOS=$((TIEMPO_TOTAL % 60))

log "=========================================="
log "RESUMEN FINAL"
log "=========================================="
log "Total de scripts ejecutados: $total_scripts"
log "Scripts exitosos: $scripts_exitosos"
log "Scripts fallidos: $scripts_fallidos"
log "Tiempo total de ejecución: ${MINUTOS} minutos y ${SEGUNDOS} segundos"
log "Fecha de finalización: $(date '+%Y-%m-%d %H:%M:%S')"
log "=========================================="

# Enviar email de notificación
if [ $scripts_fallidos -gt 0 ]; then
    log ""
    enviar_email "error"
    log "⚠ ADVERTENCIA: Algunos scripts fallaron. Revisa los logs para más detalles."
    exit 1
else
    log ""
    enviar_email "exitoso"
    log "✓ Todas las actualizaciones completadas exitosamente"
    exit 0
fi

