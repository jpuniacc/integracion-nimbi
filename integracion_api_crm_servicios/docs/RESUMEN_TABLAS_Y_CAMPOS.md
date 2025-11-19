# Resumen de Tablas y Campos - Integración Nimbi

Este documento describe las tablas que se actualizan mediante los scripts de integración, incluyendo una descripción de cada campo.

---

## 1. `01_identificadores_y_data_operacional`

**Script:** `actualizar_datos_identificadores_y_data_operacional.py`  
**Archivo CSV:** `1__Identificadores_y_data_operacional.csv`  
**Descripción:** Información básica e identificadores de alumnos de pregrado (vigentes, eliminados, suspendidos)

### Campos:

#### Información de Contacto
- **MAIL**: Correo electrónico personal del alumno
- **MAIL_INST**: Correo electrónico institucional del alumno
- **TELEFONO_ACT**: Teléfono actual del alumno
- **TELEFONO_PROC**: Teléfono de procedencia del alumno

#### Identificación del Alumno
- **RUT**: RUT del alumno (formato: CODCLI-DIG)
- **CODCLI**: Código único del cliente/alumno
- **NOMBRE_ALUMNO**: Nombre completo del alumno (nombre + apellido paterno + apellido materno)
- **NOMBRE_SOCIAL**: Nombre social del alumno (si aplica)
- **FECHA_NACIMIENTO**: Fecha de nacimiento del alumno
- **GENERO**: Género del alumno
- **NACIONALIDAD**: Nacionalidad del alumno
- **ESTADO_CIVIL**: Estado civil del alumno

#### Información del Apoderado
- **RUT_APODER**: RUT del apoderado (formato: CODAPOD-DIG)

#### Información Académica
- **ANO_INGRESO_INSTITUCION**: Año de ingreso a la institución
- **TIPO_CARRERA**: Tipo de carrera (PREGRADO)
- **NOMBRE_FACULTAD**: Nombre de la facultad
- **NOMBRE_ESCUELA**: Nombre de la escuela
- **COD_CARRERA**: Código de la carrera
- **NOMBRE_CARRERA**: Nombre de la carrera
- **CODIGO_PLAN**: Código del plan de estudios
- **NOMBRE_PLAN**: Nombre del plan de estudios
- **DURACION**: Duración de la carrera (nivel máximo)
- **JORNADA**: Jornada de estudio (Diurno, Vespertino, etc.)
- **NIVEL_ALUMNO**: Nivel actual del alumno en la carrera
- **ESTADO_ACADEMICO**: Estado académico actual (VIGENTE, ELIMINADO, SUSPENDIDO)
- **ULTIMA_MATRICULA**: Última matrícula (formato: AÑO-PERIODO)

#### Estados Académicos por Año
- **ESTADO_ACADEMICO_2022**: Estado académico en el año 2022
- **FECHA_REGISTRO_2022**: Fecha de registro del estado académico 2022
- **ESTADO_ACADEMICO_2023**: Estado académico en el año 2023
- **FECHA_REGISTRO_2023**: Fecha de registro del estado académico 2023
- **ESTADO_ACADEMICO_2024**: Estado académico en el año 2024
- **FECHA_REGISTRO_2024**: Fecha de registro del estado académico 2024
- **ESTADO_ACADEMICO_2025**: Estado académico en el año 2025
- **FECHA_REGISTRO_2025**: Fecha de registro del estado académico 2025

#### Información de Admisión
- **NEM**: Nota de Enseñanza Media
- **ANO_EGRESO_EM**: Año de egreso de enseñanza media
- **PAAVERBAL**: Puntaje PAA Verbal
- **PAAMATEMAT**: Puntaje PAA Matemáticas
- **PAAHISGEO**: Puntaje PAA Historia y Geografía
- **PSUVERBAL**: Puntaje PSU Verbal
- **PSUMATEMAT**: Puntaje PSU Matemáticas
- **PSUHISGEO**: Puntaje PSU Historia y Geografía
- **TIPOPRUEBA**: Tipo de prueba de admisión (PAA/PSU)
- **PROM_PRUEBA**: Promedio de la prueba de admisión

#### Información Geográfica
- **DIRECCION**: Dirección del alumno
- **COMUNA**: Comuna de residencia
- **CIUDAD**: Ciudad de residencia
- **REGION**: Región de residencia

