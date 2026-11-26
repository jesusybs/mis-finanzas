"""
Utilidades de formateo para números, monedas y fechas.
"""
from datetime import date, datetime
from typing import Union
from src.config import load_config


def format_currency(amount: Union[int, float], symbol: str = None) -> str:
    """Formatea un número como moneda legible (ej: $ 1,234.56)."""
    cfg = load_config().get("general", {})
    sym = symbol if symbol is not None else cfg.get("currency_symbol", "$")
    dec_sep = cfg.get("decimal_separator", ".")
    thou_sep = cfg.get("thousands_separator", ",")

    try:
        val = float(amount)
    except (ValueError, TypeError):
        val = 0.0

    negative = val < 0
    val_abs = abs(val)

    # Formato estándar con comas
    formatted = f"{val_abs:,.2f}"

    if thou_sep != "," or dec_sep != ".":
        # Intercambio personalizado si difiere de estándar
        parts = formatted.split(".")
        integer_part = parts[0].replace(",", thou_sep)
        decimal_part = parts[1]
        formatted = f"{integer_part}{dec_sep}{decimal_part}"

    prefix = "-" if negative else ""
    return f"{prefix}{sym} {formatted}"


def format_pct(value: Union[int, float], decimals: int = 1) -> str:
    """Formatea un valor decimal o porcentual a porcentaje (ej: 84.5%)."""
    try:
        val = float(value)
        return f"{val:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.0%"


def format_date(d: Union[str, date, datetime]) -> str:
    """Formatea fecha a formato estándar AAAA-MM-DD."""
    if isinstance(d, (date, datetime)):
        return d.strftime("%Y-%m-%d")
    return str(d)[:10]
