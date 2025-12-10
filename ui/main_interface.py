# streamlit_app.py
import streamlit as st
import uuid
import pandas as pd
import time
import sys
from typing import Dict, Any, List

# 1. IMPORTACIONES DE LÓGICA CENTRAL Y UTILIDADES
try:
    from n8n_client import enviar_consulta
    from data_models import SolicitudN8n
    from utils.formateo import extraer_mensaje_y_datos, formatear_datos, filtrar_registros_vacios
    from utils.intent_handler import es_reporte_local, ejecutar_guardado_local_desde_chat
except ImportError as e:
    st.error("🚨 Error al importar módulos de su proyecto:")
    st.code(f"{e}", language='python')
    sys.exit()

# ----------------------------------------------------------------------
# 2. CONFIGURACIÓN VISUAL
# ----------------------------------------------------------------------

COLOR_PRIMARIO = "#194670" 
COLOR_FONDO_CLARO = "#C5E1E6" 

st.set_page_config(page_title="Piki Chatbot", layout="centered")

st.markdown(
    f"""
    <style>
    .stButton > button {{
        background-color: {COLOR_PRIMARIO};
        color: white;
        border-radius: 8px;
    }}
    /* Burbujas del chat */
    [data-testid="stChatMessage"]:nth-child(even) {{
        background-color: {COLOR_FONDO_CLARO};
        border-radius: 10px;
        padding: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------------------------
# 3. CONFIGURACIÓN DEL MENÚ (TEXTO)
# ----------------------------------------------------------------------

# Definimos el menú visualmente
MENU_BIENVENIDA = """
👋 **¡Bienvenido a Piki!** Tu envío, sin estrés.

**¿Qué deseas hacer hoy?** (Escribí el número o tu consulta):

* 🔍 `[1]` **Consultar estado de un envío**
* 📤 `[2]` **Generar reporte para compartir**
* 💬 `[3]` **Iniciar chat con Piki**
* 💾 `[4]` **Generar reporte local**
* 👋 `[0]` **Borrar historial / Salir**
"""

# Mapa para traducir números a frases que la IA entienda mejor
MAPA_COMANDOS = {
    "1": "Quiero consultar el estado de un envío. ¿Me pedís el número de guía?",
    "2": "Quiero generar un reporte para compartir.",
    "3": "Hola Piki, quiero hacerte una consulta general.",
    "4": "Quiero generar un reporte local y descargarlo.",
}

# ----------------------------------------------------------------------
# 4. GESTIÓN DE ESTADO Y LÓGICA
# ----------------------------------------------------------------------

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.historial_chat = []
    
    # Agregamos el menú como primer mensaje
    st.session_state.historial_chat.append({
        "rol": "assistant",
        "texto": MENU_BIENVENIDA,
        "datos": None
    })
    
SESSION_ID = st.session_state.session_id

def mostrar_respuesta_animada(contenedor, texto: str) -> str:
    """Efecto de escritura tipo máquina."""
    salida = ""
    for char in texto:
        salida += char
        contenedor.markdown(salida)
        time.sleep(0.01) # Un poco más rápido para menús
    return salida

def format_structured_data(datos: Any) -> str:
    """Formatea datos simples (diccionarios) a texto."""
    if not datos: return ""
    if isinstance(datos, dict):
        output = f"\n\n📦 **Detalles encontrados:**\n\n"
        datos_formateados = formatear_datos(datos)
        for key, value in datos_formateados.items():
            if value: output += f"• **{key}:** `{value}`\n"
        return output
    elif isinstance(datos, list):
        return f"\n\n📄 **Se encontraron {len(datos)} resultados**."
    return str(datos)

def handle_n8n_response(prompt: str, session_id: str):
    """Lógica principal de comunicación con n8n."""
    
    # 1. TRADUCCIÓN DE COMANDOS (Nuevo)
    # Si el usuario escribe "1", enviamos la frase completa a n8n
    prompt_procesado = MAPA_COMANDOS.get(prompt.strip(), prompt)
    
    req = SolicitudN8n(entrada_chat=prompt_procesado, id_sesion=session_id, intencion="consulta_personalizada")

    with st.spinner("🤖 Piki está procesando..."):
        # time.sleep(0.3) # Opcional: reducir latencia artificial
        res = enviar_consulta(req)
        
    if not res.ok:
        return f"🚫 Error: {res.mensaje}", None, False
        
    mensaje, datos = extraer_mensaje_y_datos(res)
    datos = filtrar_registros_vacios(datos)
    is_local_report = es_reporte_local(res)
    is_table_data = isinstance(datos, list) and len(datos) > 1 and not is_local_report
    
    output_text = ""
    
    # Lógica de Reporte Local
    if is_local_report and datos:
        output_text += "✅ **Reporte Local Detectado**."
        try:
            path = ejecutar_guardado_local_desde_chat(res=res, nombre_base=f"reporte_{session_id[:4]}")
            if path: output_text += f"\n\n💾 Archivo guardado en: `{path}`"
        except Exception as e: output_text += f"\n\n❌ Error: {e}"
        
    # Formateo de texto
    formatted_data = ""
    if datos and not is_table_data:
        # Si es un solo dato, formatearlo bonito en texto
        d = datos[0] if isinstance(datos, list) else datos
        formatted_data = format_structured_data(d)
    elif is_table_data:
        formatted_data = f"\n\n📄 **Tabla con {len(datos)} resultados generada.**"

    if mensaje: output_text = f"🤖 {mensaje}\n" + output_text.strip() + formatted_data
    else: output_text = output_text.strip() + formatted_data

    if not output_text: output_text = "No se recibió respuesta válida."
        
    return output_text, datos, is_table_data

# ----------------------------------------------------------------------
# 5. MAIN
# ----------------------------------------------------------------------

def main():
    st.title("📦 PIKI - Tracking Inteligente")
    # Asegurar que las claves de session_state existen (protege contra ejecuciones
    # donde la inicialización a nivel de módulo no se haya ejecutado en esta sesión)
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'historial_chat' not in st.session_state:
        st.session_state.historial_chat = []
        st.session_state.historial_chat.append({"rol": "assistant", "texto": MENU_BIENVENIDA, "datos": None})
    # Actualizar la variable global SESSION_ID para usar el id actual de la sesión
    global SESSION_ID
    SESSION_ID = st.session_state.session_id
    
    # Renderizado del historial
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["texto"])
            # Si hay tabla guardada en el historial, mostrarla
            if mensaje.get("is_table_data") and mensaje.get("datos"):
                st.dataframe(pd.DataFrame(mensaje["datos"]), use_container_width=True)

    # Input del usuario
    user_input = st.chat_input("Escribe una opción [1-4] o tu consulta...")

    if user_input:
        # Lógica especial para opción [0] Salir/Limpiar
        if user_input.strip() == "0":
            st.session_state.historial_chat = [] # Limpiamos historial
            st.session_state.session_id = str(uuid.uuid4()) # Nueva sesión
            # Volvemos a agregar el menú
            st.session_state.historial_chat.append({"rol": "assistant", "texto": MENU_BIENVENIDA, "datos": None})
            st.rerun()

        # 1. Mostrar mensaje del usuario
        # Si es un número, mostramos el número, pero internamente Piki sabe qué significa
        st.session_state.historial_chat.append({"rol": "user", "texto": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Procesar
        output_text, raw_data, is_table_data = handle_n8n_response(user_input, SESSION_ID)

        # 3. Respuesta Asistente
        with st.chat_message("assistant"):
            cont = st.empty()
            final_text = mostrar_respuesta_animada(cont, output_text)
            
            if is_table_data and raw_data:
                st.dataframe(pd.DataFrame(raw_data), use_container_width=True)
        
        # 4. Guardar en historial
        st.session_state.historial_chat.append({
            "rol": "assistant", 
            "texto": final_text, 
            "datos": raw_data, 
            "is_table_data": is_table_data
        })
        
        st.rerun()

if __name__ == "__main__":
    main()