import requests, random
from data_models import SolicitudN8n, RespuestaN8n
from config import N8N_WEBHOOK_URL, API_KEY, TIMEOUT, SESSION_PREFIX

def nuevo_id_sesion() -> str:
    """Genera un ID de sesión nuevo para cada conversación"""
    return f"{SESSION_PREFIX}_{random.randint(1000, 9999)}"

def enviar_consulta(solicitud):
    """Envía una consulta al webhook de n8n y devuelve la respuesta."""
    carga_util = {
        "chatInput": solicitud.entrada_chat,
        "sessionId": solicitud.id_sesion,
    }

    if solicitud.intencion:
        carga_util["intent"] = solicitud.intencion
    if solicitud.parametros:
        carga_util["params"] = solicitud.parametros

    encabezados = {
        "Content-Type": "application/json",
    }
    if API_KEY:
        encabezados["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        respuesta = requests.post(N8N_WEBHOOK_URL, json=carga_util, headers=encabezados, timeout=TIMEOUT)
        respuesta.raise_for_status()
        try:
            datos = respuesta.json()
            
            # n8n puede devolver: 
            # 1. Array con un objeto: [{ mensaje_ia, data, accion, query_sql }]
            # 2. Objeto directo: { mensaje_ia, data, ... }
            # 3. Datos directos: { "Cantidad de envíos fallidos": "1" }
            
            # Caso 1: Si es un array con un elemento, extraer ese elemento
            if isinstance(datos, list) and len(datos) == 1 and isinstance(datos[0], dict):
                elemento = datos[0]
                return RespuestaN8n(
                    ok = True,
                    mensaje = elemento.get("mensaje_ia") or elemento.get("mensaje"),
                    datos = elemento.get("data"),
                )
            # Caso 2: Si es un dict con campos específicos de n8n
            elif isinstance(datos, dict) and ('mensaje_ia' in datos or 'mensaje' in datos or 'data' in datos):
                return RespuestaN8n(
                    ok = True,
                    mensaje = datos.get("mensaje_ia") or datos.get("mensaje"),
                    datos = datos.get("data"),
                )
            # Caso 3: Respuesta directa sin estructura
            else:
                return RespuestaN8n(
                    ok = True,
                    mensaje = None,
                    datos = datos,
                )
        except ValueError:
            return RespuestaN8n(
                ok = True, 
                mensaje = respuesta.text,
            )
    except requests.RequestException as e:
        return RespuestaN8n(
            ok=False,
            mensaje=f"Error de conexión al webhook de n8n: {str(e)}",
            datos=None,
        )
