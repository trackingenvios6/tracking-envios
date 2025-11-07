from n8n_client import send_query, new_session_id
from data_models import N8nRequest #se define en data_models.py
from report_generator import generate_excel_csv
import re

APP_TITLE = "Tracking de Envíos"

def validar_codigo_envio(codigo: str) -> bool:
    return bool(re.fullmatch(r'[A-Z0-9]{10,20}', codigo.strip(), flags=re.I))

def print_menu():
    print(f"=== {APP_TITLE} ===")
    print("[1] Consultar estado de un envío")
    print("[2] Generar reporte de envios fallidos")
    print("[3] Generar reporte por repartidos o localidad")
    print("[4] Otro")
    print("[h] Ayuda [0] Salir")

def handle_opcion_1(session_id: str):
    codigo = input("Ingrese el código de envío: ").strip()
    if not validar_codigo_envio(codigo):
        print("Código de envío inválido. Debe contener entre 10 y 20 caracteres alfanuméricos.")
        return
    req = N8nRequest( 
        chat_input = f"Consultar estado del envío con código {codigo}",
        session_id = session_id
        intent = "consultar_estado",
        params = {"codigo": codigo},
    )
    res = send_query(req)
    if res.ok:
        print(res.message or "No se encontró información para el código proporcionado.")
    else:
        print(f"Error al consultar el envío: {res.message}")

def handle_opcion_2(session_id):
    req = N8nRequest(
        chat_input = "Generar reporte de envíos fallidos",
        session_id = session_id,
        intent = "reporte_fallidos",
    )
    res = send_query(req)
    if res.ok and res.data:
        path = generate_excel_csv(res.data, filename = "reporte_envios_fallidos", to = "xlsx")
        print(f"Reporte generado exitosamente: {path}")
    elif res.ok:
        print("No hay envíos fallidos para generar el reporte.")
    else:
        print(f"Error al generar el reporte: {res.message}")

def handle_opcion_3(session_id: str):
    localidad = input("Ingrese la localidad (o deje vacío para filtrar por repartidor): ").strip() or None
    repartidor = input("Ingrese el nombre del repartidor (o deje vacío para filtrar por localidad): ").strip() or None
    if not localidad and not repartidor:
        print("Debe proporcionar al menos una localidad o un repartidor para generar el reporte.")
        return
    req = N8nRequest(
        chat_input = f"Generar reporte de localidad o repartidor",
        session_id = session_id,
        intent = "reporte_repartidor_localidad",
        params = {"localidad": localidad, "repartidor": repartidor},
    )

    res = send_query(req)

    if res.ok and res.data:
        path = generate_excel_csv(res.data, filename = "reporte_localida_repoartidor", to = "xlsx")
        print(f"Reporte generado exitosamente: {path}")
    elif res.ok:
        print(res.message or"No hay datos para el filtro proporcionado.")
    else:
        print(f"Error al generar el reporte: {res.message}")

def handle_opcion_4(session_id: str):
    consulta = input("Ingrese su consulta personalizada: ").strip()
    if not consulta:
        print("La consulta no puede estar vacía.")
        return
    req = N8nRequest(
        chat_input = consulta,
        session_id = session_id,
        intent = "consulta_personalizada",
    )
    res = send_query(req)
    if res.ok and res.data:
        path = generate_excel_csv(res.data, filename = "reporte_consulta_personalizada", to = "xlsx")
        print(f"Reporte generado exitosamente: {path}")
        print(f"Archivo disponible en: {path}")
    elif res.ok:
        print(res.message or "No se encontró información para la consulta proporcionada.")
    else:
        print(f"Error al procesar la consulta: {res.message}")

def main():
    session_id = new_session_id()
    # print(f"(Sesión: {session_id})")
    while True:
        print_menu()
        opcion = input("Seleccione una opción: ").strip().lower()
        if opcion == "1":
            handle_opcion_1(session_id)
        elif opcion == "2":
            handle_opcion_2(session_id)
        elif opcion == "3":
            handle_opcion_3(session_id)
        elif opcion == "4":
            handle_opcion_4(session_id)
        elif opcion == "h":
            print("Ayuda: Seleccione una opción del menú para realizar una acción específica.")
        elif opcion == "0":
            print("Saliendo del programa. Hasta luego!")
            break
        else:
            print("Opción inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()