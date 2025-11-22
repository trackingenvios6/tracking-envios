from n8n_client import send_query, new_session_id 
from data_models import N8nRequest
from report_generator import generar_reporte, solicitar_configuracion_salida 
import re 


APP_TITLE = "Bienvenido a Piki. Tu envío, sin estrés." 


def validar_codigo_envio(codigo: str) -> bool: 

    return bool(re.fullmatch(r'[A-Z0-9]{1,20}', codigo.strip(), flags=re.I)) 


def menu_principal():
    print(f"=== {APP_TITLE} ===") 
    print("[1] Consultar estado de un envío") 
    print("[2] Generar reporte para compartir")
    print("[3] Consulta personalizada")
    print("[4] Generar reporte local")
    print("[0] Salir")


def menu_compartir():
    print(f"=== {APP_TITLE} ===") 
    print("[1] Compartir reporte de envíos fallidos") 
    print("[2] Compartir reporte de repartidores")
    print("[3] Consulta personalizada")
    print("[4] Volver al menú principal")
    print("[0] Salir")

def menu_local():
    print(f"=== {APP_TITLE} ===") 
    print("[1] Descargar el reporte de envíos fallidos") 
    print("[2] Descargar el reporte de repartidores")
    print("[3] Consulta personalizada")
    print("[4] Volver al menú principal")
    print("[0] Salir")

def menu_plataforma_compartir():
    print("=== Seleccione la plataforma para compartir ===")
    print("[1] Drive")
    print("[2] Gmail")
    print("[3] Sheets")
    print("[4] Volver al menú anterior")
    print("[0] Salir")

def mostrar_resultado_reporte(path: str, destino: str = "") -> None:
    if destino == "compartir":
        print(f"Reporte generado y listo para compartir en plataforma: {path}")
    elif destino == "local":
        print(f"Reporte descargado localmente en: {path}")
    else:
        print(f"Reporte generado exitosamente: {path}")

def obtener_configuracion_local() -> tuple[str, str]:
    return solicitar_configuracion_salida()

def normalizar_registros_respuesta(datos):
    if datos is None:
        return []
    if isinstance(datos, list):
        return datos
    if isinstance(datos, dict):
        interno = datos.get("data")
        if isinstance(interno, list):
            return interno
        return [datos]
    return [datos]

def exportar_reporte_local(data, nombre_base: str, formato: str, directorio: str) -> str | None:
    try:
        return generar_reporte(
            data = data,
            filename = nombre_base,
            formato = formato,
            directorio = directorio,
            preview = True,
        )
    except Exception as e:
        print(f"Error al generar el reporte: {e}")
        return None

def seleccionar_plataforma_compartir() -> str:
    while True:
        menu_plataforma_compartir()
        opcion = input("Seleccione una plataforma: ").strip().lower()
        if opcion == "1":
            return "drive"
        if opcion == "2":
            return "gmail"
        if opcion == "3":
            return "sheets"
        if opcion == "4":
            return "volver"
        if opcion == "0":
            return "salir"
        print("Opción inválida. Intente nuevamente.")

def solicitar_email_destino() -> str:
    patron = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    while True:
        correo = input("Ingrese el correo electrónico para la notificación: ").strip()
        if re.fullmatch(patron, correo):
            return correo
        print("Correo inválido. Intente nuevamente.")

def solicitar_filtros_reparto():
    while True:
        print("=== Seleccione el criterio para el reporte de repartidores ===")
        print("[1] Filtrar por localidad")
        print("[2] Filtrar por repartidor")
        print("[3] Filtrar por ambos")
        print("[4] Cancelar")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            localidad = input("Ingrese la localidad: ").strip()
            if not localidad:
                print("La localidad no puede estar vacía.")
                continue
            return {"localidad": localidad, "repartidor": None}
        if opcion == "2":
            repartidor = input("Ingrese el nombre del repartidor: ").strip()
            if not repartidor:
                print("El nombre del repartidor no puede estar vacío.")
                continue
            return {"localidad": None, "repartidor": repartidor}
        if opcion == "3":
            localidad = input("Ingrese la localidad: ").strip()
            repartidor = input("Ingrese el nombre del repartidor: ").strip()
            if not localidad or not repartidor:
                print("Debe completar ambos campos.")
                continue
            return {"localidad": localidad, "repartidor": repartidor}
        if opcion == "4":
            return None
        print("Opción inválida. Intente nuevamente.")

