"""
Motor de Insights Financieros y Diagnostico de Salud Financiera (0 a 100).
Formato sobrio y analitico, sin emojis, compatible con variantes de encabezados.
"""
from datetime import date
from typing import Any, Dict, List
import pandas as pd
from src.config import load_config
from src.services.budget import get_budget_vs_actual, get_budget_pace_projection
from src.utils.formatting import format_currency, format_pct


def compute_financial_health_score(
    provider, target_month: str
) -> Dict[str, Any]:
    df_movs = provider.get_sheet("Movimientos")
    df_cuentas = provider.get_sheet("Cuentas_Metodos")
    df_deudas = provider.get_sheet("Deudas")
    bva = get_budget_vs_actual(provider, target_month)

    ingresos = 0.0
    gastos = 0.0
    ahorros = 0.0
    if not df_movs.empty and "Fecha" in df_movs.columns:
        m_movs = df_movs[df_movs["Fecha"].astype(str).str.startswith(target_month)]
        if not m_movs.empty:
            m_movs["Monto_num"] = pd.to_numeric(m_movs["Monto"], errors="coerce").fillna(0.0)
            ingresos = m_movs[m_movs["Tipo"] == "Ingreso"]["Monto_num"].sum()
            gastos = m_movs[m_movs["Tipo"] == "Gasto"]["Monto_num"].sum()
            ahorros = m_movs[m_movs["Tipo"] == "Ahorro"]["Monto_num"].sum()

    ahorro_rate = (ahorros / ingresos) if ingresos > 0 else 0.0
    pilar_ahorro = min(25.0, max(0.0, (ahorro_rate / 0.20) * 25.0))

    pilar_presupuesto = 35.0
    if not bva.empty:
        cats_con_pres = bva[bva["Presupuesto"] > 0]
        if not cats_con_pres.empty:
            excedidas = cats_con_pres[cats_con_pres["Pct_Ejecucion"] > 100.0]
            alertas = cats_con_pres[(cats_con_pres["Pct_Ejecucion"] >= 80.0) & (cats_con_pres["Pct_Ejecucion"] <= 100.0)]
            penalizacion = (len(excedidas) * 10.0) + (len(alertas) * 3.0)
            pilar_presupuesto = max(0.0, 35.0 - penalizacion)

    cuotas_deuda = 0.0
    if not df_deudas.empty and "Cuota mensual" in df_deudas.columns:
        cuotas_deuda = pd.to_numeric(df_deudas["Cuota mensual"], errors="coerce").fillna(0.0).sum()

    ratio_deuda = (cuotas_deuda / ingresos) if ingresos > 0 else 0.0
    if ratio_deuda <= 0.15:
        pilar_deuda = 25.0
    elif ratio_deuda <= 0.30:
        pilar_deuda = 20.0
    elif ratio_deuda <= 0.45:
        pilar_deuda = 10.0
    else:
        pilar_deuda = 0.0

    saldo_liquido = 0.0
    if not df_cuentas.empty and "Saldo actual" in df_cuentas.columns:
        saldos = pd.to_numeric(df_cuentas["Saldo actual"], errors="coerce").fillna(0.0)
        saldo_liquido = saldos[saldos > 0].sum()

    meses_cobertura = (saldo_liquido / gastos) if gastos > 0 else 0.0
    pilar_fondo = min(15.0, max(0.0, (meses_cobertura / 3.0) * 15.0))

    score_total = int(round(pilar_ahorro + pilar_presupuesto + pilar_deuda + pilar_fondo))

    if score_total >= 85:
        nivel = "Excelente"
        mensaje = "Gestion optima. Mantiene margen positivo en presupuesto y ahorro continuo."
    elif score_total >= 70:
        nivel = "Bueno"
        mensaje = "Buen control general. Capacidad de ajuste en rubros variables."
    elif score_total >= 50:
        nivel = "Regular"
        mensaje = "Atencion: Ciertas partidas superan el presupuesto o la deuda reduce liquidez."
    else:
        nivel = "Critico"
        mensaje = "Alerta: Gastos cercanos o superiores a ingresos. Se sugiere ajuste presupuestario."

    return {
        "Score_Total": score_total,
        "Nivel": nivel,
        "Mensaje": mensaje,
        "Color": "#111827",
        "Desglose": {
            "Ahorro": {"Puntos": round(pilar_ahorro, 1), "Max": 25, "Tasa_Real": format_pct(ahorro_rate * 100)},
            "Presupuesto": {"Puntos": round(pilar_presupuesto, 1), "Max": 35, "Detalle": "Desviacion por categoria"},
            "Deudas": {"Puntos": round(pilar_deuda, 1), "Max": 25, "Ratio": format_pct(ratio_deuda * 100)},
            "Fondo_Emergencia": {"Puntos": round(pilar_fondo, 1), "Max": 15, "Meses_Cobertura": f"{meses_cobertura:.1f} meses"},
        }
    }


