#!/usr/bin/env python3
"""
Script para sincronizar la última conexión de Google a la tabla de identificadores.
Actualiza el campo ultima_conexion_google en 01_identificadores_y_data_operacional
usando los datos de 12_usuarios_google.

Este script debe ejecutarse DESPUÉS de:
- actualizar_datos_identificadores_y_data_operacional.py
- actualizar_usuarios_google.py
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Cargar .env del proyecto
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ENV_PATH = PROJECT_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)

# Configuración de PostgreSQL desde .env
POSTGRES_CONFIG = {
    'host': os.getenv('DB_HOST', '172.16.0.206'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', '5432')),
}
DB_SEARCH_PATH = os.getenv('DB_SEARCH_PATH', 'nimbi, public')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'nimbi')


def log(mensaje):
    """Imprime mensaje con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}", flush=True)


def sincronizar_conexion_google():
    """
    Actualiza el campo ultima_conexion_google en la tabla 01_identificadores_y_data_operacional
    con la última conexión de Google de cada usuario, basándose en el email institucional.
    """
    log("Conectando a PostgreSQL...")
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SET search_path TO {DB_SEARCH_PATH};")
        
        # Verificar que existen datos en ambas tablas
        log("Verificando datos en las tablas...")
        
        cursor.execute(f'SELECT COUNT(*) FROM {DB_SCHEMA}."01_identificadores_y_data_operacional";')
        total_identificadores = cursor.fetchone()[0]
        log(f"  → Registros en 01_identificadores_y_data_operacional: {total_identificadores}")
        
        cursor.execute(f'SELECT COUNT(*) FROM {DB_SCHEMA}."12_usuarios_google";')
        total_google = cursor.fetchone()[0]
        log(f"  → Registros en 12_usuarios_google: {total_google}")
        
        if total_identificadores == 0:
            log("⚠ No hay registros en la tabla de identificadores. Abortando.")
            return 0
        
        if total_google == 0:
            log("⚠ No hay registros en la tabla de Google. Abortando.")
            return 0
        
        # Ejecutar el UPDATE
        log("Ejecutando sincronización de ultima_conexion_google...")
        
        update_query = f'''
        UPDATE {DB_SCHEMA}."01_identificadores_y_data_operacional" AS t01
        SET ultima_conexion_google = t12.ultima_conexion::text
        FROM {DB_SCHEMA}."12_usuarios_google" AS t12
        WHERE LOWER(t01.mail_inst) = LOWER(t12.email);
        '''
        
        inicio = time.time()
        cursor.execute(update_query)
        registros_actualizados = cursor.rowcount
        conn.commit()
        duracion = time.time() - inicio
        
        log(f"✓ UPDATE completado en {duracion:.2f} segundos")
        log(f"✓ Registros actualizados: {registros_actualizados}")
        
        # Estadísticas adicionales
        cursor.execute(f'''
            SELECT COUNT(*) 
            FROM {DB_SCHEMA}."01_identificadores_y_data_operacional"
            WHERE ultima_conexion_google IS NOT NULL;
        ''')
        con_conexion = cursor.fetchone()[0]
        
        cursor.execute(f'''
            SELECT COUNT(*) 
            FROM {DB_SCHEMA}."01_identificadores_y_data_operacional"
            WHERE ultima_conexion_google IS NULL;
        ''')
        sin_conexion = cursor.fetchone()[0]
        
        log(f"  → Alumnos con fecha de conexión Google: {con_conexion}")
        log(f"  → Alumnos sin fecha de conexión Google: {sin_conexion}")
        
        return registros_actualizados
        
    except Exception as e:
        log(f"✗ Error durante la sincronización: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Función principal"""
    log("=" * 70)
    log("SINCRONIZACIÓN ÚLTIMA CONEXIÓN GOOGLE → TABLA IDENTIFICADORES")
    log("=" * 70)
    
    inicio = time.time()
    
    try:
        # Ejecutar sincronización
        log("\n1. Sincronizando ultima_conexion_google...")
        registros = sincronizar_conexion_google()
        
        # Resumen final
        duracion = time.time() - inicio
        log("\n" + "=" * 70)
        log("RESUMEN")
        log("=" * 70)
        log(f"✓ Registros actualizados: {registros}")
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