def enviar_reporte_compartir(session_id: str, chat_input: str, descripcion: str, tipo: str, plataforma: str, params_extra = None) -> None:
    params = {
        "tipo": tipo,
        "plataforma": plataforma,
    }
    if params_extra:
        params.update({k: v for k, v in params_extra.items() if v is not None})

    req = N8nRequest(
        chat_input = chat_input,
        session_id = session_id,
        intent = f"compartir_{tipo}",
        params = params,
    )
    res = send_query(req)
    if res.ok:
        if res.message:
            print(res.message)
        if res.data:
            if isinstance(res.data, dict):
                url = res.data.get("url") or res.data.get("link")
                if url:
                    print(f"Acceso directo: {url}")
                descripcion = res.data.get("descripcion")
                if descripcion:
                    print(descripcion)
            else:
                print(res.data)
        elif not res.message:
            print("n8n procesó la solicitud correctamente.")
    else:
        print(f"Error al compartir el reporte: {res.message}")

#? Vamos a centrarnos especificamente en esta funcion 'consultar_estado_envio'
def consultar_estado_envio(session_id: str) -> None:

    #! Solicitamos al usuario el codigo del envio cuyo estado quiere revisar
    codigo = input("Ingrese el código de envío: ").strip()

    #* Ignoro totalmente el funcionamiento de 'validar_codigo_envio' y creo que es una funcion innecesaria, al menos por el momento.
    # if not validar_codigo_envio(codigo):
    #     print("Código de envío inválido. Debe contener entre 1 y 20 caracteres alfanuméricos.")
    #     return

    #! Armo un objeto del tipo 'N8nRequest', que simplemente lo utilizo para estructurar solicitudes a n8n
    req = N8nRequest(
        chat_input = f"Consultar estado del envío con código {codigo}",#? Guardo la consulta predefinida con el codigo de forma dinamica, ya que varia segun el codigo ingresado por el usuario
        session_id = session_id, #? Opcional, como ya mencione
        intent = "consultar_estado",#? Genero la intención del usuario, en este caso, consultar_estado
        params = {"codigo": codigo},#? Defino los parametros de la consulta SQL que se deberá realizar, en este caso 'codigo'
    )

    #! Acá comienza la magia, se genera una solicitud a n8n: hace click derecho en 'send_query' y clickea 'go to definition'
    respuesta_request_n8n = send_query(req)

    #* Bien, volvemos aca, una vez obtenido el N8nRequest, lo almacenamos en la variable respuesta_request_n8n que va a representar la información obtenida
    #* desde n8n, actualmente, si no me equivoco (verificar en todo caso), la estructura que devuelve n8n es la siguiente: 
    """
        json {
            data : {
                #? Toda la data de la consulta obtenida
            }
        }
    """
    
    #! Si tenemos en cuenta que n8n devuelve una respuesta con la estructura anterior, nos daremos cuenta que los campos a los que estamos intentando acceder en
    #! la seguidilla de if's que hay acá no son validos, porque sencillamente no existen esos campos.

    #TODO -> Hay que hacer que la estructura de respuesta recibida desde n8n sea la misma que la que se espera acá en python.
    if respuesta_request_n8n.ok:
        if respuesta_request_n8n.message:
            print(respuesta_request_n8n.message)
        if respuesta_request_n8n.data:
            if isinstance(respuesta_request_n8n.data, dict):
                for clave, valor in respuesta_request_n8n.data.items():
                    print(f"{clave}: {valor}")
            else:
                print(respuesta_request_n8n.data)
        elif not respuesta_request_n8n.message:
            print("No se encontró información para el código proporcionado.")
    else:
        print(f"Error al consultar el envío: {respuesta_request_n8n.message}")

def generar_reporte_envios_fallidos(session_id: str, destino: str) -> None:
    req = N8nRequest(
        chat_input = "Generar reporte de envíos fallidos",
        session_id = session_id,
        intent = "reporte_fallidos", 
    ) 

    res = send_query(req)
    registros = normalizar_registros_respuesta(res.data)

    if destino == "local":
        formato_local, directorio_local = obtener_configuracion_local()
        path = exportar_reporte_local(registros, "reporte_envios_fallidos", formato_local, directorio_local)
    else:
        path = generar_reporte(registros, filename="reporte_envios_fallidos", formato="xlsx", preview=False)

    if path:
        mostrar_resultado_reporte(path, destino)
        if not registros:
            print("Nota: el reporte no contiene registros. Revisa el archivo para más detalles.")

    if not res.ok:
        advertencia = res.message or "n8n no devolvió mensaje; se generó un reporte vacío."
        print(f"Advertencia: {advertencia}")

def generar_reporte_repartidores(session_id: str, destino: str) -> None:
    filtros = solicitar_filtros_reparto()
    if not filtros:
        return
    req = N8nRequest(
        chat_input = "Generar reporte de localidad o repartidor",
        session_id = session_id,
        intent = "reporte_repartidor_localidad",
        params = filtros,
    )

    res = send_query(req)
    registros = normalizar_registros_respuesta(res.data)

    if destino == "local":
        formato_local, directorio_local = obtener_configuracion_local()
        path = exportar_reporte_local(registros, "reporte_localidad_repartidor", formato_local, directorio_local)
    else:
        path = generar_reporte(registros, filename="reporte_localidad_repartidor", formato="xlsx", preview=False)

    if path:
        mostrar_resultado_reporte(path, destino)
        if not registros:
            print("Nota: el reporte no contiene registros. Revisa el archivo para más detalles.")

    if not res.ok:
        advertencia = res.message or "n8n no devolvió mensaje; se generó un reporte vacío."
        print(f"Advertencia: {advertencia}")

