"""
util.formateo
Funciones para procesar y normalizar respuestas de n8n y datos de envíos.
Estas fueron movidas desde `main.py` sin cambios en su lógica.
"""
import json
from typing import Any, Tuple


def formatear_datos(datos: Any):
	"""Filtra valores 'null'/vacíos de un diccionario (pero mantiene None para mostrar como 'No asignado')."""
	if not isinstance(datos, dict):
		return datos
	# Solo filtramos strings "null" y strings vacíos, pero NO None
	return {k: v for k, v in datos.items() if v != "null" and v != ""}


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
		else:
			# Si no hay campo data/datos, mantener el dict completo
			datos = res.datos
	
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


def filtrar_registros_vacios(datos):
	"""
	Filtra registros completamente vacíos ({}) de una lista.
	
	Mantiene diccionarios que tienen claves, incluso si los valores son None.
	Esto permite que el código que muestra "No asignado" siga funcionando.
	
	Args:
		datos: Puede ser lista, dict u otro tipo
		
	Returns:
		Lista filtrada sin diccionarios vacíos o datos originales
		
	Examples:
		>>> filtrar_registros_vacios([{}, {"nombre": "Juan"}])
		[{"nombre": "Juan"}]
		
		>>> filtrar_registros_vacios([{"estado": None}])
		[{"estado": None}]  # Se mantiene porque tiene claves
	"""
	if isinstance(datos, list):
		return [d for d in datos if not (isinstance(d, dict) and len(d) == 0)]
	return datos
