"""
Punto de entrada minimalista para la aplicación.

Importa funciones del código reorganizado (ui, handlers, utils) y solo mantiene
el loop principal y la creación de la sesión.
"""
from n8n_client import nuevo_id_sesion

from ui.menus import menu_principal
from ui.validaciones import manejar_continuar
from handlers.consultas import (
    consultar_estado_envio,
    iniciar_chat_con_piki,
)
from handlers.compartir import manejar_menu_compartir
from handlers.reportes import manejar_menu_local


def main():
    """Función principal que inicia la aplicación.

    Genera un ID de sesión único, muestra el menú principal en un bucle
    y delega las acciones según la opción seleccionada por el usuario.
    """
    id_sesion = nuevo_id_sesion()

    menu_activo = "principal"  # Controla qué menú mostrar

    while True:
        if menu_activo == "principal":
            menu_principal()
            opcion = input("Seleccione una opción: ").strip().lower()

            if opcion == "1":
                consultar_estado_envio(id_sesion)
                destino = manejar_continuar()
                if destino == "salir":
                    break
                menu_activo = destino

            elif opcion == "2":
                menu_activo = "compartir"

            elif opcion == "3":
                iniciar_chat_con_piki(id_sesion)
                destino = manejar_continuar()
                if destino == "salir":
                    break
                menu_activo = destino

            elif opcion == "4":
                menu_activo = "local"

            elif opcion == "0":
                print("Saliendo del programa. ¡Hasta luego! 👋")
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")

        elif menu_activo == "compartir":
            continuar = manejar_menu_compartir(id_sesion)
            if not continuar:
                break
            destino = manejar_continuar()
            if destino == "salir":
                break
            menu_activo = destino

        elif menu_activo == "local":
            continuar = manejar_menu_local(id_sesion)
            if not continuar:
                break
            destino = manejar_continuar()
            if destino == "salir":
                break
            menu_activo = destino


if __name__ == "__main__":
    main()