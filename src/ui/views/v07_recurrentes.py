"""
Vista 7: Gastos Recurrentes y Calendario (Minimalista B/N).
"""
from datetime import date
import streamlit as st
import pandas as pd
from src.services.transactions import register_movement
from src.utils.formatting import format_currency


def render_view(provider):
    st.subheader("Recurrentes y Calendario de Pagos")

    df_rec = provider.get_sheet("Gastos_Recurrentes")
    df_ing = provider.get_sheet("Ingresos_Esperados")
    df_movs = provider.get_sheet("Movimientos")

    today = date.today()
    cur_month_str = f"{today.year:04d}-{today.month:02d}"

    st.write(f"**Cronograma de Pagos y Cobros para {cur_month_str}**")

    registrados_este_mes = set()
    if not df_movs.empty and "Fecha" in df_movs.columns:
        m_movs = df_movs[df_movs["Fecha"].astype(str).str.startswith(cur_month_str)]
        registrados_este_mes = set(m_movs["Descripcion"].astype(str).str.lower().tolist())

    items_calendario = []
    if not df_rec.empty and "Dia de cobro" in df_rec.columns:
        for _, r in df_rec.iterrows():
            nombre = str(r.get("Nombre", ""))
            dia = int(r.get("Dia de cobro", 1) or 1)
            monto = float(r.get("Monto", 0.0) or 0.0)
            cat = str(r.get("Categoria", ""))
            cuenta = str(r.get("Cuenta debito", ""))
            ya_reg = nombre.lower() in registrados_este_mes
            items_calendario.append({
                "Dia": dia,
                "Tipo": "Gasto Recurrente",
                "Concepto": nombre,
                "Categoria": cat,
                "Monto": monto,
                "Cuenta": cuenta,
                "Estado": "Registrado" if ya_reg else "Pendiente",
            })

    if not df_ing.empty and "Dia de cobro" in df_ing.columns:
        for _, r in df_ing.iterrows():
            fuente = str(r.get("Fuente", ""))
            dia = int(r.get("Dia de cobro", 1) or 1)
            monto = float(r.get("Monto", 0.0) or 0.0)
            cuenta = str(r.get("Cuenta destino", ""))
            ya_reg = fuente.lower() in registrados_este_mes
            items_calendario.append({
                "Dia": dia,
                "Tipo": "Ingreso Esperado",
                "Concepto": fuente,
                "Categoria": "Ingreso",
                "Monto": monto,
                "Cuenta": cuenta,
                "Estado": "Cobrado" if ya_reg else "Por cobrar",
            })

    if items_calendario:
        df_cal = pd.DataFrame(items_calendario).sort_values(by="Dia")
        st.dataframe(df_cal, use_container_width=True, hide_index=True)
    else:
        st.info("No hay recurrentes configurados.")

    st.markdown("---")
    st.write("**Registro de Recurrentes del Mes**")
    col_btn, _ = st.columns([2, 3])
    with col_btn:
        if st.button("Registrar Recurrentes Pendientes en Excel", type="primary"):
            generados = 0
            for item in items_calendario:
                if item["Tipo"] == "Gasto Recurrente" and item["Estado"] == "Pendiente":
                    dia_str = f"{item['Dia']:02d}"
                    fecha_pago = f"{cur_month_str}-{dia_str}"
                    nuevo_mov = {
                        "Fecha": fecha_pago,
                        "Tipo": "Gasto",
                        "Categoria": item["Categoria"],
                        "Subcategoria": "Recurrente",
                        "Descripcion": item["Concepto"],
                        "Comercio/Lugar": item["Concepto"],
                        "Monto": item["Monto"],
                        "Metodo de pago": "Debito Automatico",
                        "Cuenta": item["Cuenta"],
                        "Etiquetas": "recurrente,fijo",
                        "Recurrente": "si",
                        "Nota": f"Generado para {cur_month_str}",
                    }
                    ok, _, _ = register_movement(provider, nuevo_mov)
                    if ok:
                        generados += 1
            if generados > 0:
                st.success(f"Se registraron {generados} gastos recurrentes en Excel.")
                st.rerun()
            else:
                st.info("Todos los gastos recurrentes ya estan registrados en el mes.")

    with st.expander("Configurar Nuevo Gasto Recurrente"):
        with st.form("form_nuevo_recurrente"):
            c1, c2, c3 = st.columns(3)
            with c1:
                r_nom = st.text_input("Nombre / Servicio", placeholder="Alquiler, Gimnasio, etc.")
                r_monto = st.number_input("Monto", min_value=1.0, value=25.0, step=5.0)
            with c2:
                r_dia = st.number_input("Dia de cobro (1 al 31)", min_value=1, max_value=31, value=5)
                df_cats = provider.get_sheet("Categorias")
                cats_opts = sorted(df_cats["Categoria"].dropna().unique().tolist()) if not df_cats.empty else ["Servicios"]
                r_cat = st.selectbox("Categoria", cats_opts)
            with c3:
                df_cuentas = provider.get_sheet("Cuentas_Metodos")
                cue_opts = df_cuentas["Cuenta"].dropna().tolist() if not df_cuentas.empty else ["Banco"]
                r_cuenta = st.selectbox("Cuenta de debito", cue_opts)
                r_auto = st.selectbox("Auto registrar cada mes", ["Si", "No"])

            btn_save_rec = st.form_submit_button("Guardar Recurrente")
        if btn_save_rec and r_nom:
            provider.append_row("Gastos_Recurrentes", {
                "Nombre": r_nom,
                "Monto": r_monto,
                "Frecuencia": "Mensual",
                "Dia de cobro": r_dia,
                "Categoria": r_cat,
                "Cuenta debito": r_cuenta,
                "Auto registrar": r_auto,
            })
            st.success("Gasto recurrente guardado en Excel.")
            st.rerun()