def generar_consulta_personalizada_local(session_id: str) -> None:
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
    registros = normalizar_registros_respuesta(res.data)

    formato_local, directorio_local = obtener_configuracion_local()
    path = exportar_reporte_local(registros, "reporte_consulta_personalizada", formato_local, directorio_local)
    if path:
        mostrar_resultado_reporte(path, destino="local")
        if not registros:
            print("Nota: el reporte no contiene registros. Revisa el archivo para más detalles.")

    if not res.ok:
        advertencia = res.message or "n8n no devolvió mensaje; se generó un reporte vacío."
        print(f"Advertencia: {advertencia}")

def manejar_menu_compartir(session_id: str) -> bool:
    while True:
        menu_compartir()
        opcion = input("Seleccione una opción: ").strip().lower()
        descripcion = ""
        tipo = ""
        parametros = {}
        if opcion == "1":
            descripcion = "el reporte de envíos fallidos"
            tipo = "fallidos"
            parametros = {}
        elif opcion == "2":
            filtros = solicitar_filtros_reparto()
            if not filtros:
                continue
            descripcion = "el reporte de repartidores"
            tipo = "repartidores"
            parametros = filtros
        elif opcion == "3":
            consulta = input("Ingrese la consulta personalizada que desea compartir: ").strip()
            if not consulta:
                print("La consulta no puede estar vacía.")
                continue
            descripcion = "el reporte personalizado solicitado"
            tipo = "personalizado"
            parametros = {"consulta": consulta}
        elif opcion == "4":
            return True
        elif opcion == "0":
            print("Saliendo del programa. Hasta luego!")
            return False
        else:
            print("Opción inválida. Por favor, intente de nuevo.")
            continue

        plataforma = seleccionar_plataforma_compartir()
        if plataforma == "volver":
            continue
        if plataforma == "salir":
            print("Saliendo del programa. Hasta luego!")
            return False

        correo = solicitar_email_destino()
        parametros["destinatario"] = correo

        chat_input = (
            parametros.get("consulta")
            if tipo == "personalizado"
            else f"Compartir {descripcion} mediante {plataforma}"
        )

        enviar_reporte_compartir(
            session_id = session_id,
            chat_input = chat_input if chat_input else f"Compartir {descripcion} mediante {plataforma}",
            descripcion = descripcion,
            tipo = tipo,
            plataforma = plataforma,
            params_extra = parametros,
        )

def manejar_menu_local(session_id: str) -> bool:
    while True:
        menu_local()
        opcion = input("Seleccione una opción: ").strip().lower()
        if opcion == "1":
            generar_reporte_envios_fallidos(session_id, destino="local")
        elif opcion == "2":
            generar_reporte_repartidores(session_id, destino="local")
        elif opcion == "3":
            generar_consulta_personalizada_local(session_id)
        elif opcion == "4":
            return True
        elif opcion == "0":
            print("Saliendo del programa. Hasta luego!")
            return False
        else:
            print("Opción inválida. Por favor, intente de nuevo.")

def consulta_personalizada_directa(session_id: str) -> None:
    consulta = input("Ingrese su consulta en lenguaje natural: ").strip()
    if not consulta:
        print("La consulta no puede estar vacía.")
        return
    req = N8nRequest(
        chat_input = consulta,
        session_id = session_id,
        intent = "consulta_personalizada",
    )
    res = send_query(req)
    if res.ok:
        if res.message:
            print(res.message)
        if res.data:
            if isinstance(res.data, dict):
                url = res.data.get("url") or res.data.get("link")
                if url:
                    print(f"Acceso directo: {url}")
                descripcion = res.data.get("descripcion")
                if descripcion:
                    print(descripcion)
            else:
                print(res.data)
        elif not res.message:
            print("La consulta fue procesada correctamente, pero no se recibieron datos adicionales.")
    else:
        print(f"Error al procesar la consulta: {res.message}")

def main():
    session_id = new_session_id()
    # print(f"(Sesión: {session_id})")
    while True:
        menu_principal()
        opcion = input("Seleccione una opción: ").strip().lower()
        if opcion == "1":
            consultar_estado_envio(session_id)
        elif opcion == "2":
            if not manejar_menu_compartir(session_id):
                break
        elif opcion == "3":
            consulta_personalizada_directa(session_id)
        elif opcion == "4":
            if not manejar_menu_local(session_id):
                break
        elif opcion == "0":
            print("Saliendo del programa. Hasta luego!")
            break
        else:
            print("Opción inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()
