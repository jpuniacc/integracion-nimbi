-- ============================================================================
-- QUERY ADAPTADA PARA POSTGRESQL CON FOREIGN TABLES
-- Esta es la adaptación de la query original de SQL Server
-- ============================================================================

SELECT   
    COALESCE(cat2.name, '') AS CATEGORIA,   
    COALESCE(cat.name, '') AS SUBCATEGORIA,  
    CASE 
        WHEN cat.idnumber LIKE '%-%' 
        THEN regexp_replace(cat.idnumber, '^.*-', '')  
        ELSE cat.idnumber 
    END AS cod_carrera,  
    cs.id AS IDCOURSE,  
    u2.id AS USERID_DOCENTE,  
    COALESCE(CONCAT(u2.lastname, ' ', u2.firstname), '') AS DOCENTE,  
    u2.email AS EMAIL_DOCENTE,  
    cs.fullname AS ASIGNATURA,  
    to_timestamp(cs.startdate) AS FECHA_INICIO_CURSO,  
    sec.section AS SEMANA_UNIDAD,  
    u.id AS USERID_ALUMNO,  
    COALESCE(CONCAT(u.lastname, ' ', u.firstname), '') AS ALUMNO,  
    u.email AS EMAIL_ALUMNO,  
    cs.visible AS CURSO_VISIBLE,  
    cs.format AS FORMATO_CURSO,  
    cm.instance,  
    cm.id AS id_course_module,  
    COALESCE(
        CASE 
            WHEN dsd.name LIKE '%foro%' THEN 'forum' 
            ELSE dsd.modulo 
        END, 
        ''
    ) AS modulo,  
    dsd.id,  
    dsd.name,  
    COALESCE(dsd.FECHA_INICIO_TAREA, '') AS FECHA_INICIO_TAREA,  
    COALESCE(dsd.FECHA_ENTREGA_TAREA, '') AS FECHA_ENTREGA_TAREA,  
    COALESCE(dsd.FECHA_LIMITE, '') AS FECHA_LIMITE,  
    COALESCE(dsd.ESCALA_Puntuacion, '') AS ESCALA_Puntuacion,  
    notas.finalgrade,  
    COALESCE(notas.CALIFICADO, 'NO') AS CALIFICADO,  
    COALESCE(notas.FECHA_CALIFICADO, '') AS FECHA_CALIFICADO  
