"""
handlers.consultas
Contiene las funciones `consultar_estado_envio` y `consulta_personalizada_directa`.
Funciones movidas desde `main.py` sin cambios en la lógica.
"""
from n8n_client import enviar_consulta
from data_models import SolicitudN8n
from ui.validaciones import validar_codigo_envio
from utils.formateo import extraer_mensaje_y_datos, formatear_datos


def consultar_estado_envio(session_id: str) -> None:
	"""Consulta y muestra el estado de un envío específico."""
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


def consulta_personalizada_directa(session_id: str) -> None:
	"""Procesa una consulta personalizada y muestra resultados directamente en consola."""
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
    
	mensaje, datos = extraer_mensaje_y_datos(res)
	if mensaje:
		print(mensaje)

	# Solo mostrar error si NO hay mensaje y NO hay datos
	if not mensaje and not datos:
		if not res.ok:
			print(f"Error al procesar la consulta: {res.mensaje or 'Error desconocido'}")
		else:
			print("La consulta fue procesada correctamente, pero no se recibieron datos.")
