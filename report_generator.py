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
    os.makedirs(path, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _normalize_data(data: Any) -> list[dict]:
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
    registros = _normalize_data(data)
    if not registros:
        return pd.DataFrame()
    if all(isinstance(r, dict) for r in registros):
        return pd.json_normalize(registros, sep=".")
    return pd.DataFrame(registros, columns=["valor"])


def _preview(df: pd.DataFrame, rows: int = 5) -> None:
    print("\n=== Vista previa del reporte ===")
    if df.empty:
        print("(Sin registros para mostrar)")
        return
    print(df.head(rows).to_string(index=False))
    if len(df) > rows:
        print(f"... ({len(df)} filas en total)")
    else:
        print(f"Total de filas: {len(df)}")


def _menu_formato() -> str:
    while True:
        print("=== Seleccione el formato del reporte ===")
        print("[1] Excel (.xlsx)")
        print("[2] CSV (.csv)")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            return "xlsx"
        if opcion == "2":
            return "csv"
        print("Opción inválida. Intente nuevamente.")


def _dialogo_directorio() -> str:
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
