"""
Módulo de Configuración para la Aplicación de Finanzas Personales.
Carga ajustes desde config.yaml y provee valores por defecto seguros.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {
        "name": "Mi Control de Finanzas",
        "version": "1.0.0",
        "storage_mode": "excel",
    },
    "storage": {
        "excel": {"filepath": "finanzas.xlsx"},
        "google_sheets": {
            "credentials_file": "credentials.json",
            "spreadsheet_name": "Mis Finanzas Personales",
        },
    },
    "general": {
        "currency_symbol": "$",
        "currency_code": "USD",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "month_start_day": 1,
        "alert_yellow_pct": 80.0,
        "alert_red_pct": 100.0,
    },
    "theme": {
        "default_mode": "dark",
    },
}


def load_config() -> Dict[str, Any]:
    """Carga config.yaml; si no existe, retorna DEFAULT_CONFIG."""
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            # Mezcla segura con defaults
            merged = DEFAULT_CONFIG.copy()
            for k, v in data.items():
                if isinstance(v, dict) and k in merged:
                    merged[k].update(v)
                else:
                    merged[k] = v
            return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg: Dict[str, Any]) -> None:
    """Guarda la configuración actualizada en config.yaml."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False, allow_unicode=True)
