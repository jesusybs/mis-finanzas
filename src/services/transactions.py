"""
Servicio para gestion de transacciones (Movimientos), validaciones,
categorizacion automatica y actualizacion de saldos.
"""
from datetime import date, datetime
import re
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

KEYWORD_RULES = [
    (r"(uber|cabify|taxi|didi)", "Transporte", "Transporte Publico / Taxi", "Necesidad"),
    (r"(shell|ypf|axion|combustible|gasolina|nafta)", "Transporte", "Combustible", "Necesidad"),
    (r"(supermercado|carrefour|coto|dia|jumbo|walmart|exito|chango)", "Alimentacion", "Supermercado", "Necesidad"),
    (r"(restaurante|parrilla|pizza|burger|mcdonald|sushi|delivery|rappi|pedidosya)", "Alimentacion", "Restaurantes y Delivery", "Deseo"),
    (r"(cafe|café|starbucks|havanna|snack|panaderia)", "Alimentacion", "Cafe y Snacks", "Deseo"),
    (r"(farmacia|farmacity|medicamento|remedio|salud|droga)", "Salud", "Farmacia y Medicamentos", "Necesidad"),
    (r"(netflix|spotify|disney|prime|hbo|streaming|youtube)", "Ocio y Salidas", "Streaming y Suscripciones", "Deseo"),
    (r"(cine|teatro|concierto|recital|show|entradas)", "Ocio y Salidas", "Cine, Conciertos y Salidas", "Deseo"),
    (r"(luz|edenor|edesur|electricidad|enel)", "Servicios", "Electricidad", "Necesidad"),
    (r"(agua|aysa|gas|metrogas|naturgy)", "Servicios", "Agua y Gas", "Necesidad"),
    (r"(internet|fibertel|telecom|movistar|claro|personal|wifi)", "Servicios", "Internet y Telefonia", "Necesidad"),
    (r"(alquiler|expensas|hipoteca|inmobiliaria)", "Vivienda", "Alquiler / Hipoteca", "Necesidad"),
    (r"(tarjeta|visa|mastercard|amex|resumen)", "Pago de Deudas", "Tarjeta de Credito", "Necesidad"),
    (r"(fondo|inversion|cedear|accion|plazo fijo|sp500)", "Ahorro e Inversion", "Inversiones", "Ahorro"),
]


def suggest_category(description: str, merchant: str = "") -> Optional[Tuple[str, str]]:
    text = f"{description} {merchant}".lower()
    for pattern, cat, subcat, _ in KEYWORD_RULES:
        if re.search(pattern, text):
            return cat, subcat
    return None


def get_next_mov_id(df_movs: pd.DataFrame) -> str:
    if df_movs.empty or "ID" not in df_movs.columns:
        return "MOV-1001"

    ids = []
    for val in df_movs["ID"].dropna():
        s = str(val).strip()
        if s.startswith("MOV-"):
            try:
                ids.append(int(s.split("-")[1]))
            except ValueError:
                pass
    if not ids:
        return "MOV-1001"
    return f"MOV-{max(ids) + 1}"


def validate_movement_data(data: Dict[str, Any]) -> List[str]:
    errors = []
    try:
        monto = float(data.get("Monto", 0))
        if monto <= 0:
            errors.append("El monto debe ser un numero positivo mayor a 0.")
    except (ValueError, TypeError):
        errors.append("El monto ingresado no es valido.")

    if not data.get("Fecha"):
        errors.append("Debe especificar una fecha.")
    else:
        try:
            datetime.strptime(str(data["Fecha"])[:10], "%Y-%m-%d")
        except ValueError:
            errors.append("La fecha debe tener el formato AAAA-MM-DD.")

    if not data.get("Tipo"):
        errors.append("Debe seleccionar el Tipo.")

    cat = data.get("Categoria") or data.get("Categoría")
    if not cat:
        errors.append("Debe seleccionar una Categoria.")

    if not data.get("Cuenta"):
        errors.append("Debe seleccionar la Cuenta.")

    return errors