#### Información Adicional
- **ES_CAMBIO_CARRERA**: Indica si el alumno ha realizado cambio de carrera (SI/NO)
- **FECHA_CAMBIO**: Fecha del cambio de carrera (si aplica)
- **FECHA_CORTE**: Fecha de corte de la información

---

## 2. `03_encuesta_docente`

**Script:** `actualizar_encuesta_docente.py`  
**Descripción:** Resultados de encuestas de evaluación docente realizadas por alumnos (desde 2022)

### Campos:

#### Identificación de la Encuesta
- **NOMBRE_ENCUESTA**: Nombre de la encuesta aplicada
- **ANIO**: Año de la encuesta
- **PERIODO**: Período académico de la encuesta

#### Información de la Pregunta
- **NRO_PREGUNTA**: Número de la pregunta
- **PREGUNTA**: Texto de la pregunta

#### Información del Ramo/Curso
- **CODRAMO**: Código del ramo/curso
- **NOMBRE_RAMO**: Nombre del ramo/curso
- **SECCION_RAMO**: Sección del ramo

#### Información de la Carrera
- **CODCARR**: Código de la carrera
- **NOMBRE_CARRERA**: Nombre de la carrera
- **JORNADA**: Jornada de estudio
- **MODALIDAD**: Modalidad de estudio

#### Información del Docente
- **RUT_DOCENTE**: RUT del docente evaluado
- **NOMBRE_DOCENTE**: Nombre del docente

#### Información del Alumno
- **CODCLI**: Código del cliente/alumno que respondió
- **NOMBRE_USUARIO**: Nombre de usuario del alumno (con dominio @uniacc.edu)

#### Respuesta de la Encuesta
- **CODRESPUESTA**: Código de la respuesta
- **ID_RESP**: ID de la respuesta
- **RESPUESTA**: Texto de la respuesta
- **OPCION**: Opción seleccionada (si aplica)
- **TEXTOLIBRE**: Texto libre de la respuesta (si aplica)
- **OBSERVACION**: Observaciones adicionales

#### Información General
- **NIVEL_GLOBAL**: Nivel académico (PREGRADO)
- **FECHA_CORTE**: Fecha de corte de la información

---

## 3. `04_notas_y_asistencias`

**Script:** `actualizar_notas_y_asistencia.py`  
**Archivo CSV:** `4__Notas_y_asistencia.csv`  
**Descripción:** Notas y asistencia de alumnos en ramos/cursos desde 2022

### Campos:

#### Información Básica
- **CODCLI**: Código del cliente/alumno
- **RUT**: RUT del alumno
- **NOMBRES**: Nombres del alumno
- **PATERNO**: Apellido paterno del alumno
- **MATERNO**: Apellido materno del alumno

#### Información del Ramo/Curso
- **NOMBRE_RAMO**: Nombre del ramo/asignatura
- **COD_RAMO**: Código del ramo del alumno
- **COD_RAMO_ACTA**: Código del ramo planificado (acta)
- **SECCION**: Sección del ramo
- **ID_SECCION**: ID único de la sección
- **NOMBRE_PROFESOR**: Nombre del profesor

#### Información Académica
- **PERIODO**: Período académico
- **ANIO**: Año académico
- **CARRERA_ALUMNO**: Nombre de la carrera del alumno
- **ESTADO_ALUMNO**: Estado académico del alumno

#### Notas Parciales
- **NOTA_1**: Nota del parcial 1
- **PONDERACION_1**: Ponderación del parcial 1 (%)
- **NOTA_2**: Nota del parcial 2
- **PONDERACION_2**: Ponderación del parcial 2 (%)
- **NOTA_3**: Nota del parcial 3
- **PONDERACION_3**: Ponderación del parcial 3 (%)
- **NOTA_4**: Nota del parcial 4
- **PONDERACION_4**: Ponderación del parcial 4 (%)
- **NOTA_5**: Nota del parcial 5
- **PONDERACION_5**: Ponderación del parcial 5 (%)
- **NOTA_6**: Nota del parcial 6
- **PONDERACION_6**: Ponderación del parcial 6 (%)
- **NOTA_7**: Nota del parcial 7
- **PONDERACION_7**: Ponderación del parcial 7 (%)

