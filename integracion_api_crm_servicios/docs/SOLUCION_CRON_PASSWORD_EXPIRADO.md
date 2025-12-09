# Solución: Cron no funciona por contraseña expirada

## Problema Identificado

El cron no está ejecutando los scripts porque la contraseña del usuario `cl159906175` ha expirado.

Log del sistema:
```
Dec 04 05:00:01 devsclapp1 CRON[756352]: pam_unix(cron:account): expired password for user cl159906175 (password aged)
```

## Soluciones

### Opción 1: Cambiar la contraseña del usuario (Recomendado)

Como administrador del sistema, ejecuta:

```bash
sudo passwd cl159906175
```

Esto permitirá que cron ejecute los scripts nuevamente.

### Opción 2: Configurar el cron como root (Alternativa)

Si no puedes cambiar la contraseña, puedes configurar el cron para ejecutarse como root:

1. Editar el crontab de root:
```bash
sudo crontab -e
```

2. Agregar la línea con `sudo -u`:
```cron
0 5 * * 1-5 sudo -u cl159906175 /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

**Nota:** Esto requiere configurar sudoers para permitir que root ejecute comandos como este usuario sin contraseña.

### Opción 3: Desactivar expiración de contraseña (Solo si es seguro)

Como administrador, puedes configurar que la contraseña no expire:

```bash
sudo chage -M 99999 cl159906175
```

Esto establece que la contraseña no expire en 99999 días.

### Opción 4: Configurar el cron para ignorar verificación de contraseña (No recomendado)

Editar `/etc/pam.d/cron` para desactivar la verificación de contraseña expirada (NO recomendado por seguridad).

## Verificar la solución

Después de aplicar la solución:

1. Verificar que cron puede ejecutar comandos del usuario:
```bash
sudo -u cl159906175 crontab -l
```

2. Verificar que no hay más errores en los logs:
```bash
sudo grep "cl159906175" /var/log/syslog | grep "expired password" | tail -5
```

3. Esperar al próximo horario de ejecución o probar manualmente:
```bash
sudo -u cl159906175 /home/cl159906175/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

## Prevención Futura

1. **Configurar alertas**: Configurar alertas antes de que la contraseña expire
2. **Política de contraseñas**: Establecer una política que notifique antes de la expiración
3. **Monitoreo**: Revisar regularmente los logs de cron para detectar problemas temprano

## Verificar estado actual

Para ver cuándo expira la contraseña:

```bash
sudo chage -l cl159906175
```

Esto mostrará información sobre:
- Último cambio de contraseña
- Días hasta expiración
- Días antes de aviso
- Días de inactividad permitidos