def check_possible_duplicates(
    provider, fecha: str, monto: float, comercio: str, tolerance_days: int = 3
) -> List[Dict[str, Any]]:
    df = provider.get_sheet("Movimientos")
    if df.empty or "Fecha" not in df.columns or "Monto" not in df.columns:
        return []

    try:
        target_date = datetime.strptime(str(fecha)[:10], "%Y-%m-%d").date()
    except Exception:
        return []

    duplicates = []
    for _, row in df.iterrows():
        try:
            row_date = datetime.strptime(str(row["Fecha"])[:10], "%Y-%m-%d").date()
            diff_days = abs((row_date - target_date).days)
            row_monto = float(row["Monto"])
            row_comercio = str(row.get("Comercio/Lugar", "")).lower().strip()
            target_com = comercio.lower().strip()

            if diff_days <= tolerance_days and abs(row_monto - monto) < 0.01:
                if row_comercio == target_com or not target_com or not row_comercio:
                    duplicates.append(row.to_dict())
        except Exception:
            continue
    return duplicates


def register_movement(provider, data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
    errors = validate_movement_data(data)
    if errors:
        return False, " | ".join(errors), None

    df_movs = provider.get_sheet("Movimientos")
    mov_id = data.get("ID") or get_next_mov_id(df_movs)
    data["ID"] = mov_id

    # Compatibilidad de claves con o sin tildes
    if "Categoria" not in df_movs.columns and "Categoría" in df_movs.columns:
        if "Categoria" in data:
            data["Categoría"] = data.pop("Categoria")
    elif "Categoria" in df_movs.columns and "Categoría" in data:
        data["Categoria"] = data.pop("Categoría")

    if "Descripcion" not in df_movs.columns and "Descripción" in df_movs.columns:
        if "Descripcion" in data:
            data["Descripción"] = data.pop("Descripcion")
    elif "Descripcion" in df_movs.columns and "Descripción" in data:
        data["Descripcion"] = data.pop("Descripción")

    if "Recurrente" not in df_movs.columns and "¿Recurrente?" in df_movs.columns:
        if "Recurrente" in data:
            data["¿Recurrente?"] = data.pop("Recurrente")
    elif "Recurrente" in df_movs.columns and "¿Recurrente?" in data:
        data["Recurrente"] = data.pop("¿Recurrente?")

    data.setdefault("Subcategoria", "")
    data.setdefault("Comercio/Lugar", "")
    data.setdefault("Metodo de pago", "Tarjeta de Debito")
    data.setdefault("Etiquetas", "")
    data.setdefault("Nota", "")

    try:
        provider.append_row("Movimientos", data)
        _update_account_balance_on_transaction(
            provider, data["Cuenta"], float(data["Monto"]), data["Tipo"], is_reversal=False
        )
        return True, f"Movimiento {mov_id} guardado.", mov_id
    except Exception as e:
        return False, f"Error al guardar movimiento: {str(e)}", None


def _update_account_balance_on_transaction(
    provider, account_name: str, amount: float, tipo: str, is_reversal: bool = False
) -> None:
    df_cuentas = provider.get_sheet("Cuentas_Metodos")
    if df_cuentas.empty or "Cuenta" not in df_cuentas.columns:
        return

    sign = -1 if tipo in ["Gasto", "Ahorro", "Pago de deuda"] else 1
    if is_reversal:
        sign *= -1

    for idx, row in df_cuentas.iterrows():
        if str(row["Cuenta"]).strip() == str(account_name).strip():
            try:
                curr_balance = float(row.get("Saldo actual", 0.0) or 0.0)
            except Exception:
                curr_balance = 0.0
            new_balance = curr_balance + (sign * amount)
            df_cuentas.at[idx, "Saldo actual"] = round(new_balance, 2)
            break

    try:
        provider.save_sheet("Cuentas_Metodos", df_cuentas)
    except Exception:
        pass