#### Notas Finales
- **NOTA_PRESENTACION**: Promedio ponderado de parciales (redondeado a 2 decimales)
- **NOTA_EXAMEN**: Nota del examen
- **NOTA_FINAL**: Nota final del ramo
- **ESTADO**: Estado de la nota (I=Inscrito, R=Reprobado)
- **CANTIDAD_NOTAS_RAMO**: Cantidad de notas del ramo
- **PONDERACION_NOTAS_PARA_EXAMEN**: Porcentaje de ponderación de notas para examen
- **PODERACION_NOTA_EXAMEN**: Porcentaje de ponderación de la nota de examen

#### Asistencia
- **ASISTENCIA**: Porcentaje de asistencia (redondeado a 2 decimales)
- **TOTAL_CLASES**: Total de clases del ramo
- **TOTAL_ASISTENCIA**: Total de clases asistidas
- **TOTAL_JUSTIFICACIONES**: Total de justificaciones
- **TOTAL_INASISTENCIAS**: Total de inasistencias
- **PORCENTAJE_INASISTENCIA**: Porcentaje de inasistencia
- **PORCENTAJE_JUSTIFICACIONES**: Porcentaje de justificaciones

#### Información General
- **FECHA_CORTE**: Fecha de corte de la información

---

## 4. `05_beneficios_alumnos`

**Script:** `actualizar_beneficios_alumnos.py`  
**Archivo CSV:** `05_beneficios_alumnos.csv`  
**Descripción:** Beneficios asignados a alumnos (becas, descuentos, etc.) desde 2022

### Campos:

#### Identificación
- **CODCLI**: Código del cliente/alumno

#### Información del Beneficio
- **ANIO_BENEFICIO**: Año del beneficio
- **PERIODO_BENEFICIO**: Período del beneficio
- **CODIGO_BENEFICIO**: Código del beneficio
- **DESCRIPCION_BENEFICIO**: Descripción del beneficio
- **MONTO_BENEFICIO**: Monto del beneficio
- **ORIGEN_BENEFICIO**: Origen del beneficio
- **TIPO_BENEFICIO**: Tipo de beneficio
- **APLICA_EN**: Dónde aplica el beneficio (matrícula, arancel, etc.)

#### Estado del Beneficio
- **ESTADO_BENEFICIO**: Estado del beneficio (PROCESO, POSTULADO, APROBADO, ASIGNADO, RECHAZADO)

#### Información General
- **FECHA_CORTE**: Fecha de corte de la información

---

## 5. `07_datos_moodle_operacional`

**Script:** `actualizar_datos_moodle_operacional.py`  
**Descripción:** Información operacional de cursos y actividades en Moodle

### Campos:

#### Identificación del Curso
- **ANIO_CURSO**: Año del curso
- **PERIODO**: Período académico
- **ID_CURSO**: ID del curso en Moodle
- **RAMO**: Nombre del ramo/asignatura
- **CARRERA**: Código de la carrera
- **CATEGORIA**: Categoría del curso
- **SUBCATEGORIA**: Subcategoría del curso

#### Fechas del Curso
- **FECHA_INICIO_CURSO**: Fecha de inicio del curso
- **FECHA_TERMINO_CURSO**: Fecha de término del curso
- **DIAS_DURACION_CURSO**: Días de duración del curso

#### Estado del Ramo
- **ESTADO_RAMO**: Estado del ramo (RAMO ACTIVO, RAMO CERRADO, POR INICIAR)
- **DIAS_DESDE_CIERRE**: Días transcurridos desde el cierre (si está cerrado)

#### Información del Alumno
- **ID_ALUMNO**: ID del alumno en Moodle
- **CODCLI**: Código del cliente/alumno
- **RUT**: RUT del alumno
- **NOMBRE_ALUMNO**: Nombre del alumno
- **EMAIL_ALUMNO**: Correo electrónico del alumno

#### Información del Docente
- **PROFESOR**: Nombre del profesor
- **EMAIL_PROFESOR**: Correo electrónico del profesor
- **ULTIMO_ACCESO_DOCENTE**: Último acceso del docente al curso

