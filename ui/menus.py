"""
ui.menus
Contiene todas las funciones que imprimen menús en la aplicación.
Versión mejorada con Rich para mejor visualización con colores y formato.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

APP_TITLE = "Bienvenido a Piki. Tu envío, sin estrés."
APP_SUBTITLE = "Sistema de Tracking de Envíos"


def menu_principal():
	"""Muestra el menú principal de la aplicación con formato mejorado."""
	console.print()  # Espacio superior
	
	# Título principal con panel
	title = Text()
	title.append("📦 ", style="bold yellow")
	title.append("PIKI", style="bold cyan")
	title.append(" - Tu envío, sin estrés", style="italic bright_white")
	
	console.print(Panel(
		title,
		border_style="cyan",
		box=box.DOUBLE,
		expand=False,
		padding=(0, 2)
	))
	
	console.print()  # Espacio
	
	# Crear tabla de opciones
	table = Table(
		show_header=False,
		box=box.ROUNDED,
		border_style="bright_cyan",
		padding=(0, 2),
		expand=False,
		width=70
	)
	
	table.add_column("Opción", style="bold cyan", width=8)
	table.add_column("Descripción", style="bright_white")
	
	table.add_row("🔍 [1]", "Consultar estado de un envío")
	table.add_row("📤 [2]", "Generar reporte para compartir")
	table.add_row("💬 [3]", "Consulta personalizada")
	table.add_row("💾 [4]", "Generar reporte local")
	table.add_row("", "")  # Separador
	table.add_row("👋 [0]", "[red]Salir[/red]")
	
	console.print(table)
	console.print()  # Espacio inferior


def menu_compartir():
	"""Muestra el menú de opciones para compartir reportes."""
	console.print()
	
	# Título
	title = Text()
	title.append("📤 ", style="bold yellow")
	title.append("Compartir Reportes", style="bold magenta")
	
	console.print(Panel(
		title,
		border_style="magenta",
		box=box.ROUNDED,
		expand=False,
		padding=(0, 2)
	))
	
	console.print()
	
	# Tabla de opciones
	table = Table(
		show_header=False,
		box=box.ROUNDED,
		border_style="bright_magenta",
		padding=(0, 2),
		expand=False,
		width=70
	)
	
	table.add_column("Opción", style="bold magenta", width=8)
	table.add_column("Descripción", style="bright_white")
	
	table.add_row("❌ [1]", "Compartir reporte de envíos fallidos")
	table.add_row("🚚 [2]", "Compartir reporte de repartidores")
	table.add_row("✨ [3]", "Consulta personalizada")
	table.add_row("", "")
	table.add_row("⬅️  [4]", "[yellow]Volver al menú principal[/yellow]")
	table.add_row("👋 [0]", "[red]Salir[/red]")
	
	console.print(table)
	console.print()


def menu_local():
	"""Muestra el menú de opciones para generar reportes locales."""
	console.print()
	
	# Título
	title = Text()
	title.append("💾 ", style="bold yellow")
	title.append("Reportes Locales", style="bold green")
	
	console.print(Panel(
		title,
		border_style="green",
		box=box.ROUNDED,
		expand=False,
		padding=(0, 2)
	))
	
	console.print()
	
	# Tabla de opciones
	table = Table(
		show_header=False,
		box=box.ROUNDED,
		border_style="bright_green",
		padding=(0, 2),
		expand=False,
		width=70
	)
	
	table.add_column("Opción", style="bold green", width=8)
	table.add_column("Descripción", style="bright_white")
	
	table.add_row("❌ [1]", "Descargar el reporte de envíos fallidos")
	table.add_row("🚚 [2]", "Descargar el reporte de repartidores")
	table.add_row("✨ [3]", "Consulta personalizada")
	table.add_row("", "")
	table.add_row("⬅️  [4]", "[yellow]Volver al menú principal[/yellow]")
	table.add_row("👋 [0]", "[red]Salir[/red]")
	
	console.print(table)
	console.print()


def menu_continuar():
	"""Muestra el menú de continuación después de completar una acción."""
	console.print()
	console.print()
	
	# Título
	title = Text()
	title.append("🎯 ", style="bold yellow")
	title.append("¿Qué deseas hacer ahora?", style="bold bright_white")
	
	console.print(Panel(
		title,
		border_style="bright_yellow",
		box=box.HEAVY,
		expand=False,
		padding=(0, 2)
	))
	
	console.print()
	
	# Tabla de opciones
	table = Table(
		show_header=False,
		box=box.ROUNDED,
		border_style="bright_yellow",
		padding=(0, 2),
		expand=False,
		width=75
	)
	
	table.add_column("Opción", style="bold yellow", width=8)
	table.add_column("Descripción", style="bright_white")
	
	table.add_row("🏠 [1]", "Volver al menú principal - Consultar envíos y más opciones")
	table.add_row("📤 [2]", "Generar reporte para compartir - Enviar por Drive o Gmail")
	table.add_row("💾 [3]", "Generar reporte local - Descargar en tu computadora")
	table.add_row("", "")
	table.add_row("👋 [0]", "[red]Salir[/red]")
	
	console.print(table)
	console.print()


def menu_plataforma_compartir():
	"""Muestra el menú de selección de plataforma para compartir."""
	console.print()
	
	# Título
	title = Text()
	title.append("🌐 ", style="bold yellow")
	title.append("Selecciona la Plataforma", style="bold blue")
	
	console.print(Panel(
		title,
		border_style="blue",
		box=box.ROUNDED,
		expand=False,
		padding=(0, 2)
	))
	
	console.print()
	
	# Tabla de opciones
	table = Table(
		show_header=False,
		box=box.ROUNDED,
		border_style="bright_blue",
		padding=(0, 2),
		expand=False,
		width=60
	)
	
	table.add_column("Opción", style="bold blue", width=8)
	table.add_column("Descripción", style="bright_white")
	
	table.add_row("☁️  [1]", "Google Drive")
	table.add_row("📧 [2]", "Gmail")
	table.add_row("", "")
	table.add_row("⬅️  [3]", "[yellow]Volver al menú anterior[/yellow]")
	table.add_row("👋 [0]", "[red]Salir[/red]")
	
	console.print(table)
	console.print()
