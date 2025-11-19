e#!/bin/bash
# Script para probar la conexión del usuario nimbi_integracion

# Configuración (ajustar según tu entorno)
PGHOST="${PGHOST:-172.16.0.206}"
PGPORT="${PGPORT:-5432}"
PGUSER="nimbi_integracion"
PGDATABASE="postgres"

echo "========================================="
echo "Probando conexión de usuario: nimbi_integracion"
echo "Servidor: $PGHOST:$PGPORT"
echo "Base de datos: $PGDATABASE"
echo "========================================="
echo ""

# Test 1: Verificar conexión y usuario actual
echo "1. Verificando conexión y usuario actual..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT current_user as usuario, current_database() as base_datos, version();" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Conexión exitosa"
else
    echo "❌ Error en la conexión"
    exit 1
fi

echo ""
echo "2. Verificando acceso al esquema nimbi..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'nimbi';" 2>&1

echo ""
echo "3. Verificando permisos en tablas del esquema nimbi..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT table_schema, table_name, privilege_type FROM information_schema.role_table_grants WHERE grantee = 'nimbi_integracion' AND table_schema = 'nimbi' LIMIT 5;" 2>&1

echo ""
echo "4. Probando SELECT en una tabla (si existe)..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT COUNT(*) as total_registros FROM nimbi.\"01_identificadores_y_data_operacional\" LIMIT 1;" 2>&1

echo ""
echo "5. Verificando que NO puede hacer INSERT (debe fallar)..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "CREATE TEMP TABLE test_write (id INT); INSERT INTO test_write VALUES (1);" 2>&1 | grep -i "permission\|error" || echo "⚠️  El usuario podría tener permisos de escritura (revisar)"

echo ""
echo "========================================="
echo "Pruebas completadas"
echo "========================================="

