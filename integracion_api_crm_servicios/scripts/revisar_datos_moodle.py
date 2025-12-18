#!/usr/bin/env python3
"""
Script temporal para extraer datos de Moodle y guardarlos en JSON
para revisar qué campos y datos están disponibles
"""

import os
import json
import pyodbc
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parent
ENV_PATH = PROJECT_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)

# Configuración de SQL Server
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

def conectar_sqlserver():
    """Conecta a SQL Server"""
    conn_str = (
        f"DRIVER={SQLSERVER_CONFIG['driver']};"
        f"SERVER={SQLSERVER_CONFIG['server']},{SQLSERVER_CONFIG['port']};"
        f"DATABASE={SQLSERVER_CONFIG['database']};"
        f"UID={SQLSERVER_CONFIG['username']};"
        f"PWD={SQLSERVER_CONFIG['password']};"
        f"Encrypt={SQLSERVER_CONFIG['encrypt']};"
        f"TrustServerCertificate={SQLSERVER_CONFIG['trust_server_certificate']};"
    )
    return pyodbc.connect(conn_str, timeout=60)

def extraer_datos_muestra(query, limite=10000):
    """Extrae una muestra de datos para revisión"""
    print(f"  → Conectando a SQL Server...")
    conn = conectar_sqlserver()
    cursor = conn.cursor()
    
    try:
        # Agregar TOP al query para limitar resultados
        if 'SELECT' in query.upper():
            query_limitada = query.replace('SELECT', f'SELECT TOP {limite}', 1)
        else:
            query_limitada = query
        
        print(f"  → Ejecutando query (límite: {limite} registros)...")
        cursor.execute(query_limitada)
        print(f"  → Query ejecutada, obteniendo nombres de columnas...")
        
        # Obtener nombres de columnas
        columnas = [column[0] for column in cursor.description]
        print(f"  → Total de columnas: {len(columnas)}")
        
        # Obtener datos con progreso
        print(f"  → Extrayendo datos...")
        datos = []
        contador = 0
        for row in cursor.fetchall():
            fila = {}
            for i, col in enumerate(columnas):
                valor = row[i]
                # Convertir tipos no serializables
                if hasattr(valor, 'isoformat'):  # datetime, date
                    fila[col] = valor.isoformat()
                else:
                    fila[col] = valor
            datos.append(fila)
            contador += 1
            if contador % 1000 == 0:
                print(f"    → Procesados {contador} registros...")
        
        print(f"  → Total de registros extraídos: {len(datos)}")
        return columnas, datos
        
    finally:
        cursor.close()
        conn.close()
        print(f"  → Conexión cerrada")

def main():
    print("Extrayendo datos de Moodle para revisión...")
    
    # Leer query SQL
    query_file = REPO_ROOT / "sql/7_datos_moodle_operacional.sql"
    with open(query_file, 'r', encoding='utf-8') as f:
        query = f.read().strip()
    
    # Limpiar punto y coma final
    if query.endswith(';'):
        query = query[:-1]
    
    # Extraer muestra (10,000 registros)
    print("Extrayendo muestra de 10,000 registros...")
    columnas, datos = extraer_datos_muestra(query, limite=10000)
    
    # Guardar en JSON
    output_dir = SCRIPT_DIR / "backups"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "muestra_datos_moodle.json"
    
    resultado = {
        'columnas': columnas,
        'total_columnas': len(columnas),
        'total_registros_muestra': len(datos),
        'datos': datos
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✓ Datos guardados en: {output_file}")
    print(f"✓ Total de columnas: {len(columnas)}")
    print(f"✓ Total de registros en muestra: {len(datos)}")
    print(f"\nColumnas disponibles:")
    for i, col in enumerate(columnas, 1):
        print(f"  {i}. {col}")
    
    # También crear un resumen en Markdown
    md_file = output_dir / "muestra_datos_moodle_resumen.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Resumen de Datos Moodle\n\n")
        f.write(f"**Total de columnas:** {len(columnas)}\n\n")
        f.write(f"**Registros en muestra:** {len(datos)}\n\n")
        f.write("## Columnas Disponibles\n\n")
        for i, col in enumerate(columnas, 1):
            f.write(f"{i}. `{col}`\n")
        
        f.write("\n## Muestra de Datos (primeros 5 registros)\n\n")
        for i, registro in enumerate(datos[:5], 1):
            f.write(f"### Registro {i}\n\n")
            f.write("```json\n")
            f.write(json.dumps(registro, ensure_ascii=False, indent=2, default=str))
            f.write("\n```\n\n")
    
    print(f"✓ Resumen Markdown guardado en: {md_file}")

if __name__ == "__main__":
    main()

