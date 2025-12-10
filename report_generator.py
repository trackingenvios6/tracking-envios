"""
Generador de Reportes
=====================

Módulo para generar reportes en formato Excel o CSV a partir de datos
provenientes de n8n. Maneja normalización de datos, preview, y
configuración de salida mediante interfaz de usuario.

Funciones públicas:
    - generar_reporte: Genera un reporte en el formato especificado
    - solicitar_configuracion_salida: Solicita formato y directorio al usuario

Dependencias:
    - pandas: Para procesamiento de datos
    - openpyxl: Para generación de archivos Excel
    - tkinter: Para diálogo de selección de carpeta (opcional)
"""

import json
import os
from datetime import datetime
from typing import Any, Tuple

import pandas as pd
from config import REPORTS_DIR

try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:  # pragma: no cover
    tk = None
    filedialog = None

LAST_REPORT_PATH: str | None = None
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")


def _ensure_dir(path: str) -> None:
    """
    Crea un directorio si no existe.
    
    Args:
        path (str): Ruta del directorio a crear
    """
    os.makedirs(path, exist_ok=True)


def _timestamp() -> str:
    """
    Genera un timestamp en formato YYYYMMDD_HHMMSS.
    
    Returns:
        str: Timestamp formateado (ej: "20231124_153045")
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _normalize_data(data: Any) -> list[dict]:
    """
    Normaliza datos de entrada a una lista de diccionarios.
    
    Maneja múltiples formatos de entrada y los convierte a un formato
    uniforme que puede ser procesado por pandas.
    
    Args:
        data (Any): Datos a normalizar (puede ser None, str, dict, list, u otro)
    
    Returns:
        list[dict]: Lista de diccionarios normalizada
    
    Casos manejados:
        - None: Retorna lista vacía
        - String JSON: Parsea y retorna como lista
        - String no-JSON: Retorna [{"valor": string}]
        - Dict: Retorna [dict]
        - List: Retorna la lista tal cual
        - Otro tipo: Retorna [{"valor": data}]
    """
    if data is None:
        return []

    if isinstance(data, str):
        raw = data.strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return [{"valor": raw}]
        else:
            data = parsed

    if isinstance(data, dict):
        return [data]

    if isinstance(data, list):
        return data

    return [{"valor": data}]


def _to_dataframe(data: Any) -> pd.DataFrame:
    """
    Convierte datos normalizados a un DataFrame de pandas.
    
    Aplana estructuras JSON anidadas usando json_normalize.
    
    Args:
        data (Any): Datos a convertir
    
    Returns:
        pd.DataFrame: DataFrame con los datos procesados
    
    Nota:
        - Campos anidados se aplanan con separador "."
        - Si no hay registros, retorna DataFrame vacío
    """
    registros = _normalize_data(data)
    if not registros:
        return pd.DataFrame()
    if all(isinstance(r, dict) for r in registros):
        return pd.json_normalize(registros, sep=".")
    return pd.DataFrame(registros, columns=["valor"])


def _preview(df: pd.DataFrame, rows: int = 5, max_cols: int = 5) -> None:
    """
    Muestra una vista previa del DataFrame en consola con formato de tabla.
    
    Args:
        df (pd.DataFrame): DataFrame a previsualizar
        rows (int, optional): Número de filas a mostrar. Default: 5
        max_cols (int, optional): Número máximo de columnas a mostrar. Default: 5
    """
    print("\n=== Vista previa del reporte ===")
    if df.empty:
        print("(Sin registros para mostrar)")
        return
    
    # Configurar pandas para mejor visualización
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 40)
    
    preview_df = df.head(rows)
    
    # Obtener nombres de columnas y limitar si hay muchas
    all_columns = list(preview_df.columns)
    total_cols = len(all_columns)
    
    # Si hay más columnas que el límite, truncar y agregar indicador
    if total_cols > max_cols:
        columns = all_columns[:max_cols]
        columns_hidden = total_cols - max_cols
        show_hidden_indicator = True
    else:
        columns = all_columns
        columns_hidden = 0
        show_hidden_indicator = False
    
    # Calcular anchos de columnas
    col_widths = {}
    
    for col in columns:
        # Ancho mínimo: el mayor entre el nombre de columna y el contenido
        max_content_width = preview_df[col].astype(str).str.len().max()
        col_widths[col] = max(len(str(col)), max_content_width, 8)  # mínimo 8
    
    # Si hay columnas ocultas, agregar columna indicadora "..."
    if show_hidden_indicator:
        indicator_col = "..."
        columns.append(indicator_col)
        col_widths[indicator_col] = 5
    
    # Crear línea separadora
    separator_parts = ['+']
    for col in columns:
        separator_parts.append('-' * (col_widths[col] + 2))
        separator_parts.append('+')
    separator = ''.join(separator_parts)
    
    # Imprimir línea superior
    print(separator)
    
    # Imprimir encabezado
    header_parts = ['|']
    for col in columns:
        header_parts.append(f' {str(col):<{col_widths[col]}} ')
        header_parts.append('|')
    print(''.join(header_parts))
    
    # Línea separadora entre encabezado y datos
    print(separator)
    
    # Imprimir filas de datos
    for _, row in preview_df.iterrows():
        row_parts = ['|']
        for col in columns:
            if col == "...":
                # Columna indicadora de columnas ocultas
                value = "..."
            else:
                value = str(row[col]) if pd.notna(row[col]) else ''
                # Truncar si es muy largo
                if len(value) > col_widths[col]:
                    value = value[:col_widths[col]-3] + '...'
            row_parts.append(f' {value:<{col_widths[col]}} ')
            row_parts.append('|')
        print(''.join(row_parts))
    
    # Línea inferior
    print(separator)
    
    # Mostrar información de filas y columnas
    if len(df) > rows or show_hidden_indicator:
        info_parts = []
        if len(df) > rows:
            info_parts.append(f"{len(df)} filas en total")
        if show_hidden_indicator:
            info_parts.append(f"{columns_hidden} columna{'s' if columns_hidden > 1 else ''} oculta{'s' if columns_hidden > 1 else ''}")
        print(f"... ({', '.join(info_parts)})")
    else:
        print(f"Total: {len(df)} fila{'s' if len(df) != 1 else ''}, {total_cols} columna{'s' if total_cols != 1 else ''}")


def _menu_formato() -> str | None:
    """
    Muestra menú interactivo para seleccionar formato de reporte.
    
    Returns:
        str | None: Formato seleccionado ("xlsx" o "csv"), o None si se cancela
    """
    from ui.menus import menu_formato_reporte
    from ui.console_utils import print_info, print_error
    
    while True:
        menu_formato_reporte()
        print_info("Presiona Enter o [0] para cancelar")
        opcion = input("Opción: ").strip()
        
        # Permitir cancelar
        if not opcion or opcion == "0":
            print_info("Operación cancelada.")
            return None
        
        if opcion == "1":
            return "xlsx"
        if opcion == "2":
            return "csv"
        print_error("Opción inválida. Intente nuevamente.")


def _dialogo_directorio() -> str:
    """
    Abre un diálogo gráfico para seleccionar directorio de destino.
    
    Returns:
        str: Ruta del directorio seleccionado, o directorio por defecto
             si el usuario cancela o tkinter no está disponible
    
    Fallback:
        - Si tkinter no está disponible: usa REPORTS_DIR o Downloads
        - Si el usuario cancela: usa REPORTS_DIR o Downloads
    """
    if tk and filedialog:
        try:
            root = tk.Tk()
            root.withdraw()
            selected = filedialog.askdirectory(title="Seleccioná la carpeta destino para el reporte")
            root.destroy()
            if selected:
                return selected
        except Exception:
            pass
    return REPORTS_DIR or DEFAULT_DOWNLOAD_DIR


def solicitar_configuracion_salida() -> Tuple[str, str]:
    """
    Solicita al usuario el formato y directorio para el reporte.
    
    Interfaz interactiva que combina menú de texto para formato
    y diálogo gráfico (si está disponible) para directorio.
    
    Returns:
        Tuple[str, str]: Tupla con (formato, directorio)
            - formato: "xlsx" o "csv"
            - directorio: Ruta del directorio seleccionado
    """
    formato = _menu_formato()
    directorio = _dialogo_directorio()
    print(f"Formato seleccionado: {formato.upper()} - Carpeta: {directorio}")
    return formato, directorio


def generar_reporte(
    data: Any,
    filename: str = "reporte",
    formato: str | None = None,
    directorio: str | None = None,
    use_timestamp: bool = True,
    preview: bool = True,
) -> str:
    """
    Genera un reporte en Excel o CSV a partir de datos.
    
    Función principal del módulo que:
    1. Normaliza los datos a DataFrame
    2. Opcionalmente muestra preview
    3. Guarda el archivo en el formato y directorio especificados
    4. Retorna la ruta del archivo generado
    
    Args:
        data (Any): Datos a incluir en el reporte (puede ser dict, list, str JSON, etc.)
        filename (str, optional): Nombre base del archivo. Default: "reporte"
        formato (str | None, optional): Formato del archivo ("xlsx" o "csv"). Default: "xlsx"
        directorio (str | None, optional): Directorio destino. Default: REPORTS_DIR o Downloads
        use_timestamp (bool, optional): Si agregar timestamp al nombre. Default: True
        preview (bool, optional): Si mostrar vista previa en consola. Default: True
    
    Returns:
        str: Ruta completa del archivo generado
    
    Ejemplos:
        >>> generar_reporte([{"nombre": "Juan", "edad": 30}])
        "C:\\Users\\...\\reporte_20231124_153045.xlsx"
        
        >>> generar_reporte(data, formato="csv", use_timestamp=False)
        "C:\\Users\\...\\reporte.csv"
    
    Nota:
        La ruta del último reporte generado se guarda en LAST_REPORT_PATH
    """
    global LAST_REPORT_PATH

    df = _to_dataframe(data)
    if preview:
        _preview(df)

    ext = (formato or "xlsx").lower()
    destino = directorio or REPORTS_DIR or DEFAULT_DOWNLOAD_DIR
    _ensure_dir(destino)

    nombre = f"{filename}_{_timestamp()}" if use_timestamp else filename
    path = os.path.join(destino, f"{nombre}.{ext}")

    if ext == "csv":
        df.to_csv(path, index=False, encoding="utf-8")
    else:
        df.to_excel(path, index=False, engine="openpyxl")

    LAST_REPORT_PATH = path
    print(f"Archivo guardado en: {path}")
    return path
