import requests
import random
from data_models import SolicitudN8n, RespuestaN8n
from config import N8N_WEBHOOK_URL, API_KEY, TIMEOUT, SESSION_PREFIX


def nuevo_id_sesion() -> str:
    """
    Genera un ID de sesión nuevo para cada conversación.

    Returns:
        str: Identificador único de sesión con el prefijo definido en configuración.
    """
    return f"{SESSION_PREFIX}_{random.randint(1000, 9999)}"


def enviar_consulta(solicitud: SolicitudN8n) -> RespuestaN8n:
    """
    Envía una consulta al webhook de n8n y procesa la respuesta obtenida.

    Se utiliza una estrategia de "guard clauses" para validar condiciones
    de error o entradas inválidas desde el inicio, evitando que el flujo
    principal del procesamiento quede anidado innecesariamente.

    Args:
        solicitud (SolicitudN8n): Datos enviados al servidor, incluyendo texto,
            id de sesión, intención opcional y parámetros adicionales.

    Returns:
        RespuestaN8n: Respuesta estandarizada con estado, mensaje y datos.
    """

    # ▶ Guard Clause: solicitud o entrada inválida
    if not solicitud or not solicitud.entrada_chat:
        return RespuestaN8n(
            ok=False,
            mensaje="Solicitud inválida: se requiere entrada de usuario.",
            datos=None,
        )

    # Construcción del cuerpo de la petición para n8n
    carga_util = {
        "chatInput": solicitud.entrada_chat,
        "sessionId": solicitud.id_sesion,
    }

    # Parámetros opcionales
    if solicitud.intencion:
        carga_util["intent"] = solicitud.intencion

    if solicitud.parametros:
        carga_util["params"] = solicitud.parametros

    # Encabezados para la petición HTTP
    encabezados = {"Content-Type": "application/json"}
    if API_KEY:
        encabezados["Authorization"] = f"Bearer {API_KEY}"

    # ▶ Realizar solicitud HTTP
    try:
        respuesta_http = requests.post(
            N8N_WEBHOOK_URL,
            json=carga_util,
            headers=encabezados,
            timeout=TIMEOUT
        )
        respuesta_http.raise_for_status()

    except requests.RequestException as error:
        # ▶ Guard Clause: error de red o HTTP
        return RespuestaN8n(
            ok=False,
            mensaje=f"Error de conexión al webhook de n8n: {str(error)}",
            datos=None,
        )

    # ▶ Intentar decodificar JSON
    try:
        contenido = respuesta_http.json()
    except ValueError:
        # Si no es JSON, devolver el texto crudo
        return RespuestaN8n(
            ok=True,
            mensaje=respuesta_http.text,
            datos=None,
        )

    # ─────────────────────────────────────────────
    #  Interpretación de la respuesta del servidor
    # ─────────────────────────────────────────────
    #
    # n8n puede responder de diferentes formas:
    #
    # 1) Lista con un diccionario dentro
    # 2) Diccionario con claves conocidas
    # 3) Cualquier otro tipo de dato (se devuelve tal cual)
    #

    # Caso 1: lista con un solo diccionario
    if isinstance(contenido, list) and len(contenido) == 1 and isinstance(contenido[0], dict):
        elemento = contenido[0]
        return RespuestaN8n(
            ok=True,
            mensaje=elemento.get("mensaje_ia") or elemento.get("mensaje"),
            datos=elemento.get("data"),
        )

    # Caso 2: diccionario con estructura típica de n8n
    if isinstance(contenido, dict) and (
        "mensaje_ia" in contenido or
        "mensaje" in contenido or
        "data" in contenido
    ):
        return RespuestaN8n(
            ok=True,
            mensaje=contenido.get("mensaje_ia") or contenido.get("mensaje"),
            datos=contenido.get("data"),
        )

    # Caso 3: respuesta directa sin estructura conocida
    return RespuestaN8n(
        ok=True,
        mensaje=None,
        datos=contenido,
    )
