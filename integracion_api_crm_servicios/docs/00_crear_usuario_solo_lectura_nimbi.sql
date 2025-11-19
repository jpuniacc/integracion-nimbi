-- ============================================
-- Script para crear usuario de solo lectura
-- Esquema: nimbi
-- ============================================

-- 1. Crear el usuario (cambiar 'password_segura' por valores reales)
-- IMPORTANTE: Cambiar la contraseña antes de ejecutar
CREATE USER nimbi_integracion WITH PASSWORD 'N1mbi_2025.,@';

-- 2. Otorgar privilegios de conexión a la base de datos
GRANT CONNECT ON DATABASE postgres TO nimbi_integracion;

-- 3. Otorgar privilegios de uso del esquema nimbi
GRANT USAGE ON SCHEMA nimbi TO nimbi_integracion;

-- 4. Otorgar privilegios de solo lectura en todas las tablas del esquema nimbi
-- Para tablas existentes
GRANT SELECT ON ALL TABLES IN SCHEMA nimbi TO nimbi_integracion;

-- 5. Otorgar privilegios de solo lectura en tablas futuras (default privilege)
-- Esto asegura que las nuevas tablas también tengan permisos de lectura
ALTER DEFAULT PRIVILEGES IN SCHEMA nimbi 
    GRANT SELECT ON TABLES TO nimbi_integracion;

-- 6. Otorgar privilegios de uso en secuencias (si hay alguna)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA nimbi TO nimbi_integracion;
ALTER DEFAULT PRIVILEGES IN SCHEMA nimbi 
    GRANT USAGE, SELECT ON SEQUENCES TO nimbi_integracion;

-- 7. Verificar los privilegios otorgados
-- Ejecutar esto después para verificar:
-- SELECT table_schema, table_name, privilege_type 
-- FROM information_schema.role_table_grants 
-- WHERE grantee = 'nimbi_integracion' AND table_schema = 'nimbi';

-- NOTAS IMPORTANTES:
-- - El usuario solo podrá hacer SELECT en las tablas del esquema nimbi
-- - No podrá INSERT, UPDATE, DELETE, TRUNCATE, ni DROP
-- - No tendrá acceso a otros esquemas a menos que se otorguen permisos explícitos
-- - Cambiar la contraseña antes de ejecutar este script

