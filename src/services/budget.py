"""
Servicio de Presupuesto, Regla 50/30/20 y Proyecciones.
Soporta variantes con y sin tildes en encabezados de columnas.
"""
from calendar import monthrange
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


def _find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def get_month_str(d: Optional[date] = None) -> str:
    dt = d or date.today()
    return f"{dt.year:04d}-{dt.month:02d}"


def get_budget_vs_actual(
    provider, target_month: str
) -> pd.DataFrame:
    df_pres = provider.get_sheet("Presupuesto")
    df_movs = provider.get_sheet("Movimientos")
    df_cats = provider.get_sheet("Categorias")
    if df_cats.empty:
        df_cats = provider.get_sheet("Categorías")

    cat_col_mov = _find_col(df_movs, ["Categoria", "Categoría"]) or "Categoria"
    cat_col_pres = _find_col(df_pres, ["Categoria", "Categoría"]) or "Categoria"
    cat_col_cat = _find_col(df_cats, ["Categoria", "Categoría"]) or "Categoria"
    pres_val_col = _find_col(df_pres, ["Monto Presupuestado", "Presupuesto"]) or "Monto Presupuestado"

    # Filtrar presupuesto del mes
    if not df_pres.empty and "Mes" in df_pres.columns:
        pres_m = df_pres[df_pres["Mes"] == target_month].copy()
    else:
        pres_m = pd.DataFrame(columns=["Mes", cat_col_pres, pres_val_col])

    # Filtrar gastos del mes
    if not df_movs.empty and "Fecha" in df_movs.columns:
        movs_m = df_movs[
            (df_movs["Fecha"].astype(str).str.startswith(target_month)) &
            (df_movs["Tipo"] == "Gasto")
        ].copy()
    else:
        movs_m = pd.DataFrame(columns=[cat_col_mov, "Monto"])

    if not movs_m.empty and cat_col_mov in movs_m.columns:
        movs_m["Monto"] = pd.to_numeric(movs_m["Monto"], errors="coerce").fillna(0.0)
        actual_by_cat = movs_m.groupby(cat_col_mov)["Monto"].sum().reset_index()
        actual_by_cat = actual_by_cat.rename(columns={cat_col_mov: "Categoria", "Monto": "Gasto_Real"})
    else:
        actual_by_cat = pd.DataFrame(columns=["Categoria", "Gasto_Real"])

    all_cats = []
    if not df_cats.empty and cat_col_cat in df_cats.columns:
        all_cats = sorted(df_cats[cat_col_cat].dropna().unique().tolist())
    elif not pres_m.empty and cat_col_pres in pres_m.columns:
        all_cats = sorted(pres_m[cat_col_pres].dropna().unique().tolist())

    records = []
    for cat in all_cats:
        pres_val = 0.0
        if not pres_m.empty and cat_col_pres in pres_m.columns and cat in pres_m[cat_col_pres].values:
            pres_val = float(pres_m[pres_m[cat_col_pres] == cat][pres_val_col].iloc[0] or 0.0)

        real_val = 0.0
        if not actual_by_cat.empty and cat in actual_by_cat["Categoria"].values:
            real_val = float(actual_by_cat[actual_by_cat["Categoria"] == cat]["Gasto_Real"].iloc[0] or 0.0)

        diff = pres_val - real_val
        pct = (real_val / pres_val * 100.0) if pres_val > 0 else (100.0 if real_val > 0 else 0.0)

        if pres_val == 0 and real_val > 0:
            estado = "SIN_PRESUPUESTO"
        elif pct > 100.0:
            estado = "EXCEDIDO"
        elif pct >= 80.0:
            estado = "ALERTA"
        else:
            estado = "OK"

        records.append({
            "Categoria": cat,
            "Presupuesto": pres_val,
            "Gasto_Real": real_val,
            "Diferencia": diff,
            "Pct_Ejecucion": pct,
            "Estado": estado,
        })

    return pd.DataFrame(records)


def calculate_50_30_20(
    provider, target_month: str
) -> Dict[str, Any]:
    df_movs = provider.get_sheet("Movimientos")
    df_cats = provider.get_sheet("Categorias")
    if df_cats.empty:
        df_cats = provider.get_sheet("Categorías")

    result = {
        "Ingresos_Totales": 0.0,
        "Necesidades_Monto": 0.0,
        "Necesidades_Pct": 0.0,
        "Deseos_Monto": 0.0,
        "Deseos_Pct": 0.0,
        "Ahorro_Monto": 0.0,
        "Ahorro_Pct": 0.0,
        "Total_Distribuido": 0.0,
    }

    if df_movs.empty or "Fecha" not in df_movs.columns:
        return result

    df_m = df_movs[df_movs["Fecha"].astype(str).str.startswith(target_month)].copy()
    if df_m.empty:
        return result

    cat_col_mov = _find_col(df_m, ["Categoria", "Categoría"]) or "Categoria"
    cat_col_cat = _find_col(df_cats, ["Categoria", "Categoría"]) or "Categoria"
    clasif_col = _find_col(df_cats, ["Clasificacion 50/30/20", "Clasificación 50/30/20"]) or "Clasificacion 50/30/20"

    df_m["Monto"] = pd.to_numeric(df_m["Monto"], errors="coerce").fillna(0.0)
    ingresos = df_m[df_m["Tipo"] == "Ingreso"]["Monto"].sum()
    result["Ingresos_Totales"] = float(ingresos)

    cat_map = {}
    if not df_cats.empty and cat_col_cat in df_cats.columns and clasif_col in df_cats.columns:
        for _, r in df_cats.iterrows():
            cat = str(r[cat_col_cat]).strip()
            clasif = str(r[clasif_col]).strip().capitalize()
            cat_map[cat] = clasif

    nec = 0.0
    des = 0.0
    aho = 0.0

    for _, r in df_m.iterrows():
        tipo = str(r.get("Tipo", ""))
        cat = str(r.get(cat_col_mov, "")).strip()
        monto = float(r.get("Monto", 0.0))

        if tipo == "Ahorro":
            aho += monto
        elif tipo == "Pago de deuda":
            nec += monto
        elif tipo == "Gasto":
            clasif = cat_map.get(cat, "Deseo")
            if clasif == "Necesidad":
                nec += monto
            elif clasif == "Ahorro":
                aho += monto
            else:
                des += monto

    total_dist = nec + des + aho
    result["Necesidades_Monto"] = nec
    result["Deseos_Monto"] = des
    result["Ahorro_Monto"] = aho
    result["Total_Distribuido"] = total_dist

    base = ingresos if ingresos > 0 else total_dist
    if base > 0:
        result["Necesidades_Pct"] = round(nec / base * 100.0, 1)
        result["Deseos_Pct"] = round(des / base * 100.0, 1)
        result["Ahorro_Pct"] = round(aho / base * 100.0, 1)

    return result


