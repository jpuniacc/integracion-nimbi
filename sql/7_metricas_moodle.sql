-- ========================================
-- MÉTRICAS DE MOODLE PARA MODELO
-- Calcula métricas agregadas por estudiante/periodo
-- Basado en la tabla nimbi."07_datos_moodle_operacional"
-- ========================================

WITH InteraccionesPorCurso AS (
    -- Agregar por curso para calcular métricas por curso
    SELECT 
        CODCLI,
        ANIO_CURSO,
        PERIODO,
        ID_CURSO,
        
        -- Total de posteos en foros (es constante por estudiante/curso, tomar máximo)
        COALESCE(MAX(CANTIDAD_POSTEOS), 0) as total_posteos,
        
        -- Actividades completadas (con estado calificado SI o con nota)
        SUM(CASE 
            WHEN ESTADO_CALIFICADO = 'SI' OR NOTA IS NOT NULL 
            THEN 1 
            ELSE 0 
        END) as actividades_completadas,
        
        -- Total de interacciones por curso (posteos + actividades completadas)
        COALESCE(MAX(CANTIDAD_POSTEOS), 0) + 
        SUM(CASE 
            WHEN ESTADO_CALIFICADO = 'SI' OR NOTA IS NOT NULL 
            THEN 1 
            ELSE 0 
        END) as total_interacciones_curso,
        
        -- Proxy de visitas: contar actividades únicas por curso
        COUNT(DISTINCT NOMBRE_ACTIVIDAD) as proxy_visitas_curso,
        
        -- Semanas del curso (días / 7)
        MAX(CEILING(CAST(DIAS_DURACION_CURSO AS FLOAT) / 7.0)) as semanas_curso,
        
        -- Flags por curso
        MAX(CASE 
            WHEN TIPO_MODULO = 'forum' 
                AND (CANTIDAD_POSTEOS > 0 OR ESTADO_CALIFICADO = 'SI') 
            THEN 1 
            ELSE 0 
        END) as ha_interactuado_foros_curso,
        
        MAX(CASE 
            WHEN TIPO_MODULO = 'assign' 
                AND ESTADO_CALIFICADO = 'SI' 
            THEN 1 
            ELSE 0 
        END) as ha_enviado_tareas_curso,
        
        MAX(CASE 
            WHEN TIPO_MODULO = 'quiz' 
                AND ESTADO_CALIFICADO = 'SI' 
            THEN 1 
            ELSE 0 
        END) as ha_respondido_quiz_curso
        
    FROM nimbi."07_datos_moodle_operacional"
    WHERE CODCLI IS NOT NULL
        AND ANIO_CURSO IS NOT NULL
        AND PERIODO IS NOT NULL
        AND ID_CURSO IS NOT NULL
    GROUP BY CODCLI, ANIO_CURSO, PERIODO, ID_CURSO
),
MetricasAgregadas AS (
    -- Agregar por estudiante/periodo (sumando todos los cursos)
    SELECT 
        CODCLI,
        ANIO_CURSO,
        PERIODO,
        
        -- Número de cursos del estudiante en el periodo
        COUNT(DISTINCT ID_CURSO) as num_cursos,
        
        -- Totales de interacciones y visitas (sumando todos los cursos)
        SUM(total_interacciones_curso) as total_interacciones_todos_cursos,
        SUM(proxy_visitas_curso) as total_visitas_todos_cursos,
        
        -- Promedio de semanas entre todos los cursos del estudiante
        -- Si hay múltiples cursos con diferentes duraciones, usamos el promedio
        AVG(semanas_curso) as promedio_semanas,
        
        -- Flags agregados (máximo = OR lógico: si ocurrió en al menos un curso)
        MAX(ha_interactuado_foros_curso) as ha_interactuado_en_foros,
        MAX(ha_enviado_tareas_curso) as ha_enviado_tareas,
        MAX(ha_respondido_quiz_curso) as ha_respondido_quiz
        
    FROM InteraccionesPorCurso
    GROUP BY CODCLI, ANIO_CURSO, PERIODO
)
SELECT 
    CODCLI,
    ANIO_CURSO,
    PERIODO,
    
    -- Métricas promedio semanal
    -- Fórmula: SUM(interacciones) / (Número de cursos * Promedio de semanas)
    -- Cuando hay múltiples cursos con diferentes duraciones, usamos el promedio de semanas
    CASE 
        WHEN num_cursos * promedio_semanas > 0 
        THEN CAST(total_interacciones_todos_cursos AS FLOAT) / (num_cursos * promedio_semanas)
        ELSE 0 
    END as interacciones_promedio_semanal_por_curso,
    
    CASE 
        WHEN num_cursos * promedio_semanas > 0 
        THEN CAST(total_visitas_todos_cursos AS FLOAT) / (num_cursos * promedio_semanas)
        ELSE 0 
    END as visitas_curso_promedio_semanal_por_curso,
    
    -- Cambio interno (no disponible, NULL)
    NULL::TEXT as cambio_interno,
    
    -- Flags booleanos
    CASE WHEN ha_interactuado_en_foros = 1 THEN TRUE ELSE FALSE END as ha_interactuado_en_foros,
    CASE WHEN ha_enviado_tareas = 1 THEN TRUE ELSE FALSE END as ha_enviado_tareas,
    CASE WHEN ha_respondido_quiz = 1 THEN TRUE ELSE FALSE END as ha_respondido_quiz,
    
    -- Campos adicionales para referencia/debugging (opcionales, pueden comentarse)
    num_cursos,
    total_interacciones_todos_cursos,
    total_visitas_todos_cursos,
    promedio_semanas
    
FROM MetricasAgregadas
ORDER BY CODCLI, ANIO_CURSO, PERIODO;

