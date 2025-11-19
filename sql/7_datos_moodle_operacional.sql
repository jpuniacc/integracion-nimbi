-- ========================================
-- REPORTE COMPLETO DE ACTIVIDADES Y CURSOS
-- Con validación de estado del ramo (activo/cerrado)
-- Con clasificación de evaluaciones sumativas
-- ========================================

SELECT
    -- === AÑO CURSO ===
    S.ANO AS ANIO_CURSO,
    S.PERIODO,
    -- === IDENTIFICACIÓN ===
    CA.USERID_ALUMNO AS ID_ALUMNO,
    (SELECT TOP 1 A.CODCLI FROM UNIACC.DBO.RA_NOTA X, UNIACC.DBO.MT_ALUMNO A WHERE A.CODCLI=X.CODCLI AND A.RUT=C.CODCLI AND X.ANO=S.ANO AND X.PERIODO=S.PERIODO AND X.RAMOEQUIV=S.CODRAMO AND X.CODSECC=S.CODSECC) AS CODCLI,
    C.CODCLI+'-'+C.DIG AS RUT,
    CA.ALUMNO AS NOMBRE_ALUMNO,
    CA.EMAIL_ALUMNO,

    -- === CURSO ===
    CA.IDCOURSE AS ID_CURSO,
    CA.ASIGNATURA AS RAMO,
    CA.cod_carrera AS CARRERA,
    CA.CATEGORIA,
    CA.SUBCATEGORIA,

    -- === FECHAS DEL CURSO (desde ra_seccio) ===
    CONVERT(VARCHAR(10), S.FECHAINICIAL, 103) AS FECHA_INICIO_CURSO,
    CONVERT(VARCHAR(10), S.FECHAFINAL, 103) AS FECHA_TERMINO_CURSO,
    DATEDIFF(DAY, S.FECHAINICIAL, S.FECHAFINAL) AS DIAS_DURACION_CURSO,

    -- ✅ ESTADO DEL RAMO
    CASE
        WHEN S.FECHAFINAL < CAST(GETDATE() AS DATE) THEN 'RAMO CERRADO'
        WHEN S.FECHAINICIAL > CAST(GETDATE() AS DATE) THEN 'POR INICIAR'
        ELSE 'RAMO ACTIVO'
    END AS ESTADO_RAMO,

    CASE
        WHEN S.FECHAFINAL < CAST(GETDATE() AS DATE)
        THEN DATEDIFF(DAY, S.FECHAFINAL, GETDATE())
        ELSE NULL
    END AS DIAS_DESDE_CIERRE,

    -- === DOCENTE ===
    CA.DOCENTE AS PROFESOR,
    CA.EMAIl_DOCENTE AS EMAIL_PROFESOR,

    CASE
        WHEN CR.ULTIMO_ACCESO_DOCENTE IS NOT NULL
        THEN CONVERT(VARCHAR(19), CR.ULTIMO_ACCESO_DOCENTE, 120)
        ELSE NULL
    END AS ULTIMO_ACCESO_PROFESOR,

    CASE
        WHEN CR.ULTIMO_ACCESO_DOCENTE IS NOT NULL
        THEN DATEDIFF(DAY, CR.ULTIMO_ACCESO_DOCENTE, GETDATE())
        ELSE NULL
    END AS DIAS_SIN_ACCESO_PROFESOR,

    CASE
        WHEN CR.FECHA_TERMINO_CURSO < CAST(GETDATE() AS DATE) THEN 'Ramo Cerrado'
        WHEN CR.ULTIMO_ACCESO_DOCENTE IS NULL THEN 'Sin Accesos'
        WHEN DATEDIFF(DAY, CR.ULTIMO_ACCESO_DOCENTE, GETDATE()) > 30 THEN 'Inactivo +30 días'
        WHEN DATEDIFF(DAY, CR.ULTIMO_ACCESO_DOCENTE, GETDATE()) > 14 THEN 'Inactivo +14 días'
        WHEN DATEDIFF(DAY, CR.ULTIMO_ACCESO_DOCENTE, GETDATE()) > 7 THEN 'Inactivo +7 días'
        ELSE 'Activo'
    END AS ALERTA_ACTIVIDAD_PROFESOR,

    -- === INFORMACIÓN DE PARTICIPACIÓN DEL ALUMNO ===
    CR.CANTIDAD_POSTEOS,

    CASE
        WHEN CR.ULTIMO_ACCESO IS NOT NULL
        THEN CONVERT(VARCHAR(19), CR.ULTIMO_ACCESO, 120)
        ELSE NULL
    END AS ULTIMO_ACCESO_ALUMNO,

    CASE
        WHEN CR.ULTIMO_ACCESO IS NOT NULL
        THEN DATEDIFF(DAY, CR.ULTIMO_ACCESO, GETDATE())
        ELSE NULL
    END AS DIAS_SIN_ACCESO_ALUMNO,

    CASE
        WHEN CR.FECHA_TERMINO_CURSO < CAST(GETDATE() AS DATE) THEN 'Ramo Cerrado'
        WHEN CR.ULTIMO_ACCESO IS NULL THEN 'Sin Accesos'
        WHEN DATEDIFF(DAY, CR.ULTIMO_ACCESO, GETDATE()) > 30 THEN 'Inactivo +30 días'
        WHEN DATEDIFF(DAY, CR.ULTIMO_ACCESO, GETDATE()) > 14 THEN 'Inactivo +14 días'
        WHEN DATEDIFF(DAY, CR.ULTIMO_ACCESO, GETDATE()) > 7 THEN 'Inactivo +7 días'
        ELSE 'Activo'
    END AS ALERTA_ACTIVIDAD_ALUMNO,

    -- === DETALLE ACTIVIDAD ===
    CA.SEMANA_UNIDAD AS UNIDAD,
    CA.modulo AS TIPO_MODULO,

    -- ✅ CLASIFICACIÓN DETALLADA DE TIPO DE EVALUACIÓN
    CASE
        WHEN CA.name LIKE '%final%' OR CA.name LIKE '%Final%' THEN 'Trabajo Final'
        WHEN CA.name LIKE '%examen%' OR CA.name LIKE '%Examen%' THEN 'Examen'
        WHEN CA.name LIKE '%exam%' OR CA.name LIKE '%Exam%' THEN 'Examen'
        WHEN CA.name LIKE '%recuper%' OR CA.name LIKE '%Recuper%' THEN 'Recuperación'
        WHEN CA.name LIKE '%repetición%' OR CA.name LIKE '%Repetición%' THEN 'Repetición'
        WHEN CA.name LIKE '%Control%' OR CA.name LIKE '%control%' THEN 'Control/Quiz'
        WHEN CA.name LIKE '%Trabajo%' OR CA.name LIKE '%trabajo%' THEN 'Trabajo'
        WHEN CA.name LIKE '%Tarea%' OR CA.name LIKE '%tarea%' THEN 'Tarea'
        WHEN CA.name LIKE '%Evaluación%' AND CA.modulo = 'forum' THEN 'Foro Evaluado'
        WHEN CA.name LIKE '%evaluación%' AND CA.modulo = 'forum' THEN 'Foro Evaluado'
        WHEN CA.modulo = 'forum' THEN 'Foro'
        WHEN CA.modulo = 'quiz' THEN 'Control/Quiz'
        WHEN CA.modulo = 'assign' THEN 'Tarea/Trabajo'
        ELSE 'Otra Actividad'
    END AS TIPO_EVALUACION,

    -- ✅ INDICADOR: ¿ES EVALUACIÓN SUMATIVA? (Tiene escala y/o nota)
    CASE
        WHEN CA.ESCALA_Puntuacion IS NOT NULL AND LTRIM(RTRIM(CA.ESCALA_Puntuacion)) != '' THEN 'SI'
        WHEN CA.finalgrade IS NOT NULL THEN 'SI'
        ELSE 'NO'
    END AS ES_EVALUACION_SUMATIVA,

    -- ✅ INDICADOR: ¿ES NOTA FINAL DE RAMO? (Final/Examen/Recuperación)
    CASE
        WHEN CA.name LIKE '%final%' OR CA.name LIKE '%Final%'
          OR CA.name LIKE '%examen%' OR CA.name LIKE '%Examen%'
          OR CA.name LIKE '%exam%' OR CA.name LIKE '%Exam%'
          OR CA.name LIKE '%recuper%' OR CA.name LIKE '%Recuper%'
          OR CA.name LIKE '%repetición%' OR CA.name LIKE '%Repetición%'
        THEN 'SI'
        ELSE 'NO'
    END AS ES_NOTA_FINAL_RAMO,

    CA.name AS NOMBRE_ACTIVIDAD,

      -- === FECHAS DE LA ACTIVIDAD - NORMALIZADAS A DD/MM/YYYY ===

    -- FECHA_ENTREGA: Normalizada a DD/MM/YYYY
    CASE
        -- Si contiene texto descriptivo (no es fecha)
        WHEN CA.FECHA_ENTREGA_TAREA = 'Sin fecha' OR CA.FECHA_ENTREGA_TAREA = '' OR CA.FECHA_ENTREGA_TAREA IS NULL
        THEN NULL
        -- Si ya está en formato DD/MM/YYYY (sin hora)
        WHEN CA.FECHA_ENTREGA_TAREA LIKE '__/__/____' AND LEN(CA.FECHA_ENTREGA_TAREA) = 10
        THEN CA.FECHA_ENTREGA_TAREA
        -- Si es datetime válido (con o sin hora), convertir a DD/MM/YYYY
        WHEN ISDATE(CA.FECHA_ENTREGA_TAREA) = 1
        THEN CONVERT(VARCHAR(10), CONVERT(datetime, CA.FECHA_ENTREGA_TAREA), 103)
        -- Cualquier otro caso, devolver NULL
        ELSE NULL
    END AS FECHA_ENTREGA,

    -- FECHA_LIMITE: Normalizada a DD/MM/YYYY
    CASE
        WHEN CA.FECHA_LIMITE = 'Sin fecha' OR CA.FECHA_LIMITE = '' OR CA.FECHA_LIMITE IS NULL
        THEN NULL
        WHEN CA.FECHA_LIMITE LIKE '__/__/____' AND LEN(CA.FECHA_LIMITE) = 10
        THEN CA.FECHA_LIMITE
        WHEN ISDATE(CA.FECHA_LIMITE) = 1
        THEN CONVERT(VARCHAR(10), CONVERT(datetime, CA.FECHA_LIMITE), 103)
        ELSE NULL
    END AS FECHA_LIMITE,

    -- === CALIFICACIÓN ===
    CA.ESCALA_Puntuacion AS ESCALA,
    CA.finalgrade AS NOTA,
    CA.CALIFICADO AS ESTADO_CALIFICADO,

    -- FECHA_CALIFICACION: Normalizada a DD/MM/YYYY
    CASE
        WHEN CA.FECHA_CALIFICADO = 'Sin fecha' OR CA.FECHA_CALIFICADO = '' OR CA.FECHA_CALIFICADO IS NULL
        THEN NULL
        WHEN CA.FECHA_CALIFICADO LIKE '__/__/____' AND LEN(CA.FECHA_CALIFICADO) = 10
        THEN CA.FECHA_CALIFICADO
        WHEN ISDATE(CA.FECHA_CALIFICADO) = 1
        THEN CONVERT(VARCHAR(10), CONVERT(datetime, CA.FECHA_CALIFICADO), 103)
        ELSE NULL
    END AS FECHA_CALIFICACION,

    -- === INDICADORES VISUALES ===
    CASE
        WHEN CA.CALIFICADO = 'SI' THEN 'Calificado'
        WHEN CA.CALIFICADO = 'NO' AND CR.FECHA_TERMINO_CURSO < CAST(GETDATE() AS DATE)
        THEN 'Pendiente (Ramo Cerrado)'
        WHEN CA.CALIFICADO = 'NO' THEN 'Pendiente'
        ELSE 'Sin Estado'
    END AS ESTADO_CALIFICACION,

    -- === ORDEN ===
    ROW_NUMBER() OVER (
        PARTITION BY CA.USERID_ALUMNO, CA.IDCOURSE
        ORDER BY CA.SEMANA_UNIDAD,
                 CASE
                    WHEN ISDATE(CA.FECHA_ENTREGA_TAREA) = 1
                    THEN CONVERT(datetime, CA.FECHA_ENTREGA_TAREA)
                    ELSE NULL
                 END
    ) AS NUM_ACTIVIDAD_EN_CURSO,

    -- === METADATA ===
    CR.FORMATO_CURSO,
    CA.CURSO_VISIBLE,
    CONVERT(VARCHAR(10), GETDATE(), 23) AS FECHA_CORTE

