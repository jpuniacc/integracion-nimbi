-- ============================================================================
-- CONFIGURACIÓN DE FOREIGN DATA WRAPPER PARA MARIADB (ECAMPUS5)
-- ============================================================================

-- 1. Crear el Foreign Server (sin dbname, se especifica en cada tabla)
CREATE SERVER IF NOT EXISTS ecampus5_mariadb
FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (
    host '172.16.1.129',
    port '3306'
);

-- 2. Crear User Mapping (ajusta el usuario según tu necesidad)
-- IMPORTANTE: Reemplaza 'postgres' con el usuario que ejecutará las queries
CREATE USER MAPPING IF NOT EXISTS FOR postgres
SERVER ecampus5_mariadb
OPTIONS (
    username 'ro_user',
    password 'yL14HW0xg5VjGYSr9O0K'
);

-- 3. CREAR FOREIGN TABLES
-- ============================================================================

-- mdl_course
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_course (
    id bigint,
    category bigint,
    fullname text,
    shortname text,
    startdate bigint,
    visible smallint,
    format text
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_course'
);

-- mdl_context
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_context (
    id bigint,
    contextlevel bigint,
    instanceid bigint,
    path text,
    depth smallint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_context'
);

-- mdl_role_assignments
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_role_assignments (
    id bigint,
    roleid bigint,
    contextid bigint,
    userid bigint,
    timemodified bigint,
    modifierid bigint,
    component text,
    itemid bigint,
    sortorder bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_role_assignments'
);

-- mdl_user
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_user (
    id bigint,
    username text,
    password text,
    firstname text,
    lastname text,
    email text,
    deleted smallint,
    suspended smallint,
    timecreated bigint,
    timemodified bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_user'
);

-- mdl_course_categories
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_course_categories (
    id bigint,
    name text,
    idnumber text,
    description text,
    parent bigint,
    sortorder bigint,
    coursecount bigint,
    visible smallint,
    timemodified bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_course_categories'
);

-- mdl_course_modules
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_course_modules (
    id bigint,
    course bigint,
    module bigint,
    instance bigint,
    section bigint,
    idnumber text,
    added bigint,
    score smallint,
    indent integer,
    visible smallint,
    visibleoncoursepage smallint,
    visibleold smallint,
    groupmode smallint,
    groupingid bigint,
    completion smallint,
    completionview smallint,
    completionexpected bigint,
    showdescription smallint,
    availability text,
    deletioninprogress smallint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_course_modules'
);

-- mdl_course_sections
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_course_sections (
    id bigint,
    course bigint,
    section integer,
    name text,
    summary text,
    summaryformat smallint,
    sequence text,
    visible smallint,
    availability text,
    timemodified bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_course_sections'
);

-- mdl_modules
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_modules (
    id bigint,
    name text,
    cron bigint,
    lastcron bigint,
    search text,
    visible smallint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_modules'
);

-- mdl_assign
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_assign (
    id bigint,
    course bigint,
    name text,
    intro text,
    introformat smallint,
    alwaysshowdescription smallint,
    nosubmissions smallint,
    submissiondrafts smallint,
    sendnotifications smallint,
    sendlatenotifications smallint,
    sendstudentnotifications smallint,
    duedate bigint,
    allowsubmissionsfromdate bigint,
    grade bigint,
    timemodified bigint,
    requiresubmissionstatement smallint,
    completionsubmit smallint,
    cutoffdate bigint,
    gradingduedate bigint,
    teamsubmission smallint,
    requireallteammemberssubmit smallint,
    teamsubmissiongroupingid bigint,
    blindmarking smallint,
    hidegrader smallint,
    revealidentities smallint,
    attemptreopenmethod text,
    maxattempts integer,
    markingworkflow smallint,
    markingallocation smallint,
    showonlyactiveenrol_option smallint,
    coursemodule bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_assign'
);

