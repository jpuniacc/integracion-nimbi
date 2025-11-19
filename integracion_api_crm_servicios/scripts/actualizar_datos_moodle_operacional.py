#!/usr/bin/env python3
"""
Script para actualizar datos Moodle operacional desde SQL Server a PostgreSQL
Ejecuta la query 7_datos_moodle_operacional.sql y carga los datos
"""

import os
import pyodbc
import psycopg2
from psycopg2.extras import execute_values
from datetime import date
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el .env del proyecto
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent  # integracion_api_crm_servicios
REPO_ROOT = PROJECT_DIR.parent   # integracion_nimbi
ENV_PATH = PROJECT_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)

# Configuración de SQL Server (origen) desde .env
SQLSERVER_CONFIG = {
    'server': os.getenv('SQLSERVER_SERVER', '192.168.135.20'),
    'database': os.getenv('SQLSERVER_DATABASE', 'UNIACC'),
    'username': os.getenv('SQLSERVER_USERNAME', 'nimbi'),
    'password': os.getenv('SQLSERVER_PASSWORD', ''),
    'driver': '{' + os.getenv('SQLSERVER_DRIVER', 'ODBC Driver 18 for SQL Server') + '}',
    'encrypt': os.getenv('SQLSERVER_ENCRYPT', 'no'),
    'trust_server_certificate': os.getenv('SQLSERVER_TRUSTSERVERCERTIFICATE', 'no'),
    'port': os.getenv('SQLSERVER_PORT', '1433'),
}

