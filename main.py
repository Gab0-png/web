import os
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ============================================================================
# CONFIGURACIÓN DE FASTAPI
# ============================================================================

app = FastAPI(
    title="Portafolio Personal",
    description="Portafolio personal desarrollado con FastAPI y SMTP (Gmail)",
    version="2.0.0"
)

# Montar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar plantillas Jinja2
templates = Jinja2Templates(directory="templates")

# ============================================================================
# CONFIGURACIÓN DE CORREO (SMTP)
# ============================================================================

# Datos del remitente (tu cuenta de Gmail)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "gabito150906@gmail.com")  # <-- tu Gmail
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Contraseña de aplicación

def send_email(to_email: str, subject: str, message_body: str) -> bool:
    """
    Envía un correo utilizando SMTP de Gmail.
    """
    try:
        msg = MIMEText(message_body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        # Conexión segura con Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"Correo enviado exitosamente a {to_email}")
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

# ============================================================================
# RUTAS
# ============================================================================

@app.get("/")
async def home(request: Request):
    """
    Ruta principal que renderiza la página de inicio (index.html).
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/send_email")
async def send_email_endpoint(
    nombre: str = Form(...),
    email: str = Form(...),
    mensaje: str = Form(...)
):
    """
    Endpoint para enviar correos desde el formulario de contacto.
    """
    if not nombre or not email or not mensaje:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Todos los campos son requeridos"}
        )

    if '@' not in email:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Email inválido"}
        )

    message_body = f"""
Nuevo mensaje de contacto desde tu portafolio web:

Nombre: {nombre}
Email: {email}

Mensaje:
{mensaje}
"""

    # Envía el correo a ti mismo
    success = send_email(
        to_email=EMAIL_ADDRESS,
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
# PUNTO DE ENTRADA LOCAL
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

