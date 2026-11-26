"""
Vista 3: Historial de Movimientos, Filtros e Importador Bancario (B/N).
"""
import streamlit as st
import pandas as pd
from src.services.transactions import register_movement
from src.services.bank_importer import parse_bank_file, detect_column_mappings, prepare_import_candidates
from src.utils.formatting import format_currency


def render_view(provider):
    st.subheader("Movimientos")

    tab_lista, tab_importar = st.tabs(["Historial y Filtros", "Importar Extracto Bancario"])

    df_movs = provider.get_sheet("Movimientos")

    with tab_lista:
        if df_movs.empty:
            st.info("No hay movimientos registrados.")
            return

        with st.expander("Filtros de Busqueda", expanded=True):
            f1, f2, f3 = st.columns(3)
            with f1:
                tipo_filter = st.multiselect("Tipo", options=df_movs["Tipo"].dropna().unique().tolist())
            with f2:
                cat_filter = st.multiselect("Categoria", options=sorted(df_movs["Categoria"].dropna().unique().tolist()))
            with f3:
                cuenta_filter = st.multiselect("Cuenta", options=df_movs["Cuenta"].dropna().unique().tolist())

            f4, f5 = st.columns([2, 1])
            with f4:
                search_text = st.text_input("Buscar texto en Descripcion o Comercio", placeholder="supermercado, combustible, etc.")
            with f5:
                sort_order = st.selectbox("Orden", ["Mas recientes primero", "Mas antiguos primero"])

        filtered = df_movs.copy()
        if tipo_filter:
            filtered = filtered[filtered["Tipo"].isin(tipo_filter)]
        if cat_filter:
            filtered = filtered[filtered["Categoria"].isin(cat_filter)]
        if cuenta_filter:
            filtered = filtered[filtered["Cuenta"].isin(cuenta_filter)]
        if search_text:
            s = search_text.lower()
            filtered = filtered[
                filtered["Descripcion"].astype(str).str.lower().str.contains(s) |
                filtered["Comercio/Lugar"].astype(str).str.lower().str.contains(s)
            ]

        ascending = sort_order == "Mas antiguos primero"
        filtered["Fecha_dt"] = pd.to_datetime(filtered["Fecha"], errors="coerce")
        filtered.sort_values(by="Fecha_dt", ascending=ascending, inplace=True)
        filtered.drop(columns=["Fecha_dt"], inplace=True)

        st.caption(f"{len(filtered)} de {len(df_movs)} movimientos")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        col_exp1, _ = st.columns([1, 4])
        with col_exp1:
            csv_data = filtered.to_csv(index=False).encode("utf-8")
            st.download_button("Exportar CSV", data=csv_data, file_name="movimientos.csv", mime="text/csv")

        st.markdown("---")
        st.write("**Modificar o Eliminar Registro**")
        all_ids = df_movs["ID"].dropna().astype(str).tolist()
        if all_ids:
            selected_id = st.selectbox("Seleccionar ID de movimiento", options=all_ids)
            selected_row = df_movs[df_movs["ID"].astype(str) == selected_id].iloc[0].to_dict()

            with st.expander(f"Editar o Eliminar {selected_id}"):
                with st.form("form_editar_mov"):
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        new_fecha = st.text_input("Fecha", value=str(selected_row.get("Fecha", "")))
                    with e2:
                        new_desc = st.text_input("Descripcion", value=str(selected_row.get("Descripcion", "")))
                    with e3:
                        new_monto = st.number_input("Monto", value=float(selected_row.get("Monto", 0.0)))

                    e4, e5 = st.columns(2)
                    with e4:
                        new_cat = st.text_input("Categoria", value=str(selected_row.get("Categoria", "")))
                    with e5:
                        new_cuenta = st.text_input("Cuenta", value=str(selected_row.get("Cuenta", "")))

                    btn_save_edit = st.form_submit_button("Guardar Cambios")

                if btn_save_edit:
                    updated = selected_row.copy()
                    updated["Fecha"] = new_fecha
                    updated["Descripcion"] = new_desc
                    updated["Monto"] = new_monto
                    updated["Categoria"] = new_cat
                    updated["Cuenta"] = new_cuenta
                    if provider.update_row("Movimientos", selected_id, updated):
                        st.success(f"Movimiento {selected_id} actualizado.")
                        st.rerun()

                st.markdown("---")
                confirm_del = st.checkbox(f"Confirmar eliminacion de {selected_id}")
                if st.button("Eliminar Registro", type="secondary"):
                    if confirm_del:
                        if provider.delete_row("Movimientos", selected_id):
                            st.warning(f"Movimiento {selected_id} eliminado.")
                            st.rerun()
                    else:
                        st.error("Marque la casilla de confirmacion.")

    with tab_importar:
        st.write("**Importar Extracto Bancario (CSV o Excel)**")
        uploaded_file = st.file_uploader("Subir archivo (.csv, .xlsx, .xls)", type=["csv", "xlsx", "xls"])
        if uploaded_file:
            bytes_data = uploaded_file.read()
            df_bank, err = parse_bank_file(bytes_data, uploaded_file.name)
            if err:
                st.error(err)
            elif df_bank is not None and not df_bank.empty:
                st.write(f"Archivo leido: {len(df_bank)} filas.")
                st.dataframe(df_bank.head(5), use_container_width=True)

                cols = list(df_bank.columns)
                mappings = detect_column_mappings(cols)

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    idx_f = cols.index(mappings["Fecha"]) if mappings["Fecha"] in cols else 0
                    sel_fecha = st.selectbox("Columna Fecha", options=cols, index=idx_f)
                with m2:
                    idx_d = cols.index(mappings["Descripción"]) if mappings["Descripción"] in cols else 0
                    sel_desc = st.selectbox("Columna Descripcion", options=cols, index=idx_d)
                with m3:
                    idx_m = cols.index(mappings["Monto"]) if mappings["Monto"] in cols else 0
                    sel_monto = st.selectbox("Columna Monto", options=cols, index=idx_m)
                with m4:
                    df_cue = provider.get_sheet("Cuentas_Metodos")
                    cue_opts = df_cue["Cuenta"].dropna().tolist() if not df_cue.empty else ["Banco"]
                    sel_cuenta = st.selectbox("Cuenta de destino", options=cue_opts)

                if st.button("Previsualizar Datos"):
                    candidates = prepare_import_candidates(
                        provider, df_bank, sel_fecha, sel_desc, sel_monto, default_cuenta=sel_cuenta
                    )
                    st.session_state["import_candidates"] = candidates

                if "import_candidates" in st.session_state and st.session_state["import_candidates"]:
                    cands = st.session_state["import_candidates"]
                    df_cands = pd.DataFrame(cands)
                    st.dataframe(df_cands, use_container_width=True)

                    if st.button(f"Confirmar e Importar {len(cands)} Filas", type="primary"):
                        guardados = 0
                        for c in cands:
                            c_clean = c.copy()
                            c_clean.pop("Es_Duplicado", None)
                            ok, _, _ = register_movement(provider, c_clean)
                            if ok:
                                guardados += 1
                        st.success(f"Se importaron {guardados} movimientos.")
                        del st.session_state["import_candidates"]
                        st.rerun()
