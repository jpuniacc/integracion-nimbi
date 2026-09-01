#!/usr/bin/env python3
"""
Script para actualizar usuarios de Google Workspace a PostgreSQL
Extrae usuarios del directorio de Google y los carga a la base de datos

Soporta dos modos de autenticación:
1. OAuth2 (token.json + credentials.json) - Para uso con token existente
2. Service Account (service_account.json) - Para automatización completa
"""

import os
import sys
import time
import json
from datetime import date, datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Importaciones de Google API
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Error: Instalar dependencias de Google API")
    print("pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)

# Cargar .env del proyecto
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parent
ENV_PATH = PROJECT_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)

# Directorio de archivos de Google
GOOGLE_DIR = SCRIPT_DIR / 'google'

# Configuración de Google API desde .env
GOOGLE_CONFIG = {
    # Archivos de autenticación
    'credentials_file': os.getenv('GOOGLE_CREDENTIALS_FILE', str(GOOGLE_DIR / 'credentials.json')),
    'token_file': os.getenv('GOOGLE_TOKEN_FILE', str(GOOGLE_DIR / 'token.json')),
    'service_account_file': os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', str(GOOGLE_DIR / 'service_account.json')),
    # Email admin para Service Account
    'admin_email': os.getenv('GOOGLE_ADMIN_EMAIL', ''),
    # Modo de autenticación: 'oauth2' o 'service_account'
    'auth_mode': os.getenv('GOOGLE_AUTH_MODE', 'oauth2'),
    # Scopes
    'scopes': ['https://www.googleapis.com/auth/admin.directory.user.readonly'],
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
DB_SCHEMA = os.getenv('DB_SCHEMA', 'nimbi')
DB_TABLE = '12_usuarios_google'


def log(mensaje):
    """Imprime mensaje con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}", flush=True)


def obtener_servicio_oauth2():
    """
    Autentica con Google API usando OAuth2 (token.json + credentials.json).
    Ideal cuando ya tienes un token generado.
    """
    log("Autenticando con OAuth2...")
    
    token_file = GOOGLE_CONFIG['token_file']
    credentials_file = GOOGLE_CONFIG['credentials_file']
    scopes = GOOGLE_CONFIG['scopes']
    
    creds = None
    
    # Intentar cargar token existente
    if os.path.exists(token_file):
        log(f"  → Cargando token desde: {token_file}")
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    
    # Si no hay credenciales válidas, intentar refrescar o crear nuevas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log("  → Token expirado, refrescando...")
            creds.refresh(Request())
            # Guardar token refrescado
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            log("  → Token refrescado y guardado")
        else:
            # Necesita autenticación interactiva
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"No se encuentra: {credentials_file}")
            
            log("  ⚠ Se requiere autenticación interactiva...")
            log("  → Ejecuta el script manualmente la primera vez")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(host='localhost', port=8080, open_browser=False)
            
            # Guardar token para próximas ejecuciones
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            log(f"  → Token guardado en: {token_file}")
    
    log("✓ Autenticación OAuth2 exitosa")
    return build('admin', 'directory_v1', credentials=creds)


def obtener_servicio_service_account():
    """
    Autentica con Google API usando cuenta de servicio y delegación de dominio.
    Ideal para automatización sin interacción del usuario.
    """
    log("Autenticando con Service Account...")
    
    key_file = GOOGLE_CONFIG['service_account_file']
    admin_email = GOOGLE_CONFIG['admin_email']
    scopes = GOOGLE_CONFIG['scopes']
    
    # Verificar archivo de credenciales
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"No se encuentra el archivo: {key_file}")
    
    if not admin_email:
        raise ValueError("GOOGLE_ADMIN_EMAIL no está configurado en .env")
    
    log(f"  → Archivo de credenciales: {key_file}")
    log(f"  → Delegando autoridad de: {admin_email}")
    
    # Autenticación con Cuenta de Servicio
    creds = service_account.Credentials.from_service_account_file(
        key_file, scopes=scopes
    )
    
    # Delegación de autoridad (Impersonation)
    delegated_creds = creds.with_subject(admin_email)
    
    log("✓ Autenticación Service Account exitosa")
    return build('admin', 'directory_v1', credentials=delegated_creds)


def obtener_servicio_google():
    """
    Obtiene el servicio de Google API según el modo de autenticación configurado.
    Modos: 'oauth2' (default) o 'service_account'
    """
    log("Conectando a Google Workspace API...")
    
    auth_mode = GOOGLE_CONFIG['auth_mode'].lower()
    log(f"  → Modo de autenticación: {auth_mode}")
    
    if auth_mode == 'service_account':
        return obtener_servicio_service_account()
    else:
        # Por defecto usar OAuth2
        return obtener_servicio_oauth2()


def extraer_usuarios_google():
    """
    Extrae todos los usuarios del directorio de Google Workspace.
    Maneja paginación automáticamente.
    """
    log("Extrayendo usuarios de Google Workspace...")
    
    service = obtener_servicio_google()
    todos_los_usuarios = []
    page_token = None
    
    inicio = time.time()
    
    while True:
        # Petición a la API (máximo 500 por página)
        results = service.users().list(
            customer='my_customer',
            maxResults=500,
            pageToken=page_token,
            orderBy='email'
        ).execute()
        
        users = results.get('users', [])
        todos_los_usuarios.extend(users)
        
        log(f"  → Recuperados {len(todos_los_usuarios)} usuarios...")
        
        # Manejo de paginación
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    duracion = time.time() - inicio
    log(f"✓ Extracción completada: {len(todos_los_usuarios)} usuarios en {duracion:.2f} segundos")
    
    return todos_los_usuarios


def procesar_usuarios(usuarios_raw):
    """
    Procesa los datos crudos de la API de Google y los convierte
    al formato esperado para PostgreSQL.
    """
    log("Procesando datos de usuarios...")
    
    fecha_corte = date.today()
    registros = []
    
    for u in usuarios_raw:
        # Procesar fecha de última conexión
        last_login_raw = u.get('lastLoginTime')
        if last_login_raw and last_login_raw != '1970-01-01T00:00:00.000Z':
            # Formato original: 2023-10-27T14:30:00.000Z
            try:
                fecha_login = last_login_raw.split('T')[0]
            except:
                fecha_login = None
        else:
            fecha_login = None
        
        # Construir registro
        registro = (
            u.get('primaryEmail'),                          # email
            u.get('name', {}).get('givenName'),             # nombre
            u.get('name', {}).get('familyName'),            # apellido
            u.get('name', {}).get('fullName'),              # nombre_completo
            'Suspendido' if u.get('suspended') else 'Activo',  # estado
            u.get('orgUnitPath'),                           # unidad_organizativa
            fecha_login,                                    # ultima_conexion
            fecha_corte,                                    # fecha_corte
        )
        registros.append(registro)
    
    log(f"✓ Procesados {len(registros)} registros")
    return registros


def cargar_a_postgresql(registros):
    """Carga los datos procesados a PostgreSQL"""
    log("Conectando a PostgreSQL...")
    
    fecha_corte = date.today()
    log(f"Fecha de corte: {fecha_corte}")
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SET search_path TO {DB_SEARCH_PATH};")
        
        # Truncate (full refresh)
        log(f'Limpiando tabla {DB_SCHEMA}."{DB_TABLE}"...')
        cursor.execute(f'TRUNCATE TABLE {DB_SCHEMA}."{DB_TABLE}" RESTART IDENTITY CASCADE;')
        conn.commit()
        
        # Query de inserción
        insert_query = f'''
        INSERT INTO {DB_SCHEMA}."{DB_TABLE}" (
            email, nombre, apellido, nombre_completo, 
            estado, unidad_organizativa, ultima_conexion, fecha_corte
        ) VALUES %s
        '''
        
        # Insertar datos en lotes
        log("Insertando datos en PostgreSQL...")
        batch_size = 1000
        total_insertados = 0
        
        for i in range(0, len(registros), batch_size):
            batch = registros[i:i + batch_size]
            execute_values(cursor, insert_query, batch)
            conn.commit()
            total_insertados += len(batch)
            log(f"  → Insertados {total_insertados}/{len(registros)} registros...")
        
        # Verificar total
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


def main():
    """Función principal"""
    log("=" * 70)
    log("ACTUALIZACIÓN USUARIOS GOOGLE WORKSPACE → POSTGRESQL")
    log("=" * 70)
    
    inicio = time.time()
    
    try:
        # 1. Extraer usuarios de Google
        log("\n1. Extrayendo usuarios de Google Workspace...")
        usuarios_raw = extraer_usuarios_google()
        
        if len(usuarios_raw) == 0:
            log("⚠ No se extrajeron usuarios. Abortando.")
            return 1
        
        # 2. Procesar datos
        log("\n2. Procesando datos...")
        registros = procesar_usuarios(usuarios_raw)
        
        # 3. Cargar a PostgreSQL
        log("\n3. Cargando datos a PostgreSQL...")
        total = cargar_a_postgresql(registros)
        
        # 4. Resumen final
        duracion = time.time() - inicio
        log("\n" + "=" * 70)
        log("RESUMEN")
        log("=" * 70)
        log(f"✓ Usuarios extraídos de Google: {len(usuarios_raw)}")
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

