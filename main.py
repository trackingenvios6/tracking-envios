import json
import re
from n8n_client import enviar_consulta, nuevo_id_sesion
from data_models import SolicitudN8n
from report_generator import generar_reporte, solicitar_configuracion_salida
from error_handler import (
    validar_respuesta_n8n,
    mostrar_mensaje_si_existe,
    obtener_mensaje_desde_data,
    normalizar_registros_respuesta,
    MSG_SIN_ENVIOS_FALLIDOS,
    MSG_SIN_DATOS_FILTRO,
    MSG_SIN_DATOS_CONSULTA,
)


# ============================================================================
# CONSTANTES
# ============================================================================

APP_TITLE = "Bienvenido a Piki. Tu envío, sin estrés."


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================
 


def validar_codigo_envio(codigo: str) -> bool:
    """
    Valida el formato de un código de envío.
    
    El código debe contener solo caracteres alfanuméricos (A-Z, 0-9)
    con una longitud entre 1 y 20 caracteres.
    
    Args:
        codigo (str): Código de envío a validar
    
    Returns:
        bool: True si el código es válido, False en caso contrario
    
    Ejemplos:
        >>> validar_codigo_envio("ABC123")
        True
        >>> validar_codigo_envio("ABC-123")
        False
    """
    return bool(re.fullmatch(r'[A-Z0-9]{1,20}', codigo.strip(), flags=re.I)) 


def formatear_datos(datos):
    """
    Filtra valores None/null/vacíos de un diccionario.
    
    Remueve todas las entradas con valores None, "null" (string) o cadenas vacías,
    dejando solo información relevante para mostrar al usuario.
    
    Args:
        datos: Diccionario con datos a formatear (o cualquier otro tipo)
    
    Returns:
        dict: Diccionario filtrado sin valores nulos/vacíos, o los datos originales
              si no es un diccionario
    """
    if not isinstance(datos, dict):
        return datos
    return {k: v for k, v in datos.items() if v is not None and v != "null" and v != ""}


# ============================================================================
# FUNCIONES DE MENÚS
# ============================================================================

def menu_principal():
    """
    Muestra el menú principal de la aplicación.
    
    Opciones disponibles:
    - Consultar estado de un envío
    - Generar reporte para compartir
    - Consulta personalizada
    - Generar reporte local
    - Salir
    """
    print(f"=== {APP_TITLE} ===") 
    print("[1] Consultar estado de un envío") 
    print("[2] Generar reporte para compartir")
    print("[3] Consulta personalizada")
    print("[4] Generar reporte local")
    print("[0] Salir")


def menu_compartir():
    """
    Muestra el menú de opciones para compartir reportes.
    
    Permite seleccionar qué tipo de reporte compartir en plataformas
    como Drive, Gmail o Sheets.
    """
    print(f"=== {APP_TITLE} ===")
    print("[1] Compartir reporte de envíos fallidos")
    print("[2] Compartir reporte de repartidores")
    print("[3] Consulta personalizada")
    print("[4] Volver al menú principal")
    print("[0] Salir")


def menu_local():
    """
    Muestra el menú de opciones para generar reportes locales.
    
    Permite seleccionar qué tipo de reporte descargar localmente
    en formato Excel o CSV.
    """
    print(f"=== {APP_TITLE} ===")
    print("[1] Descargar el reporte de envíos fallidos")
    print("[2] Descargar el reporte de repartidores")
    print("[3] Consulta personalizada")
    print("[4] Volver al menú principal")
    print("[0] Salir")


def menu_plataforma_compartir():
    """
    Muestra el menú de selección de plataforma para compartir.
    
    Plataformas disponibles:
    - Google Drive
    - Gmail
    - Google Sheets
    """
    print("=== Seleccione la plataforma para compartir ===")
    print("[1] Drive")
    print("[2] Gmail")
    print("[3] Sheets")
    print("[4] Volver al menú anterior")
    print("[0] Salir")


def mostrar_resultado_reporte(path: str, destino: str = "") -> None:
    """
    Muestra un mensaje con la ruta del reporte generado.
    
    El mensaje varía según el tipo de destino (compartir, local, o genérico).
    
    Args:
        path (str): Ruta del archivo generado
        destino (str, optional): Tipo de destino ("compartir", "local", o vacío)
    """
    if destino == "compartir":
        print(f"Reporte generado y listo para compartir en plataforma: {path}")
    elif destino == "local":
        print(f"Reporte descargado localmente en: {path}")
    else:
        print(f"Reporte generado exitosamente: {path}")



