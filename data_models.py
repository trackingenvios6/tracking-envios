class SolicitudN8n:
    def __init__(self, entrada_chat, id_sesion, intencion = None, parametros = None):
        self.entrada_chat = entrada_chat
        self.id_sesion = id_sesion
        self.intencion = intencion
        self.parametros = parametros if parametros is not None else {}

class RespuestaN8n: 
    def __init__(self, ok, mensaje = None, datos = None, error = None):
        self.ok = ok
        self.mensaje = mensaje
        self.datos = datos
        self.error = error