# Configuración de PostgreSQL (destino) desde .env
POSTGRES_CONFIG = {
    'host': os.getenv('DB_HOST', '172.16.0.206'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', '5432')),
}
DB_SEARCH_PATH = os.getenv('DB_SEARCH_PATH', 'nimbi, public')

def log(mensaje):
    """Imprime mensaje con timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def leer_query_sql():
    """Lee el archivo SQL con la query"""
    # Ruta al archivo SQL dentro del repo o variable de entorno SQL_FILE_MOODLE
    sql_from_env = os.getenv('SQL_FILE_MOODLE')
    if sql_from_env:
        query_file = Path(sql_from_env)
    else:
        query_file = REPO_ROOT / "sql/7_datos_moodle_operacional.sql"
    
    if not query_file.exists():
        raise FileNotFoundError(f"No se encuentra el archivo: {query_file}")
    
    with open(query_file, 'r', encoding='utf-8') as f:
        query = f.read().strip()
    
    # Limpiar punto y coma final si existe
    if query.endswith(';'):
        query = query[:-1]
    
    return query

def conectar_sqlserver():
    """Conecta a SQL Server"""
    log("Conectando a SQL Server...")
    
    try:
        # Construir connection string
        conn_str = (
            f"DRIVER={SQLSERVER_CONFIG['driver']};"
            f"SERVER={SQLSERVER_CONFIG['server']},{SQLSERVER_CONFIG['port']};"
            f"DATABASE={SQLSERVER_CONFIG['database']};"
            f"UID={SQLSERVER_CONFIG['username']};"
            f"PWD={SQLSERVER_CONFIG['password']};"
            f"Encrypt={SQLSERVER_CONFIG['encrypt']};"
            f"TrustServerCertificate={SQLSERVER_CONFIG['trust_server_certificate']};"
        )
        
        conn = pyodbc.connect(conn_str, timeout=60)
        log("✓ Conexión a SQL Server exitosa")
        return conn
        
    except Exception as e:
        log(f"✗ Error al conectar a SQL Server: {e}")
        raise

def extraer_datos_sqlserver(query):
    """Extrae datos de SQL Server"""
    log("Extrayendo datos de SQL Server...")
    
    conn = conectar_sqlserver()
    cursor = conn.cursor()
    
    try:
        inicio = time.time()
        cursor.execute(query)
        
        # Obtener nombres de columnas (usar alias exactos tal como vienen del SELECT)
        columnas = [column[0] for column in cursor.description]
        
        # Obtener todos los registros
        datos = []
        while True:
            rows = cursor.fetchmany(1000)
            if not rows:
                break
            datos.extend(rows)
            log(f"  → Extraídos {len(datos)} registros...")
        
        duracion = time.time() - inicio
        log(f"✓ Extracción completada: {len(datos)} registros en {duracion:.2f} segundos")
        
        return datos, columnas
        
    except Exception as e:
        log(f"✗ Error al extraer datos: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def limpiar_datos(datos):
    """Limpia los datos convirtiendo cadenas vacías a None para campos numéricos"""
    datos_limpios = []
    for fila in datos:
        fila_limpia = []
        for valor in fila:
            # Convertir cadenas vacías o espacios en blanco a None
            if isinstance(valor, str) and valor.strip() == '':
                fila_limpia.append(None)
            else:
                fila_limpia.append(valor)
        datos_limpios.append(tuple(fila_limpia))
    return datos_limpios

def cargar_a_postgresql(datos, columnas):
    """Carga los datos a PostgreSQL"""
    log("Conectando a PostgreSQL...")
    
    fecha_corte = date.today()
    log(f"Fecha de corte: {fecha_corte}")
    
    # Conectar a PostgreSQL
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()
    
    try:
        # Establecer el search_path
        cursor.execute("SET search_path TO " + DB_SEARCH_PATH + ";")
        
        # Limpiar la tabla (full refresh)
        log('Limpiando tabla nimbi."07_datos_moodle_operacional"...')
        cursor.execute('TRUNCATE TABLE nimbi."07_datos_moodle_operacional" RESTART IDENTITY CASCADE;')
        conn.commit()
        
        # Preparar los datos - La fecha_corte ya viene en los datos de SQL Server
        log("Preparando datos para inserción...")
        
        # Limpiar datos: convertir cadenas vacías a None
        log("Limpiando datos (convirtiendo cadenas vacías a NULL)...")
        datos_limpios = limpiar_datos(datos)
        
        # Query de inserción
        insert_query = f"""
        INSERT INTO nimbi."07_datos_moodle_operacional" (
            {', '.join(columnas)}
        ) VALUES %s
        """
        
        # Insertar datos en lotes
        log("Insertando datos en PostgreSQL...")
        batch_size = 1000
        total_insertados = 0
        
        for i in range(0, len(datos_limpios), batch_size):
            batch = datos_limpios[i:i + batch_size]
            execute_values(cursor, insert_query, batch)
            conn.commit()
            total_insertados += len(batch)
            log(f"  → Insertados {total_insertados}/{len(datos)} registros...")
        
        # Verificar total
        cursor.execute('SELECT COUNT(*) FROM nimbi."07_datos_moodle_operacional";')
        total_en_bd = cursor.fetchone()[0]
        
        log(f"✓ Carga completada exitosamente!")
        log(f"✓ Total de registros en la tabla: {total_en_bd}")
        
        return total_en_bd
        
    except Exception as e:
        log(f"✗ Error durante la carga: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Función principal"""
    log("=" * 70)
    log("ACTUALIZACIÓN DATOS MOODLE OPERACIONAL: SQL SERVER → POSTGRESQL")
    log("=" * 70)
    
    inicio = time.time()
    
    try:
        # 1. Leer query SQL
        log("\n1. Leyendo archivo SQL...")
        query = leer_query_sql()
        log("✓ Query cargada correctamente")
        
        # 2. Extraer datos de SQL Server
        log("\n2. Extrayendo datos de SQL Server...")
        datos, columnas = extraer_datos_sqlserver(query)
        
        if len(datos) == 0:
            log("⚠ No se extrajeron datos. Abortando.")
            return 1
        
        # 3. Cargar a PostgreSQL
        log("\n3. Cargando datos a PostgreSQL...")
        total = cargar_a_postgresql(datos, columnas)
        
        # 4. Resumen final
        duracion = time.time() - inicio
        log("\n" + "=" * 70)
        log("RESUMEN")
        log("=" * 70)
        log(f"✓ Registros extraídos de SQL Server: {len(datos)}")
        log(f"✓ Registros en PostgreSQL: {total}")
        log(f"✓ Tiempo total: {duracion:.2f} segundos")
        log("=" * 70)
        
        return 0
        
    except Exception as e:
        log(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