#### Actividades y Evaluaciones
- **TIPO_ACTIVIDAD**: Tipo de actividad (Tarea, Foro, Quiz, etc.)
- **NOMBRE_ACTIVIDAD**: Nombre de la actividad
- **FECHA_INICIO_ACTIVIDAD**: Fecha de inicio de la actividad
- **FECHA_TERMINO_ACTIVIDAD**: Fecha de término de la actividad
- **ES_EVALUACION_SUMATIVA**: Indica si es evaluación sumativa (SI/NO)
- **NOTA_ACTIVIDAD**: Nota obtenida en la actividad
- **ESTADO_ACTIVIDAD**: Estado de la actividad (Completada, Pendiente, etc.)

#### Accesos y Participación
- **ULTIMO_ACCESO_ALUMNO**: Último acceso del alumno al curso
- **TOTAL_ACCESOS**: Total de accesos del alumno al curso
- **TOTAL_ACTIVIDADES**: Total de actividades del curso
- **ACTIVIDADES_COMPLETADAS**: Cantidad de actividades completadas por el alumno

---

## 6. `09_datos_academicos`

**Script:** `actualizar_datos_academicos.py`  
**Archivo CSV:** `9__Datos_académicos.csv`  
**Descripción:** Información académica de alumnos de pregrado (vigentes, eliminados, suspendidos)

### Campos:

#### Identificación
- **CODCLI**: Código del cliente/alumno

#### Información de la Carrera
- **NOMBRE_CARRERA**: Nombre de la carrera
- **CODIGO_PLAN**: Código del plan de estudios
- **COD_CARRERA**: Código de la carrera
- **JORNADA**: Jornada de estudio (DIURNO, VESPERTINO, SEMIPRESENCIAL, A DISTANCIA)
- **MODALIDAD**: Modalidad de estudio
- **TIPO_CARRERA**: Tipo de carrera (PREGRADO)

#### Estado Académico
- **ESTADO_ACADEMICO**: Estado académico actual (VIGENTE, ELIMINADO, SUSPENDIDO)
- **SITUACION**: Situación específica del alumno (ALUMNO REGULAR, o código de situación)
- **TIPO_SEGUIMIENTO**: Tipo de seguimiento requerido (AVANCE ACADEMICO, REINGRESO, SIN CLASIFICAR)

#### Información de Ingreso
- **ANO_INGRESO_INSTITUCION**: Año de ingreso a la institución

#### Información General
- **FECHA_CORTE**: Fecha de corte de la información

---

## 7. `10_solicitudes_crm`

**Script:** `actualizar_solicitudes_crm.py`  
**Descripción:** Solicitudes/incidencias del sistema CRM (desde 2025)

### Campos:

#### Identificación de la Solicitud
- **cod_incidencia**: Código único de la incidencia/solicitud
- **cod_alurut**: Código alternativo del RUT del alumno
- **des_incidencia**: Descripción de la incidencia

#### Información de la Carrera
- **cod_carrera**: Código de la carrera
- **des_carrera**: Descripción/nombre de la carrera
- **cod_escuela**: Código de la escuela
- **des_escuela**: Descripción/nombre de la escuela

#### Información del Cliente
- **codcli**: Código del cliente

#### Información del Consejero
- **des_consejero**: Nombre del consejero asignado

#### Estado y Categorización
- **cod_estado**: Código del estado de la solicitud
- **des_estado**: Descripción del estado
- **cod_categoria**: Código de la categoría
- **des_categoria**: Descripción de la categoría
- **cod_subcategoria**: Código de la subcategoría
- **des_subcategoria**: Descripción de la subcategoría

#### Asignaciones
- **des_login_ingreso**: Login del usuario que ingresó la solicitud
- **des_login_asignado**: Login del usuario asignado
- **des_login_derivado**: Login del usuario al que se derivó
- **asignado_login**: Login del usuario asignado (objeto)
- **asignado_nombre**: Nombre del usuario asignado

#### Fechas y Tiempos
- **fec_ingreso**: Fecha de ingreso de la solicitud
- **fec_ultmod**: Fecha de última modificación
- **nro_minuto_total**: Número total de minutos
- **nro_minuto_etapa**: Número de minutos en la etapa actual
- **nro_minuto_vencido**: Número de minutos vencidos

#### Información Adicional
- **cod_grupo_incidencia**: Código del grupo de incidencia
- **des_observacion**: Observaciones
- **des_respuesta**: Respuesta a la solicitud
- **des_grupo**: Descripción del grupo
- **des_anulacion**: Motivo de anulación (si aplica)
- **bool_portal**: Indica si fue ingresada por portal (true/false)
- **bool_nuevo**: Indica si es nueva (true/false)

