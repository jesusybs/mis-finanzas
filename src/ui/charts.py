"""
Modulo de Graficos Plotly Responsivos en Estilo Minimalista (B/N y Escala de Grises).
Optimizados para renderizarse sin desbordamientos en cualquier tamano de pantalla.
"""
from calendar import monthrange
from datetime import date
from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.config import load_config

PLOT_TEMPLATE = "plotly_white"
COLOR_BLACK = "#18181B"
COLOR_DARK_GREY = "#52525B"
COLOR_MID_GREY = "#A1A1AA"
COLOR_LIGHT_GREY = "#F4F4F5"


def _get_currency_symbol() -> str:
    cfg = load_config()
    return cfg.get("general", {}).get("currency_symbol", "$")


def chart_budget_vs_actual(df_bva: pd.DataFrame) -> go.Figure:
    sym = _get_currency_symbol()
    if df_bva.empty:
        return go.Figure()

    df_sorted = df_bva.sort_values(by="Presupuesto", ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_sorted["Categoria"],
        x=df_sorted["Presupuesto"],
        name="Presupuesto",
        orientation="h",
        marker=dict(color=COLOR_LIGHT_GREY, line=dict(color=COLOR_MID_GREY, width=1)),
        hovertemplate="<b>%{y}</b><br>Plan: " + sym + " %{x:,.2f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        y=df_sorted["Categoria"],
        x=df_sorted["Gasto_Real"],
        name="Real",
        orientation="h",
        marker=dict(color=COLOR_BLACK),
        hovertemplate="<b>%{y}</b><br>Real: " + sym + " %{x:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="group",
        title=dict(text="<b>Presupuesto vs. Real</b>", font=dict(size=13, color=COLOR_BLACK)),
        xaxis=dict(title="", tickformat=",.0f"),
        yaxis=dict(title="", tickfont=dict(size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=380,
    )
    return fig


def chart_expense_donut(df_movs: pd.DataFrame, target_month: str) -> go.Figure:
    sym = _get_currency_symbol()
    if df_movs.empty:
        return go.Figure()

    cat_col = "Categoria" if "Categoria" in df_movs.columns else "Categoría"
    df_m = df_movs[
        (df_movs["Fecha"].astype(str).str.startswith(target_month)) &
        (df_movs["Tipo"] == "Gasto")
    ].copy()
    if df_m.empty:
        return go.Figure()

    df_m["Monto"] = pd.to_numeric(df_m["Monto"], errors="coerce").fillna(0.0)
    grouped = df_m.groupby(cat_col)["Monto"].sum().reset_index()
    grouped = grouped[grouped["Monto"] > 0]

    greys = ["#18181B", "#3F3F46", "#52525B", "#71717A", "#A1A1AA", "#D4D4D8", "#E4E4E7"]

    fig = px.pie(
        grouped,
        names=cat_col,
        values="Monto",
        hole=0.6,
        color_discrete_sequence=greys,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Monto: " + sym + " %{value:,.2f}<extra></extra>"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text="<b>Distribucion de Gastos</b>", font=dict(size=13, color=COLOR_BLACK)),
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
        height=380,
    )
    return fig


def chart_expense_treemap(df_movs: pd.DataFrame, target_month: str) -> go.Figure:
    sym = _get_currency_symbol()
    if df_movs.empty:
        return go.Figure()

    cat_col = "Categoria" if "Categoria" in df_movs.columns else "Categoría"
    sub_col = "Subcategoria" if "Subcategoria" in df_movs.columns else "Subcategoría"

    df_m = df_movs[
        (df_movs["Fecha"].astype(str).str.startswith(target_month)) &
        (df_movs["Tipo"] == "Gasto")
    ].copy()
    if df_m.empty:
        return go.Figure()

    df_m["Monto"] = pd.to_numeric(df_m["Monto"], errors="coerce").fillna(0.0)
    df_m[sub_col] = df_m[sub_col].fillna("General").replace("", "General")
    grouped = df_m.groupby([cat_col, sub_col])["Monto"].sum().reset_index()

    fig = px.treemap(
        grouped,
        path=[cat_col, sub_col],
        values="Monto",
        color="Monto",
        color_continuous_scale="Greys",
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Total: " + sym + " %{value:,.2f}<extra></extra>"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text="<b>Desglose por Categoria y Subcategoria</b>", font=dict(size=13, color=COLOR_BLACK)),
        margin=dict(l=5, r=5, t=40, b=5),
        height=380,
    )
    return fig


def chart_monthly_evolution(df_movs: pd.DataFrame) -> go.Figure:
    sym = _get_currency_symbol()
    if df_movs.empty or "Fecha" not in df_movs.columns:
        return go.Figure()

    df = df_movs.copy()
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0.0)
    df["Mes"] = df["Fecha"].astype(str).str[:7]

    pivot = df.pivot_table(index="Mes", columns="Tipo", values="Monto", aggfunc="sum", fill_value=0.0)
    pivot = pivot.tail(12)

    fig = go.Figure()
    if "Ingreso" in pivot.columns:
        fig.add_trace(go.Scatter(
            x=pivot.index, y=pivot["Ingreso"], name="Ingresos", mode="lines+markers",
            line=dict(color=COLOR_BLACK, width=2.5),
            hovertemplate="Ingresos: " + sym + " %{y:,.2f}<extra></extra>"
        ))
    if "Gasto" in pivot.columns:
        fig.add_trace(go.Scatter(
            x=pivot.index, y=pivot["Gasto"], name="Gastos", mode="lines+markers",
            line=dict(color=COLOR_DARK_GREY, width=2, dash="dash"),
            hovertemplate="Gastos: " + sym + " %{y:,.2f}<extra></extra>"
        ))
    if "Ahorro" in pivot.columns:
        fig.add_trace(go.Scatter(
            x=pivot.index, y=pivot["Ahorro"], name="Ahorro", mode="lines+markers",
            line=dict(color=COLOR_MID_GREY, width=1.5, dash="dot"),
            hovertemplate="Ahorro: " + sym + " %{y:,.2f}<extra></extra>"
        ))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text="<b>Evolucion Mensual (12 Meses)</b>", font=dict(size=13, color=COLOR_BLACK)),
        xaxis=dict(title="", tickfont=dict(size=10)),
        yaxis=dict(title="", tickformat=",.0f", tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=360,
    )
    return fig


