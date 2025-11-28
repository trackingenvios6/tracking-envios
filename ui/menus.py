"""
ui.menus
Contiene todas las funciones que imprimen menús en la aplicación.
Las funciones fueron migradas desde `main.py` sin modificaciones en su lógica.
"""

APP_TITLE = "Bienvenido a Piki. Tu envío, sin estrés."


def menu_principal():
    """Muestra el menú principal de la aplicación."""
    print(f"=== {APP_TITLE} ===")
    print("[1] Consultar estado de un envío")
    print("[2] Generar reporte para compartir")
    print("[3] Consulta personalizada")
    print("[4] Generar reporte local")
    print("[0] Salir")


def menu_compartir():
    """Muestra el menú de opciones para compartir reportes."""
    print(f"=== {APP_TITLE} ===")
    print("[1] Compartir reporte de envíos fallidos")
    print("[2] Compartir reporte de repartidores")
    print("[3] Consulta personalizada")
    print("[4] Volver al menú principal")
    print("[0] Salir")


def menu_local():
    """Muestra el menú de opciones para generar reportes locales."""
    print(f"=== {APP_TITLE} ===")
    print("[1] Descargar el reporte de envíos fallidos")
    print("[2] Descargar el reporte de repartidores")
    print("[3] Consulta personalizada")
    print("[4] Volver al menú principal")
    print("[0] Salir")


def menu_continuar():
    """Muestra el menú de continuación después de completar una acción."""
    print("\n" + "="*60)
    print("¿Qué deseas hacer ahora?")
    print("="*60)
    print("[1] Volver al menú principal - Consultar envíos y más opciones")
    print("[2] Generar reporte para compartir - Enviar por Drive o Gmail")
    print("[3] Generar reporte local - Descargar en tu computadora")
    print("[0] Salir")
    print("="*60)


def menu_plataforma_compartir():
    """Muestra el menú de selección de plataforma para compartir."""
    print("=== Seleccione la plataforma para compartir ===")
    print("[1] Drive")
    print("[2] Gmail")
    print("[3] Volver al menú anterior")
    print("[0] Salir")
