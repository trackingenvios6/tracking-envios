"""
handlers.consultas
Contiene las funciones `consultar_estado_envio` y `consulta_personalizada_directa`.
Funciones movidas desde `main.py` sin cambios en la lógica.
"""
from n8n_client import enviar_consulta
from data_models import SolicitudN8n
from ui.validaciones import validar_codigo_envio
from utils.formateo import extraer_mensaje_y_datos, formatear_datos
from ui.console_utils import (
	print_procesando,
	spinner_procesando,
	print_mensaje_n8n,
	print_url,
	print_error,
	print_campo,
	print_info,
	print_separador
)


def consultar_estado_envio(session_id: str) -> None:
	"""Consulta y muestra el estado de un envío específico."""
	print_info("Presiona Enter para volver al menú")
	codigo = input("Ingrese el código de envío: ").strip()
	
	# Permitir cancelar con Enter o 0
	if not codigo or codigo == "0":
		print_info("Operación cancelada.")
		return
	
	if not validar_codigo_envio(codigo):
		print_error("Código de envío inválido. Debe contener entre 1 y 20 caracteres alfanuméricos.")
		return

	
	req = SolicitudN8n(
		entrada_chat = f"Consultar estado del envío con código {codigo}",
		id_sesion = session_id,
		intencion = "consultar_estado",
		parametros = {"codigo": codigo},
	)
	
	with spinner_procesando("Consultando estado del envío..."):
		res = enviar_consulta(req)
	
	mensaje, datos = extraer_mensaje_y_datos(res)

	if mensaje:
		print_mensaje_n8n(mensaje)
		
	if datos:
		print_separador()
		if isinstance(datos, list) and len(datos) > 0:
			# Si es una lista con elementos, tomar el primero
			if isinstance(datos[0], dict):
				datos_limpios = formatear_datos(datos[0])
				for clave, valor in datos_limpios.items():
					print_campo(clave, valor)
			else:
				print(datos[0])
		elif isinstance(datos, dict):
			datos_limpios = formatear_datos(datos)
			for clave, valor in datos_limpios.items():
				print_campo(clave, valor)
		else:
			print(datos)
		print_separador()
		
	elif not mensaje:
		print_info("No se encontró información para el código proporcionado.")

	if not res.ok and not mensaje:
		print_error(f"Error al consultar el envío: {res.mensaje}")


def consulta_personalizada_directa(session_id: str) -> None:
	"""Procesa una consulta personalizada y muestra resultados directamente en consola."""
	print_info("Presiona Enter para volver al menú")
	consulta = input("Ingrese su consulta en lenguaje natural: ").strip()
	
	# Permitir cancelar con Enter o 0
	if not consulta or consulta == "0":
		print_info("Operación cancelada.")
		return
	
	print_procesando("Procesando su consulta, aguarde...")
	
	req = SolicitudN8n(
		entrada_chat = consulta,
		id_sesion = session_id,
		intencion = "consulta_personalizada",
	)
	res = enviar_consulta(req)
	
	mensaje, datos = extraer_mensaje_y_datos(res)
	
	# Mostrar el mensaje si existe
	if mensaje:
		print_mensaje_n8n(mensaje)
	
	# Mostrar los datos si existen
	if datos:
		if isinstance(datos, list):
			# Si es una lista de registros (como repartidores)
			print_separador()
			for idx, registro in enumerate(datos, 1):
				print_info(f"Registro {idx}")
				if isinstance(registro, dict):
					for clave, valor in registro.items():
						print_campo(clave, valor)
					print_separador()
				else:
					print(registro)
		elif isinstance(datos, dict):
			# Si es un diccionario único - Mostrar URL/link primero si existe
			# Buscar URL en múltiples posibles campos (Drive usa webViewLink)
			url = (datos.get("url") or 
			       datos.get("link") or 
			       datos.get("webViewLink") or 
			       datos.get("webContentLink"))
			if url:
				print_url(url)
			
			# Mostrar descripción si existe
			descripcion_extra = datos.get("descripcion")
			if descripcion_extra:
				print(f"📝 {descripcion_extra}")
			
			# Mostrar otros campos (excluyendo los ya mostrados y campos internos)
			campos_mostrados = {
				'url', 'link', 'webViewLink', 'webContentLink', 
				'descripcion', 'accion', 'query_sql', 
				'mensaje_ia', 'mensaje', 'message'
			}
			for clave, valor in datos.items():
				if clave not in campos_mostrados:
					print_campo(clave, valor)
		else:
			# Cualquier otro tipo de dato
			print(datos)

	# Solo mostrar error si NO hay mensaje y NO hay datos
	if not mensaje and not datos:
		if not res.ok:
			print(f"Error al procesar la consulta: {res.mensaje or 'Error desconocido'}")
		else:
			print("La consulta fue procesada correctamente, pero no se recibieron datos.")
