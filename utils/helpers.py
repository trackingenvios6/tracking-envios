"""
util.helpers
Contiene funciones auxiliares para trabajar con datos y exportar reportes.
Movidas desde `main.py` y `error_handler.py`.
"""
from typing import Any
from report_generator import generar_reporte, solicitar_configuracion_salida


def obtener_mensaje_desde_data(data: Any) -> str | None:
	"""Extrae el mensaje de la IA desde diferentes estructuras de datos."""
	if isinstance(data, dict):
		return data.get("mensaje_ia")
	if isinstance(data, list) and data and isinstance(data[0], dict):
		return data[0].get("mensaje_ia")
	return None


def obtener_configuracion_local() -> tuple[str, str]:
	"""Solicita al usuario la configuración para exportación local.

	Delega a `report_generator.solicitar_configuracion_salida`.
	"""
	return solicitar_configuracion_salida()


def exportar_reporte_local(data, nombre_base: str, formato: str, directorio: str) -> str | None:
	"""Generar archivo local usando `report_generator.generar_reporte` y retorna la ruta."""
	try:
		return generar_reporte(
			data=data,
			filename=nombre_base,
			formato=formato,
			directorio=directorio,
			preview=True,
		)
	except Exception as e:
		print(f"Error al generar el reporte: {e}")
		return None


def mostrar_resultado_reporte(path: str, destino: str = "") -> None:
	"""Muestra un mensaje con la ruta del reporte generado."""
	if destino == "compartir":
		print(f"Reporte generado y listo para compartir en plataforma: {path}")
	# El mensaje de archivo guardado ya lo imprime generar_reporte() en report_generator.py
	# No se imprime nada adicional para destino local
