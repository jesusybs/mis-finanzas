"""
Vista 5: Analisis y Reportes (Responsivo y Minimalista B/N).
"""
from datetime import date
import streamlit as st
import pandas as pd
from src.services.budget import get_budget_vs_actual, calculate_50_30_20
from src.ui.charts import (
    chart_monthly_evolution, chart_waterfall, chart_expense_treemap,
    chart_top_merchants, chart_dow_heatmap
)
from src.utils.exports import generate_monthly_closing_html
from src.utils.formatting import format_currency


def render_view(provider):
    st.subheader("Analisis y Reportes")

    df_movs = provider.get_sheet("Movimientos")
    if df_movs.empty:
        st.info("No hay datos de movimientos para analizar.")
        return

    raw_m = df_movs["Fecha"].astype(str).str[:7].dropna().unique().tolist()
    available_months = sorted([m for m in raw_m if len(m) == 7], reverse=True)
    today = date.today()
    cur_m = f"{today.year:04d}-{today.month:02d}"
    if cur_m not in available_months:
        available_months.insert(0, cur_m)

    col_m, col_rep = st.columns([1, 1])
    with col_m:
        sel_month = st.selectbox("Periodo a evaluar", options=available_months, index=0)
    with col_rep:
        html_report = generate_monthly_closing_html(provider, sel_month)
        st.download_button(
            "Descargar Informe (HTML / PDF)",
            data=html_report,
            file_name=f"informe_{sel_month}.html",
            mime="text/html",
            use_container_width=True,
        )

    bva = get_budget_vs_actual(provider, sel_month)
    dist = calculate_50_30_20(provider, sel_month)
    chart_config = {"displayModeBar": False, "responsive": True}

    st.write("**Tendencia Anual y Flujo**")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_monthly_evolution(df_movs), use_container_width=True, config=chart_config)
    with c2:
        st.plotly_chart(chart_waterfall(dist["Ingresos_Totales"], bva, dist["Ahorro_Monto"]), use_container_width=True, config=chart_config)

    st.markdown("---")
    st.write("**Distribucion y Concentracion**")
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(chart_expense_treemap(df_movs, sel_month), use_container_width=True, config=chart_config)
    with c4:
        st.plotly_chart(chart_top_merchants(df_movs, sel_month), use_container_width=True, config=chart_config)

    st.markdown("---")
    st.write("**Comportamiento por Dia y Mayores Gastos**")
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(chart_dow_heatmap(df_movs, sel_month), use_container_width=True, config=chart_config)
    with c6:
        st.write("Top Gastos Individuales")
        cat_col = "Categoria" if "Categoria" in df_movs.columns else "Categoría"
        desc_col = "Descripcion" if "Descripcion" in df_movs.columns else "Descripción"
        df_m = df_movs[
            (df_movs["Fecha"].astype(str).str.startswith(sel_month)) &
            (df_movs["Tipo"] == "Gasto")
        ].copy()
        if not df_m.empty:
            df_m["Monto_num"] = pd.to_numeric(df_m["Monto"], errors="coerce").fillna(0.0)
            top_singles = df_m.sort_values(by="Monto_num", ascending=False).head(8)
            top_display = top_singles[["Fecha", desc_col, "Comercio/Lugar", cat_col, "Monto_num"]].copy()
            top_display["Monto"] = top_display["Monto_num"].apply(format_currency)
            st.dataframe(top_display[["Fecha", desc_col, "Comercio/Lugar", cat_col, "Monto"]], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.write("**Matriz Anual (Categoria x Mes)**")
    cat_col_mov = "Categoria" if "Categoria" in df_movs.columns else "Categoría"
    df_all_gastos = df_movs[df_movs["Tipo"] == "Gasto"].copy()
    if not df_all_gastos.empty:
        df_all_gastos["Monto"] = pd.to_numeric(df_all_gastos["Monto"], errors="coerce").fillna(0.0)
        df_all_gastos["Mes"] = df_all_gastos["Fecha"].astype(str).str[:7]
        matriz = df_all_gastos.pivot_table(index=cat_col_mov, columns="Mes", values="Monto", aggfunc="sum", fill_value=0.0)
        st.dataframe(matriz.style.format(format_currency), use_container_width=True)