def chart_budget_pace_curve(df_movs: pd.DataFrame, target_month: str, total_budget: float) -> go.Figure:
    sym = _get_currency_symbol()
    y, m = int(target_month.split("-")[0]), int(target_month.split("-")[1])
    _, days_in_month = monthrange(y, m)
    today = date.today()

    df_m = df_movs[
        (df_movs["Fecha"].astype(str).str.startswith(target_month)) &
        (df_movs["Tipo"] == "Gasto")
    ].copy()

    daily_spend = {d: 0.0 for d in range(1, days_in_month + 1)}
    for _, r in df_m.iterrows():
        try:
            d_int = int(str(r["Fecha"])[8:10])
            daily_spend[d_int] += float(r.get("Monto", 0.0))
        except Exception:
            continue

    days = list(range(1, days_in_month + 1))
    accum_actual = []
    running = 0.0
    cutoff_day = today.day if (today.year == y and today.month == m) else (days_in_month if today > date(y, m, days_in_month) else 1)

    for d in days:
        if d <= cutoff_day:
            running += daily_spend[d]
            accum_actual.append(running)
        else:
            accum_actual.append(None)

    ideal_line = [(total_budget / days_in_month) * d for d in days]
    current_spent = running
    daily_pace = current_spent / max(1, cutoff_day)
    projected_line = [(daily_pace * d) for d in days]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=days, y=ideal_line, name="Presupuesto Lineal", mode="lines",
        line=dict(color=COLOR_MID_GREY, dash="dot", width=1.5),
        hovertemplate="Ideal Dia %{x}: " + sym + " %{y:,.2f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=days, y=projected_line, name="Proyeccion Ritmo", mode="lines",
        line=dict(color=COLOR_DARK_GREY, dash="dash", width=1.5),
        hovertemplate="Proyectado Dia %{x}: " + sym + " %{y:,.2f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=days[:cutoff_day], y=accum_actual[:cutoff_day], name="Gasto Real", mode="lines+markers",
        line=dict(color=COLOR_BLACK, width=2.5),
        hovertemplate="Real Dia %{x}: " + sym + " %{y:,.2f}<extra></extra>"
    ))

    fig.add_hline(y=total_budget, line_dash="solid", line_color="#000000", annotation_text=f"Limite: {sym} {total_budget:,.2f}")

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text="<b>Ritmo de Gasto Acumulado</b>", font=dict(size=13, color=COLOR_BLACK)),
        xaxis=dict(title="Dia del Mes", dtick=4, tickfont=dict(size=10)),
        yaxis=dict(title="", tickformat=",.0f", tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=360,
    )
    return fig


