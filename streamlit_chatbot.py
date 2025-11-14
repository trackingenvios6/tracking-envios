import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import requests

# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Chatbot de Tracking de Envíos", layout="centered")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ==========================================
# CARGA DE DATOS LOCAL (solo si existe la carpeta)
# ==========================================
@st.cache_data
def load_data():
    envios_path = os.path.join(DATA_DIR, "envios.csv")
    movimientos_path = os.path.join(DATA_DIR, "movimientos.csv")
    repartidores_path = os.path.join(DATA_DIR, "repartidores.csv")

    def safe_load(path, cols):
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame(columns=cols)
        return df

    envios = safe_load(envios_path, [
        "codigo", "remitente_nombre", "remitente_apellido", "destinatario_nombre", "destinatario_apellido",
        "email_remitente", "email_destinatario", "domicilio_destinatario", "peso", "tipo_envio", "estado"
    ])
    movimientos = safe_load(movimientos_path, [
        "codigo", "estado", "centro_distribucion", "repartidor", "motivo", "timestamp"
    ])
    repartidores = safe_load(repartidores_path, [
        "nombre", "apellido", "direccion", "telefono", "email", "fecha_nacimiento", "localidades_asignadas"
    ])
    return envios, movimientos, repartidores

# ==========================================
# EFECTO DE RESPUESTA ANIMADA
# ==========================================
def mostrar_respuesta_animada(texto):
    contenedor = st.empty()
    salida = ""
    for char in texto:
        salida += char
        contenedor.markdown(salida)
        time.sleep(0.02)

# ==========================================
# CONEXIÓN CON N8N
# ==========================================
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/prueba2"  # ✅ tu URL

def enviar_mensaje_n8n(session_id, mensaje):
    payload = {
        "sessionId": session_id,
        "chatInput": mensaje
    }
    try:
        # Aumento el timeout a 30s
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=300)

        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                return {"error": "La respuesta de n8n no fue un JSON válido."}

        elif response.status_code == 504:
            return {"error": "El flujo de n8n tardó demasiado en responder (timeout)."}
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}

    except requests.exceptions.Timeout:
        return {"error": "⏱️ El servidor n8n tardó demasiado en responder."}

    except requests.exceptions.ConnectionError:
        return {"error": "🚫 No se pudo conectar con n8n. Verificá que esté corriendo."}

    except Exception as e:
        return {"error": f"⚠️ Error inesperado: {str(e)}"}


# ==========================================
# RESPUESTAS LOCALES DE BACKUP
# ==========================================
def procesar_consulta_local(mensaje):
    mensaje = mensaje.lower().strip()
    if any(p in mensaje for p in ["hola", "buenas", "ayuda", "qué podés hacer"]):
        return (
            "👋 ¡Hola! Soy el asistente de tracking. Puedo ayudarte con:\n"
            "- Ver movimientos de un envío (ej: 'detalle del envío AB0012352')\n"
            "- Listar envíos fallidos\n"
            "- Generar un Excel con las localidades por repartidor\n"
            "- Guardar los envíos no entregados"
        )
    return "No entendí la consulta. Probá con algo como: 'detalle del envío AB0012352'."

# ==========================================
# FORMATEO DE FECHA
# ==========================================
def formatear_fecha(fecha_iso):
    try:
        fecha = datetime.fromisoformat(fecha_iso.replace("Z", ""))
        return fecha.strftime("%d/%m/%Y %H:%M hs")
    except:
        return fecha_iso

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
def main():
    st.title("💬 Chatbot de Tracking de Envíos")
    st.write("Interactuá conmigo para consultar información sobre el sistema conectado a Supabase (vía n8n).")

    envios, movimientos, repartidores = load_data()

    if "historial_chat" not in st.session_state:
        st.session_state.historial_chat = []
        st.session_state.historial_chat.append({
            "rol": "assistant",
            "texto": "👋 ¡Bienvenido! Podés consultarme el estado de un envío o pedirme ayuda para ver qué puedo hacer."
        })

    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["texto"])

    user_input = st.chat_input("Escribí tu consulta aquí...")

    if user_input:
        st.session_state.historial_chat.append({"rol": "user", "texto": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            respuesta_n8n = enviar_mensaje_n8n("user123", user_input)

            # Si hubo error o no se conecta
            if "error" in respuesta_n8n:
                texto_respuesta = procesar_consulta_local(user_input)
                mostrar_respuesta_animada(texto_respuesta)
                st.session_state.historial_chat.append({"rol": "assistant", "texto": texto_respuesta})
            else:
                # ✅ Caso en que el flujo devuelve data (como en tu ejemplo de Postman)
                if "data" in respuesta_n8n:
                    envio = respuesta_n8n["data"]
                    llegada = formatear_fecha(envio.get("Llegada Estimada", "N/D"))
                    texto_respuesta = (
                        f"📦 **Estado del envío solicitado:**\n\n"
                        f"• **Código:** `{envio.get('Cód. Envío', 'N/D')}`\n"
                        f"• **Dirección destino:** `{envio.get('Dirección Destino', 'N/D')}`\n"
                        f"• **Llegada estimada:** `{llegada}`"
                    )
                else:
                    texto_respuesta = respuesta_n8n.get("respuesta", "No se recibió una respuesta válida del servidor.")

                mostrar_respuesta_animada(texto_respuesta)
                st.session_state.historial_chat.append({"rol": "assistant", "texto": texto_respuesta})


if __name__ == "__main__":
    main()
