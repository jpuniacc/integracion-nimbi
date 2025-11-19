#!/usr/bin/env python3
"""
Script para actualizar beneficios de alumnos desde SQL Server a PostgreSQL
Ejecuta la query 5_beneficios_alumnos.sql, carga los datos,
genera un archivo CSV con formato cliente Nimbi y lo sube al servidor SFTP
"""

import os
import pyodbc
import psycopg2
from psycopg2.extras import execute_values
from datetime import date
import time
import sys
import re
import pandas as pd
import paramiko
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

# Configuración de CSV (formato Nimbi)
CSV_CONFIG = {
    'encoding': 'utf-8',
    'separator': ';',
    'include_index': False,
    'quoting': 1,  # QUOTE_ALL - Comillas dobles en todos los campos
    'na_rep': '',  # Valores NULL como cadena vacía
}

# Directorio para archivos CSV temporales
TEMP_CSV_DIR = PROJECT_DIR / 'temp_csv'
TEMP_CSV_DIR.mkdir(exist_ok=True)

# Nombre del archivo CSV de salida
CSV_OUTPUT_NAME = "05_beneficios_alumnos.csv"

# Configuración SFTP (desde .env o valores por defecto)
SFTP_CONFIG = {
    'host': os.getenv('SFTP_HOST', '192.168.135.15'),
    'user': os.getenv('SFTP_USER', 'nimbi'),
    'password': os.getenv('SFTP_PASSWORD', 'n1mb1..25'),
    'port': int(os.getenv('SFTP_PORT', '22')),
    'upload_path': '/sftp/nimbi/',  # Ruta destino en el servidor SFTP
    'timeout': int(os.getenv('SFTP_TIMEOUT', '600')),  # 10 minutos
}

