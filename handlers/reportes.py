"""
handlers.reportes
Funciones relacionadas con la generación de reportes y el submenú local.
Movidas desde `main.py` sin cambios.
"""
from n8n_client import enviar_consulta
from data_models import SolicitudN8n
from report_generator import generar_reporte
from error_handler import (
	validar_respuesta_n8n,
	mostrar_mensaje_si_existe,
	MSG_SIN_ENVIOS_FALLIDOS,
	MSG_SIN_DATOS_FILTRO,
	MSG_SIN_DATOS_CONSULTA,
)
from ui.validaciones import solicitar_filtros_reparto
from utils.helpers import obtener_configuracion_local, exportar_reporte_local, mostrar_resultado_reporte
from ui.console_utils import spinner_procesando


def generar_reporte_envios_fallidos(session_id: str, destino: str) -> None:
	"""Genera un reporte de todos los envíos con estado fallido."""
	req = SolicitudN8n(
		entrada_chat = "Generar reporte de envíos fallidos",
		id_sesion = session_id,
		intencion = "reporte_fallidos",
	)

	with spinner_procesando("Consultando datos de envíos fallidos"):
		res = enviar_consulta(req)
	valido, registros, mensaje = validar_respuesta_n8n(res, MSG_SIN_ENVIOS_FALLIDOS)
	if not valido:
		return

	if destino == "local":
		config = obtener_configuracion_local()
		if config is None:
			return  # Usuario canceló
		formato_local, directorio_local = config
		path = exportar_reporte_local(registros, "reporte_envios_fallidos", formato_local, directorio_local)
	else:
		path = generar_reporte(registros, filename="reporte_envios_fallidos", formato="xlsx", preview=False)

	if path:
		mostrar_resultado_reporte(path, destino)
	mostrar_mensaje_si_existe(mensaje)


def generar_reporte_repartidores(session_id: str, destino: str) -> None:
	"""Genera un reporte filtrado por repartidor y/o localidad."""
	filtros = solicitar_filtros_reparto()
	if not filtros:
		return
	req = SolicitudN8n(
		entrada_chat = "Generar reporte de localidad o repartidor",
		id_sesion = session_id,
		intencion = "reporte_repartidor_localidad",
		parametros = filtros,
	)

	with spinner_procesando("Consultando datos de repartidores"):
		res = enviar_consulta(req)
	valido, registros, mensaje = validar_respuesta_n8n(res, MSG_SIN_DATOS_FILTRO)
	if not valido:
		return

	if destino == "local":
		config = obtener_configuracion_local()
		if config is None:
			return  # Usuario canceló
		formato_local, directorio_local = config
		path = exportar_reporte_local(registros, "reporte_localidad_repartidor", formato_local, directorio_local)
	else:
		path = generar_reporte(registros, filename="reporte_localidad_repartidor", formato="xlsx", preview=False)

	if path:
		mostrar_resultado_reporte(path, destino)
	mostrar_mensaje_si_existe(mensaje)


def generar_consulta_personalizada_local(session_id: str) -> None:
	"""Genera un reporte local basado en una consulta personalizada del usuario."""
	consulta = input("Ingrese su consulta personalizada: ").strip()
	if not consulta:
		print("La consulta no puede estar vacía.")
		return
	req = SolicitudN8n(
		entrada_chat = consulta,
		id_sesion = session_id,
		intencion = "consulta_personalizada",
	)
	with spinner_procesando("Procesando consulta personalizada"):
		res = enviar_consulta(req)
	valido, registros, mensaje = validar_respuesta_n8n(res, MSG_SIN_DATOS_CONSULTA)
	if not valido:
		return

	config = obtener_configuracion_local()
	if config is None:
		return  # Usuario canceló
	formato_local, directorio_local = config
	path = exportar_reporte_local(registros, "reporte_consulta_personalizada", formato_local, directorio_local)
	if path:
		mostrar_resultado_reporte(path, destino="local")
	mostrar_mensaje_si_existe(mensaje)


def manejar_menu_local(session_id: str) -> bool:
	"""Maneja la lógica del submenú de reportes locales."""
	from ui.menus import menu_local
	while True:
		menu_local()
		opcion = input("Seleccione una opción: ").strip().lower()
		if opcion == "1":
			generar_reporte_envios_fallidos(session_id, destino="local")
			return True
		elif opcion == "2":
			generar_reporte_repartidores(session_id, destino="local")
			return True
		elif opcion == "3":
			generar_consulta_personalizada_local(session_id)
			return True
		elif opcion == "4":
			return True
		elif opcion == "0":
			print("Saliendo del programa. Hasta luego!")
			return False
		else:
			print("Opción inválida. Por favor, intente de nuevo.")

