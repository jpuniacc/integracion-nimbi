#!/usr/bin/env python3
import os
import json
import time
import sys
from datetime import datetime, date
from pathlib import Path

import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Cargar .env (si existe)
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

def log(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}", flush=True)

API_CONFIG = {
    'base_url': os.getenv('API_BASE_URL', 'https://servicios-api.uniacc.crm-mantis.cl').rstrip('/'),
    'usuario': os.getenv('API_USUARIO'),
    'clave': os.getenv('API_CLAVE'),
    'timeout_conexion': int(os.getenv('API_TIMEOUT_CONEXION', '30')),  # Timeout para establecer conexión
    'timeout_lectura': int(os.getenv('API_TIMEOUT_LECTURA', '300')),  # Timeout para leer respuesta (5 minutos)
    'max_reintentos': int(os.getenv('API_MAX_REINTENTOS', '3')),  # Número máximo de reintentos
    'delay_reintento': int(os.getenv('API_DELAY_REINTENTO', '5')),  # Segundos entre reintentos
}

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', '5432')),
}

# Fecha de inicio: Siempre desde 01/2025 (configurable vía variables de entorno)
FECHA_INICIO = {
    'ano': int(os.getenv('FECHA_INICIO_ANO', '2025')),  # Año inicial
    'mes': int(os.getenv('FECHA_INICIO_MES', '1')),     # Mes inicial (siempre enero)
}

DB_SEARCH_PATH = os.getenv('DB_SEARCH_PATH', 'nimbi, public')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'nimbi')
DB_TABLE = os.getenv('DB_TABLE', '10_solicitudes_crm')

