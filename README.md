# Integración Nimbi - Migración de Datos SQL Server a PostgreSQL

Sistema de integración para migrar datos desde SQL Server (eCampus5) a PostgreSQL y generar archivos CSV para el cliente Nimbi, con subida automática a servidor SFTP.

## 📋 Descripción

Este proyecto automatiza la extracción de datos académicos, operacionales y administrativos desde SQL Server, su carga en PostgreSQL, y la generación de archivos CSV con formato específico para su posterior procesamiento por el sistema Nimbi. Los archivos CSV se suben automáticamente a un servidor SFTP configurado.

## 🏗️ Estructura del Proyecto

```
integracion_nimbi/
├── integracion_api_crm_servicios/
│   ├── docs/                          # Documentación del proyecto
│   │   ├── RESUMEN_TABLAS_Y_CAMPOS.md # Descripción detallada de tablas y campos
│   │   ├── GUIA_VERSIONADO_GIT.md     # Guía para versionar el proyecto
│   │   ├── CONFIGURAR_GIT_SERVIDOR.md # Configuración de Git en servidor
│   │   └── ...
│   ├── scripts/                       # Scripts Python de migración
│   │   ├── actualizar_datos_identificadores_y_data_operacional.py
│   │   ├── actualizar_datos_academicos.py
│   │   ├── actualizar_notas_y_asistencia.py
│   │   ├── actualizar_beneficios_alumnos.py
│   │   ├── actualizar_datos_moodle_operacional.py
│   │   ├── actualizar_datos_sies.py
│   │   ├── actualizar_encuesta_docente.py
│   │   ├── actualizar_informe_finanzas.py
│   │   ├── actualizar_solicitudes_crm.py
│   │   ├── ejecutar_actualizaciones_diarias.sh  # Script de ejecución diaria
│   │   ├── logs/                      # Logs de ejecución
│   │   └── backups/                   # Backups de datos
│   ├── temp_csv/                      # Archivos CSV temporales generados
│   └── requirement.txt                # Dependencias Python
├── sql/                               # Queries SQL para extracción de datos
│   ├── 1_Identificadores_y_data_operacional.sql
│   ├── 4_notas_y_asistencia.sql
│   ├── 5_beneficios_alumnos.sql
│   └── ...
└── integracion_analitica/             # Scripts de migración a base analítica
```

## 🔧 Requisitos

- **Python 3.8+**
- **PostgreSQL** (base de datos destino)
- **SQL Server** (base de datos origen - eCampus5)
- **Acceso SFTP** (para subida de archivos CSV)

### Dependencias Python

Las dependencias se encuentran en `integracion_api_crm_servicios/requirement.txt`:

- `pyodbc==5.3.0` - Conexión a SQL Server
- `psycopg2-binary==2.9.11` - Conexión a PostgreSQL
- `pandas==2.2.3` - Manipulación de datos y generación de CSV
- `paramiko==3.5.1` - Cliente SFTP
- `python-dotenv==1.2.1` - Gestión de variables de entorno

## ⚙️ Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en `integracion_api_crm_servicios/` con las siguientes variables:

```env
# SQL Server (eCampus5)
SQLSERVER_HOST=tu_servidor_sql
SQLSERVER_DATABASE=ecampus5
SQLSERVER_USER=usuario
SQLSERVER_PASSWORD=contraseña

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_DATABASE=nimbi
POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña
POSTGRES_PORT=5432

# SFTP
SFTP_HOST=192.168.135.15
SFTP_USER=nimbi
SFTP_PASSWORD=contraseña
SFTP_PORT=22
SFTP_TIMEOUT=600
```

### 2. Instalación de Dependencias

```bash
cd integracion_api_crm_servicios
python3 -m venv .venv-crm
source .venv-crm/bin/activate
pip install -r requirement.txt
```

### 3. Configuración de Base de Datos

Asegúrate de que la base de datos PostgreSQL tenga el esquema `nimbi` creado con las tablas necesarias. Consulta la documentación en `docs/RESUMEN_TABLAS_Y_CAMPOS.md` para más detalles.

## 🚀 Uso

### Ejecución Manual de Scripts

Cada script puede ejecutarse individualmente:

```bash
cd integracion_api_crm_servicios/scripts
source ../.venv-crm/bin/activate
python actualizar_datos_identificadores_y_data_operacional.py
```

### Ejecución Automatizada (Cron)

