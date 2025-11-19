# Configuración de Cron para Actualizaciones Diarias

Este documento explica cómo configurar un cron job para ejecutar automáticamente las actualizaciones diarias de datos.

## Prerrequisitos

1. Asegúrate de que el script `ejecutar_actualizaciones_diarias.sh` tenga permisos de ejecución:
```bash
chmod +x /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

2. Verifica que el entorno virtual esté configurado correctamente y que el script encuentre la ruta correcta.

## Opción 1: Editar Crontab Manualmente

1. Abre el crontab del usuario:
```bash
crontab -e
```

2. Agrega la siguiente línea para ejecutar las actualizaciones diariamente a las 2:00 AM:
```cron
0 2 * * * /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

3. O si prefieres ejecutarlo a las 3:00 AM:
```cron
0 3 * * * /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

## Opción 2: Usar el Script de Configuración

Puedes usar el script `configurar_cron.sh` que se incluye en este directorio.

## Formato de Crontab

El formato de cron es:
```
minuto hora día_mes mes día_semana comando
```

Ejemplos:
- `0 2 * * *` - Todos los días a las 2:00 AM
- `0 3 * * *` - Todos los días a las 3:00 AM
- `0 1 * * 1` - Todos los lunes a la 1:00 AM
- `30 2 * * *` - Todos los días a las 2:30 AM

## Verificar Configuración

Para ver tus cron jobs configurados:
```bash
crontab -l
```

## Ver Logs

Los logs se guardan en:
```
/home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/logs/actualizaciones_YYYYMMDD.log
```

Para ver el log del día actual:
```bash
tail -f /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/logs/actualizaciones_$(date +%Y%m%d).log
```

## Notas Importantes

1. **Entorno Virtual**: Asegúrate de que la variable `VENV_PATH` en el script bash apunte a la ubicación correcta de tu entorno virtual.

2. **Variables de Entorno**: El script usa el archivo `.env` del proyecto. Asegúrate de que esté configurado correctamente.

3. **Permisos**: El usuario que ejecuta el cron debe tener permisos para:
   - Leer el archivo `.env`
   - Ejecutar los scripts Python
   - Escribir en el directorio de logs
   - Conectarse a SQL Server y PostgreSQL

4. **Tiempo de Ejecución**: Algunos scripts (como `actualizar_encuesta_docente.py`) pueden tardar 10-20 minutos debido al alto volumen de datos.

5. **Notificaciones por Email**: El script puede enviar emails automáticamente con el resumen de ejecución. Ver sección "Configuración de Email" más abajo.

## Configuración de Email

El script puede enviar automáticamente un email con el resumen de ejecución al finalizar. Para configurarlo:

### Opción 1: Variables de Entorno en el Crontab

Agrega las variables de entorno directamente en el crontab:

```cron
EMAIL_RECIPIENTS="admin@example.com operaciones@example.com"
EMAIL_FROM="noreply@example.com"
0 2 * * * /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

### Opción 2: Variables de Entorno Globales

Agrega las variables al archivo `.env` del proyecto o al `.bashrc` del usuario:

```bash
export EMAIL_RECIPIENTS="juan.silva@uniacc.cl hans.vidal@uniacc.cl"
export EMAIL_FROM="integracion_nimbi@uniacc.local"
```

### Opción 3: Editar el Script Directamente

Edita el script `ejecutar_actualizaciones_diarias.sh` y modifica las líneas:

```bash
EMAIL_RECIPIENTS="admin@example.com operaciones@example.com"
EMAIL_FROM="noreply@example.com"
```

### Configuración del Servidor de Email

Para que funcione el envío de emails, necesitas:

1. **Instalar mailx** (si no está instalado):
   ```bash
   sudo apt-get install mailutils
   # o
   sudo yum install mailx
   ```

2. **Configurar el servidor SMTP** (opcional, según tu sistema):
   - El sistema usará el servidor SMTP configurado por defecto
   - Para configurar SMTP personalizado, edita `/etc/ssmtp/ssmtp.conf` o `/etc/mail.rc`

3. **Probar el envío de email**:
   ```bash
   echo "Test" | mail -s "Test" tu@email.com
   ```

### Contenido del Email

El email incluirá:
- Estado de la ejecución (exitoso o con errores)
- Resumen de scripts ejecutados (total, exitosos, fallidos)
- Tiempo total de ejecución
- Log completo de la ejecución

### Ejemplo de Asunto del Email

- **Exitoso**: `[Integración NIMBI] Actualizaciones Diarias - ✓ Completado Exitosamente`
- **Con Errores**: `[Integración NIMBI] Actualizaciones Diarias - ✗ Error en la Ejecución`

## Solución de Problemas

### El cron no se ejecuta
- Verifica que el servicio cron esté corriendo: `systemctl status cron` (o `systemctl status crond` en algunos sistemas)
- Revisa los logs del sistema: `grep CRON /var/log/syslog` (o `journalctl -u cron`)

### Permisos denegados
- Asegúrate de que el script tenga permisos de ejecución: `chmod +x ejecutar_actualizaciones_diarias.sh`
- Verifica que el usuario tenga acceso a los archivos necesarios

### El venv no se encuentra
- Edita el script `ejecutar_actualizaciones_diarias.sh` y ajusta la variable `VENV_PATH` con la ruta correcta

### Variables de entorno no cargadas
- El cron no tiene el mismo entorno que tu sesión de terminal
- Los scripts usan el archivo `.env`, asegúrate de que esté en la ubicación correcta

### Emails no se envían
- Verifica que `mail` o `mailx` estén instalados: `which mail` o `which mailx`
- Verifica que las variables `EMAIL_RECIPIENTS` estén configuradas correctamente
- Prueba enviar un email manualmente: `echo "test" | mail -s "test" tu@email.com`
- Revisa los logs del sistema para errores de email: `grep mail /var/log/syslog`
- Si usas SMTP externo, verifica la configuración en `/etc/ssmtp/ssmtp.conf`

