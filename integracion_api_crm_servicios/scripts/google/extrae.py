#!/home/csantibanez/google_env/bin/python3
import os.path
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

os.chdir('/home/csantibanez')

# Alcance de SOLO LECTURA
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly']

def obtener_servicio():
    """Maneja la autenticación y devuelve el servicio de la API."""
    creds = None
    # El archivo token.json almacena los tokens de acceso del usuario.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay credenciales válidas, solicita al usuario que inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: No se encuentra el archivo 'credentials.json'")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # Usamos el puerto 8080 fijo para el túnel SSH
            creds = flow.run_local_server(
            host='localhost', 
            port=8080, 
            open_browser=False) 
        # Guarda las credenciales para la próxima ejecución
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('admin', 'directory_v1', credentials=creds)

def extraer_usuarios():
    service = obtener_servicio()
    if not service:
        return

    todos_los_usuarios = []
    page_token = None
    
    print("Iniciando conexión con Google Workspace...")

    while True:
        # Petición a la API (máximo 500 por página para eficiencia)
        results = service.users().list(
            customer='my_customer',
            maxResults=500,
            pageToken=page_token,
            orderBy='email'
        ).execute()

        users = results.get('users', [])
        todos_los_usuarios.extend(users)

        # Verificar si hay otra página de resultados
        page_token = results.get('nextPageToken')
        if not page_token:
            break
        
        print(f"Progreso: {len(todos_los_usuarios)} usuarios recuperados...")

    return todos_los_usuarios

def guardar_a_csv(usuarios, nombre_archivo='usuarios_gsuite.csv'):
    """Guarda la lista de diccionarios en un archivo CSV."""
    if not usuarios:
        print("No hay datos para guardar.")
        return

    campos = ['Email', 'Nombre Completo', 'Estado', 'Ultima Conexion']
    
    try:
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for u in usuarios:
                writer.writerow({
                    'Email': u.get('primaryEmail'),
                    'Nombre Completo': u.get('name', {}).get('fullName'),
                    'Estado': 'Suspendido' if u.get('suspended') else 'Activo',
                    'Ultima Conexion': u.get('lastLoginTime', 'Nunca')
                })
        print(f"\n✅ Éxito: Se ha creado el archivo '{nombre_archivo}' con {len(usuarios)} registros.")
    except IOError as e:
        print(f"Error al escribir el CSV: {e}")

if __name__ == '__main__':
    print("--- Extractor de Usuarios Google Workspace ---")
    lista = extraer_usuarios()
    if lista:
        guardar_a_csv(lista)
