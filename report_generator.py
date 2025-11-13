import os
import pandas as pd
from config import REPORTS_DIR

def _ensure_reports_dir() -> None:
    """Crea la carpeta de reportes si no existe."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_excel_csv(data_list: list[dict], filename: str, to: str = "xlsx") -> str:
    """
    Genera un archivo Excel o CSV a partir de una lista de diccionarios.

    Args:
        data_list (list[dict]): Lista de registros, ej. [{'codigo': 'AB123', 'estado': 'EN_TRANSITO'}, ...]
        filename (str): Nombre base del archivo (sin extensión).
        to (str): Formato de salida ('xlsx' o 'csv'). Por defecto 'xlsx'.

    Returns:
        str: Ruta completa del archivo generado.
    """
    _ensure_reports_dir()

    # Crear DataFrame incluso si la lista está vacía
    df = pd.DataFrame(data_list or [])

    # Construir ruta final
    path = os.path.join(REPORTS_DIR, f"{filename}.{to.lower()}")

    if to.lower() == 'csv':
        df.to_csv(path, index=False, encoding = "utf-8")
    else:
        df.to_excel(path, index=False, engine='openpyxl')  
    return path
