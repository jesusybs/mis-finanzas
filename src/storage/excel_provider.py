"""
Proveedor de almacenamiento para Excel local (finanzas.xlsx).
Implementa operaciones atómicas, bloqueo seguro contra archivos abiertos y respaldos.
"""
from datetime import datetime
from pathlib import Path
import shutil
import tempfile
from typing import Any, Dict, List, Optional
import openpyxl
import pandas as pd
from src.config import load_config
from src.storage.base import BaseDataProvider
from src.storage.backup_manager import make_backup, restore_backup
from src.storage.template_builder import create_master_spreadsheet


class ExcelProvider(BaseDataProvider):
    """Manejador robusto para el archivo Excel finanzas.xlsx."""

    def __init__(self, filepath: Optional[str] = None):
        if filepath:
            self.filepath = Path(filepath)
        else:
            cfg = load_config()
            self.filepath = Path(cfg.get("storage", {}).get("excel", {}).get("filepath", "finanzas.xlsx"))

        # Si el archivo no existe, crearlo inmediatamente desde la plantilla
        if not self.filepath.exists():
            create_master_spreadsheet(self.filepath, include_demo_data=True)

    def is_connected(self) -> bool:
        """Verifica existencia y legibilidad del archivo."""
        if not self.filepath.exists():
            return False
        try:
            with open(self.filepath, "rb") as f:
                f.read(10)
            return True
        except Exception:
            return False

    def check_file_lock(self) -> Optional[str]:
        """Comprueba si el archivo está bloqueado por Excel."""
        if not self.filepath.exists():
            return None
        try:
            with open(self.filepath, "a+b") as f:
                pass
            return None
        except PermissionError:
            return (
                f"El archivo '{self.filepath.name}' parece estar abierto en Microsoft Excel u otra aplicación. "
                "Por favor, ciérralo temporalmente para que la aplicación pueda guardar los cambios."
            )
        except Exception as e:
            return f"Error al verificar acceso al archivo: {str(e)}"

    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Lee una pestaña como DataFrame de Pandas."""
        try:
            # Leer con openpyxl data_only=True para evaluar fórmulas si existen
            wb = openpyxl.load_workbook(self.filepath, data_only=True)
            if sheet_name not in wb.sheetnames:
                return pd.DataFrame()
            ws = wb[sheet_name]
            data = list(ws.values)
            wb.close()

            if not data or len(data) < 1:
                return pd.DataFrame()

            headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(data[0])]
            rows = data[1:] if len(data) > 1 else []
            df = pd.DataFrame(rows, columns=headers)
            # Limpiar filas totalmente vacías
            df = df.dropna(how="all")
            return df
        except Exception as e:
            # Fallback con pandas directo
            try:
                return pd.read_excel(self.filepath, sheet_name=sheet_name)
            except Exception:
                return pd.DataFrame()

    def save_sheet(self, sheet_name: str, df: pd.DataFrame) -> None:
        """Reemplaza los datos de una pestaña respetando el resto del libro."""
        lock_err = self.check_file_lock()
        if lock_err:
            raise PermissionError(lock_err)

        # Respaldo automático antes de sobreescritura
        self.create_backup(reason=f"pre_save_{sheet_name}")

        wb = openpyxl.load_workbook(self.filepath)
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            # Conservar estilo del encabezado si ya existe
            header_vals = [cell.value for cell in ws[1]] if ws.max_row >= 1 else list(df.columns)
            ws.delete_rows(2, ws.max_row)
        else:
            ws = wb.create_sheet(sheet_name)
            ws.append(list(df.columns))

        # Escribir filas del DataFrame
        for row in df.itertuples(index=False):
            ws.append(list(row))

        self._atomic_save(wb)

    def append_row(self, sheet_name: str, row_dict: Dict[str, Any]) -> None:
        """Agrega una fila atómicamente a una pestaña."""
        lock_err = self.check_file_lock()
        if lock_err:
            raise PermissionError(lock_err)

        wb = openpyxl.load_workbook(self.filepath)
        if sheet_name not in wb.sheetnames:
            ws = wb.create_sheet(sheet_name)
            ws.append(list(row_dict.keys()))
        else:
            ws = wb[sheet_name]

        headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        row_values = []
        for h in headers:
            val = row_dict.get(h, "")
            # Normalizar tipos
            if isinstance(val, (datetime, pd.Timestamp)):
                val = val.strftime("%Y-%m-%d")
            row_values.append(val)

        ws.append(row_values)
        self._atomic_save(wb)

    def update_row(
        self, sheet_name: str, row_id: Any, row_dict: Dict[str, Any], id_col: str = "ID"
    ) -> bool:
        """Actualiza una fila existente por ID."""
        lock_err = self.check_file_lock()
        if lock_err:
            raise PermissionError(lock_err)

        wb = openpyxl.load_workbook(self.filepath)
        if sheet_name not in wb.sheetnames:
            wb.close()
            return False

        ws = wb[sheet_name]
        headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        if id_col not in headers:
            wb.close()
            return False

        id_idx = headers.index(id_col) + 1
        found_row = None
        for r in range(2, ws.max_row + 1):
            if str(ws.cell(r, id_idx).value) == str(row_id):
                found_row = r
                break

        if not found_row:
            wb.close()
            return False

        for h, val in row_dict.items():
            if h in headers:
                c_idx = headers.index(h) + 1
                if isinstance(val, (datetime, pd.Timestamp)):
                    val = val.strftime("%Y-%m-%d")
                ws.cell(found_row, c_idx, value=val)

        self._atomic_save(wb)
        return True

    def delete_row(self, sheet_name: str, row_id: Any, id_col: str = "ID") -> bool:
        """Elimina una fila identificada por su ID."""
        lock_err = self.check_file_lock()
        if lock_err:
            raise PermissionError(lock_err)

        wb = openpyxl.load_workbook(self.filepath)
        if sheet_name not in wb.sheetnames:
            wb.close()
            return False

        ws = wb[sheet_name]
        headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        if id_col not in headers:
            wb.close()
            return False

        id_idx = headers.index(id_col) + 1
        found_row = None
        for r in range(2, ws.max_row + 1):
            if str(ws.cell(r, id_idx).value) == str(row_id):
                found_row = r
                break

        if not found_row:
            wb.close()
            return False

        ws.delete_rows(found_row)
        self._atomic_save(wb)
        return True

    def _atomic_save(self, wb: openpyxl.Workbook) -> None:
        """Guarda en archivo temporal y reemplaza atómicamente para prevenir corrupción."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            wb.save(tmp_path)
            wb.close()
            shutil.move(str(tmp_path), str(self.filepath))
        except Exception as e:
            if tmp_path.exists():
                tmp_path.unlink()
            raise e

    def create_backup(self, reason: str = "manual") -> Optional[Path]:
        """Crea una copia de seguridad en /backups."""
        try:
            return make_backup(self.filepath, reason=reason)
        except Exception:
            return None

    def restore_backup(self, backup_file: Path) -> bool:
        """Restaura una copia de seguridad."""
        return restore_backup(backup_file, self.filepath)
