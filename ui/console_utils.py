"""
ui.console_utils
Utilidades centralizadas para formatear y colorear la salida de consola usando Rich.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live
from contextlib import contextmanager
from typing import Optional

# Instancia global de console
console = Console()

# Paleta de colores y estilos unificados
STYLES = {
	'mensaje_n8n': 'cyan',
	'url': 'bold green',
	'error': 'bold red',
	'exito': 'bold green',
	'procesando': 'yellow italic',
	'no_asignado': 'dim yellow',
	'titulo': 'bold blue',
	'warning': 'yellow',
	'info': 'blue',
}


@contextmanager
def spinner_procesando(mensaje: str):
	"""
	Context manager que muestra un spinner animado mientras se procesa.
	
	Usage:
		with spinner_procesando("Consultando datos..."):
			resultado = enviar_consulta(req)
	
	Args:
		mensaje: Texto a mostrar durante la carga
	"""
	# Crear texto con estilo
	texto_spinner = Text()
	texto_spinner.append("⏳ ", style="bold")
	texto_spinner.append(mensaje, style=STYLES['procesando'])
	
	spinner = Spinner("dots", text=texto_spinner)
	
	with Live(spinner, console=console, refresh_per_second=10):
		yield


def print_procesando(mensaje: str) -> None:
	"""
	Muestra mensaje de procesando (versión simple sin animación).
	
	Args:
		mensaje: Texto a mostrar
	"""
	console.print(f"\n⏳ {mensaje}", style=STYLES['procesando'])


def print_mensaje_n8n(mensaje: str) -> None:
	"""
	Muestra mensaje de n8n en color cyan.
	
	Args:
		mensaje: Mensaje de n8n a mostrar
	"""
	console.print(mensaje, style=STYLES['mensaje_n8n'])


def print_url(url: str, label: str = "Acceso directo") -> None:
	"""
	Muestra URL destacada en verde brillante.
	
	Args:
		url: URL a mostrar
		label: Etiqueta para la URL
	"""
	console.print(f"\n🔗 {label}: {url}", style=STYLES['url'])


def print_error(mensaje: str) -> None:
	"""
	Muestra mensaje de error en rojo.
	
	Args:
		mensaje: Mensaje de error
	"""
	console.print(f"❌ {mensaje}", style=STYLES['error'])


def print_exito(mensaje: str) -> None:
	"""
	Muestra mensaje de éxito en verde.
	
	Args:
		mensaje: Mensaje de éxito
	"""
	console.print(f"✅ {mensaje}", style=STYLES['exito'])


def print_warning(mensaje: str) -> None:
	"""
	Muestra advertencia en amarillo.
	
	Args:
		mensaje: Mensaje de advertencia
	"""
	console.print(f"⚠️  {mensaje}", style=STYLES['warning'])


def print_info(mensaje: str) -> None:
	"""
	Muestra información en azul.
	
	Args:
		mensaje: Mensaje informativo
	"""
	console.print(f"ℹ️  {mensaje}", style=STYLES['info'])


def print_campo(clave: str, valor: any) -> None:
	"""
	Muestra un campo clave-valor con formato apropiado.
	
	Args:
		clave: Nombre del campo
		valor: Valor del campo (si es None se muestra "No asignado")
	"""
	if valor is None:
		console.print(f"{clave}: No asignado", style=STYLES['no_asignado'])
	else:
		print(f"{clave}: {valor}")


def print_separador(caracter: str = "─", longitud: int = 60) -> None:
	"""
	Imprime una línea separadora.
	
	Args:
		caracter: Carácter a usar para la línea
		longitud: Longitud de la línea
	"""
	console.print(caracter * longitud, style="dim")


def print_panel(contenido: str, titulo: Optional[str] = None, border_style: str = "blue") -> None:
	"""
	Muestra contenido dentro de un panel con bordes.
	
	Args:
		contenido: Texto a mostrar en el panel
		titulo: Título opcional del panel
		border_style: Estilo del borde
	"""
	panel = Panel(contenido, title=titulo, border_style=border_style)
	console.print(panel)


def print_menu_opciones(titulo: str, opciones: list[tuple[str, str]], color_opciones: str = "yellow", color_cancelar: str = "red") -> None:
	"""
	Muestra un menú con opciones de manera uniforme.
	
	Args:
		titulo: Título del menú
		opciones: Lista de tuplas (numero, descripcion)
		color_opciones: Color para las opciones normales
		color_cancelar: Color para las opciones de cancelar/salir
	"""
	console.print(f"\n{titulo}", style="bold cyan")
	for numero, descripcion in opciones:
		if "cancelar" in descripcion.lower() or "salir" in descripcion.lower() or numero == "0":
			console.print(f"[{numero}] {descripcion}", style=color_cancelar)
		else:
			console.print(f"[{numero}] {descripcion}", style=color_opciones)
