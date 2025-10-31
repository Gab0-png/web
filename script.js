/**
 * Script para el portafolio personal
 * Maneja la funcionalidad del formulario de contacto
 */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el formulario de contacto
    const contact_form = document.getElementById('contact_form');
    
    // Agregar evento de envío al formulario
    if (contact_form) {
        contact_form.addEventListener('submit', handle_form_submit);
    }
});

/**
 * Maneja el envío del formulario de contacto
 * @param {Event} event - Evento del formulario
 */
async function handle_form_submit(event) {
    // Prevenir el comportamiento por defecto del formulario
    event.preventDefault();
    
    // Obtener los elementos del formulario
    const nombre_input = document.getElementById('nombre');
    const email_input = document.getElementById('email');
    const mensaje_input = document.getElementById('mensaje');
    const status_message = document.getElementById('status_message');
    const submit_button = event.target.querySelector('button[type="submit"]');
    
    // Obtener los valores del formulario
    const nombre = nombre_input.value.trim();
    const email = email_input.value.trim();
    const mensaje = mensaje_input.value.trim();
    
    // Validar que los campos no estén vacíos
    if (!nombre || !email || !mensaje) {
        show_status_message(status_message, 'Por favor completa todos los campos', 'error');
        return;
    }
    
    // Validar formato de email básico
    if (!validate_email(email)) {
        show_status_message(status_message, 'Por favor ingresa un email válido', 'error');
        return;
    }
    
    // Deshabilitar el botón de envío durante la solicitud
    submit_button.disabled = true;
    const original_text = submit_button.textContent;
    submit_button.textContent = 'Enviando...';
    
    try {
        // Crear el objeto FormData
        const form_data = new FormData();
        form_data.append('nombre', nombre);
        form_data.append('email', email);
        form_data.append('mensaje', mensaje);
        
        // Enviar la solicitud al servidor
        const response = await fetch('/send_email', {
            method: 'POST',
            body: form_data
        });
        
        // Parsear la respuesta JSON
        const data = await response.json();
        
        // Verificar si la solicitud fue exitosa
        if (response.ok && data.success) {
            // Mostrar mensaje de éxito
            show_status_message(status_message, data.message, 'success');
            
            // Limpiar el formulario
            contact_form.reset();
            
            // Limpiar el mensaje después de 5 segundos
            setTimeout(() => {
                status_message.classList.add('hidden');
            }, 5000);
        } else {
            // Mostrar mensaje de error
            show_status_message(status_message, data.message || 'Error al enviar el correo', 'error');
        }
    } catch (error) {
        // Manejar errores de red
        console.error('Error:', error);
        show_status_message(status_message, 'Error de conexión. Intenta de nuevo.', 'error');
    } finally {
        // Restaurar el botón de envío
        submit_button.disabled = false;
        submit_button.textContent = original_text;
    }
}

/**
 * Valida el formato de un email
 * @param {string} email - Email a validar
 * @returns {boolean} - True si el email es válido, False en caso contrario
 */
function validate_email(email) {
    // Expresión regular simple para validar email
    const email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return email_regex.test(email);
}

/**
 * Muestra un mensaje de estado en el formulario
 * @param {HTMLElement} element - Elemento donde mostrar el mensaje
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de mensaje ('success' o 'error')
 */
function show_status_message(element, message, type) {
    // Limpiar clases anteriores
    element.classList.remove('success', 'error', 'hidden');
    
    // Agregar la clase del tipo de mensaje
    element.classList.add(type);
    
    // Establecer el texto del mensaje
    element.textContent = message;
    
    // Mostrar el elemento
    element.classList.remove('hidden');
}
