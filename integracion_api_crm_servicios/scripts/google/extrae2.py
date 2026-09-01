import csv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURACIÓN ---
# 1. Tu archivo JSON de la Cuenta de Servicio
KEY_FILE = 'service_account.json' 

# 2. Email de un Super Admin de tu dominio UNIACC
ADMIN_EMAIL = 'tu-email-admin@uniacc.cl' 

# 3. Permisos de solo lectura para el directorio
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly']

def obtener_usuarios():
    try:
        if not os.path.exists(KEY_FILE):
            print(f"❌ Error: No se encuentra el archivo {KEY_FILE}")
            return None

        # Autenticación con Cuenta de Servicio
        print(f"Cargando credenciales y delegando autoridad de {ADMIN_EMAIL}...")
        creds = service_account.Credentials.from_service_account_file(
            KEY_FILE, scopes=SCOPES)
        
        # Delegación de autoridad (Impersonation)
        delegated_creds = creds.with_subject(ADMIN_EMAIL)
        
        # Construcción del servicio de API
        service = build('admin', 'directory_v1', credentials=delegated_creds)

        todos_los_usuarios = []
        page_token = None

        print("Conectando con Google Workspace API...")

        while True:
            # Petición a la API
            results = service.users().list(
                customer='my_customer',
                maxResults=500,
                pageToken=page_token,
                orderBy='email'
            ).execute()

            users = results.get('users', [])
            todos_los_usuarios.extend(users)

            print(f"-> Recuperados {len(todos_los_usuarios)} usuarios...")

            # Manejo de paginación
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        return todos_los_usuarios

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def guardar_a_csv(usuarios):
    if not usuarios:
        return

    nombre_archivo = 'reporte_usuarios_google.csv'
    # Definición de columnas para el CSV
    columnas = [
        'Email', 
        'Nombre', 
        'Apellido', 
        'Estado', 
        'Unidad Organizativa', 
        'Ultima Conexion'
    ]

    try:
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
            
            for u in usuarios:
                # Procesar la fecha de última conexión
                last_login_raw = u.get('lastLoginTime', 'Nunca ha ingresado')
                
                # Si hay fecha, la limpiamos para que solo muestre AAAA-MM-DD
                if last_login_raw != 'Nunca ha ingresado':
                    # El formato original es 2023-10-27T14:30:00.000Z
                    fecha_limpia = last_login_raw.split('T')[0]
                else:
                    fecha_limpia = last_login_raw

                writer.writerow({
                    'Email': u.get('primaryEmail'),
                    'Nombre': u.get('name', {}).get('givenName'),
                    'Apellido': u.get('name', {}).get('familyName'),
                    'Estado': 'Suspendido' if u.get('suspended') else 'Activo',
                    'Unidad Organizativa': u.get('orgUnitPath'),
                    'Ultima Conexion': fecha_limpia
                })
        
        print(f"\n✅ ¡Éxito! Archivo generado: {nombre_archivo}")
        print(f"Total de registros procesados: {len(usuarios)}")
        
    except Exception as e:
        print(f"❌ Error al guardar el CSV: {e}")

if __name__ == '__main__':
    print("--- Iniciando Extracción de Directorio Google Workspace ---")
    lista_final = obtener_usuarios()
    if lista_final:
        guardar_a_csv(lista_final)