def get_budget_pace_projection(
    provider, target_month: str
) -> Dict[str, Any]:
    y, m = int(target_month.split("-")[0]), int(target_month.split("-")[1])
    _, days_in_month = monthrange(y, m)
    today = date.today()

    if today.year == y and today.month == m:
        current_day = min(today.day, days_in_month)
    elif today > date(y, m, days_in_month):
        current_day = days_in_month
    else:
        current_day = 1

    df_bva = get_budget_vs_actual(provider, target_month)
    total_budget = df_bva["Presupuesto"].sum()
    total_spent = df_bva["Gasto_Real"].sum()

    ideal_daily_burn = total_budget / days_in_month if days_in_month > 0 else 0.0
    actual_daily_burn = total_spent / current_day if current_day > 0 else 0.0

    projected_total = actual_daily_burn * days_in_month
    projected_diff = total_budget - projected_total

    exhaustion_day = None
    if actual_daily_burn > 0 and total_budget > 0:
        day_float = total_budget / actual_daily_burn
        if day_float <= days_in_month:
            exhaustion_day = int(day_float)

    return {
        "Dias_En_Mes": days_in_month,
        "Dia_Actual": current_day,
        "Presupuesto_Total": total_budget,
        "Gasto_Actual": total_spent,
        "Ritmo_Diario_Ideal": ideal_daily_burn,
        "Ritmo_Diario_Real": actual_daily_burn,
        "Gasto_Proyectado_Fin_Mes": projected_total,
        "Diferencia_Proyectada": projected_diff,
        "Dia_Agotamiento_Estimado": exhaustion_day,
    }


def copy_previous_month_budget(provider, source_month: str, target_month: str) -> Tuple[bool, str]:
    df_pres = provider.get_sheet("Presupuesto")
    if df_pres.empty or "Mes" not in df_pres.columns:
        return False, "No hay datos de presupuesto registrados para copiar."

    cat_col = _find_col(df_pres, ["Categoria", "Categoría"]) or "Categoria"
    val_col = _find_col(df_pres, ["Monto Presupuestado", "Presupuesto"]) or "Monto Presupuestado"

    source_data = df_pres[df_pres["Mes"] == source_month]
    if source_data.empty:
        return False, f"El mes de origen {source_month} no tiene presupuesto asignado."

    existing_in_target = set(df_pres[df_pres["Mes"] == target_month][cat_col].tolist())
    to_add = []
    for _, r in source_data.iterrows():
        cat = r[cat_col]
        if cat not in existing_in_target:
            to_add.append({
                "Mes": target_month,
                cat_col: cat,
                val_col: r[val_col]
            })

    if not to_add:
        return True, f"El mes {target_month} ya cuenta con todas las categorias de {source_month}."

    for item in to_add:
        provider.append_row("Presupuesto", item)

    return True, f"Se copiaron {len(to_add)} categorias a {target_month}."


def suggest_budget_from_history(provider, target_month: str) -> Dict[str, float]:
    df_movs = provider.get_sheet("Movimientos")
    if df_movs.empty or "Fecha" not in df_movs.columns:
        return {}

    cat_col = _find_col(df_movs, ["Categoria", "Categoría"]) or "Categoria"

    y, m = int(target_month.split("-")[0]), int(target_month.split("-")[1])
    past_months = []
    for i in range(1, 4):
        pm = m - i
        py = y
        if pm <= 0:
            pm += 12
            py -= 1
        past_months.append(f"{py:04d}-{pm:02d}")

    df_past = df_movs[
        (df_movs["Tipo"] == "Gasto") &
        (df_movs["Fecha"].astype(str).str[:7].isin(past_months))
    ].copy()

    if df_past.empty:
        return {}

    df_past["Monto"] = pd.to_numeric(df_past["Monto"], errors="coerce").fillna(0.0)
    grouped = df_past.groupby([cat_col, df_past["Fecha"].astype(str).str[:7]])["Monto"].sum().reset_index()
    avg_by_cat = grouped.groupby(cat_col)["Monto"].mean().round(2).to_dict()

    return avg_by_cat
