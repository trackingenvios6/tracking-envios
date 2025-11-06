import requests
from data_models import N8nRequest, N8nResponse
from config import N8N_WEBHOOK_URL, API_KEY, TIMEOUT, SESSION_PREFIX
import random

def nwe_session_id() -> str:
    #genera un id de sesion nuevo para cada conversacion
    return f"{SESSION_PREFIX}_{random.randint(1000, 9999)}"

def send_query(req):
    """Envía una consulta al webhook de n8n y devuelve la respuesta."""
    payload = {
        "chat_input": req.chat_input,
        "session_id": req.session_id,
    }

    if req.intent:
        payload["intent"] = req.intent 
    if req.params:
        payload["params"] = req.params

    headers = {
        "Content-Type": "application/json",}
    if API_KEY:
        headers["Authorization"] = f"bearer {API_KEY}"
    try:
        respuesta = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=TIMEOUT)
        respuesta.raise_for_status()
        try:
            data = respuesta.json()
        except ValueError:
            return N8nResponse(
                ok=data.get("ok", False),
                message=data.get("message"),
                data=data.get("data"),
            )
    except requests.RequestException as e:
        return N8nResponse(
            ok=False,
            message=f"Error de conexión al webhook de n8n: {str(e)}",
            data=None,
        )