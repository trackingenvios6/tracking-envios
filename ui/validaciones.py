"""
ui.validaciones
Funciones que solicitan y validan datos al usuario. Migradas desde `main.py`.
"""
import re
from typing import Optional
from ui.menus import menu_plataforma_compartir, menu_continuar
from ui.console_utils import print_error, print_info


def validar_codigo_envio(codigo: str) -> bool:
	"""Valida el formato de un código de envío."""
	return bool(re.fullmatch(r'[A-Z0-9]{1,20}', codigo.strip(), flags=re.I))


def seleccionar_plataforma_compartir() -> str:
	"""Solicita al usuario que seleccione una plataforma para compartir reportes."""
	while True:
		menu_plataforma_compartir()
		opcion = input("Seleccione una plataforma: ").strip().lower()
		if opcion == "1":
			return "drive"
		if opcion == "2":
			return "gmail"
		if opcion == "3":
			return "volver"
		if opcion == "0":
			return "salir"
		print_error("❌ Opción inválida. Intente nuevamente.")


def solicitar_email_destino() -> str:
	"""Solicita y valida un correo electrónico de destino."""
	patron = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
	while True:
		correo = input("Ingrese el correo electrónico para la notificación: ").strip()
		if re.fullmatch(patron, correo):
			return correo
		print_error("❌ Correo inválido. Intente nuevamente.")


def solicitar_filtros_reparto():
	"""Solicita al usuario los filtros para generar reporte de repartidores."""
	from ui.menus import menu_criterio_repartidor
	
	while True:
		menu_criterio_repartidor()
		print_info("💡 Puedes cancelar con Enter o seleccionar [4]")
		opcion = input("\nOpción: ").strip()
		if opcion == "1":
			localidad = input("Ingrese la localidad: ").strip()
			if not localidad:
				print_error("❌ La localidad no puede estar vacía.")
				continue
			return {"localidad": localidad, "repartidor": None}
		if opcion == "2":
			repartidor = input("Ingrese el nombre del repartidor: ").strip()
			if not repartidor:
				print_error("❌ El nombre del repartidor no puede estar vacío.")
				continue
			return {"localidad": None, "repartidor": repartidor}
		if opcion == "3":
			localidad = input("Ingrese la localidad: ").strip()
			repartidor = input("Ingrese el nombre del repartidor: ").strip()
			if not localidad or not repartidor:
				print_error("❌ Debe completar ambos campos.")
				continue
			return {"localidad": localidad, "repartidor": repartidor}
		if opcion == "4" or opcion == "0" or not opcion:
			print_info("Operación cancelada.")
			return None
		print_error("❌ Opción inválida. Intente nuevamente.")


def manejar_continuar() -> str:
	"""Maneja la navegación después de completar una acción."""
	while True:
		menu_continuar()
		opcion = input("\nSelecciona una opción: ").strip()
		if opcion == "1":
			return "principal"
		elif opcion == "2":
			return "compartir"
		elif opcion == "3":
			return "local"
		elif opcion == "0":
			print("Saliendo del programa. ¡Hasta luego! 👋")
			return "salir"
		else:
			print("❌ Opción inválida. Por favor, intenta de nuevo.")
