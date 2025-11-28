"""
util.formateo
Funciones para procesar y normalizar respuestas de n8n y datos de envíos.
Estas fueron movidas desde `main.py` sin cambios en su lógica.
"""
import json
from typing import Any, Tuple


def formatear_datos(datos: Any):
	"""Filtra valores None/null/vacíos de un diccionario."""
	if not isinstance(datos, dict):
		return datos
	return {k: v for k, v in datos.items() if v is not None and v != "null" and v != ""}


def extraer_mensaje_y_datos(res) -> Tuple[str | None, Any]:
	"""Extrae mensaje y datos de la respuesta de n8n conforme a diferentes formatos."""
	mensaje = res.mensaje
	datos = res.datos

	if isinstance(res.datos, str):
		try:
			parsed = json.loads(res.datos)
			if isinstance(parsed, dict):
				mensaje = parsed.get("mensaje_ia") or mensaje
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
		mensaje = res.datos.get("mensaje_ia") or mensaje
		if "data" in res.datos:
			datos = res.datos.get("data")
		elif "datos" in res.datos:
			datos = res.datos.get("datos")

	return mensaje, datos


def normalizar_registros_respuesta(datos):
	"""Normaliza diferentes formatos de respuesta a una lista de registros."""
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