#### Información del Alumno
- **alumno_nombre**: Nombre del alumno
- **alumno_apepri**: Apellido paterno del alumno
- **alumno_apeseg**: Apellido materno del alumno
- **alumno_email**: Correo electrónico del alumno
- **alumno_telefono**: Teléfono del alumno
- **alumno_celular**: Celular del alumno

#### Información General
- **fecha_corte**: Fecha de corte de la información

---

## 8. `11_datos_sies`

**Script:** `actualizar_datos_sies.py`  
**Descripción:** Información del Sistema de Información de Educación Superior (SIES) desde 2022

### Campos:

#### Identificación
- **periodo**: Período académico
- **codcli**: Código del cliente/alumno
- **codplan**: Código del plan de estudios

#### Información SIES
- **sies_completo**: Información completa del SIES
- **anio_ing_act**: Año de ingreso actual
- **sem_ing_act**: Semestre de ingreso actual
- **anio_ing_ori**: Año de ingreso original
- **sem_ing_ori**: Semestre de ingreso original

#### Información General
- **fecha_corte**: Fecha de corte de la información (agregada en la carga)

---

## 9. `13_informacion_finanzas`

**Script:** `actualizar_informe_finanzas.py`  
**Descripción:** Información financiera de alumnos (matrículas, aranceles, pagos, descuentos, becas)

### Campos:

#### Identificación
- **CODCLI**: Código del cliente/alumno
- **RUT**: RUT del alumno
- **NOMBRE_ALUMNO**: Nombre completo del alumno

#### Información de la Carrera
- **NOMBRE_CARRERA**: Nombre de la carrera
- **NOMBRE_AREA**: Nombre del área
- **MODALIDAD**: Modalidad de estudio

#### Información del Período
- **PERIODO**: Período académico

#### Información del Apoderado
- **RUT_APODER**: RUT del apoderado
- **NOMBRE_APODERADO**: Nombre del apoderado

#### Matrícula
- **MAT_PRIMER_AÑO**: Indica si es matrícula de primer año
- **MONTO_MATRICULA**: Monto total de la matrícula
- **CUOTA_MATRICULA**: Número de cuotas de matrícula
- **DESC_MATRICULA**: Descuento aplicado a matrícula
- **BECA_MATRICULA**: Beca aplicada a matrícula
- **VALOR_TOTAL_MATRICULA**: Valor total de matrícula después de descuentos/becas

#### Arancel
- **MONTO_ARANCEL**: Monto total del arancel
- **CUOTA_ARANCEL**: Número de cuotas de arancel
- **DESC_ARANCEL**: Descuento aplicado a arancel
- **BECA_ARANCEL**: Beca aplicada a arancel
- **VALOR_TOTAL_ARANCEL**: Valor total de arancel después de descuentos/becas

#### Pagos y Vencimientos
- **PAGOS_POR_MORA**: Pagos realizados por mora
- **CUOTAS_MATRICULA_VENCIDAS**: Cantidad de cuotas de matrícula vencidas
- **MONTO_MATRICULA_VENCIDAS**: Monto de matrícula vencida
- **MONTO_ARANCEL_VENCIDAS**: Monto de arancel vencido
- **MONTO_MATRICULA_POR_VENCER**: Monto de matrícula por vencer
- **MONTO_ARANCEL_POR_VENCER**: Monto de arancel por vencer

#### Información General
- **FECHA_CORTE**: Fecha de corte de la información

---

## Notas Generales

- **FECHA_CORTE**: Campo común en todas las tablas que indica la fecha en que se realizó la extracción de datos
- Todas las tablas se actualizan mediante **TRUNCATE** (limpieza completa) antes de insertar nuevos datos
- Los scripts extraen datos desde **SQL Server** y los cargan en **PostgreSQL** (schema `nimbi`)
- Las siguientes tablas generan archivos CSV que se suben automáticamente al servidor SFTP:
  - `01_identificadores_y_data_operacional` → `1__Identificadores_y_data_operacional.csv`
  - `04_notas_y_asistencias` → `4__Notas_y_asistencia.csv`
  - `05_beneficios_alumnos` → `05_beneficios_alumnos.csv`
- Los datos se filtran generalmente para incluir solo información desde 2022 en adelante

---

**Última actualización:** Noviembre 2025

