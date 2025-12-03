"""
handlers.compartir
Contiene `enviar_reporte_compartir` y `manejar_menu_compartir` movidos desde `main.py`.
"""
from n8n_client import enviar_consulta
from data_models import SolicitudN8n
from ui.validaciones import (
	seleccionar_plataforma_compartir,
	solicitar_email_destino,
	solicitar_filtros_reparto,
)
from utils.helpers import obtener_mensaje_desde_data
from ui.console_utils import (
	spinner_procesando,
	print_mensaje_n8n,
	print_url,
	print_error,
	print_exito,
	print_info
)


def enviar_reporte_compartir(session_id: str, chat_input: str, descripcion: str, tipo: str, plataforma: str, params_extra = None) -> None:
	"""Envía un reporte a n8n para ser compartido en una plataforma externa."""
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
	
	with spinner_procesando(f"Generando {descripcion} para compartir"):
		res = enviar_consulta(req)
	if res.ok:
		mensaje = obtener_mensaje_desde_data(res.datos) or res.mensaje
		if mensaje:
			print_mensaje_n8n(mensaje)
		if res.datos:
			if isinstance(res.datos, dict):
				url = res.datos.get("url") or res.datos.get("link") or res.datos.get("webViewLink") or res.datos.get("webContentLink")
				if url:
					print_url(url)
				descripcion_extra = res.datos.get("descripcion")
				if descripcion_extra:
					print(descripcion_extra)
			else:
				print(res.datos)
		elif not mensaje:
			print_exito("n8n procesó la solicitud correctamente.")
	else:
		print_error(f"Error al compartir el reporte: {res.mensaje}")


def manejar_menu_compartir(session_id: str) -> bool:
	"""Maneja la lógica del submenú de compartir reportes."""
	from ui.menus import menu_compartir
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
			print_info("Presiona Enter para volver al menú")
			consulta = input("Ingrese la consulta personalizada que desea compartir: ").strip()
			if not consulta or consulta == "0":
				print_info("Operación cancelada.")
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
			print_error("❌ Opción inválida. Por favor, intente de nuevo.")
			continue

		plataforma = seleccionar_plataforma_compartir()
		if plataforma == "volver":
			continue
		if plataforma == "salir":
			print("Saliendo del programa. Hasta luego!")
			return False

		# Solo solicitar email si la plataforma es Gmail
		if plataforma == "gmail":
			correo = solicitar_email_destino()
			parametros["email_destinatario"] = correo

		entrada_chat = (
			parametros.get("consulta")
			if tipo == "personalizado"
			else f"Compartir {descripcion} mediante {plataforma}"
		)

		enviar_reporte_compartir(
			session_id = session_id,
			chat_input = entrada_chat,
			descripcion = descripcion,
			tipo = tipo,
			plataforma = plataforma,
			params_extra = parametros,
		)
		# Retornar True después de completar la acción
		return True

