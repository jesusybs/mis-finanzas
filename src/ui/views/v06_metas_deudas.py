"""
Vista 6: Metas de Ahorro y Cancelacion de Deudas (Minimalista B/N).
"""
import streamlit as st
import pandas as pd
from src.services.debts_goals import calculate_savings_goals_progress, simulate_debt_payoff
from src.utils.formatting import format_currency


def render_view(provider):
    st.subheader("Metas y Deudas")

    tab_metas, tab_deudas = st.tabs(["Metas de Ahorro", "Estrategias de Pago de Deudas"])

    with tab_metas:
        df_metas = provider.get_sheet("Metas_Ahorro")

        capacidad_ahorro = st.number_input(
            "Capacidad mensual de ahorro destinada a metas",
            min_value=0.0,
            value=300.0,
            step=50.0
        )

        progress_data = calculate_savings_goals_progress(df_metas, capacidad_ahorro)

        if not progress_data:
            st.info("No hay metas de ahorro registradas en la hoja.")
        else:
            for m in progress_data:
                col_info, col_prog = st.columns([2, 3])
                with col_info:
                    st.write(f"**{m['Nombre']}**")
                    st.write(f"Objetivo: {format_currency(m['Objetivo'])} | Acumulado: {format_currency(m['Acumulado'])} ({m['Porcentaje']}%)")
                    st.write(f"Restante: {format_currency(m['Remanente'])}")
                    if m["Fecha_Limite"]:
                        st.caption(f"Fecha limite: {m['Fecha_Limite']}")
                    if m["Fecha_Estimada"]:
                        st.caption(f"Estimacion: {m['Fecha_Estimada']} ({m['Meses_Faltantes']} meses)")
                with col_prog:
                    st.progress(min(1.0, m["Porcentaje"] / 100.0))
                    st.caption(f"Estado: {m['Estado']}")
                st.markdown("---")

        with st.expander("Anadir Nueva Meta"):
            with st.form("form_nueva_meta"):
                c1, c2 = st.columns(2)
                with c1:
                    nom_meta = st.text_input("Nombre de la Meta", placeholder="Fondo de emergencia, etc.")
                    obj_meta = st.number_input("Monto Objetivo", min_value=10.0, value=1000.0, step=50.0)
                with c2:
                    lim_meta = st.date_input("Fecha limite")
                    ini_meta = st.number_input("Aportes acumulados iniciales", min_value=0.0, value=0.0)
                btn_crear_meta = st.form_submit_button("Guardar Meta")
            if btn_crear_meta and nom_meta:
                provider.append_row("Metas_Ahorro", {
                    "Nombre": nom_meta,
                    "Monto objetivo": obj_meta,
                    "Fecha limite": str(lim_meta),
                    "Aportes acumulados": ini_meta,
                })
                st.success("Meta guardada en Excel.")
                st.rerun()

    with tab_deudas:
        df_deudas = provider.get_sheet("Deudas")

        st.write("**Registrar Nueva Deuda**")
        with st.expander("Anadir Nueva Deuda", expanded=df_deudas.empty):
            with st.form("form_nueva_deuda"):
                d1, d2 = st.columns(2)
                with d1:
                    acreedor = st.text_input("Acreedor / Nombre de la Deuda", placeholder="Banco Union, Prestamo personal, Tarjeta, etc.")
                    monto_orig = st.number_input("Monto Original (Bs.)", min_value=0.0, value=1000.0, step=100.0)
                    saldo_act = st.number_input("Saldo Actual Pendiente (Bs.)", min_value=0.0, value=1000.0, step=100.0)
                with d2:
                    tasa_int = st.number_input("Tasa de Interes Anual (%)", min_value=0.0, value=12.0, step=0.5)
                    cuota_min = st.number_input("Cuota Mensual Minima (Bs.)", min_value=0.0, value=100.0, step=20.0)
                    vencimiento = st.date_input("Fecha Limite / Vencimiento")
                btn_crear_deuda = st.form_submit_button("Guardar Deuda en el Sistema", type="primary")

            if btn_crear_deuda and acreedor:
                provider.append_row("Deudas", {
                    "Acreedor": acreedor,
                    "Monto original": monto_orig,
                    "Saldo actual": saldo_act,
                    "Tasa de interes (%)": tasa_int,
                    "Cuota mensual": cuota_min,
                    "Fecha vencimiento": str(vencimiento),
                })
                st.success(f"Deuda '{acreedor}' guardada correctamente.")
                st.rerun()

        if df_deudas.empty or "Saldo actual" not in df_deudas.columns:
            st.info("No hay deudas registradas aun. Use el formulario de arriba para ingresar su primera deuda.")
            return

        st.markdown("---")
        st.write("**Deudas Activas Registradas**")
        st.dataframe(df_deudas, use_container_width=True, hide_index=True)

        pago_extra = st.number_input(
            "Pago extra mensual a destinar a cancelacion (Bs.)",
            min_value=0.0,
            value=100.0,
            step=25.0
        )

        sim = simulate_debt_payoff(df_deudas, extra_monthly_payment=pago_extra)

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total Deuda Activa", format_currency(sim["Total_Deuda"]))
        with k2:
            st.metric("Total Cuotas Minimas", format_currency(sim["Total_Cuota_Minima"]))
        with k3:
            st.metric("Ahorro Intereses con Avalancha", format_currency(sim["Diferencia_Intereses"]))

        st.markdown("---")
        st.write("**Comparativa de Estrategias de Cancelacion**")
        col_snow, col_av = st.columns(2)

        with col_snow:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Metodo Bola de Nieve</div>
                    <p style="font-size: 0.8rem; color: #52525B; margin: 0.25rem 0;">Prioriza pagar deudas de menor a mayor saldo actual.</p>
                    <div class="kpi-number">{sim['Snowball']['Meses']} meses</div>
                    <div style="font-size: 0.82rem; margin-top: 0.35rem; color: #18181B;">Intereses totales: <b>{format_currency(sim['Snowball']['Intereses_Totales'])}</b></div>
                    <div style="font-size: 0.75rem; color: #71717A; margin-top: 0.25rem;">Orden: {', '.join(sim['Snowball']['Orden'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_av:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Metodo Avalancha</div>
                    <p style="font-size: 0.8rem; color: #52525B; margin: 0.25rem 0;">Prioriza pagar deudas con mayor tasa de interes anual.</p>
                    <div class="kpi-number">{sim['Avalanche']['Meses']} meses</div>
                    <div style="font-size: 0.82rem; margin-top: 0.35rem; color: #18181B;">Intereses totales: <b>{format_currency(sim['Avalanche']['Intereses_Totales'])}</b></div>
                    <div style="font-size: 0.75rem; color: #71717A; margin-top: 0.25rem;">Orden: {', '.join(sim['Avalanche']['Orden'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