Para ejecutar todas las actualizaciones diarias automáticamente, configura un cron job:

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar diariamente a las 2:00 AM
0 2 * * * /ruta/completa/integracion_nimbi/integracion_api_crm_servicios/scripts/ejecutar_actualizaciones_diarias.sh
```

O usa el script de configuración:

```bash
cd integracion_api_crm_servicios/scripts
./configurar_cron_usuario.sh
```

## 📊 Scripts Disponibles

| Script | Descripción | Archivo CSV Generado |
|--------|-------------|---------------------|
| `actualizar_datos_identificadores_y_data_operacional.py` | Identificadores y datos operacionales de alumnos | `1__Identificadores_y_data_operacional.csv` |
| `actualizar_datos_academicos.py` | Datos académicos de alumnos | `2__Datos_academicos.csv` |
| `actualizar_encuesta_docente.py` | Resultados de encuestas docentes | `3__Encuesta_docente.csv` |
| `actualizar_notas_y_asistencia.py` | Notas y asistencia de alumnos | `4__Notas_y_asistencia.csv` |
| `actualizar_beneficios_alumnos.py` | Beneficios asignados a alumnos | `05_beneficios_alumnos.csv` |
| `actualizar_datos_moodle_operacional.py` | Datos operacionales de Moodle | `7__Datos_moodle_operacional.csv` |
| `actualizar_datos_sies.py` | Datos SIES (Sistema de Información de Educación Superior) | `11__Datos_sies.csv` |
| `actualizar_informe_finanzas.py` | Información financiera | `13__Informacion_finanzas.csv` |
| `actualizar_solicitudes_crm.py` | Solicitudes del CRM | `14__Solicitudes_crm.csv` |

## 📁 Formato de Archivos CSV

Los archivos CSV generados siguen el siguiente formato:

- **Encoding**: UTF-8
- **Separador**: Punto y coma (`;`)
- **Delimitador de texto**: Comillas dobles (`"`) en todos los campos
- **Valores NULL**: Cadena vacía
- **Sin escape de backslashes**: Los backslashes innecesarios se eliminan automáticamente

## 📚 Documentación

- **[RESUMEN_TABLAS_Y_CAMPOS.md](integracion_api_crm_servicios/docs/RESUMEN_TABLAS_Y_CAMPOS.md)**: Descripción detallada de todas las tablas y campos que se migran
- **[GUIA_VERSIONADO_GIT.md](integracion_api_crm_servicios/docs/GUIA_VERSIONADO_GIT.md)**: Guía paso a paso para versionar el proyecto con Git
- **[CONFIGURAR_GIT_SERVIDOR.md](integracion_api_crm_servicios/docs/CONFIGURAR_GIT_SERVIDOR.md)**: Configuración de Git en el servidor
- **[CRON_SETUP.md](integracion_api_crm_servicios/docs/CRON_SETUP.md)**: Configuración de tareas programadas

## 🔍 Logs

Los logs de ejecución se guardan en `integracion_api_crm_servicios/scripts/logs/` con el formato:
- `actualizaciones_YYYYMMDD.log`

Cada script también muestra información en consola durante su ejecución.

## 🔐 Seguridad

- **Nunca subas el archivo `.env` al repositorio** (está en `.gitignore`)
- Las credenciales de base de datos y SFTP deben mantenerse seguras
- Los archivos CSV temporales se generan localmente y se eliminan después de la subida (opcional)

## 🛠️ Mantenimiento

### Verificar Estado de Ejecuciones

```bash
# Ver último log
tail -f integracion_api_crm_servicios/scripts/logs/actualizaciones_$(date +%Y%m%d).log

# Verificar conexión SFTP
cd integracion_api_crm_servicios/docs
./verificar_sftp_chroot.sh
```

### Limpieza de Archivos Temporales

Los archivos CSV en `temp_csv/` pueden eliminarse manualmente si es necesario:

```bash
rm integracion_api_crm_servicios/temp_csv/*.csv
```

## 📝 Notas Importantes

- Los scripts realizan un `TRUNCATE` de las tablas destino antes de insertar nuevos datos
- La conexión SFTP maneja automáticamente entornos con chroot jail
- Todos los scripts incluyen manejo de errores y logging detallado
- Los archivos CSV se validan antes de la subida a SFTP

## 🤝 Contribución

Para contribuir al proyecto:

1. Crea una rama nueva desde `master`
2. Realiza tus cambios
3. Verifica que los scripts funcionen correctamente
4. Crea un Pull Request con una descripción clara de los cambios

## 📄 Licencia

Este proyecto es propiedad de Universidad UNIACC.

## 👥 Contacto

Para consultas o soporte, contactar al equipo de desarrollo.

---

**Última actualización:** Noviembre 2025

