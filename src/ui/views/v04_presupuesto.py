"""
Vista 4: Editor de Presupuesto (Minimalista B/N).
"""
from datetime import date
import streamlit as st
import pandas as pd
from src.services.budget import (
    get_budget_vs_actual, copy_previous_month_budget, suggest_budget_from_history
)
from src.utils.formatting import format_currency


def render_view(provider):
    st.subheader("Presupuesto Mensual")

    df_pres = provider.get_sheet("Presupuesto")
    df_cats = provider.get_sheet("Categorias")

    all_cats = sorted(df_cats["Categoria"].dropna().unique().tolist()) if not df_cats.empty else ["Vivienda", "Alimentacion", "Transporte"]

    today = date.today()
    default_m = f"{today.year:04d}-{today.month:02d}"

    month_opts = [default_m]
    next_m_val = today.month + 1 if today.month < 12 else 1
    next_y_val = today.year if today.month < 12 else today.year + 1
    month_opts.append(f"{next_y_val:04d}-{next_m_val:02d}")
    if not df_pres.empty and "Mes" in df_pres.columns:
        for m in df_pres["Mes"].dropna().unique():
            if m not in month_opts:
                month_opts.append(str(m))
    month_opts = sorted(list(set(month_opts)), reverse=True)

    col_m, _ = st.columns([2, 4])
    with col_m:
        sel_month = st.selectbox("Mes a presupuestar", options=month_opts, index=0)

    st.write("**Opciones de Carga Rapida**")
    h1, h2, h3 = st.columns(3)

    prev_m_val = today.month - 1 if today.month > 1 else 12
    prev_y_val = today.year if today.month > 1 else today.year - 1
    prev_m_str = f"{prev_y_val:04d}-{prev_m_val:02d}"
    with h1:
        if st.button(f"Copiar Mes Anterior ({prev_m_str})"):
            ok, msg = copy_previous_month_budget(provider, prev_m_str, sel_month)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)

    with h2:
        if st.button("Sugerir por Promedio de 3 Meses"):
            sug_map = suggest_budget_from_history(provider, sel_month)
            if sug_map:
                df_curr = provider.get_sheet("Presupuesto")
                df_curr = df_curr[df_curr["Mes"] != sel_month]
                new_rows = []
                for cat, amount in sug_map.items():
                    new_rows.append({"Mes": sel_month, "Categoria": cat, "Monto Presupuestado": amount})
                df_updated = pd.concat([df_curr, pd.DataFrame(new_rows)], ignore_index=True)
                provider.save_sheet("Presupuesto", df_updated)
                st.success(f"Presupuesto sugerido guardado para {len(new_rows)} categorias.")
                st.rerun()
            else:
                st.info("Sin datos historicos suficientes.")

    with h3:
        with st.popover("Regla 50/30/20"):
            ingreso_ref = st.number_input("Ingreso mensual base", min_value=100.0, value=3000.0, step=100.0)
            st.write(f"- Necesidades (50%): **{format_currency(ingreso_ref * 0.50)}**")
            st.write(f"- Deseos (30%): **{format_currency(ingreso_ref * 0.30)}**")
            st.write(f"- Ahorro (20%): **{format_currency(ingreso_ref * 0.20)}**")

    st.markdown("---")
    st.write(f"**Asignacion de Presupuesto para {sel_month}**")

    bva = get_budget_vs_actual(provider, sel_month)

    with st.form("form_guardar_presupuestos"):
        budget_inputs = {}
        cols_grid = st.columns(3)
        for idx, cat in enumerate(all_cats):
            col_target = cols_grid[idx % 3]
            current_val = 0.0
            if not bva.empty and cat in bva["Categoria"].values:
                current_val = float(bva[bva["Categoria"] == cat]["Presupuesto"].iloc[0] or 0.0)

            with col_target:
                budget_inputs[cat] = st.number_input(
                    f"{cat}",
                    min_value=0.0,
                    value=current_val,
                    step=25.0,
                    key=f"pres_{cat}_{sel_month}"
                )

        btn_guardar_pres = st.form_submit_button("Guardar Presupuesto", type="primary", use_container_width=True)

    if btn_guardar_pres:
        df_p = provider.get_sheet("Presupuesto")
        if not df_p.empty and "Mes" in df_p.columns:
            df_p = df_p[df_p["Mes"] != sel_month]

        nuevas_filas = []
        for cat, val in budget_inputs.items():
            if val > 0:
                nuevas_filas.append({"Mes": sel_month, "Categoria": cat, "Monto Presupuestado": val})

        df_final = pd.concat([df_p, pd.DataFrame(nuevas_filas)], ignore_index=True)
        provider.save_sheet("Presupuesto", df_final)
        st.success("Presupuesto guardado.")
        st.rerun()

    st.markdown("---")
    st.write("**Seguimiento de Ejecucion**")
    if not bva.empty:
        for _, r in bva.iterrows():
            cat = r["Categoria"]
            pres = r["Presupuesto"]
            real = r["Gasto_Real"]
            pct = min(1.0, (real / pres)) if pres > 0 else 0.0
            col_lbl, col_bar, col_vals = st.columns([2, 5, 3])
            with col_lbl:
                st.write(f"**{cat}**")
            with col_bar:
                st.progress(pct)
            with col_vals:
                st.caption(f"{format_currency(real)} de {format_currency(pres)} ({r['Pct_Ejecucion']:.1f}%)")