# ============================================================================
# FUNCIONES DE PROCESAMIENTO DE DATOS
# ============================================================================

def extraer_mensaje_y_datos(res):
    """
    Extrae mensaje y datos de la respuesta de n8n, manejando diferentes formatos.
    
    Esta función es crítica para normalizar las respuestas de n8n, que pueden
    venir en múltiples formatos (string JSON, dict, dict anidado, etc.).
    
    Args:
        res (RespuestaN8n): Objeto con la respuesta de n8n
    
    Returns:
        tuple[str | None, any]: Tupla con (mensaje_extraido, datos_procesados)
    
    Casos manejados:
        - res.datos como string JSON:
            * Parsea el JSON
            * Extrae mensaje de: mensaje_ia, mensaje, message
            * Extrae datos de: data, datos, o el objeto completo
        
        - res.datos como dict:
            * Busca campos anidados (mensaje_ia, data, etc.)
            * Prioriza campos específicos sobre el objeto completo
        
        - Cualquier otro tipo:
            * Mantiene mensaje original de res.mensaje
            * Mantiene datos originales de res.datos
    
    Nota: Esta función es esencial para mantener compatibilidad con
          las diferentes versiones y configuraciones de n8n.
    """
    mensaje = res.mensaje
    datos = res.datos
    
    if isinstance(res.datos, str):
        try:
            parsed = json.loads(res.datos)
            if isinstance(parsed, dict):
                # Intenta extraer mensaje de múltiples campos posibles
                mensaje = (
                    parsed.get("mensaje_ia") or 
                    parsed.get("mensaje") or 
                    parsed.get("message") or 
                    mensaje
                )
                # Extrae datos del campo 'data' si existe, sino usa todo el parsed
                if "data" in parsed:
                    datos = parsed.get("data")
                elif "datos" in parsed:
                    datos = parsed.get("datos")
                else:
                    datos = parsed
            else:
                datos = parsed
        except Exception:
            pass
    elif isinstance(res.datos, dict):
        # Manejo específico para la estructura de n8n
        mensaje = (
            res.datos.get("mensaje_ia") or 
            res.datos.get("mensaje") or 
            res.datos.get("message") or 
            mensaje
        )
        # Si hay un campo 'data' dentro, úsalo; sino usa res.datos directamente
        if "data" in res.datos:
            datos = res.datos.get("data")
        elif "datos" in res.datos:
            datos = res.datos.get("datos")
        # Si no hay campo data/datos, mantén res.datos como está
    
    return mensaje, datos


# ============================================================================
# FUNCIONES DE CONFIGURACIÓN Y EXPORTACIÓN
# ============================================================================

def obtener_configuracion_local() -> tuple[str, str]:
    """
    Solicita al usuario la configuración para exportación local de reportes.
    
    Delega la solicitud a la función del módulo report_generator que
    pide al usuario el formato (Excel/CSV) y directorio de destino.
    
    Returns:
        tuple[str, str]: Tupla con (formato, directorio)
            - formato: "xlsx" o "csv"
            - directorio: Ruta donde guardar el archivo
    """
    return solicitar_configuracion_salida()



def exportar_reporte_local(data, nombre_base: str, formato: str, directorio: str) -> str | None:
    """
    Genera un reporte local (Excel o CSV) con los datos proporcionados.
    
    Maneja errores de generación y muestra mensajes apropiados.
    
    Args:
        data: Datos a incluir en el reporte (lista de diccionarios)
        nombre_base (str): Nombre base del archivo (sin extensión)
        formato (str): Formato del archivo ("xlsx" o "csv")
        directorio (str): Directorio donde guardar el archivo
    
    Returns:
        str | None: Ruta completa del archivo generado, o None si hay error
    """
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


# ============================================================================
# FUNCIONES DE ENTRADA DE USUARIO
# ============================================================================

def seleccionar_plataforma_compartir() -> str:
    """
    Solicita al usuario que seleccione una plataforma para compartir reportes.
    
    Muestra un menú interactivo y valida la selección.
    
    Returns:
        str: Plataforma seleccionada ("drive", "gmail", "sheets", "volver", o "salir")
    """
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