FROM DWH_ECAMPUS_SERVER.DWEcampus.dbo.Cursos_Actividades CA

LEFT JOIN DWH_ECAMPUS_SERVER.DWEcampus.dbo.Cursos_Reportev3 CR
    ON CA.IDCOURSE = CR.IDCOURSE
    AND CA.USERID_ALUMNO = CR.USERID_ALUMNO
    AND CA.EMAIL_ALUMNO = CR.EMAIL_ALUMNO
LEFT JOIN UNIACC.DBO.RA_SECCIO S
    ON CA.IDCOURSE=S.IDCURSOMOODLE
LEFT JOIN UNIACC.DBO.MT_CLIENT C
    ON CA.EMAIL_ALUMNO=C.MAIL_INST
WHERE
    CA.CURSO_VISIBLE = 1
    AND CA.USERID_ALUMNO IS NOT NULL
    AND (CA.CATEGORIA != 'Master' OR CA.CATEGORIA IS NULL)
    --AND CA.EMAIL_ALUMNO = 'hans.vidal@uniacc.edu'
    --AND CA.ASIGNATURA = 'COMERCIO ELECTRONICO Y WEB ENGINEERING - 201 - 464721'
    AND NOT (CA.modulo = 'forum' AND (
        CA.name LIKE '%Sala de Clase%'
        OR CA.name LIKE '%dudas%'
        OR CA.name LIKE '%Pregúntale%'
    ))

ORDER BY
    CA.ASIGNATURA,
    CA.SEMANA_UNIDAD,
    CASE
        WHEN ISDATE(CA.FECHA_ENTREGA_TAREA) = 1
        THEN CONVERT(datetime, CA.FECHA_ENTREGA_TAREA)--731712
        ELSE NULL
    END;