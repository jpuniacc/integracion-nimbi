# Guía del Crontab

## Formato del Crontab

El formato básico de una línea de crontab es:

```
minuto hora día_mes mes día_semana comando
```

### Campos

| Campo | Rango | Descripción |
|-------|-------|-------------|
| **minuto** | 0-59 | Minuto de la hora |
| **hora** | 0-23 | Hora del día (0 = medianoche) |
| **día_mes** | 1-31 | Día del mes |
| **mes** | 1-12 | Mes del año |
| **día_semana** | 0-7 | Día de la semana (0 y 7 = domingo, 1 = lunes, etc.) |

### Días de la Semana

- `0` o `7` = Domingo
- `1` = Lunes
- `2` = Martes
- `3` = Miércoles
- `4` = Jueves
- `5` = Viernes
- `6` = Sábado

## Tu Configuración Actual

```cron
0 5 * * 1-5 /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

**Explicación:**
- `0` = Minuto 0 (en punto)
- `5` = Hora 5 (5 AM)
- `*` = Todos los días del mes
- `*` = Todos los meses
- `1-5` = Lunes a viernes
- Luego va el comando a ejecutar

## Ejemplos de Configuración

### Ejecutar todos los días a las 2 AM
```cron
0 2 * * * /ruta/al/script.sh
```

### Ejecutar solo lunes a las 5 AM
```cron
0 5 * * 1 /ruta/al/script.sh
```

### Ejecutar lunes, miércoles y viernes a las 3 AM
```cron
0 3 * * 1,3,5 /ruta/al/script.sh
```

### Ejecutar cada 15 minutos
```cron
*/15 * * * * /ruta/al/script.sh
```

### Ejecutar cada hora
```cron
0 * * * * /ruta/al/script.sh
```

### Ejecutar cada día laboral (lunes a viernes) a las 5 AM
```cron
0 5 * * 1-5 /ruta/al/script.sh
```

### Ejecutar solo los fines de semana (sábado y domingo) a las 6 AM
```cron
0 6 * * 0,6 /ruta/al/script.sh
```

## Comandos para Trabajar con Crontab

### Ver el crontab actual
```bash
sudo -u cl159906175 crontab -l
```

### Editar el crontab
```bash
sudo -u cl159906175 crontab -e
```

### Eliminar todo el crontab
```bash
sudo -u cl159906175 crontab -r
```

### Instalar un crontab desde un archivo
```bash
sudo -u cl159906175 crontab /ruta/al/archivo.txt
```

### Agregar una línea específica
```bash
# Método 1: Usando echo y pipe
echo "0 5 * * 1-5 /ruta/al/script.sh" | sudo -u cl159906175 crontab -

# Método 2: Agregar a lo existente
(crontab -l 2>/dev/null; echo "0 5 * * 1-5 /ruta/al/script.sh") | sudo -u cl159906175 crontab -
```

## Variables de Entorno en Crontab

Puedes agregar variables de entorno al inicio del crontab:

```cron
PATH=/usr/local/bin:/usr/bin:/bin
SHELL=/bin/bash
HOME=/home/cl159906175

0 5 * * 1-5 /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

## Redirección de Salida y Errores

Puedes redirigir la salida y errores a archivos:

```cron
# Redirigir salida a un archivo
0 5 * * 1-5 /ruta/al/script.sh >> /ruta/al/log.log 2>&1

# Redirigir salida y errores a archivos separados
0 5 * * 1-5 /ruta/al/script.sh >> /ruta/al/output.log 2>> /ruta/al/error.log

# Descartar salida (solo errores)
0 5 * * 1-5 /ruta/al/script.sh > /dev/null 2>&1
```

## Comentarios en Crontab

Puedes agregar comentarios con `#`:

```cron
# Actualizaciones diarias de lunes a viernes a las 5 AM
0 5 * * 1-5 /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

## Verificar que el Cron Está Funcionando

### Ver logs del sistema
```bash
# Ver logs de cron
sudo tail -f /var/log/syslog | grep CRON

# Ver logs de cron en systemd
sudo journalctl -u cron -f
```

### Probar el script manualmente
```bash
/home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

## Solución de Problemas

### El cron no se ejecuta

1. **Verificar que el servicio cron está corriendo:**
   ```bash
   sudo systemctl status cron
   ```

2. **Verificar permisos del script:**
   ```bash
   ls -l /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
   chmod +x /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
   ```

3. **Verificar que el usuario tiene permisos:**
   ```bash
   sudo -u cl159906175 whoami
   ```

4. **Verificar rutas absolutas:**
   - Siempre usa rutas absolutas en el crontab
   - No uses `~` o rutas relativas

### El script se ejecuta pero falla

1. **Verificar variables de entorno:**
   - El cron tiene un entorno mínimo
   - Agrega variables necesarias al crontab o al script

2. **Verificar logs del script:**
   ```bash
   tail -f /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/logs/actualizaciones_*.log
   ```

3. **Ejecutar el script manualmente con el usuario del cron:**
   ```bash
   sudo -u cl159906175 /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
   ```

## Ejemplo Completo de Crontab

```cron
# Variables de entorno
PATH=/usr/local/bin:/usr/bin:/bin
SHELL=/bin/bash
HOME=/home/cl159906175

# Actualizaciones diarias - Lunes a Viernes a las 5 AM
0 5 * * 1-5 /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh >> /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/logs/cron.log 2>&1
```

## Notas Importantes

1. **Rutas absolutas**: Siempre usa rutas completas en el crontab
2. **Permisos**: El script debe tener permisos de ejecución
3. **Variables de entorno**: El cron tiene un entorno mínimo, define las necesarias
4. **Logs**: Configura redirección de salida para ver qué pasa
5. **Testing**: Siempre prueba el script manualmente antes de confiar en el cron