#Verificar bien la varible correo --> mail
def solicitar_email_destino() -> str:
    """
    Solicita y valida un correo electrónico de destino.
    
    Utiliza expresión regular para validar el formato del email.
    Continúa solicitando hasta recibir un email válido.
    
    Returns:
        str: Correo electrónico validado
    """
    patron = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    while True:
        correo = input("Ingrese el correo electrónico para la notificación: ").strip()
        if re.fullmatch(patron, correo):
            return correo
        print("Correo inválido. Intente nuevamente.")

#verificar bien la varible se puede imprimir directo lo que responde la ia
def solicitar_filtros_reparto():
    """
    Solicita al usuario los filtros para generar reporte de repartidores.
    
    Permite filtrar por:
    - Solo localidad
    - Solo repartidor  
    - Ambos criterios
    
    Returns:
        dict | None: Diccionario con filtros {"localidad": str | None, "repartidor": str | None}.
                     Retorna None si el usuario cancela.
    """
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


# ============================================================================
# FUNCIONES DE REPORTES Y CONSULTAS
# ============================================================================

def enviar_reporte_compartir(session_id: str, chat_input: str, descripcion: str, tipo: str, plataforma: str, params_extra = None) -> None:
    """
    Envía un reporte a n8n para ser compartido en una plataforma externa.
    
    Esta función prepara los parámetros, envía la solicitud a n8n y procesa
    la respuesta para mostrar mensajes y enlaces al usuario.
    
    Args:
        session_id (str): ID de la sesión actual
        chat_input (str): Mensaje de entrada para n8n
        descripcion (str): Descripción del reporte para mensajes al usuario
        tipo (str): Tipo de reporte ("fallidos", "repartidores", "personalizado")
        plataforma (str): Plataforma destino ("drive", "gmail", "sheets")
        params_extra (dict, optional): Parámetros adicionales (filtros, destinatario, etc.)
    """
    parametros = {
        "tipo": tipo,
        "plataforma": plataforma,
    }
    if params_extra:
        parametros.update({k: v for k, v in params_extra.items() if v is not None})

    req = SolicitudN8n(
        entrada_chat = chat_input,
        id_sesion = session_id,
        intencion = f"compartir_{tipo}",
        parametros = parametros,
    )
    res = enviar_consulta(req)
    if res.ok:
        mensaje = obtener_mensaje_desde_data(res.datos) or res.mensaje
        if mensaje:
            print(mensaje)
        if res.datos: #Anda a chequearlo bien
            if isinstance(res.datos, dict):
                url = res.datos.get("url") or res.datos.get("link")
                if url:
                    print(f"Acceso directo: {url}")
                descripcion = res.datos.get("descripcion")
                if descripcion:
                    print(descripcion)
            else:
                print(res.datos)
        elif not mensaje:
            print("n8n procesó la solicitud correctamente.")
    else:
        print(f"Error al compartir el reporte: {res.mensaje}")


def consultar_estado_envio(session_id: str) -> None:
    """
    Consulta y muestra el estado de un envío específico.
    
    Solicita al usuario el código de envío, lo valida, consulta a n8n
    y muestra la información del estado del envío formateada.
    
    Args:
        session_id (str): ID de la sesión actual
    """
    codigo = input("Ingrese el código de envío: ").strip()
    if not validar_codigo_envio(codigo):
        print("Código de envío inválido. Debe contener entre 1 y 20 caracteres alfanuméricos.")
        return

    req = SolicitudN8n(
        entrada_chat = f"Consultar estado del envío con código {codigo}",
        id_sesion = session_id,
        intencion = "consultar_estado",
        parametros = {"codigo": codigo},
    )
    res = enviar_consulta(req)
    mensaje, datos = extraer_mensaje_y_datos(res)

    if mensaje:
        print(mensaje)
    if datos:
        if isinstance(datos, dict):
            datos_limpios = formatear_datos(datos)
            for clave, valor in datos_limpios.items():
                print(f"{clave}: {valor}")
        else:
            print(datos)
    elif not mensaje:
        print("No se encontró información para el código proporcionado.")

    if not res.ok and not mensaje:
        print(f"Error al consultar el envío: {res.mensaje}")


