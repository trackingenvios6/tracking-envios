import requests, random
from data_models import N8nRequest, N8nResponse
from config import N8N_WEBHOOK_URL, API_KEY, TIMEOUT, SESSION_PREFIX

def new_session_id() -> str:
    #genera un id de sesion nuevo para cada conversacion
    return f"{SESSION_PREFIX}_{random.randint(1000, 9999)}"


#! La función "send_query" envía una request mal estructurada a n8n, esto ocasiona que el programa
#! de python no sepa como "leer" esta información, debido a esto, al intentar acceder a campos
#! inexistentes en la respuesta obtenida desde n8n, el resultado es un None o valor vacío

#? La función "send_query" toma por parametro un elemento "req" o request, que será la solicitud
#? que enviemos a n8n, recordemos que la estructura se ve algo así:
"""
    req = N8nRequest(
        chat_input = f"Consultar estado del envío con código {codigo}", #! Consulta del usuario
        session_id = session_id, #? identificador de sesión (opcional)
        intent = "consultar_estado", #! Intención del usuario (perfecto, no se debe hacer desde n8n)
        params = {"codigo": codigo}, #! Parametros para la consulta, por ejemplo, un codigo de envío 
        #? Cabe aclarar que el campo "params" es, a su vez, otro diccionario ya que pueden haber
        #? múltiples parámetros para realizar la consulta, como ocurre con la opción "enviar_reporte_compartir"
        #? que recibe 2 parametros: "tipo" y "plataforma" 
    )
"""
def send_query(req):

    #! Cabe aclarar que la solicitud a n8n se va a componer de un input (llamado "chatInput") del usuario que será
    #! interpretado por el agente de ia, este input está dentro del campo "body" del JSON de n8n,
    #! de la siguiente manera: json->body->chatInput 

    #! Es importante entender que n8n va a recibir un JSON que indique la consulta ingresada
    #! por consola por el usuario y un identificado de sesión (opcional, ya que se puede generar)
    #! desde n8n para que funcione el nodo de simple memory
    
    #? Como vimos recien (arriba donde está el comentario en verde que dice req = N8nRequest...) el parametro de la función "send_query" recibe un "req" que tiene 
    #? un campo "chat_input", entonces armamos un payload (que vamos a utilizar para armar una solicitud formal a n8n) que contenga esta consulta y el sessionId
    payload = {
        "chatInput": req.chat_input, #! Importante ya que permite a n8n saber qué está consultando el usuario
        "sessionId": req.session_id,  #? Secundario ya que se puede generar desde n8n, pero funciona igual.
    }

    #* Ahora, queremos que desde python se sepa exactamente la intención del usuario, ya que esto le facilita la tarea a n8n y resta trabajo de análisis
    #* Para ello, verificamos que el campo "intent" del parametro "req" contenga algo

    #! Si req.intent tiene algo, entonces...
    if req.intent:
        #! Creo un nuevo campo "intent" en el diccionario "payload" y le asigno el valor de la intencion almacenada en "req"
        payload["intent"] = req.intent
    
    #* Ocurre algo similar con los parametros de la consulta, intento averiguar qué parametros de consulta se generaron durante el uso de la consola

    #! Si hay parametros de consulta en el parametro "req", entonces...
    if req.params:

        #! Creo un campo "params" (parametros) en el diccionario "payload" y le asigno el valor del campo "params" de "req"
        payload["params"] = req.params

    #? Ahora, si estuvieramos utilizando autenticaciones de usuario, la forma ideal de permitir a los usuarios autorizados para que accedan a nuestro sistema sería
    #? a traves de los headers o cabeceras, aunque actualmente no estamos verificando esto y, creo, que se podría eliminar momentaneamente.
    headers = {
        "Content-Type": "application/json",}
    #! Si hay una API key, entonces...
    if API_KEY:

        #! Creo un campo "Authorization" en el diccionario "headers" y le asigno el valor "Bearer + API key"
        headers["Authorization"] = f"Bearer {API_KEY}"


    #* Perfecto, hasta ahora tenemos todo lo necesario para crear una solicitud funcional para n8n:
    #* 1. Un payload con el input del usuario, la intención y los parametros de consulta
    #* 2. Un header para verificar al usuario y el recurso al que quiere acceder 

    #! Definimos una estructura "try/except" para el manejo de errores y excepciones
    
    #! Basicamente, le digo a Python che, hace esto y si te salta un error del tipo 'requests.RequestException', entonces hace esto otro, es como un if
    try:

        #! Quiero dejar en claro que la estructura de retorno que debemos esperar de n8n sería algo como:   
        """
            json {
                "data" : {
                    #? Aca irian los datos obtenidos a partir de la consulta a la base de datos
                },
                "accion" : #? Aca iria la accion que solicito el usuario: 'enviar', 'descargar'...
                "sql_query" : #? Consulta ejecutada sobre la base de datos que trajo la info que está en el campo 'data'    
            }
        """

        #* Hasta ahora, estuvimos viendo cómo se construyen todas las partes necesarias para armar un request a n8n, ahora vamos a generar una solicitud hexa y derexa

        #! La variable 'respueta_request_n8n' va a representar nuestra solicitud a n8n, para ello, tenemos que decirle que se conecte al webhook y enviarle la información
        #! que queremos que le llegue 
        
        #? Si nos fijamos el método 'post' de la libreria 'requests', podemos ver que tiene estos 4 campos que indicamos aca: 'json', 'headers', 'timeout' y un par mas
        #? como 'data' o 'params', es por eso que le decimos, che quiero que el json que envies sea 'payload' que es la estructura que armamos para que n8n sepa que 
        #? informacion debe procesar
        respuesta_request_n8n = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=TIMEOUT)
        respuesta_request_n8n.raise_for_status()

        #TODO -> Comprobar la estructura interna de 'respuesta_request_n8n' para saber si coincide con la estructura que estamos esperando.
        data = respuesta_request_n8n.json() 

        print(data) #! Deberíamos esperar una estructura como la que vimos recien

        #! Esta parte no va a funcionar, porque data no tienen ningun campo 'ok', 'message' ni data, sino que está guardando el resultado de la consulta,
        #! los campos que va a tener el json 'data' serán los nombres y valores de las columnas y registros obtenidos desde la base de datos, por eso hay que revisar 
        #! la estructura que recibe python, porque no sabe cómo interpretar esta información de entrada
        return N8nResponse(
            ok = data.get("ok", False),
            message = data.get("message"),
            data = data.get("data"),
        )
    
    
    #! Esta excepcion se dispara cuando hay un error al realizar la solicitud a n8n, por cualquier motivo, entonces se devuelve un objeto N8nResponse con la
    #! información correspondiente sobre el error.

    #* Esto, para mí, es una solución innecesaria, en lugar, se podría mostrar un mensaje por consola o retornar un string con el error
    except requests.RequestException as e:
        return N8nResponse(
            ok=False,
            message=f"Error de conexión al webhook de n8n: {str(e)}",
            data=None,
        )
    
    #? Bien, volvé al archivo "main_copy.py", linea 194