def obtener_token():
    log("Obteniendo token de autenticación...")
    url = f"{API_CONFIG['base_url']}/login/externo"
    payload = {
        'usuario': API_CONFIG['usuario'],
        'clave': API_CONFIG['clave']
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    token = data.get('token')
    if not token:
        raise RuntimeError("No se recibió token en la respuesta")
    log("✓ Token obtenido exitosamente")
    return token

def descargar_solicitudes(token, ano, mes):
    """Descarga solicitudes con reintentos automáticos"""
    log(f"Descargando solicitudes de {mes:02d}/{ano}...")
    url = f"{API_CONFIG['base_url']}/reportes/solicitudes"
    headers = {'Authorization': token}
    params = {'nro_ano': ano, 'nro_mes': mes}
    
    # Configurar timeout como tupla (conexión, lectura)
    timeout_conexion = API_CONFIG['timeout_conexion']
    timeout_lectura = API_CONFIG['timeout_lectura']
    timeout = (timeout_conexion, timeout_lectura)
    
    max_reintentos = API_CONFIG['max_reintentos']
    delay_reintento = API_CONFIG['delay_reintento']
    
    # Log del timeout configurado (solo en el primer intento)
    log(f"  → Timeout configurado: conexión={timeout_conexion}s, lectura={timeout_lectura}s")
    
    for intento in range(1, max_reintentos + 1):
        try:
            if intento > 1:
                log(f"  → Reintento {intento}/{max_reintentos} para {mes:02d}/{ano}...")
                # Esperar más tiempo entre reintentos para darle tiempo al servidor
                tiempo_espera = delay_reintento * (intento - 1)
                log(f"  → Esperando {tiempo_espera} segundos antes del reintento...")
                time.sleep(tiempo_espera)
            
            # Crear una sesión para mejor manejo de conexiones
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(
                url, 
                params=params, 
                timeout=timeout,
                stream=False  # No usar stream para evitar problemas de IncompleteRead
            )
            response.raise_for_status()
            datos = response.json()
            
            if not isinstance(datos, list):
                log(f"⚠ Respuesta inesperada para {mes:02d}/{ano}")
                return []
            
            log(f"✓ Descargados {len(datos)} registros de {mes:02d}/{ano}")
            return datos
            
        except requests.exceptions.Timeout as e:
            tipo_timeout = "lectura" if "Read timed out" in str(e) or "read timeout" in str(e).lower() else "conexión"
            log(f"✗ Timeout de {tipo_timeout} al descargar {mes:02d}/{ano} (intento {intento}/{max_reintentos}): {e}")
            if intento == max_reintentos:
                log(f"✗ No se pudo descargar {mes:02d}/{ano} después de {max_reintentos} intentos")
                return []
                
        except (requests.exceptions.ChunkedEncodingError, 
                ConnectionError,
                OSError) as e:
            # Errores de conexión interrumpida (IncompleteRead está dentro de ChunkedEncodingError)
            log(f"✗ Conexión interrumpida al descargar {mes:02d}/{ano} (intento {intento}/{max_reintentos}): {type(e).__name__}: {e}")
            if intento == max_reintentos:
                log(f"✗ No se pudo descargar {mes:02d}/{ano} después de {max_reintentos} intentos")
                return []
                
        except requests.exceptions.RequestException as e:
            log(f"✗ Error al descargar datos de {mes:02d}/{ano} (intento {intento}/{max_reintentos}): {e}")
            if intento == max_reintentos:
                log(f"✗ No se pudo descargar {mes:02d}/{ano} después de {max_reintentos} intentos")
                return []
    
    return []

def obtener_meses_a_descargar():
    """
    Calcula dinámicamente los meses a descargar desde FECHA_INICIO hasta el mes actual.
    Soporta múltiples años automáticamente.
    
    Ejemplo: Si estamos en diciembre 2026 y FECHA_INICIO es 01/2025,
    descargará todos los meses desde 01/2025 hasta 12/2026.
    """
    hoy = date.today()
    ano_actual, mes_actual = hoy.year, hoy.month
    meses = []
    ano, mes = FECHA_INICIO['ano'], FECHA_INICIO['mes']
    
    # Iterar desde fecha inicio hasta mes actual (inclusive)
    while (ano < ano_actual) or (ano == ano_actual and mes <= mes_actual):
        meses.append((ano, mes))
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
    
    return meses

def convertir_fecha(fecha_str):
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def preparar_registro(item, fecha_corte):
    return (
        item.get('cod_incidencia'),
        item.get('cod_alurut'),
        item.get('cod_carrera'),
        item.get('des_carrera'),
        item.get('codcli'),
        item.get('des_consejero'),
        item.get('cod_estado'),
        item.get('des_estado'),
        item.get('des_incidencia'),
        item.get('cod_categoria'),
        item.get('des_categoria'),
        item.get('cod_subcategoria'),
        item.get('des_subcategoria'),
        item.get('des_login_ingreso'),
        item.get('des_login_asignado'),
        item.get('des_login_derivado'),
        convertir_fecha(item.get('fec_ingreso')),
        convertir_fecha(item.get('fec_ultmod')),
        item.get('nro_minuto_total'),
        item.get('nro_minuto_etapa'),
        item.get('nro_minuto_vencido'),
        item.get('cod_grupo_incidencia'),
        item.get('des_observacion'),
        item.get('des_respuesta'),
        item.get('des_grupo'),
        item.get('des_anulacion'),
        item.get('bool_portal'),
        item.get('cod_escuela'),
        item.get('des_escuela'),
        item.get('bool_nuevo'),
        (item.get('asignado') or {}).get('des_login'),
        (item.get('asignado') or {}).get('des_nombre'),
        (item.get('alumno') or {}).get('des_nombre'),
        (item.get('alumno') or {}).get('des_apepri'),
        (item.get('alumno') or {}).get('des_apeseg'),
        (item.get('alumno') or {}).get('des_email'),
        (item.get('alumno') or {}).get('des_telefono'),
        (item.get('alumno') or {}).get('des_celular'),
        fecha_corte,
    )

def cargar_a_postgresql(datos):
    log("Conectando a PostgreSQL...")
    fecha_corte = date.today().strftime("%Y-%m-%d")
    log(f"Fecha de corte: {fecha_corte}")

    # De-duplicar por cod_incidencia
    log("Eliminando registros duplicados...")
    unicos = {}
    for item in datos:
        cod = item.get('cod_incidencia')
        if cod:
            unicos[cod] = item
    datos = list(unicos.values())
    log(f"Registros únicos a insertar: {len(datos)}")

    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()
    try:
        cursor.execute("SET search_path TO " + DB_SEARCH_PATH + ";")

        # Truncate total
        log(f"Limpiando tabla {DB_SCHEMA}.\"{DB_TABLE}\"...")
        cursor.execute(f'TRUNCATE TABLE {DB_SCHEMA}."{DB_TABLE}" RESTART IDENTITY CASCADE;')
        conn.commit()

        log("Preparando datos para inserción...")
        registros = [preparar_registro(item, fecha_corte) for item in datos]

        insert_query = f'''
        INSERT INTO {DB_SCHEMA}."{DB_TABLE}" (
            cod_incidencia, cod_alurut, cod_carrera, des_carrera, codcli,
            des_consejero, cod_estado, des_estado, des_incidencia,
            cod_categoria, des_categoria, cod_subcategoria, des_subcategoria,
            des_login_ingreso, des_login_asignado, des_login_derivado,
            fec_ingreso, fec_ultmod, nro_minuto_total, nro_minuto_etapa,
            nro_minuto_vencido, cod_grupo_incidencia, des_observacion,
            des_respuesta, des_grupo, des_anulacion, bool_portal,
            cod_escuela, des_escuela, bool_nuevo,
            asignado_login, asignado_nombre,
            alumno_nombre, alumno_apepri, alumno_apeseg, alumno_email,
            alumno_telefono, alumno_celular, fecha_corte
        ) VALUES %s
        '''

        log("Insertando datos en PostgreSQL...")
        batch_size = 1000
        total_insertados = 0
        for i in range(0, len(registros), batch_size):
            batch = registros[i:i + batch_size]
            execute_values(cursor, insert_query, batch)
            conn.commit()
            total_insertados += len(batch)
            log(f"  → Insertados {total_insertados}/{len(registros)} registros...")

        cursor.execute(f'SELECT COUNT(*) FROM {DB_SCHEMA}."{DB_TABLE}";')
        total_en_bd = cursor.fetchone()[0]
        log("✓ Carga completada exitosamente!")
        log(f"✓ Total de registros en la tabla: {total_en_bd}")
        return total_en_bd
    except Exception as e:
        log(f"✗ Error durante la carga: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def guardar_backup(datos, sufijo="backup"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_dir = Path(__file__).parent
    backup_dir = script_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    filename = backup_dir / f"solicitudes_crm_{sufijo}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    log(f"✓ Backup temporal guardado: {filename}")
    return str(filename)

def eliminar_backup(filename):
    try:
        p = Path(filename)
        if p.exists():
            p.unlink()
            log(f"✓ Backup temporal eliminado: {filename}")
        return True
    except Exception as e:
        log(f"⚠ No se pudo eliminar el backup {filename}: {e}")
        return False

def main():
    log("=" * 70)
    log("ACTUALIZACIÓN AUTOMÁTICA DE SOLICITUDES CRM")
    log("=" * 70)
    inicio = time.time()
    try:
        token = obtener_token()
        meses = obtener_meses_a_descargar()
        log(f"\nDescargando datos de {len(meses)} meses (desde {FECHA_INICIO['mes']:02d}/{FECHA_INICIO['ano']})")
        todos = []
        delay_entre_meses = int(os.getenv('API_DELAY_ENTRE_MESES', '10'))  # Delay entre descargas de meses
        for i, (ano, mes) in enumerate(meses, 1):
            datos_mes = descargar_solicitudes(token, ano, mes)
            todos.extend(datos_mes)
            # Esperar entre descargas para no sobrecargar la API (excepto en el último mes)
            if i < len(meses):
                log(f"  → Esperando {delay_entre_meses} segundos antes de la siguiente descarga...")
                time.sleep(delay_entre_meses)
        log(f"\n✓ Total de registros descargados: {len(todos)}")
        if len(todos) == 0:
            log("⚠ No se descargaron datos. Abortando.")
            return 1
        backup_filename = guardar_backup(todos)
        log("\n" + "=" * 70)
        total = cargar_a_postgresql(todos)
        eliminar_backup(backup_filename)
        duracion = time.time() - inicio
        log("\n" + "=" * 70)
        log("RESUMEN")
        log("=" * 70)
        log(f"✓ Registros descargados: {len(todos)}")
        log(f"✓ Registros en base de datos: {total}")
        log(f"✓ Tiempo total: {duracion:.2f} segundos")
        log("=" * 70)
        return 0
    except Exception as e:
        log(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())