def generar_reporte_envios_fallidos(session_id: str, destino: str) -> None:
    """
    Genera un reporte de todos los envíos con estado fallido.
    
    Consulta a n8n los envíos fallidos y genera un reporte en Excel/CSV
    según el destino especificado (local o para compartir).
    
    Args:
        session_id (str): ID de la sesión actual
        destino (str): Destino del reporte ("local" para descarga, otro para compartir)
    """
    req = SolicitudN8n(
        entrada_chat = "Generar reporte de envíos fallidos",
        id_sesion = session_id,
        intencion = "reporte_fallidos", 
    ) 

    res = enviar_consulta(req)
    
    # Validar respuesta usando el helper centralizado
    valido, registros, mensaje = validar_respuesta_n8n(res, MSG_SIN_ENVIOS_FALLIDOS)
    if not valido:
        return

    # Solo solicitar formato si hay datos para exportar
    if destino == "local":
        formato_local, directorio_local = obtener_configuracion_local()
        path = exportar_reporte_local(registros, "reporte_envios_fallidos", formato_local, directorio_local)
    else:
        path = generar_reporte(registros, filename="reporte_envios_fallidos", formato="xlsx", preview=False)

    if path:
        mostrar_resultado_reporte(path, destino)
    mostrar_mensaje_si_existe(mensaje)


def generar_reporte_repartidores(session_id: str, destino: str) -> None:
    """
    Genera un reporte filtrado por repartidor y/o localidad.
    
    Solicita al usuario los criterios de filtrado (localidad, repartidor, o ambos),
    consulta a n8n y genera un reporte en Excel/CSV.
    
    Args:
        session_id (str): ID de la sesión actual
        destino (str): Destino del reporte ("local" para descarga, otro para compartir)
    """
    filtros = solicitar_filtros_reparto()
    if not filtros:
        return
    req = SolicitudN8n(
        entrada_chat = "Generar reporte de localidad o repartidor",
        id_sesion = session_id,
        intencion = "reporte_repartidor_localidad",
        parametros = filtros,
    )

    res = enviar_consulta(req)
    
    # Validar respuesta usando el helper centralizado
    valido, registros, mensaje = validar_respuesta_n8n(res, MSG_SIN_DATOS_FILTRO)
    if not valido:
        return

    # Solo solicitar formato si hay datos para exportar
    if destino == "local":
        formato_local, directorio_local = obtener_configuracion_local()
        path = exportar_reporte_local(registros, "reporte_localidad_repartidor", formato_local, directorio_local)
    else:
        path = generar_reporte(registros, filename="reporte_localidad_repartidor", formato="xlsx", preview=False)

    if path:
        mostrar_resultado_reporte(path, destino)
    mostrar_mensaje_si_existe(mensaje)


def generar_consulta_personalizada_local(session_id: str) -> None:
    """
    Genera un reporte local basado en una consulta personalizada del usuario.
    
    Permite al usuario ingresar una consulta en lenguaje natural, la envía a n8n
    para procesamiento y genera un reporte local con los resultados.
    
    Args:
        session_id (str): ID de la sesión actual
    """
    consulta = input("Ingrese su consulta personalizada: ").strip()
    if not consulta:
        print("La consulta no puede estar vacía.")
        return
    req = SolicitudN8n(
        entrada_chat = consulta,
        id_sesion = session_id,
        intencion = "consulta_personalizada",
    )
    res = enviar_consulta(req)
    
    # Validar respuesta usando el helper centralizado
    valido, registros, mensaje = validar_respuesta_n8n(res, MSG_SIN_DATOS_CONSULTA)
    if not valido:
        return

    # Solo solicitar formato si hay datos para exportar
    formato_local, directorio_local = obtener_configuracion_local()
    path = exportar_reporte_local(registros, "reporte_consulta_personalizada", formato_local, directorio_local)
    if path:
        mostrar_resultado_reporte(path, destino="local")
    mostrar_mensaje_si_existe(mensaje)


# ============================================================================
# FUNCIONES DE MANEJO DE MENÚS (HANDLERS)
# ============================================================================

def manejar_menu_compartir(session_id: str) -> bool:
    """
    Maneja la lógica del submenú de compartir reportes.
    
    Muestra el menú, procesa la selección del usuario, solicita plataforma
    y correo de destino, y envía el reporte a n8n para ser compartido.
    
    Args:
        session_id (str): ID de la sesión actual
    
    Returns:
        bool: True si debe volver al menú principal, False si debe salir del programa
    """
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

        entrada_chat = (
            parametros.get("consulta")
            if tipo == "personalizado"
            else f"Compartir {descripcion} mediante {plataforma}"
        )

        enviar_reporte_compartir(
            id_sesion = session_id,
            entrada_chat = entrada_chat,
            descripcion = descripcion,
            tipo = tipo,
            plataforma = plataforma,
            params_extra = parametros,
        )


