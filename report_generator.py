import os
import pandas as pd
from config import REPORTS_DIR

def _ensure_reports_dir():
    """Ensure that the reports directory exists."""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def generate_excel_csv_report(data, report_name):
    """
    dat_list : lista de dicts [{'codigo': 'AB123', 'estado': 'EN_TRANSITO' }, ...]
    filename: nombre sin extensión (p.ej. 'envios_fallidos')
    to:  'xlsx' o 'csv'
    return: ruta completa del archivo generado
    """
    _ensure_reports_dir()
    
    df = pd.DataFrame(data_list or [])

    path = os.path.join(REPORTS_DIR, f"{filename}.{to.lower()}")

    if to.lower() == 'csv':
        df.to_csv(path, index=False, encoding = "utf-8")
    else:
        df.to_excel(path, index=False, engine='openpyxl')  
    return path
