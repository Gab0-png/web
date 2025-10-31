import os
import pickle
import base64
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from starlette.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleAuthRequest
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# ============================================================================
# CONFIGURACIÓN DE FASTAPI
# ============================================================================

app = FastAPI(
    title="Portafolio Personal",
    description="Portafolio personal desarrollado con FastAPI y Gmail API",
    version="1.0.0"
)

# Montar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar plantillas Jinja2
templates = Jinja2Templates(directory="templates")

# ============================================================================
# CONFIGURACIÓN DE GMAIL API
# ============================================================================

# Scopes requeridos para enviar correos
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

def get_gmail_service():
    """
    Obtiene el servicio de Gmail autenticado.
    Usa OAuth 2.0 para autenticación.
    
    Returns:
        Servicio de Gmail autenticado o None si hay error
    """
    creds = None
    
    # Si existe token.pickle, cargarlo
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, obtener nuevas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleAuthRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, GMAIL_SCOPES)
            creds = flow.run_local_server(host='127.0.0.1', port=8080)
        
        # Guardar las credenciales para próximas ejecuciones
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def send_gmail_message(recipient_email: str, subject: str, message_body: str) -> bool:
    """
    Envía un correo usando la API de Gmail.
    
    Args:
        recipient_email (str): Email del destinatario
        subject (str): Asunto del correo
        message_body (str): Cuerpo del mensaje
    
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        # Verificar que el archivo de credenciales existe
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"Error: {CREDENTIALS_FILE} no encontrado")
            return False
        
        # Obtener el servicio de Gmail
        service = get_gmail_service()
        
        # Crear el mensaje
        message = MIMEText(message_body)
        message['to'] = recipient_email
        message['subject'] = subject
        
        # Codificar el mensaje en base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Enviar el mensaje
        send_message = {'raw': raw_message}
        service.users().messages().send(userId='me', body=send_message).execute()
        
        print(f"Correo enviado exitosamente a {recipient_email}")
        return True
    
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

# ============================================================================
# RUTAS
# ============================================================================

@app.get("/")
async def home(request: Request):
    """
    Ruta principal que renderiza la página de inicio (index.html).
    
    Args:
        request (Request): Objeto de solicitud de Starlette
    
    Returns:
        TemplateResponse: Renderiza index.html
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/send_email")
async def send_email(
    nombre: str = Form(...),
    email: str = Form(...),
    mensaje: str = Form(...)
):
    """
    Endpoint para enviar correos desde el formulario de contacto.
    
    Args:
        nombre (str): Nombre del remitente
        email (str): Email del remitente
        mensaje (str): Mensaje a enviar
    
    Returns:
        JSONResponse: Estado de éxito o error con mensaje descriptivo
    """
    # Validar que los campos no estén vacíos
    if not nombre or not email or not mensaje:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Todos los campos son requeridos"}
        )
    
    # Validar formato de email básico
    if '@' not in email or '.' not in email:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Email inválido"}
        )
    
    # Preparar el cuerpo del mensaje
    message_body = f"""Nuevo mensaje de contacto:

Nombre: {nombre}
Email: {email}

Mensaje:
{mensaje}
"""
    
    # Enviar el correo
    success = send_gmail_message(
        recipient_email="titandediamond@gmail.com", # GMAIL
        subject=f"Nuevo mensaje de {nombre}",
        message_body=message_body
    )
    
    if success:
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Correo enviado exitosamente"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Error al enviar el correo"}
        )

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