def manejar_menu_local(session_id: str) -> bool:
    """
    Maneja la lógica del submenú de reportes locales.
    
    Muestra el menú, procesa la selección del usuario y genera reportes
    locales en formato Excel o CSV.
    
    Args:
        session_id (str): ID de la sesión actual
    
    Returns:
        bool: True si debe volver al menú principal, False si debe salir del programa
    """
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
    """
    Procesa una consulta personalizada y muestra resultados directamente en consola.
    
    Permite al usuario ingresar consultas en lenguaje natural. El agente de IA
    procesa la consulta y retorna una respuesta que se muestra directamente,
    sin generar archivos de reporte.
    
    Nota: Como trabaja con sesión, el usuario puede hacer consultas de seguimiento
          sobre los datos de consultas anteriores (ej: "cuál es el porcentaje total?").
    
    Args:
        session_id (str): ID de la sesión actual
    """
    consulta = input("Ingrese su consulta en lenguaje natural: ").strip()
    if not consulta:
        print("La consulta no puede estar vacía.")
        return
    
    req = SolicitudN8n(
        entrada_chat = consulta,
        id_sesion = session_id,
        intencion = "consulta_personalizada",
    )
    res = enviar_consulta(req)
    
    # Extraer mensaje y datos usando la función mejorada
    mensaje, datos = extraer_mensaje_y_datos(res)
    
    # Mostrar el mensaje si existe
    if mensaje:
        print(mensaje)
    
    """# Mostrar los datos, comentado para nuevas implementaciones.
    if datos:
        if isinstance(datos, dict):
            # Mostrar los datos del diccionario
            for clave, valor in datos.items():
                # Filtrar campos internos que no son para el usuario
                if clave not in ['accion', 'query_sql', 'mensaje_ia', 'mensaje', 'message']:
                    print(f"{clave}: {valor}")
        elif isinstance(datos, list):
            # Mostrar lista de registros
            for idx, registro in enumerate(datos, 1):
                print(f"\n--- Registro {idx} ---")
                if isinstance(registro, dict):
                    for clave, valor in registro.items():
                        print(f"{clave}: {valor}")
                else:
                    print(registro)
        else:
            print(datos)
            """
    
    #otra consulta personalizada, por si quiere hacer mas consultas sobre esa consulta anterior, 
    #Al estar en una sesion, se puede volver a llamar a la sesion en la que estabas haciendo las peticiones, y trabajar con esos datos recibidos, por ejemplo: entonces, cual seria el porcentaje total de envios fallido?

    # Solo mostrar error si NO hay mensaje y NO hay datos
    if not mensaje and not datos:
        if not res.ok:
            print(f"Error al procesar la consulta: {res.mensaje or 'Error desconocido'}")
        else:
            print("La consulta fue procesada correctamente, pero no se recibieron datos.")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que inicia la aplicación.
    
    Genera un ID de sesión único, muestra el menú principal en un bucle
    y delega las acciones según la opción seleccionada por el usuario.
    
    Flujo:
        1. Genera ID de sesión
        2. Muestra menú principal
        3. Procesa selección del usuario:
           - Opción 1: Consultar estado de envío
           - Opción 2: Menú de compartir reportes
           - Opción 3: Consulta personalizada directa
           - Opción 4: Menú de reportes locales
           - Opción 0: Salir
        4. Repite hasta que el usuario elija salir
    """
    id_sesion = nuevo_id_sesion()
    # print(f"(Sesión: {id_sesion})")
    while True:
        menu_principal()
        opcion = input("Seleccione una opción: ").strip().lower()
        if opcion == "1":
            consultar_estado_envio(id_sesion)
        elif opcion == "2":
            if not manejar_menu_compartir(id_sesion):
                break
        elif opcion == "3":
            consulta_personalizada_directa(id_sesion)
        elif opcion == "4":
            if not manejar_menu_local(id_sesion):
                break
        elif opcion == "0":
            print("Saliendo del programa. Hasta luego!")
            break
        else:
            print("Opción inválida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    main()