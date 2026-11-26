"""
Vista 2: Registro Rapido de Movimientos (Minimalista B/N).
"""
from datetime import date
import streamlit as st
from src.services.transactions import (
    register_movement, suggest_category, check_possible_duplicates
)
from src.utils.formatting import format_currency


def render_view(provider):
    st.subheader("Registrar Movimiento")

    df_cats = provider.get_sheet("Categorias")
    df_cuentas = provider.get_sheet("Cuentas_Metodos")
    df_movs = provider.get_sheet("Movimientos")

    cats_list = sorted(df_cats["Categoria"].dropna().unique().tolist()) if not df_cats.empty else ["Alimentacion", "Transporte", "Vivienda"]
    cuentas_list = df_cuentas["Cuenta"].dropna().tolist() if not df_cuentas.empty else ["Banco Principal (Debito)", "Efectivo"]
    metodos_list = ["Tarjeta de Debito", "Tarjeta de Credito", "Transferencia", "Efectivo", "Billetera Digital", "Debito Automatico"]

    # Plantillas Frecuentes
    st.write("**Plantillas de Registro Rapido**")
    t1, t2, t3, t4, t5, t6 = st.columns(6)
    plantilla_data = None
    if t1.button("Comida"):
        plantilla_data = {"Tipo": "Gasto", "Categoria": "Alimentacion", "Subcategoria": "Comida Diaria / Almuerzo", "Descripcion": "Comida / Almuerzo", "Monto": 15.0, "Comercio": "Pension / Restaurante"}
    elif t2.button("Pasaje (Bs. 2.50)"):
        plantilla_data = {"Tipo": "Gasto", "Categoria": "Transporte", "Subcategoria": "Pasajes (Micro / Trufi / Teleferico)", "Descripcion": "Pasajes del dia", "Monto": 2.50, "Comercio": "Transporte Publico"}
    elif t3.button("Spotify"):
        plantilla_data = {"Tipo": "Gasto", "Categoria": "Suscripciones Digitales", "Subcategoria": "Spotify", "Descripcion": "Suscripcion Spotify", "Monto": 45.0, "Comercio": "Spotify"}
    elif t4.button("Google AI Pro"):
        plantilla_data = {"Tipo": "Gasto", "Categoria": "Suscripciones Digitales", "Subcategoria": "Google AI Pro", "Descripcion": "Suscripcion Google AI Pro", "Monto": 140.0, "Comercio": "Google"}
    elif t5.button("Ingreso IPCB"):
        plantilla_data = {"Tipo": "Ingreso", "Categoria": "IPCB Import", "Subcategoria": "Ventas / Ingresos Mercaderia", "Descripcion": "Venta / Cobro IPCB Import", "Monto": 500.0, "Comercio": "Cliente IPCB"}
    elif t6.button("Universidad"):
        plantilla_data = {"Tipo": "Gasto", "Categoria": "Educacion", "Subcategoria": "Mensualidad Universidad", "Descripcion": "Cuota Universidad", "Monto": 0.0, "Comercio": "Universidad"}
        if not df_movs.empty:
            last = df_movs.iloc[-1].to_dict()
            plantilla_data = {
                "Tipo": last.get("Tipo", "Gasto"),
                "Categoria": last.get("Categoria", cats_list[0]),
                "Subcategoria": last.get("Subcategoria", ""),
                "Descripcion": last.get("Descripcion", ""),
                "Monto": float(last.get("Monto", 0.0)),
                "Comercio": last.get("Comercio/Lugar", ""),
                "Cuenta": last.get("Cuenta", cuentas_list[0]),
                "Metodo": last.get("Metodo de pago", metodos_list[0]),
            }

    init_tipo = plantilla_data["Tipo"] if plantilla_data else "Gasto"
    init_cat = plantilla_data["Categoria"] if (plantilla_data and plantilla_data["Categoria"] in cats_list) else cats_list[0]
    init_monto = float(plantilla_data["Monto"]) if plantilla_data else 0.0
    init_desc = plantilla_data.get("Descripcion", "") if plantilla_data else ""
    init_comercio = plantilla_data.get("Comercio", "") if plantilla_data else ""

    st.markdown("---")
    with st.form("form_nuevo_movimiento", clear_on_submit=False):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            fecha_val = st.date_input("Fecha", value=date.today())
        with c2:
            tipo_val = st.selectbox("Tipo", ["Gasto", "Ingreso", "Ahorro", "Pago de deuda"], index=["Gasto", "Ingreso", "Ahorro", "Pago de deuda"].index(init_tipo))
        with c3:
            monto_val = st.number_input("Monto", min_value=0.01, value=max(0.01, init_monto), step=1.0, format="%.2f")

        c4, c5 = st.columns(2)
        with c4:
            desc_val = st.text_input("Descripcion / Concepto", value=init_desc, placeholder="Ej: Compra despensa, Pago servicio...")
        with c5:
            comercio_val = st.text_input("Comercio o Lugar", value=init_comercio, placeholder="Ej: Carrefour, Shell...")

        sugerencia = suggest_category(desc_val, comercio_val)
        cat_index = cats_list.index(sugerencia[0]) if (sugerencia and sugerencia[0] in cats_list) else cats_list.index(init_cat)

        c6, c7 = st.columns(2)
        with c6:
            cat_val = st.selectbox("Categoria", cats_list, index=cat_index)
        with c7:
            subcats = []
            if not df_cats.empty and "Categoria" in df_cats.columns and "Subcategoria" in df_cats.columns:
                subcats = df_cats[df_cats["Categoria"] == cat_val]["Subcategoria"].dropna().unique().tolist()
            subcat_val = st.selectbox("Subcategoria", options=subcats if subcats else ["General"])

        c8, c9, c10 = st.columns(3)
        with c8:
            cuenta_val = st.selectbox("Cuenta afectada", cuentas_list)
        with c9:
            metodo_val = st.selectbox("Metodo de pago", metodos_list)
        with c10:
            recurrente_val = st.radio("¿Recurrente?", ["no", "si"], horizontal=True)

        c11, c12 = st.columns([1, 2])
        with c11:
            etiquetas_val = st.text_input("Etiquetas", placeholder="fijo,ocio,super")
        with c12:
            nota_val = st.text_input("Nota adicional (opcional)", placeholder="Detalle...")

        btn_guardar = st.form_submit_button("Guardar en Excel", use_container_width=True, type="primary")

    if btn_guardar:
        nuevo_mov = {
            "Fecha": str(fecha_val),
            "Tipo": tipo_val,
            "Categoria": cat_val,
            "Subcategoria": subcat_val,
            "Descripcion": desc_val or f"{tipo_val} en {cat_val}",
            "Comercio/Lugar": comercio_val,
            "Monto": monto_val,
            "Metodo de pago": metodo_val,
            "Cuenta": cuenta_val,
            "Etiquetas": etiquetas_val,
            "Recurrente": recurrente_val,
            "Nota": nota_val,
        }

        dups = check_possible_duplicates(provider, str(fecha_val), monto_val, comercio_val)
        if dups:
            st.warning(f"Aviso: Existe un movimiento de {format_currency(monto_val)} registrado cerca de esa fecha.")

        ok, msg, nuevo_id = register_movement(provider, nuevo_mov)
        if ok:
            st.success(f"{msg}")
        else:
            st.error(f"Error: {msg}")