FROM fdw_mdl_course cs  
LEFT JOIN fdw_mdl_context c ON c.instanceid = cs.id AND c.contextlevel = 50  -- 50 = course context
LEFT JOIN fdw_mdl_role_assignments ra ON ra.contextid = c.id  
LEFT JOIN fdw_mdl_user u ON u.id = ra.userid  
LEFT JOIN fdw_mdl_context c2 ON c2.instanceid = cs.id AND c2.contextlevel = 50
LEFT JOIN fdw_mdl_role_assignments ra2 ON ra2.contextid = c2.id AND ra2.roleid = 4  
LEFT JOIN fdw_mdl_user u2 ON u2.id = ra2.userid  
LEFT JOIN fdw_mdl_course_categories cat ON cat.id = cs.category  
LEFT JOIN fdw_mdl_course_categories cat2 ON cat2.id = cat.parent  
LEFT JOIN fdw_mdl_course_modules cm ON cm.course = cs.id  
LEFT JOIN fdw_mdl_course_sections sec ON sec.id = cm.section  
LEFT JOIN fdw_mdl_modules m ON m.id = cm.module  
LEFT JOIN (  
    SELECT 
        'assign' AS modulo, 
        ass.id, 
        ass.name,  
        CASE 
            WHEN ass.allowsubmissionsfromdate = 0 THEN 'Sin fecha' 
            ELSE to_char(to_timestamp(ass.allowsubmissionsfromdate), 'YYYY-MM-DD HH24:MI:SS')
        END AS FECHA_INICIO_TAREA,  
        CASE 
            WHEN ass.duedate = 0 THEN 'Sin fecha' 
            ELSE to_char(to_timestamp(ass.duedate), 'YYYY-MM-DD HH24:MI:SS')
        END AS FECHA_ENTREGA_TAREA,  
        CASE 
            WHEN ass.cutoffdate = 0 THEN 'Sin fecha' 
            ELSE to_char(to_timestamp(ass.cutoffdate), 'YYYY-MM-DD HH24:MI:SS')
        END AS FECHA_LIMITE,  
        CASE 
            WHEN ass.grade > 0 THEN CONCAT('Puntuación ', ass.grade::text)
            WHEN ass.grade = 0 THEN 'Ninguna'  
            ELSE 'Escala desconocida' 
        END AS ESCALA_Puntuacion  
    FROM fdw_mdl_assign ass  

    UNION ALL

    SELECT 
        'quiz', 
        id, 
        name,  
        CASE 
            WHEN timeopen = 0 THEN 'Sin fecha' 
            ELSE to_char(to_timestamp(timeopen), 'YYYY-MM-DD HH24:MI:SS')
        END,  
        CASE 
            WHEN timeclose = 0 THEN 'Sin fecha' 
            ELSE to_char(to_timestamp(timeclose), 'YYYY-MM-DD HH24:MI:SS')
        END,  
        'Sin fecha',  
        ' '  
    FROM fdw_mdl_quiz  

    UNION ALL

    SELECT 
        'questionnaire', 
        ass.id, 
        ass.name,  
        CASE 
            WHEN opendate = 0 THEN 'Sin fecha' 
            ELSE to_char(to_timestamp(opendate), 'YYYY-MM-DD HH24:MI:SS')
        END,  
        CASE 
            WHEN closedate = 0 THEN 'Sin fecha' 
            ELSE to_char(to_timestamp(closedate), 'YYYY-MM-DD HH24:MI:SS')
        END,  
        'Sin fecha',  
        CASE 
            WHEN grade > 0 THEN CONCAT('Puntuación ', grade::text)
            WHEN grade = 0 THEN 'Ninguna'  
            ELSE 'Escala desconocida' 
        END  
    FROM fdw_mdl_questionnaire ass  

    UNION ALL

    SELECT 
        'forum', 
        id, 
        name,  
        'Sin fecha', 
        'Sin fecha', 
        'Sin fecha', 
        ' '  
    FROM fdw_mdl_forum  

) dsd ON cm.instance = dsd.id AND m.name = dsd.modulo  

LEFT JOIN (  
    SELECT 
        gr.itemid,  
        CASE 
            WHEN gi.itemtype = 'course' THEN 'Nota Final' 
            ELSE gi.itemname 
        END AS itemname,  
        gr.userid AS USERNOTA, 
        gr.rawscaleid,  
        CAST(gr.finalgrade AS DECIMAL(4,1)) AS finalgrade,  
        gi.courseid AS COURSENOTA,  
        gi.iteminstance AS ITEMINSTANCE_NOTA,  
        gi.itemmodule,  
        CASE 
            WHEN gr.finalgrade IS NULL THEN 'NO' 
            ELSE 'SI' 
        END AS CALIFICADO,  
        CASE 
            WHEN gr.finalgrade IS NULL THEN NULL 
            ELSE to_char(to_timestamp(gr.timemodified), 'YYYY-MM-DD HH24:MI:SS')
        END AS FECHA_CALIFICADO  
    FROM fdw_mdl_grade_grades gr  
    LEFT JOIN fdw_mdl_grade_items gi ON gi.id = gr.itemid  
    WHERE (gi.itemmodule IN ('assign', 'forum', 'quiz', 'questionnaire') 
           OR gi.itemtype = 'course')  

) notas ON notas.USERNOTA = u.id 
       AND notas.ITEMINSTANCE_NOTA = cm.instance 
       AND notas.COURSENOTA = cs.id  

WHERE ra.roleid = 5  
    AND cs.visible = 1  
    AND u.deleted = 0  
    AND cm.visible = 1  
    AND sec.visible = 1  
    AND m.name IN ('assign', 'forum', 'quiz', 'questionnaire')  
    AND u2.id IS NOT NULL  
    AND u.username NOT LIKE '%alumno%'  
    AND sec.section > 0;