def chart_waterfall(ingresos: float, df_bva: pd.DataFrame, ahorros: float) -> go.Figure:
    sym = _get_currency_symbol()
    x_labels = ["Ingresos"]
    y_vals = [ingresos]
    measures = ["absolute"]

    cat_col = "Categoria" if "Categoria" in df_bva.columns else "Categoría"

    if not df_bva.empty:
        top_cats = df_bva.sort_values(by="Gasto_Real", ascending=False).head(5)
        for _, r in top_cats.iterrows():
            if r["Gasto_Real"] > 0:
                x_labels.append(r[cat_col][:12])
                y_vals.append(-r["Gasto_Real"])
                measures.append("relative")

    if ahorros > 0:
        x_labels.append("Ahorro")
        y_vals.append(-ahorros)
        measures.append("relative")

    x_labels.append("Saldo")
    y_vals.append(0)
    measures.append("total")

    fig = go.Figure(go.Waterfall(
        name="Flujo",
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_vals,
        connector=dict(line=dict(color=COLOR_MID_GREY)),
        decreasing=dict(marker=dict(color=COLOR_DARK_GREY)),
        increasing=dict(marker=dict(color=COLOR_LIGHT_GREY, line=dict(color=COLOR_BLACK, width=1))),
        totals=dict(marker=dict(color=COLOR_BLACK)),
        hovertemplate="<b>%{x}</b><br>Monto: " + sym + " %{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text="<b>Flujo en Cascada</b>", font=dict(size=13, color=COLOR_BLACK)),
        yaxis=dict(title="", tickformat=",.0f", tickfont=dict(size=10)),
        xaxis=dict(tickfont=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=360,
    )
    return fig


def chart_top_merchants(df_movs: pd.DataFrame, target_month: str) -> go.Figure:
    sym = _get_currency_symbol()
    df_m = df_movs[
        (df_movs["Fecha"].astype(str).str.startswith(target_month)) &
        (df_movs["Tipo"] == "Gasto")
    ].copy()
    if df_m.empty:
        return go.Figure()

    df_m["Monto"] = pd.to_numeric(df_m["Monto"], errors="coerce").fillna(0.0)
    df_m["Comercio/Lugar"] = df_m["Comercio/Lugar"].fillna("Sin especificar").replace("", "Sin especificar")
    top = df_m.groupby("Comercio/Lugar")["Monto"].sum().sort_values(ascending=True).tail(8)

    fig = go.Figure(go.Bar(
        x=top.values,
        y=top.index,
        orientation="h",
        marker=dict(color=COLOR_DARK_GREY),
        hovertemplate="<b>%{y}</b><br>Gasto: " + sym + " %{x:,.2f}<extra></extra>"
    ))
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text="<b>Top Comercios</b>", font=dict(size=13, color=COLOR_BLACK)),
        xaxis=dict(title="", tickformat=",.0f", tickfont=dict(size=10)),
        yaxis=dict(title="", tickfont=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=360,
    )
    return fig


def chart_dow_heatmap(df_movs: pd.DataFrame, target_month: str) -> go.Figure:
    sym = _get_currency_symbol()
    df_m = df_movs[
        (df_movs["Fecha"].astype(str).str.startswith(target_month)) &
        (df_movs["Tipo"] == "Gasto")
    ].copy()
    if df_m.empty:
        return go.Figure()

    df_m["Fecha_dt"] = pd.to_datetime(df_m["Fecha"], errors="coerce")
    df_m["DiaSemana"] = df_m["Fecha_dt"].dt.day_name()
    df_m["Monto"] = pd.to_numeric(df_m["Monto"], errors="coerce").fillna(0.0)

    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_es = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
    dow_map = dict(zip(dow_order, dow_es))

    grouped = df_m.groupby("DiaSemana")["Monto"].sum().reindex(dow_order).fillna(0.0)
    labels = [dow_map[d] for d in dow_order]

    fig = go.Figure(go.Bar(
        x=labels,
        y=grouped.values,
        marker=dict(color=COLOR_BLACK),
        hovertemplate="<b>%{x}</b><br>Total: " + sym + " %{y:,.2f}<extra></extra>"
    ))
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text="<b>Gasto por Dia de la Semana</b>", font=dict(size=13, color=COLOR_BLACK)),
        xaxis=dict(title="", tickfont=dict(size=10)),
        yaxis=dict(title="", tickformat=",.0f", tickfont=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=340,
    )
    return fig


def chart_50_30_20_bars(dist: Dict[str, Any]) -> go.Figure:
    categories = ["Necesidad", "Deseo", "Ahorro"]
    ideal_pct = [50.0, 30.0, 20.0]
    actual_pct = [dist["Necesidades_Pct"], dist["Deseos_Pct"], dist["Ahorro_Pct"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Meta",
        x=categories,
        y=ideal_pct,
        marker=dict(color=COLOR_LIGHT_GREY, line=dict(color=COLOR_MID_GREY, width=1)),
        hovertemplate="Meta: %{y:.1f}%<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Real",
        x=categories,
        y=actual_pct,
        marker=dict(color=COLOR_BLACK),
        hovertemplate="Real: %{y:.1f}%<extra></extra>"
    ))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="group",
        title=dict(text="<b>Regla 50/30/20</b>", font=dict(size=13, color=COLOR_BLACK)),
        yaxis=dict(title="", ticksuffix="%", tickfont=dict(size=10)),
        xaxis=dict(tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=340,
    )
    return fig
