"""
Módulo de manejo de errores y validaciones para el sistema de tracking de envíos.

Este módulo centraliza:
- Constantes de mensajes de error
- Funciones de validación de respuestas de n8n
- Procesamiento de datos y mensajes
"""

from data_models import RespuestaN8n


# ============================================================================
# CONSTANTES DE MENSAJES DE ERROR
# ============================================================================

# Mensajes de error generales
ERROR_N8N_SIN_RESPUESTA = "n8n no devolvió mensaje; no se pudo generar el reporte."
ERROR_CONSULTA_VACIA = "La consulta no puede estar vacía."
ERROR_CODIGO_INVALIDO = "Código de envío inválido. Debe contener entre 1 y 20 caracteres alfanuméricos."

# Mensajes cuando no hay datos
MSG_SIN_ENVIOS_FALLIDOS = "No hay envíos fallidos para generar el reporte."
MSG_SIN_DATOS_FILTRO = "No hay datos para el filtro proporcionado."
MSG_SIN_DATOS_CONSULTA = "La consulta no devolvió datos para generar un reporte."
MSG_SIN_INFO_CODIGO = "No se encontró información para el código proporcionado."

# Mensajes de éxito
MSG_REPORTE_GENERADO = "Reporte generado exitosamente"
MSG_PROCESADO_CORRECTAMENTE = "n8n procesó la solicitud correctamente."


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def obtener_mensaje_desde_data(data) -> str | None:
    """
    Extrae el mensaje de la IA desde diferentes estructuras de datos.
    
    Args:
        data: Datos de respuesta de n8n (puede ser dict, list, etc.)
    
    Returns:
        str | None: Mensaje extraído o None si no se encuentra
    """
    if isinstance(data, dict):
        return data.get("mensaje_ia") 
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0].get("mensaje_ia") 
    return None # No se encontró mensaje

def normalizar_registros_respuesta(datos):
    """
    Normaliza diferentes formatos de respuesta a una lista de registros.
    
    Args:
        datos: Datos de respuesta de n8n
    
    Returns:
        list: Lista de registros normalizada
    """
    if datos is None:
        return []
    if isinstance(datos, list):
        return datos
    if isinstance(datos, dict):
        # Si tiene un campo 'data' interno que es lista, úsalo
        interno = datos.get("data")
        if isinstance(interno, list):
            return interno
        # Si no, devuelve el dict como único registro
        return [datos]
    return [datos]


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validar_respuesta_n8n(res: RespuestaN8n, mensaje_sin_datos: str) -> tuple[bool, list, str | None]:
    """
    Valida la respuesta de n8n y retorna si es válida, los registros y el mensaje.
    
    Esta función centraliza la validación de respuestas de n8n, verificando:
    1. Si la respuesta fue exitosa (res.ok)
    2. Si hay datos disponibles
    3. Muestra mensajes de error apropiados
    
    Args:
        res: RespuestaN8n objeto con la respuesta de n8n
        mensaje_sin_datos: Mensaje a mostrar si no hay datos disponibles
    
    Returns:
        tuple[bool, list, str | None]: 
            - bool: True si la validación es exitosa, False en caso contrario
            - list: Lista de registros normalizados (vacía si no hay datos)
            - str | None: Mensaje extraído de los datos (si existe)
    
    Ejemplos:
        >>> res = enviar_consulta(req)
        >>> valido, registros, mensaje = validar_respuesta_n8n(res, MSG_SIN_ENVIOS_FALLIDOS)
        >>> if not valido:
        >>>     return
        >>> # Procesar registros...
    """
    # Verificar si la respuesta fue exitosa
    if not res.ok:
        print(f"Error: {res.mensaje or ERROR_N8N_SIN_RESPUESTA}")
        return False, [], None
    
    # Normalizar y extraer registros
    registros = normalizar_registros_respuesta(res.datos)
    mensaje = obtener_mensaje_desde_data(res.datos)
    
    # Verificar si hay datos
    if not registros:
        print(mensaje_sin_datos)
        if mensaje:
            print(mensaje)
        return False, [], mensaje
    
    return True, registros, mensaje


def mostrar_mensaje_si_existe(mensaje: str | None) -> None:
    """
    Muestra un mensaje si existe (no es None ni vacío).
    
    Args:
        mensaje: Mensaje a mostrar
    """
    if mensaje:
        print(mensaje)
