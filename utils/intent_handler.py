"""
utils.intent_handler
Maneja intenciones especiales detectadas en respuestas de n8n.
"""
from pathlib import Path
from typing import Optional
from data_models import RespuestaN8n
from utils.helpers import exportar_reporte_local, mostrar_resultado_reporte
from report_generator import solicitar_configuracion_salida


def es_reporte_local(res: RespuestaN8n) -> bool:
    """
    Detecta si la respuesta de n8n indica intención de guardado local.
    
    Args:
        res: Respuesta de n8n a validar
        
    Returns:
        bool: True si se detecta intención de guardado local
    """
    # Verificar campo estructurado de intención
    # n8n puede devolver "reporte_local", "descargar", "guardar_local", etc.
    intenciones_validas = {"reporte_local", "descargar", "guardar_local", "download"}
    if res.intencion and res.intencion.lower() in intenciones_validas:
        return True
    
    # Fallback: buscar palabras clave en el mensaje (opcional)
    if res.mensaje:
        palabras_clave = ["reporte local", "guardar local", "descargar", "guardar en mi pc"]
        mensaje_lower = res.mensaje.lower()
        return any(palabra in mensaje_lower for palabra in palabras_clave)
    
    return False


def obtener_ruta_por_defecto() -> Path:
    """
    Retorna la ruta por defecto para guardar reportes.
    
    Returns:
        Path: Ruta a la carpeta Downloads del usuario
    """
    return Path.home() / "Downloads"


def solicitar_formato_guardado() -> str:
    """
    Pregunta al usuario el formato deseado para el reporte.
    
    Returns:
        str: Formato elegido ('xlsx', 'json', 'csv') o 'xlsx' por defecto
    """
    print("\n📁 ¿En qué formato deseas guardarlo?")
    print("   1. Excel (.xlsx)")
    print("   2. JSON (.json)")
    print("   3. CSV (.csv)")
    
    opcion = input("Opción (Enter para Excel): ").strip()
    
    formatos = {
        "1": "xlsx",
        "2": "json",
        "3": "csv",
        "": "xlsx",  # Por defecto
    }
    
    return formatos.get(opcion, "xlsx")


def ejecutar_guardado_local_desde_chat(
    res: RespuestaN8n, 
    nombre_base: str = "reporte_chat_piki"
) -> Optional[str]:
    """
    Ejecuta el guardado local de datos desde el chat con Piki.
    
    Reutiliza las funciones existentes de guardado, pero con una 
    configuración más rápida para no interrumpir el flujo del chat.
    
    Args:
        res: Respuesta de n8n con los datos a guardar
        nombre_base: Nombre base para el archivo
        
    Returns:
        Optional[str]: Ruta del archivo guardado, o None si hubo error/cancelación
    """
    # Verificar que hay datos para guardar
    if not res.datos:
        print("⚠️  No hay datos disponibles para guardar.")
        return None
    
    # Solicitar configuración de salida (formato y directorio)
    config = solicitar_configuracion_salida()
    if config is None:
        print("❌ Guardado cancelado.")
        return None
    
    formato, directorio = config
    
    # Exportar el reporte usando la función existente
    try:
        path = exportar_reporte_local(
            data=res.datos,
            nombre_base=nombre_base,
            formato=formato,
            directorio=directorio
        )
        
        if path:
            # No llamar a mostrar_resultado_reporte porque ya se muestra en generar_reporte
            return path
        else:
            print("❌ No se pudo generar el reporte.")
            return None
            
    except Exception as e:
        print(f"❌ Error al guardar el reporte: {e}")
        return None
