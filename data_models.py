class SolicitudN8n:
    """
    Representa una solicitud enviada al sistema n8n.

    Esta clase encapsula los datos necesarios para construir la consulta
    hacia el webhook, incluyendo texto del usuario, su identificador de sesión,
    y metadatos opcionales como la intención detectada o parámetros adicionales.
    """

    def __init__(self, entrada_chat, id_sesion, intencion=None, parametros=None):
        """
        Inicializa una nueva instancia de SolicitudN8n.

        Args:
            entrada_chat (str): Texto ingresado por el usuario.
            id_sesion (str): Identificador único que mantiene el contexto de la conversación.
            intencion (str, opcional): Intención detectada o asignada para el mensaje.
            parametros (dict, opcional): Conjunto de parámetros adicionales que n8n pueda necesitar.

        Notes:
            Si no se envían parámetros, se inicializa un diccionario vacío
            para evitar problemas al manipularlos posteriormente.
        """
        self.entrada_chat = entrada_chat
        self.id_sesion = id_sesion
        self.intencion = intencion
        self.parametros = parametros if parametros is not None else {}


class RespuestaN8n:
    """
    Representa la respuesta estándar retornada por n8n.

    Esta clase permite unificar distintos tipos de respuestas, ya sea que
    n8n devuelva un mensaje estructurado, datos adicionales o un error.
    """

    def __init__(self, ok, mensaje=None, datos=None, error=None, intencion=None):
        """
        Inicializa una respuesta proveniente de n8n.

        Args:
            ok (bool): Indica si la operación fue exitosa.
            mensaje (str, opcional): Mensaje generado por n8n o por el sistema.
            datos (any, opcional): Información devuelta por el workflow, puede ser dict, lista o valor primitivo.
            error (str, opcional): Descripción del error si la operación falló.
            intencion (str, opcional): Intención estructurada detectada por n8n (ej: "reporte_local", "compartir").
        """
        self.ok = ok
        self.mensaje = mensaje
        self.datos = datos
        self.error = error
        self.intencion = intencion
