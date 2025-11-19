SELECT
    b.CODCLI,
    d.nombre_l AS NOMBRE_CARRERA,
    d.CODPESTUD AS CODIGO_PLAN,
    b.codcarpr AS COD_CARRERA,
    CASE b.JORNADA
    WHEN 'AD' THEN 'A DISTANCIA'
    WHEN 'D'  THEN 'DIURNO'
    WHEN 'S'  THEN 'SEMIPRESENCIAL'
    WHEN 'V'  THEN 'VESPERTINO'
    ELSE NULL
    END AS JORNADA,
    g.descripcion AS MODALIDAD,
    b.estacad AS ESTADO_ACADEMICO,
    (SELECT MIN(ANO) FROM uniacc.dbo.MT_ALUMNO Z WHERE Z.RUT=B.RUT) AS ANO_INGRESO_INSTITUCION,
    (SELECT descripcion FROM uniacc.dbo.MT_TIPOCARR x WHERE x.tipocarr=d.tipocarr) AS TIPO_CARRERA,
    COALESCE(NULLIF(LTRIM(RTRIM(
        CASE
            WHEN b.estacad IN ('VIGENTE','EGRESADO','TITULADO') THEN ''
            ELSE (
                SELECT TOP 1 SUBSTRING(CAST(100+x.tipositu AS VARCHAR),2,2)+'-'+y.DESCRIPCION
                FROM uniacc.dbo.ra_situ x
                JOIN uniacc.dbo.RA_TIPOSITU y ON x.TIPOSITU=y.codigo
                WHERE x.codcli=b.codcli AND y.estacad=b.estacad AND x.ano=b.ano_mat
            )
        END
    )), ''), 'ALUMNO REGULAR') AS SITUACION,
    CASE
        WHEN b.estacad = 'VIGENTE' THEN 'AVANCE ACADEMICO'
        WHEN b.estacad IN ('ELIMINADO', 'SUSPENDIDO') THEN 'REINGRESO'
        ELSE 'SIN CLASIFICAR'
    END AS TIPO_SEGUIMIENTO,
CONVERT(VARCHAR(10), GETDATE(), 23) AS FECHA_CORTE
FROM uniacc.dbo.MT_ALUMNO b
JOIN uniacc.dbo.MT_CLIENT c ON b.RUT = c.codcli
JOIN uniacc.dbo.mt_carrer d ON b.codcarpr = d.codcarr
JOIN uniacc.dbo.ra_modalidad g ON d.modalidad = g.codigo
WHERE (SELECT MIN(ANO) FROM uniacc.dbo.MT_ALUMNO Z WHERE Z.RUT=B.RUT) >= 2022
  AND (SELECT descripcion FROM uniacc.dbo.MT_TIPOCARR x WHERE x.tipocarr=d.tipocarr) = 'PREGRADO'
  AND b.estacad IN ('VIGENTE', 'ELIMINADO', 'SUSPENDIDO')
ORDER BY ANO_INGRESO_INSTITUCION DESC, b.CODCLI;
