#!/usr/bin/env python3
"""
Script para actualizar encuestas docentes desde SQL Server a PostgreSQL
Ejecuta la query 3_encuenta_docente.sql (o la ruta de SQL_FILE_ENCUESTA) y carga los datos
NOTA: Esta tabla tiene alto volumen (~3.1M registros)
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

# Cargar .env del proyecto
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parent
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
    """Lee el archivo SQL con la query y la modifica para obtener todos los años"""
    # Ruta dentro del repo o desde variable de entorno SQL_FILE_ENCUESTA
    sql_from_env = os.getenv('SQL_FILE_ENCUESTA')
    if sql_from_env:
        query_file = Path(sql_from_env)
    else:
        # Nombre de archivo en repo: 3_encuenta_docente.sql
        query_file = REPO_ROOT / "sql/3_encuenta_docente.sql"
    
    if not query_file.exists():
        raise FileNotFoundError(f"No se encuentra el archivo: {query_file}")
    
    with open(query_file, 'r', encoding='utf-8') as f:
        query = f.read()
    
    # Quitar la declaración de variable (no funciona con pyodbc)
    # y reemplazar @fecha_corte directamente en el SELECT
    fecha_hoy = date.today().strftime("%Y-%m-%d")
    
    # Limpiar y modificar la query
    query = query.replace("DECLARE @fecha_corte VARCHAR(10) = CONVERT(VARCHAR(10), GETDATE(), 23);", "")
    query = query.replace("@fecha_corte", f"'{fecha_hoy}'")
    
    # Cambiar para obtener TODOS los años desde 2022
    query = query.replace("AND ANO = 2022;", "AND ANO >= 2022;")
    
    # Limpiar comentarios finales
    lines = query.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip().startswith('-- Para exportar'):
            break
        clean_lines.append(line)
    
    query = '\n'.join(clean_lines).strip()
    
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
    log("⚠ ADVERTENCIA: Esta tabla tiene alto volumen (~3M registros)")
    log("⚠ Este proceso puede tomar entre 10-20 minutos")
    
    conn = conectar_sqlserver()
    cursor = conn.cursor()
    
    try:
        inicio = time.time()
        cursor.execute(query)
        
        # Obtener nombres de columnas (respetar alias exactamente)
        columnas = [column[0] for column in cursor.description]
        
        # Obtener todos los registros con progreso mejorado
        datos = []
        count = 0
        while True:
            rows = cursor.fetchmany(5000)  # Batch más grande para mejor rendimiento
            if not rows:
                break
            datos.extend(rows)
            count += len(rows)
            
            # Mostrar progreso cada 50,000 registros
            if count % 50000 == 0:
                elapsed = time.time() - inicio
                rate = count / elapsed
                log(f"  → Extraídos {count:,} registros... ({rate:.0f} reg/seg)")
        
        duracion = time.time() - inicio
        log(f"✓ Extracción completada: {len(datos):,} registros en {duracion:.2f} segundos")
        
        return datos, columnas
        
    except Exception as e:
        log(f"✗ Error al extraer datos: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

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
        log('Limpiando tabla nimbi."03_encuesta_docente"...')
        cursor.execute('TRUNCATE TABLE nimbi."03_encuesta_docente" RESTART IDENTITY CASCADE;')
        conn.commit()
        
        # Preparar los datos - La fecha_corte ya viene en los datos de SQL Server
        log("Preparando datos para inserción...")
        log(f"Total de registros a insertar: {len(datos):,}")
        
        # Query de inserción
        insert_query = f"""
        INSERT INTO nimbi."03_encuesta_docente" (
            {', '.join(columnas)}
        ) VALUES %s
        """
        
        # Insertar datos en lotes grandes (optimizado para volumen alto)
        log("Insertando datos en PostgreSQL...")
        log("⚠ Este proceso puede tomar 10-15 minutos...")
        batch_size = 5000  # Batch más grande para mejor rendimiento
        total_insertados = 0
        inicio_insercion = time.time()
        
        for i in range(0, len(datos), batch_size):
            batch = datos[i:i + batch_size]
            execute_values(cursor, insert_query, batch)
            conn.commit()
            total_insertados += len(batch)
            
            # Mostrar progreso cada 50,000 registros
            if total_insertados % 50000 == 0 or total_insertados == len(datos):
                elapsed = time.time() - inicio_insercion
                rate = total_insertados / elapsed if elapsed > 0 else 0
                porcentaje = (total_insertados / len(datos)) * 100
                log(f"  → Insertados {total_insertados:,}/{len(datos):,} ({porcentaje:.1f}%) - {rate:.0f} reg/seg")
        
        # Verificar total
        cursor.execute('SELECT COUNT(*) FROM nimbi."03_encuesta_docente";')
        total_en_bd = cursor.fetchone()[0]
        
        log(f"✓ Carga completada exitosamente!")
        log(f"✓ Total de registros en la tabla: {total_en_bd:,}")
        
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
    log("ACTUALIZACIÓN ENCUESTAS DOCENTES: SQL SERVER → POSTGRESQL")
    log("=" * 70)
    log("⚠ TABLA DE ALTO VOLUMEN: ~3.1 MILLONES DE REGISTROS")
    log("=" * 70)
    
    inicio = time.time()
    
    try:
        # 1. Leer query SQL
        log("\n1. Leyendo archivo SQL...")
        query = leer_query_sql()
        log("✓ Query cargada y modificada para todos los años (2022+)")
        
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
        minutos = duracion / 60
        log("\n" + "=" * 70)
        log("RESUMEN FINAL")
        log("=" * 70)
        log(f"✓ Registros extraídos de SQL Server: {len(datos):,}")
        log(f"✓ Registros en PostgreSQL: {total:,}")
        log(f"✓ Tiempo total: {duracion:.2f} segundos ({minutos:.2f} minutos)")
        log(f"✓ Velocidad promedio: {len(datos)/duracion:.0f} registros/segundo")
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

