from n8n_client import send_query, new_session_id 
#send_query funcion que se encarga de hablar con n8n, mandando consultas y recibiendo respuestas; new_session_id genera un id de sesion unico para cada conversacion
from data_models import N8nRequest 
#N8nRequest trae la esttructura de datos para las solicitudes y respuestas de n8n, el model que se envia a send_query
from report_generator import generate_excel_csv 
#generate_excel_csv funcion para generar reportes en excel o csv
import re 
# libreria para trabajar con expresiones regulares, sede para validar codigos de envio

# Constante APP_TITLE para el titulo de la aplicacion, que se muestra en el menu principal

APP_TITLE = "Bienvenido a Piki. Tu envío, sin estrés." 

# Funcion para validar el codigo de envio usando expresiones regulares

# Recibe un codigo de envio como cadena y devuelve True si es valido, False en caso contrario, saca espacioos en blanco al inicio y final, solo acepta letras (A-Z) y numeros (0-9) entre 10 y 20 caracteres de longitud
def validar_codigo_envio(codigo: str) -> bool: #convierte srting de codigo a boolean
    # Valida que el código de envío tenga entre 10 y 20 caracteres alfanuméricos
    return bool(re.fullmatch(r'[A-Z0-9]{1,20}', codigo.strip(), flags=re.I)) #r indica que es una raw string (cadena cruda), evita problemas con barras invertidas
    #re.fullmatch busca coincidencia completa con la expresion regular, re.I: insensible a mayusculas y minusculas

# Funcion para imprimir el menu principal de la aplicacion, muestra las opciones disponibles para el usuario 
def print_menu():
    print(f"=== {APP_TITLE} ===") #Imprime el titulo de la aplicacion
    print("[1] Consultar estado de un envío") 
    print("[2] Generar reporte de envios fallidos")
    print("[3] Generar reporte por repartidos o localidad")
    print("[4] Realizar consulta personalizada")
    print("[h] Ayuda [0] Salir")

# Maneja la opcion 1 del menu: Consultar estado de un envio

def handle_opcion_1(session_id: str): #convierte a string el id de sesion
    codigo = input("Ingrese el código de envío: ").strip() #pide al usuario que ingrese el codigo de envio, strip elimina espacios en blanco al inicio y final
    if not validar_codigo_envio(codigo): # si no valida el codigo usando validar_codigo_envio
        print("Código de envío inválido. Debe contener entre 10 y 20 caracteres alfanuméricos.") # imprime mensaje de error
        return
    # Envia un objeto N8nRequest a n8n con el codigo de envio
    req = N8nRequest( #llama a a la clase N8nRequest para crear un nuevo objeto de solicitud
        chat_input = f"Consultar estado del envío con código {codigo}", # mensaje de entrada para n8n, utilizado por n8n/IA para entender la consulta ademas de intent y params
        session_id = session_id, #id de sesion unico para la conversacion, para agrupar consultas del usuario
        intent = "consultar_estado", # intencion de la consulta, n8n puede usar esto para determinar que flujo o accion ejecutar
        params = {"codigo": codigo} #parametros adicionales para la consulta, en este caso el codigo de envio proporcionado por el usuario
    )
    # Envía la consulta y obtiene la respuesta

    res = send_query(req) #llama a send_query para enviar la solicitud a n8n y obtener la respuesta
    if res.ok: #si la respuesta es exitosa
        print(res.message or "No se encontró información para el código proporcionado.") #Abarca tanto el mensaje de exito como el caso de no encontrar informacion
    else:
        print(f"Error al consultar el envío: {res.message}") #mensaje de error en caso de fallo en la consulta

# Maneja la opcion 2 del menu: Generar reporte de envios fallidos

def handle_opcion_2(session_id):
    req = N8nRequest(
        chat_input = "Generar reporte de envíos fallidos",
        session_id = session_id,
        intent = "reporte_fallidos", #para que n8n sepa que flujo ejecutar, me debe devolver los envios fallidos
    ) #Obs: no hay params porque el reporte es general, no requiere filtros adicionales

    res = send_query(req)

    if res.ok and res.data: #si la respuesta es exitosa y res.data TIENE datos

        path = generate_excel_csv(res.data, filename = "reporte_envios_fallidos", to = "xlsx") #genera el reporte en excel, res.data contiene los datos para el reporte
        print(f"Reporte generado exitosamente: {path}") #informa al usuario que el reporte se genero exitosamente y muestra la ruta del archivo
    elif res.ok:
        print("No hay envíos fallidos para generar el reporte.")
    else:
        print(f"Error al generar el reporte: {res.message}")

def handle_opcion_3(session_id: str):
    localidad = input("Ingrese la localidad (o deje vacío para filtrar por repartidor): ").strip() or None
    repartidor = input("Ingrese el nombre del repartidor (o deje vacío para filtrar por localidad): ").strip() or None
    if not localidad and not repartidor:
        print("Debe proporcionar al menos una localidad o un repartidor para generar el reporte.")
        return
    req = N8nRequest(
        chat_input = f"Generar reporte de localidad o repartidor",
        session_id = session_id,
        intent = "reporte_repartidor_localidad",
        params = {"localidad": localidad, "repartidor": repartidor},
    )

    res = send_query(req)

    if res.ok and res.data:
        path = generate_excel_csv(res.data, filename = "reporte_localida_repoartidor", to = "xlsx")
        print(f"Reporte generado exitosamente: {path}")
    elif res.ok:
        print(res.message or"No hay datos para el filtro proporcionado.")
    else:
        print(f"Error al generar el reporte: {res.message}")

def handle_opcion_4(session_id: str):
    consulta = input("Ingrese su consulta personalizada: ").strip()
    if not consulta:
        print("La consulta no puede estar vacía.")
        return
    req = N8nRequest(
        chat_input = consulta,
        session_id = session_id,
        intent = "consulta_personalizada",
    )
    res = send_query(req)
    if res.ok and res.data:
        path = generate_excel_csv(res.data, filename = "reporte_consulta_personalizada", to = "xlsx")
        print(f"Reporte generado exitosamente: {path}")
        print(f"Archivo disponible en: {path}")
    elif res.ok:
        print(res.message or "No se encontró información para la consulta proporcionada.")
    else:
        print(f"Error al procesar la consulta: {res.message}")

def main():
    session_id = new_session_id()
    # print(f"(Sesión: {session_id})")
    while True:
        print_menu()
        opcion = input("Seleccione una opción: ").strip().lower()
        if opcion == "1":
            handle_opcion_1(session_id)
        elif opcion == "2":
            handle_opcion_2(session_id)
        elif opcion == "3":
            handle_opcion_3(session_id)
        elif opcion == "4":
            handle_opcion_4(session_id)
        elif opcion == "h":
            print("Ayuda: Seleccione una opción del menú para realizar una acción específica.")
        elif opcion == "0":
            print("Saliendo del programa. Hasta luego!")
            break
        else:
            print("Opción inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()