def log(mensaje):
    """Imprime mensaje con timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def leer_query_sql():
    """Lee el archivo SQL con la query"""
    # Ruta dentro del repo o variable de entorno SQL_FILE_BENEFICIOS
    sql_from_env = os.getenv('SQL_FILE_BENEFICIOS')
    if sql_from_env:
        query_file = Path(sql_from_env)
    else:
        query_file = REPO_ROOT / "sql/5_beneficios_alumnos.sql"
    
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
        
        conn = pyodbc.connect(conn_str, timeout=30)
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
        
        # Obtener nombres de columnas tal cual vienen del SELECT (respetar alias)
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
        log('Limpiando tabla nimbi."05_beneficios_alumnos"...')
        cursor.execute('TRUNCATE TABLE nimbi."05_beneficios_alumnos" RESTART IDENTITY CASCADE;')
        conn.commit()
        
        # Preparar los datos - La fecha_corte ya viene en los datos de SQL Server
        log("Preparando datos para inserción...")
        
        # Query de inserción
        insert_query = f"""
        INSERT INTO nimbi."05_beneficios_alumnos" (
            {', '.join(columnas)}
        ) VALUES %s
        """
        
        # Insertar datos en lotes
        log("Insertando datos en PostgreSQL...")
        batch_size = 1000
        total_insertados = 0
        
        for i in range(0, len(datos), batch_size):
            batch = datos[i:i + batch_size]
            execute_values(cursor, insert_query, batch)
            conn.commit()
            total_insertados += len(batch)
            log(f"  → Insertados {total_insertados}/{len(datos)} registros...")
        
        # Verificar total
        cursor.execute('SELECT COUNT(*) FROM nimbi."05_beneficios_alumnos";')
        total_en_bd = cursor.fetchone()[0]
        
        log(f"✓ Carga completada exitosamente!")
        log(f"✓ Total de registros en la tabla: {total_en_bd}")
        
        return total_en_bd, conn
        
    except Exception as e:
        log(f"✗ Error durante la carga: {e}")
        conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            conn.close()  # Cerrar conexión en caso de error
        raise
    finally:
        # Solo cerrar cursor si no hubo error (la conexión se retorna)
        if cursor and not cursor.closed:
            pass  # No cerrar aquí, se retorna la conexión

def limpiar_backslashes_csv(archivo_path: Path):
    """Limpiar backslashes innecesarios del archivo CSV generado"""
    try:
        # Leer el archivo completo
        with open(archivo_path, 'r', encoding=CSV_CONFIG['encoding']) as f:
            contenido = f.read()
        
        # Contar backslashes antes de la limpieza
        backslashes_antes = contenido.count('\\')
        
        if backslashes_antes > 0:
            # Eliminar backslashes que preceden a punto y coma (escape innecesario)
            contenido_limpio = contenido.replace('\\;', ';')
            
            # Eliminar backslashes problemáticos usando regex
            contenido_limpio = re.sub(r';\\([^;])', r';\1', contenido_limpio)  # Después de ;
            contenido_limpio = re.sub(r'([^\\])\\;', r'\1;', contenido_limpio)  # Antes de ;
            contenido_limpio = re.sub(r'\\$', '', contenido_limpio, flags=re.MULTILINE)  # Final de línea
            contenido_limpio = re.sub(r'^\\', '', contenido_limpio, flags=re.MULTILINE)  # Inicio de línea
            
            # Contar backslashes después de la limpieza
            backslashes_despues = contenido_limpio.count('\\')
            eliminados = backslashes_antes - backslashes_despues
            
            if eliminados > 0:
                # Guardar el contenido limpio
                with open(archivo_path, 'w', encoding=CSV_CONFIG['encoding']) as f:
                    f.write(contenido_limpio)
                
                log(f"✓ Limpieza CSV: {eliminados} backslashes innecesarios removidos")
            else:
                log("✓ CSV ya limpio, sin backslashes problemáticos")
        else:
            log("✓ CSV sin backslashes, no requiere limpieza")
            
    except Exception as e:
        log(f"⚠ Advertencia en limpieza de backslashes: {e}")
        # No lanzar excepción, el CSV original sigue siendo válido

def generar_csv_nimbi(conn, columnas):
    """Genera archivo CSV con formato cliente Nimbi desde PostgreSQL"""
    log("Generando archivo CSV...")
    
    try:
        # Verificar que la conexión esté abierta
        if conn.closed:
            log("✗ Error: La conexión a PostgreSQL está cerrada")
            return None
        
        archivo_path = TEMP_CSV_DIR / CSV_OUTPUT_NAME
        
        inicio = time.time()
        
        # Extraer datos de PostgreSQL a DataFrame
        query = f"""
        SELECT {', '.join(columnas)}
        FROM nimbi."05_beneficios_alumnos"
        ORDER BY 1
        """
        
        log("Extrayendo datos de PostgreSQL para CSV...")
        df = pd.read_sql(query, conn)
        
        if df.empty:
            log("⚠ No hay datos para generar CSV")
            return None
        
        log(f"  → Datos extraídos: {len(df)} registros")
        
        # Generar CSV con especificaciones cliente Nimbi
        log("Escribiendo archivo CSV...")
        df.to_csv(
            archivo_path,
            sep=CSV_CONFIG['separator'],
            encoding=CSV_CONFIG['encoding'],
            index=CSV_CONFIG['include_index'],
            na_rep=CSV_CONFIG['na_rep'],
            quoting=CSV_CONFIG['quoting']  # QUOTE_ALL - Comillas dobles protegen delimitadores internos
        )
        
        # Limpiar backslashes innecesarios
        limpiar_backslashes_csv(archivo_path)
        
        duracion = time.time() - inicio
        file_size = archivo_path.stat().st_size / 1024 / 1024  # MB
        
        log(f"✓ CSV generado exitosamente!")
        log(f"✓ Archivo: {archivo_path}")
        log(f"✓ Tamaño: {file_size:.2f} MB")
        log(f"✓ Registros: {len(df)}")
        log(f"✓ Columnas: {len(df.columns)}")
        log(f"✓ Tiempo de generación: {duracion:.2f} segundos")
        
        return str(archivo_path)
        
    except Exception as e:
        log(f"✗ Error generando CSV: {e}")
        import traceback
        traceback.print_exc()
        return None

def conectar_sftp():
    """Conecta al servidor SFTP"""
    log("Conectando al servidor SFTP...")
    
    try:
        # Crear cliente SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectar
        ssh_client.connect(
            hostname=SFTP_CONFIG['host'],
            username=SFTP_CONFIG['user'],
            password=SFTP_CONFIG['password'],
            port=SFTP_CONFIG['port'],
            timeout=SFTP_CONFIG['timeout']
        )
        
        # Crear cliente SFTP
        sftp_client = ssh_client.open_sftp()
        
        log("✓ Conexión SFTP exitosa")
        return ssh_client, sftp_client
        
    except Exception as e:
        log(f"✗ Error al conectar a SFTP: {e}")
        raise

def subir_archivo_sftp(archivo_local: str) -> bool:
    """Sube un archivo al servidor SFTP"""
    log("Subiendo archivo al servidor SFTP...")
    
    ssh_client = None
    sftp_client = None
    
    try:
        # Conectar a SFTP
        ssh_client, sftp_client = conectar_sftp()
        
        # Obtener el directorio actual (puede estar en chroot jail)
        directorio_actual = None
        try:
            directorio_actual = sftp_client.getcwd()
            if directorio_actual:
                log(f"  → Directorio actual en SFTP: {directorio_actual}")
            else:
                log(f"  → Directorio actual no disponible (None)")
        except Exception as e:
            log(f"  → No se pudo obtener directorio actual: {e}")
        
        # Determinar la ruta remota correcta
        # Configuración detectada: ChrootDirectory /sftp, directorio de trabajo es /sftp/nimbi
        # Desde el chroot jail, el directorio nimbi está en /nimbi (relativo a la raíz del chroot)
        ruta_destino = SFTP_CONFIG['upload_path'].rstrip('/')
        
        # Si la ruta destino es /sftp/nimbi, el chroot está en /sftp
        # Necesitamos cambiar al directorio nimbi dentro del chroot
        if ruta_destino == '/sftp/nimbi':
            # Cambiar al directorio nimbi dentro del chroot jail
            try:
                sftp_client.chdir('nimbi')
                log(f"  → Cambiado al directorio 'nimbi' dentro del chroot jail")
                # Verificar que estamos en el directorio correcto
                try:
                    directorio_actual = sftp_client.getcwd()
                    log(f"  → Directorio actual después de cambiar: {directorio_actual}")
                except:
                    pass
                # Estamos en el directorio nimbi, usar solo el nombre del archivo
                archivo_remoto = CSV_OUTPUT_NAME
                log(f"  → Usando ruta relativa desde directorio nimbi: {archivo_remoto}")
            except Exception as e:
                log(f"  ⚠ No se pudo cambiar al directorio 'nimbi': {e}")
                # Intentar usar ruta relativa desde la raíz del chroot
                archivo_remoto = 'nimbi/' + CSV_OUTPUT_NAME
                log(f"  → Usando ruta relativa desde raíz del chroot: {archivo_remoto}")
        else:
            archivo_remoto = ruta_destino + '/' + CSV_OUTPUT_NAME if ruta_destino else CSV_OUTPUT_NAME
            log(f"  → Usando ruta: {archivo_remoto}")
        
        # Verificar que el archivo local existe
        archivo_path = Path(archivo_local)
        if not archivo_path.exists():
            log(f"✗ Error: El archivo local no existe: {archivo_local}")
            return False
        
        # Subir el archivo
        log(f"  → Subiendo: {archivo_path.name} → {archivo_remoto}")
        inicio = time.time()
        
        sftp_client.put(archivo_local, archivo_remoto)
        
        # Verificar integridad
        stat_local = archivo_path.stat()
        stat_remoto = sftp_client.stat(archivo_remoto)
        
        if stat_local.st_size != stat_remoto.st_size:
            log(f"✗ Error: Tamaño de archivo no coincide")
            log(f"  Local: {stat_local.st_size} bytes")
            log(f"  Remoto: {stat_remoto.st_size} bytes")
            return False
        
        duracion = time.time() - inicio
        file_size = stat_local.st_size / 1024 / 1024  # MB
        
        log(f"✓ Archivo subido exitosamente!")
        log(f"✓ Tamaño: {file_size:.2f} MB")
        log(f"✓ Tiempo de subida: {duracion:.2f} segundos")
        log(f"✓ Ruta remota: {archivo_remoto}")
        
        return True
        
    except Exception as e:
        log(f"✗ Error subiendo archivo a SFTP: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cerrar conexiones
        if sftp_client:
            try:
                sftp_client.close()
            except:
                pass
        if ssh_client:
            try:
                ssh_client.close()
            except:
                pass

def main():
    """Función principal"""
    log("=" * 70)
    log("ACTUALIZACIÓN BENEFICIOS ALUMNOS: SQL SERVER → POSTGRESQL")
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
        total, conn_pg = cargar_a_postgresql(datos, columnas)
        
        # 4. Generar CSV
        csv_path = None
        try:
            log("\n4. Generando archivo CSV...")
            csv_path = generar_csv_nimbi(conn_pg, columnas)
        except Exception as e:
            log(f"⚠ Error generando CSV: {e}")
        finally:
            # Cerrar conexión PostgreSQL
            if conn_pg and not conn_pg.closed:
                conn_pg.close()
        
        # 5. Subir CSV a SFTP
        sftp_exitoso = False
        if csv_path:
            try:
                log("\n5. Subiendo archivo CSV a SFTP...")
                sftp_exitoso = subir_archivo_sftp(csv_path)
            except Exception as e:
                log(f"⚠ Error subiendo a SFTP: {e}")
        else:
            log("\n5. Saltando subida a SFTP (no hay archivo CSV)")
        
        # 6. Resumen final
        duracion = time.time() - inicio
        log("\n" + "=" * 70)
        log("RESUMEN")
        log("=" * 70)
        log(f"✓ Registros extraídos de SQL Server: {len(datos)}")
        log(f"✓ Registros en PostgreSQL: {total}")
        if csv_path:
            log(f"✓ Archivo CSV generado: {csv_path}")
            if sftp_exitoso:
                log(f"✓ Archivo CSV subido a SFTP: {SFTP_CONFIG['upload_path']}{CSV_OUTPUT_NAME}")
            else:
                log("⚠ Archivo CSV no se pudo subir a SFTP")
        else:
            log("⚠ No se pudo generar el archivo CSV")
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

