  WITH EstudiantesMultiplesCareeras AS (
    -- Identificar estudiantes con múltiples CODCLI
    SELECT
      m.RUT,
      m.ANO_INGRESO_INSTITUCION,
      m.CODCLI,
      m.NOMBRE_CARRERA,
      m.ANO as ano_matricula,
      m.PERIODO as periodo_matricula,
      -- Ordenar CODCLI por fecha de matrícula para identificar secuencia
      ROW_NUMBER() OVER (
        PARTITION BY m.RUT
        ORDER BY m.ANO, m.PERIODO, m.CODCLI
      ) as orden_matricula
    FROM UConectores.dbo.PR_MATRICULA m
    WHERE m.ANO_INGRESO_INSTITUCION >= 2022
      AND m.TIPO_CARRERA = 'pregrado'
      AND m.ESTADO_ACADEMICO IN ('VIGENTE', 'ELIMINADO', 'SUSPENDIDO')
  ),
  CambiosCarrera AS (
    -- Identificar cambios de carrera
    SELECT
      actual.RUT,
      actual.ANO_INGRESO_INSTITUCION,
      anterior.CODCLI as CODCLI_ANTIGUO,
      actual.CODCLI as CODCLI_NUEVO,
      anterior.NOMBRE_CARRERA as CARRERA_ANTERIOR,
      actual.NOMBRE_CARRERA as CARRERA_NUEVA
    FROM EstudiantesMultiplesCareeras actual
    LEFT JOIN EstudiantesMultiplesCareeras anterior
      ON actual.RUT = anterior.RUT
      AND anterior.orden_matricula = actual.orden_matricula - 1
    WHERE actual.orden_matricula > 1  -- Solo los que tienen carrera anterior

    UNION

    -- Incluir casos de homologación directa (sin CODCLI anterior)
    SELECT
      m.RUT,
      m.ANO_INGRESO_INSTITUCION,
      NULL as CODCLI_ANTIGUO,
      m.CODCLI as CODCLI_NUEVO,
      NULL as CARRERA_ANTERIOR,
      m.NOMBRE_CARRERA as CARRERA_NUEVA
    FROM UConectores.dbo.PR_MATRICULA m
    WHERE m.ANO_INGRESO_INSTITUCION >= 2022
      AND m.TIPO_CARRERA = 'pregrado'
      AND m.ESTADO_ACADEMICO IN ('VIGENTE', 'ELIMINADO', 'SUSPENDIDO')
      AND m.RUT NOT IN (
        SELECT RUT
        FROM EstudiantesMultiplesCareeras
        WHERE orden_matricula > 1
      )
      AND m.CODCLI IN (
        SELECT DISTINCT ar.CODCLI
        FROM UConectores.dbo.PR_ALUMNO_RAMO ar
        WHERE ar.CONCEPTO IN ('cv', 'ho')
      )
  ),
  TransferenciasResumen AS (
    -- Calcular transferencias por CODCLI_NUEVO
    SELECT
      ar.CODCLI,
      SUM(CASE WHEN ar.CONCEPTO = 'cv' THEN 1 ELSE 0 END) as cantidad_cv,
      SUM(CASE WHEN ar.CONCEPTO = 'ho' THEN 1 ELSE 0 END) as cantidad_ho
    FROM UConectores.dbo.PR_ALUMNO_RAMO ar
    WHERE ar.CONCEPTO IN ('cv', 'ho')
    GROUP BY ar.CODCLI
  )

  -- RESULTADO FINAL
  SELECT
    cc.ANO_INGRESO_INSTITUCION,
    cc.RUT,
    cc.CODCLI_ANTIGUO,
    cc.CODCLI_NUEVO,
    ISNULL(tr.cantidad_cv, 0) as Cantidad_ramos_convalidados_CODCLI_NUEVO,
    ISNULL(tr.cantidad_ho, 0) as Cantidad_ramos_homologados_CODCLI_NUEVO,
    cc.CARRERA_ANTERIOR,
    cc.CARRERA_NUEVA,
    CASE
      WHEN cc.CODCLI_ANTIGUO IS NULL THEN 'Homologación desde otra institución'
      ELSE 'Cambio de carrera interno'
    END as tipo_caso,
    CONVERT(VARCHAR(10), GETDATE(), 23) AS FECHA_CORTE


  FROM CambiosCarrera cc
  LEFT JOIN TransferenciasResumen tr ON cc.CODCLI_NUEVO = tr.CODCLI

  ORDER BY cc.ANO_INGRESO_INSTITUCION, cc.RUT, cc.CODCLI_NUEVO;