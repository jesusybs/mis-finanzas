"""
Vista 1: Dashboard Ejecutivo (Minimalista, Sobrio y 100% Responsivo).
"""
from datetime import date
import streamlit as st
from src.services.budget import get_budget_vs_actual, calculate_50_30_20, get_budget_pace_projection
from src.services.insights import compute_financial_health_score, generate_automated_insights
from src.ui.charts import (
    chart_budget_vs_actual, chart_expense_donut, chart_budget_pace_curve, chart_50_30_20_bars
)
from src.ui.components import render_kpi_grid, render_insight_card
from src.utils.formatting import format_currency, format_pct


def render_view(provider):
    st.subheader("Dashboard Financiero")

    df_movs = provider.get_sheet("Movimientos")
    available_months = []
    if not df_movs.empty and "Fecha" in df_movs.columns:
        raw_m = df_movs["Fecha"].astype(str).str[:7].dropna().unique().tolist()
        available_months = sorted([m for m in raw_m if len(m) == 7], reverse=True)

    today = date.today()
    current_m = f"{today.year:04d}-{today.month:02d}"
    if current_m not in available_months:
        available_months.insert(0, current_m)

    selected_month = st.selectbox("Periodo a evaluar", options=available_months, index=0)

    bva = get_budget_vs_actual(provider, selected_month)
    dist = calculate_50_30_20(provider, selected_month)
    pace = get_budget_pace_projection(provider, selected_month)
    health = compute_financial_health_score(provider, selected_month)
    insights = generate_automated_insights(provider, selected_month)

    total_pres = bva["Presupuesto"].sum() if not bva.empty else 0.0
    total_gasto = bva["Gasto_Real"].sum() if not bva.empty else 0.0
    ingresos = dist["Ingresos_Totales"]
    ahorros = dist["Ahorro_Monto"]
    balance_neto = ingresos - total_gasto - ahorros
    pct_pres_total = (total_gasto / total_pres * 100.0) if total_pres > 0 else 0.0

    # Cuadricula Fluida Responsiva de Tarjetas
    kpi_items = [
        ("Ingresos", format_currency(ingresos), f"Periodo {selected_month}"),
        ("Gastos Reales", format_currency(total_gasto), f"Presupuesto: {format_currency(total_pres)}"),
        ("Ahorro", format_currency(ahorros), f"{format_pct(dist['Ahorro_Pct'])} de ingresos"),
        ("Balance Libre", format_currency(balance_neto), "Ingresos - Gastos - Ahorro"),
        ("Ejecucion Presupuesto", format_pct(pct_pres_total), f"Dia {pace['Dia_Actual']} de {pace['Dias_En_Mes']}"),
    ]
    render_kpi_grid(kpi_items)

    # Diagnostico de Salud y Observaciones
    st.write("**Diagnostico de Flujo**")
    score_col, ins_col = st.columns([1, 2])
    with score_col:
        score_html = (
            f'<div class="kpi-card" style="border-left: 4px solid #18181B; margin-bottom: 0.85rem;">'
            f'<div class="kpi-label">Puntaje Financiero</div>'
            f'<div class="kpi-number">{health["Score_Total"]}<span style="font-size: 0.9rem; font-weight: 500; color: #71717A;"> / 100</span></div>'
            f'<div style="font-size: 0.85rem; font-weight: 600; color: #18181B; margin-top: 0.25rem;">Nivel: {health["Nivel"]}</div>'
            f'<div class="kpi-caption">{health["Mensaje"]}</div>'
            f'</div>'
        )
        st.markdown(score_html, unsafe_allow_html=True)
    with ins_col:
        if insights:
            for ins in insights[:2]:
                render_insight_card(ins["titulo"], ins["mensaje"])
        else:
            st.info("Sin desvios en el presupuesto del periodo.")

    # Graficos Principales (Responsivos con Plotly)
    st.markdown("---")
    st.write("**Analisis Visual**")
    chart_config = {"displayModeBar": False, "responsive": True}

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(chart_budget_vs_actual(bva), use_container_width=True, config=chart_config)
    with g2:
        st.plotly_chart(chart_expense_donut(df_movs, selected_month), use_container_width=True, config=chart_config)

    g3, g4 = st.columns(2)
    with g3:
        st.plotly_chart(chart_budget_pace_curve(df_movs, selected_month, total_pres), use_container_width=True, config=chart_config)
    with g4:
        st.plotly_chart(chart_50_30_20_bars(dist), use_container_width=True, config=chart_config)

    # Detalle de Categorias
    st.markdown("---")
    st.write("**Detalle Presupuestario por Categoria**")
    if not bva.empty:
        display_df = bva.copy()
        display_df["Presupuesto"] = display_df["Presupuesto"].apply(format_currency)
        display_df["Gasto_Real"] = display_df["Gasto_Real"].apply(format_currency)
        display_df["Diferencia"] = display_df["Diferencia"].apply(format_currency)
        display_df["% Ejecucion"] = display_df["Pct_Ejecucion"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(
            display_df[["Categoria", "Presupuesto", "Gasto_Real", "Diferencia", "% Ejecucion", "Estado"]],
            use_container_width=True,
            hide_index=True,
        )