def generate_automated_insights(
    provider, target_month: str
) -> List[Dict[str, str]]:
    insights = []
    cfg = load_config()
    hormiga_umbral = float(cfg.get("general", {}).get("gastos_hormiga_umbral", 15.0))

    df_movs = provider.get_sheet("Movimientos")
    bva = get_budget_vs_actual(provider, target_month)
    pace = get_budget_pace_projection(provider, target_month)

    if df_movs.empty:
        return insights

    cat_col_mov = "Categoria" if "Categoria" in df_movs.columns else ("Categoría" if "Categoría" in df_movs.columns else df_movs.columns[3])

    df_m = df_movs[
        (df_movs["Fecha"].astype(str).str.startswith(target_month)) &
        (df_movs["Tipo"] == "Gasto")
    ].copy()
    if df_m.empty:
        return insights

    df_m["Monto_num"] = pd.to_numeric(df_m["Monto"], errors="coerce").fillna(0.0)
    total_gasto_mes = df_m["Monto_num"].sum()

    cat_bva_col = "Categoria" if "Categoria" in bva.columns else "Categoría"

    if not bva.empty:
        excedidas = bva[bva["Estado"] == "EXCEDIDO"]
        for _, row in excedidas.iterrows():
            cat = row[cat_bva_col]
            real = row["Gasto_Real"]
            pres = row["Presupuesto"]
            diff = abs(row["Diferencia"])
            pct = row["Pct_Ejecucion"]
            insights.append({
                "tipo": "alerta",
                "icono": "",
                "titulo": f"Presupuesto excedido en {cat}",
                "mensaje": (
                    f"Gasto real {format_currency(real)} frente a {format_currency(pres)} presupuestados "
                    f"({pct:.1f}%). Diferencia: {format_currency(diff)}."
                ),
            })

    if pace["Dia_Agotamiento_Estimado"] and pace["Dia_Agotamiento_Estimado"] <= pace["Dias_En_Mes"]:
        dia_ag = pace["Dia_Agotamiento_Estimado"]
        insights.append({
            "tipo": "alerta",
            "icono": "",
            "titulo": "Proyeccion de agotamiento de presupuesto",
            "mensaje": (
                f"Al ritmo diario promedio ({format_currency(pace['Ritmo_Diario_Real'])}/dia), "
                f"el presupuesto total se alcanzaria el dia {dia_ag} del mes. "
                f"Gasto proyectado a fin de mes: {format_currency(pace['Gasto_Proyectado_Fin_Mes'])}."
            ),
        })

    hormigas = df_m[df_m["Monto_num"] <= hormiga_umbral]
    if not hormigas.empty:
        total_hormiga = hormigas["Monto_num"].sum()
        pct_hormiga = (total_hormiga / total_gasto_mes * 100.0) if total_gasto_mes > 0 else 0.0
        cant_hormiga = len(hormigas)
        if total_hormiga > 30:
            insights.append({
                "tipo": "info",
                "icono": "",
                "titulo": "Gastos menores acumulados",
                "mensaje": (
                    f"Se registran {cant_hormiga} transacciones menores a {format_currency(hormiga_umbral)}, "
                    f"que suman {format_currency(total_hormiga)} ({pct_hormiga:.1f}% del total del mes)."
                ),
            })

    df_cats = provider.get_sheet("Categorias")
    if df_cats.empty:
        df_cats = provider.get_sheet("Categorías")

    cat_col_cat = "Categoria" if "Categoria" in df_cats.columns else "Categoría"
    if not df_cats.empty and "Tipo de gasto" in df_cats.columns:
        cats_discrecionales = set(
            df_cats[df_cats["Tipo de gasto"] == "Discrecional"][cat_col_cat].dropna().tolist()
        )
        gastos_disc = df_m[df_m[cat_col_mov].isin(cats_discrecionales)]
        if not gastos_disc.empty:
            top_disc = gastos_disc.groupby(cat_col_mov)["Monto_num"].sum().sort_values(ascending=False).head(3)
            sum_top3 = top_disc.sum()
            ahorro_10_anual = (sum_top3 * 0.10) * 12
            nombres = ", ".join(top_disc.index.tolist())
            insights.append({
                "tipo": "info",
                "icono": "",
                "titulo": "Analisis de reduccion del 10% en gastos discrecionales",
                "mensaje": (
                    f"Las 3 principales categorias discrecionales ({nombres}) suman {format_currency(sum_top3)}. "
                    f"Una reduccion del 10% representaria {format_currency(ahorro_10_anual)} al ano."
                ),
            })

    return insights
