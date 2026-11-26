"""
Fábrica para instanciar el proveedor de almacenamiento configurado.
"""
from typing import Optional
from src.config import load_config
from src.storage.base import BaseDataProvider
from src.storage.excel_provider import ExcelProvider
from src.storage.sheets_provider import GoogleSheetsProvider


def get_data_provider(override_mode: Optional[str] = None) -> BaseDataProvider:
    """Retorna el proveedor configurado (Excel o Google Sheets con fallback a Excel)."""
    cfg = load_config()
    mode = override_mode or cfg.get("app", {}).get("storage_mode", "excel")

    if mode == "google_sheets":
        provider = GoogleSheetsProvider()
        if provider.is_connected():
            return provider
        # Si no hay credenciales o conexión a Google Sheets, usar Excel con aviso
        return ExcelProvider()

    return ExcelProvider()
