--02. Encuestas docentes (ConectorIntegración) - Por Año
DECLARE @fecha_corte VARCHAR(10) = CONVERT(VARCHAR(10), GETDATE(), 23);

SELECT
    NOMBRE_ENCUESTA,
    ANO as ANIO,
    PERIODO,
    NRO_PREGUNTA,
    PREGUNTA,
    CODRAMO,
    NOMBRE_RAMO,
    SECCION_RAMO,
    CODCARR,
    NOMBRE_CARRERA,
    RUT_DOCENTE,
    NOMBRE_DOCENTE,
    CODCLI,
    NOMBRE_USUARIO + '@uniacc.edu' as NOMBRE_USUARIO,
    CODRESPUESTA,
    ID_RESP,
    RESPUESTA,
    OPCION,
    TEXTOLIBRE,
    OBSERVACION,
    JORNADA,
    MODALIDAD,
    NIVEL_GLOBAL,
    @fecha_corte AS FECHA_CORTE
FROM ConectorIntegracion.dbo.PR_ENCUESTAS WITH (NOLOCK)
WHERE NIVEL_GLOBAL = 'PREGRADO'
    AND ANO = 2022;  -- Cambiar por cada año: 2022, 2023, 2024, 2025

-- Para exportar cada año:
-- ANO = 2025 → encuestas_2025.csv (752,011 registros)
-- ANO = 2024 → encuestas_2024.csv (958,254 registros)
-- ANO = 2023 → encuestas_2023.csv (909,909 registros)
-- ANO = 2022 → encuestas_2022.csv (554,607 registros)