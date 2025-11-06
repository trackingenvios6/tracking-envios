import json
import http.client 

HOST = "localhost"
PORT = 8000 # anda a saber, xq lo tengo que sacar del n8n en docker jeje
PATH = "/webhook/MI_ID/chat" #TAMBIEN es un ejemplo que lo tengo que sacar del webhook, no tengo idea de cual es jeje

"""
def send_message_to_webhook(message): #baje y me aparecio esto asi que tuve q buscar que es y re piola que me lo haya recomendado xD (se pone a estudiar que mierda dice)
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {'Content-type': 'application/json'}
    payload = json.dumps({"message": message})
    conn.request("POST", PATH, payload, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data #uuh para, te pedi la hora nomas, se me completo solo el codigo xD
"""

def send_message_to_webhook(texto: str, session_id: str, headers: dict | None = None) -> dict: 
    #le envia un mensajito ahi pumpum a n8n y devuelve un json de respuesta.
    payload = {    
        "chatInput" : texto,
        "sessionId": session_id
    } #mucho muy importante, porque si no le mandas el sessionId, n8n te lo trata como una nueva conversacion cada vez

    body = json.dumps(payload)
    request_headers = {"content-type": "application/json"}

    if headers:
        request_headers.update(headers) 
        #si me pasan headers adicionales, los agrego
        
    conn = http.client.HTTPConnection(HOST, PORT, timeout=10) #timeout de 10 segundos para que no se cuelgue

    try: 
        conn.request("POST", PATH, body, request_headers)
        res = conn.getresponse()
        raw = res.read().decode("utf-8", errors="replace") #decodifico la respuesta

        if res.status != 200:
            return {
                "ok": False, 
                "status": res.status, 
                "reason": res.reason, 
                "body": raw} 
        #Si no es 200, me ataja el error con un mensaje de error.

        return json.loads(raw) if raw else { 
            "ok": True, 
            "reply": None
            } #si no hay body, devuelvo un ok vacio  
    
    except Exception as e:
        return {
            "ok": False, 
            "error": str(e)
            } #si hay cualquier error, lo devuelvo en el json
    
    finally:    
        conn.close()
        #cierro la conexion siempre dijo el profe mau u.u