-- mdl_quiz
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_quiz (
    id bigint,
    course bigint,
    name text,
    intro text,
    introformat smallint,
    timeopen bigint,
    timeclose bigint,
    timelimit bigint,
    overduehandling text,
    graceperiod bigint,
    preferredbehaviour text,
    canredoquestions smallint,
    attempts integer,
    attemptonlast smallint,
    grademethod smallint,
    decimalpoints smallint,
    questiondecimalpoints smallint,
    reviewattempt smallint,
    reviewcorrectness smallint,
    reviewmarks smallint,
    reviewspecificfeedback smallint,
    reviewgeneralfeedback smallint,
    reviewrightanswer smallint,
    reviewoverallfeedback smallint,
    questionsperpage bigint,
    navmethod text,
    shufflestructure smallint,
    sumgrades decimal(10,5),
    grade decimal(10,5),
    timecreated bigint,
    timemodified bigint,
    password text,
    subnet text,
    browsersecurity text,
    delay1 integer,
    delay2 integer,
    showuserpicture smallint,
    showblocks smallint,
    completionattemptsexhausted smallint,
    completionpass smallint,
    allowofflineattempts smallint,
    coursemodule bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_quiz'
);

-- mdl_questionnaire
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_questionnaire (
    id bigint,
    course bigint,
    name text,
    intro text,
    introformat smallint,
    qtype smallint,
    respondenttype text,
    resp_eligible text,
    resp_view smallint,
    opendate bigint,
    closedate bigint,
    resumed smallint,
    navigate smallint,
    grade bigint,
    timemodified bigint,
    completionsubmit smallint,
    autonum smallint,
    coursemodule bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_questionnaire'
);

-- mdl_forum
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_forum (
    id bigint,
    course bigint,
    type text,
    name text,
    intro text,
    introformat smallint,
    assessed bigint,
    assesstimestart bigint,
    assesstimefinish bigint,
    scale bigint,
    maxbytes bigint,
    maxattachments bigint,
    forcesubscribe smallint,
    trackingtype smallint,
    rsstype smallint,
    rssarticles smallint,
    timemodified bigint,
    warnafter bigint,
    blockafter bigint,
    blockperiod bigint,
    completiondiscussions smallint,
    completionreplies smallint,
    completionposts smallint,
    cmid bigint,
    coursemodule bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_forum'
);

-- mdl_grade_grades
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_grade_grades (
    id bigint,
    itemid bigint,
    userid bigint,
    rawgrade decimal(10,5),
    rawgrademax decimal(10,5),
    rawgrademin decimal(10,5),
    rawscaleid bigint,
    usermodified bigint,
    finalgrade decimal(10,5),
    hidden bigint,
    locked bigint,
    locktime bigint,
    exported bigint,
    overridden bigint,
    excluded bigint,
    feedback text,
    feedbackformat smallint,
    information text,
    informationformat smallint,
    timecreated bigint,
    timemodified bigint,
    aggregationstatus text,
    aggregationweight decimal(10,5)
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_grade_grades'
);

-- mdl_grade_items
CREATE FOREIGN TABLE IF NOT EXISTS fdw_mdl_grade_items (
    id bigint,
    courseid bigint,
    categoryid bigint,
    itemname text,
    itemtype text,
    itemmodule text,
    iteminstance bigint,
    itemnumber bigint,
    iteminfo text,
    idnumber text,
    calculation text,
    gradetype smallint,
    grademax decimal(10,5),
    grademin decimal(10,5),
    scaleid bigint,
    outcomeid bigint,
    gradepass decimal(10,5),
    multfactor decimal(10,5),
    plusfactor decimal(10,5),
    aggregationcoef decimal(10,5),
    aggregationcoef2 decimal(10,5),
    sortorder bigint,
    display decimal(10,5),
    decimals smallint,
    hidden bigint,
    locked bigint,
    locktime bigint,
    needsupdate bigint,
    weightoverride smallint,
    timecreated bigint,
    timemodified bigint
) SERVER ecampus5_mariadb
OPTIONS (
    dbname 'uniacc01',
    table_name 'mdl_grade_items'
);

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

-- Para verificar que las foreign tables se crearon correctamente:
-- SELECT * FROM fdw_mdl_course LIMIT 1;

