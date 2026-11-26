"""
Definición de la clase base abstracta para proveedores de datos (Excel / Google Sheets).
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd


class BaseDataProvider(ABC):
    """Interfaz abstracta para operaciones CRUD sobre la hoja de cálculo."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Verifica si el origen de datos está disponible y accesible."""
        pass

    @abstractmethod
    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Obtiene una pestaña específica como DataFrame de Pandas."""
        pass

    @abstractmethod
    def save_sheet(self, sheet_name: str, df: pd.DataFrame) -> None:
        """Reemplaza el contenido de una pestaña con un DataFrame."""
        pass

    @abstractmethod
    def append_row(self, sheet_name: str, row_dict: Dict[str, Any]) -> None:
        """Agrega una nueva fila al final de la pestaña especificada."""
        pass

    @abstractmethod
    def update_row(
        self, sheet_name: str, row_id: Any, row_dict: Dict[str, Any], id_col: str = "ID"
    ) -> bool:
        """Actualiza una fila existente identificada por su ID."""
        pass

    @abstractmethod
    def delete_row(self, sheet_name: str, row_id: Any, id_col: str = "ID") -> bool:
        """Elimina una fila identificada por su ID."""
        pass

    @abstractmethod
    def create_backup(self, reason: str = "manual") -> Optional[Path]:
        """Crea una copia de seguridad timestamped en la carpeta /backups."""
        pass

    @abstractmethod
    def restore_backup(self, backup_file: Path) -> bool:
        """Restaura la base de datos a partir de un archivo de respaldo."""
        pass
