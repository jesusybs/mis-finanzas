"""
Gestor de copias de seguridad automáticas y restauración.
"""
from datetime import datetime
from pathlib import Path
import shutil
from typing import List, Tuple

BACKUPS_DIR = Path(__file__).resolve().parent.parent.parent / "backups"


def ensure_backups_dir() -> Path:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    return BACKUPS_DIR


def make_backup(source_file: Path, reason: str = "auto") -> Path:
    """Copia el archivo fuente a la carpeta backups con timestamp."""
    ensure_backups_dir()
    if not source_file.exists():
        raise FileNotFoundError(f"No existe el archivo a respaldar: {source_file}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_reason = "".join(c for c in reason if c.isalnum() or c in "-_")
    backup_name = f"backup_{ts}_{clean_reason}_{source_file.name}"
    dest = BACKUPS_DIR / backup_name
    shutil.copy2(source_file, dest)
    return dest


def list_backups() -> List[Tuple[str, datetime, int, Path]]:
    """Devuelve lista de backups ordenados de más reciente a más antiguo."""
    ensure_backups_dir()
    results = []
    for f in BACKUPS_DIR.glob("backup_*.xlsx"):
        stat = f.stat()
        dt = datetime.fromtimestamp(stat.st_mtime)
        results.append((f.name, dt, stat.st_size, f))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def restore_backup(backup_file: Path, target_file: Path) -> bool:
    """Restaura un backup específico reemplazando el target_file."""
    if not backup_file.exists():
        return False
    # Antes de sobreescribir, respaldamos el actual por precaución
    if target_file.exists():
        make_backup(target_file, reason="pre_restore_safety")
    shutil.copy2(backup_file, target_file)
    return True
