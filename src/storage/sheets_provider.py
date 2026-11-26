"""
Proveedor de almacenamiento para Google Sheets (gspread).
Permite trabajar en la nube usando una cuenta de servicio de Google Cloud.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from src.config import load_config
from src.storage.base import BaseDataProvider
from src.storage.backup_manager import make_backup


class GoogleSheetsProvider(BaseDataProvider):
    """Manejador para Google Sheets mediante gspread."""

    def __init__(self, credentials_path: Optional[str] = None, spreadsheet_name: Optional[str] = None):
        cfg = load_config()
        gs_cfg = cfg.get("storage", {}).get("google_sheets", {})
        self.credentials_path = Path(credentials_path or gs_cfg.get("credentials_file", "credentials.json"))
        self.spreadsheet_name = spreadsheet_name or gs_cfg.get("spreadsheet_name", "Mis Finanzas Personales")
        self._client = None
        self._spreadsheet = None

    def is_connected(self) -> bool:
        """Verifica si las credenciales existen (en archivo o st.secrets) y se puede abrir el libro en Google Sheets."""
        try:
            import gspread
            if not self._client:
                # 1. Intentar cargar desde st.secrets si está en Streamlit Cloud
                try:
                    import streamlit as st
                    if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
                        self._client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
                except Exception:
                    pass

                # 2. Si no, cargar desde archivo local credentials.json
                if not self._client:
                    if not self.credentials_path.exists():
                        return False
                    self._client = gspread.service_account(filename=str(self.credentials_path))

            if not self._spreadsheet and self._client:
                self._spreadsheet = self._client.open(self.spreadsheet_name)
            return self._spreadsheet is not None
        except Exception:
            return False

    def _get_worksheet(self, sheet_name: str):
        if not self.is_connected():
            raise ConnectionError(
                "No hay conexión con Google Sheets. Verifica que 'credentials.json' exista "
                f"y que hayas compartido la hoja '{self.spreadsheet_name}' con el correo de la cuenta de servicio."
            )
        try:
            return self._spreadsheet.worksheet(sheet_name)
        except Exception:
            # Si la hoja no existe, crearla
            return self._spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Lee una hoja de cálculo remota como DataFrame."""
        ws = self._get_worksheet(sheet_name)
        records = ws.get_all_records()
        if not records:
            # Si no hay records estructurados, intentar con valores crudos
            vals = ws.get_all_values()
            if not vals or len(vals) < 2:
                return pd.DataFrame()
            headers = vals[0]
            rows = vals[1:]
            return pd.DataFrame(rows, columns=headers)
        return pd.DataFrame(records)

    def save_sheet(self, sheet_name: str, df: pd.DataFrame) -> None:
        """Reemplaza los datos de una hoja de Google Sheets."""
        ws = self._get_worksheet(sheet_name)
        ws.clear()
        values = [list(df.columns)] + df.fillna("").astype(str).values.tolist()
        ws.update(range_name="A1", values=values)

    def append_row(self, sheet_name: str, row_dict: Dict[str, Any]) -> None:
        """Agrega una fila al final de la hoja en Google Sheets."""
        ws = self._get_worksheet(sheet_name)
        headers = ws.row_values(1)
        if not headers:
            headers = list(row_dict.keys())
            ws.append_row(headers)

        row_values = [str(row_dict.get(h, "")) for h in headers]
        ws.append_row(row_values)

    def update_row(
        self, sheet_name: str, row_id: Any, row_dict: Dict[str, Any], id_col: str = "ID"
    ) -> bool:
        """Actualiza una fila existente por ID en Google Sheets."""
        ws = self._get_worksheet(sheet_name)
        headers = ws.row_values(1)
        if id_col not in headers:
            return False

        id_col_idx = headers.index(id_col) + 1
        cell = ws.find(str(row_id), in_column=id_col_idx)
        if not cell:
            return False

        row_num = cell.row
        for col_name, val in row_dict.items():
            if col_name in headers:
                c_idx = headers.index(col_name) + 1
                ws.update_cell(row_num, c_idx, str(val))
        return True

    def delete_row(self, sheet_name: str, row_id: Any, id_col: str = "ID") -> bool:
        """Elimina una fila por ID en Google Sheets."""
        ws = self._get_worksheet(sheet_name)
        headers = ws.row_values(1)
        if id_col not in headers:
            return False

        id_col_idx = headers.index(id_col) + 1
        cell = ws.find(str(row_id), in_column=id_col_idx)
        if not cell:
            return False

        ws.delete_rows(cell.row)
        return True

    def create_backup(self, reason: str = "manual") -> Optional[Path]:
        """Guarda un respaldo local de los datos actuales de Google Sheets."""
        try:
            excel_path = Path("finanzas.xlsx")
            if excel_path.exists():
                return make_backup(excel_path, reason=f"gsheets_{reason}")
        except Exception:
            pass
        return None

    def restore_backup(self, backup_file: Path) -> bool:
        """Restaura datos desde un respaldo local hacia Google Sheets."""
        if not backup_file.exists():
            return False
        import openpyxl
        wb = openpyxl.load_workbook(backup_file, data_only=True)
        for sname in wb.sheetnames:
            ws_local = wb[sname]
            vals = list(ws_local.values)
            if vals and len(vals) > 0:
                headers = [str(h) for h in vals[0]]
                rows = vals[1:] if len(vals) > 1 else []
                df = pd.DataFrame(rows, columns=headers)
                self.save_sheet(sname, df)
        return True
