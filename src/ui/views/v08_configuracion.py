"""
Vista 8: Configuracion del Sistema, Modo de Almacenamiento y Respaldos (B/N).
"""
from pathlib import Path
import streamlit as st
import pandas as pd
from src.config import load_config, save_config
from src.storage.backup_manager import list_backups, make_backup, restore_backup
from src.storage.template_builder import create_master_spreadsheet


def render_view(provider):
    st.subheader("Configuracion")

    cfg = load_config()

    tab_storage, tab_general, tab_cats, tab_backups = st.tabs([
        "Modo de Almacenamiento",
        "Moneda y Preferencias",
        "Categorias y Cuentas",
        "Respaldos y Restauracion"
    ])

    with tab_storage:
        st.write("**Base de Datos: Excel Local vs. Google Sheets**")

        current_mode = cfg.get("app", {}).get("storage_mode", "excel")
        st.write(f"Modo activo: **{current_mode.upper()}**")

        new_mode = st.radio(
            "Origen de almacenamiento:",
            options=["excel", "google_sheets"],
            format_func=lambda x: "Modo Excel Local (finanzas.xlsx)" if x == "excel" else "Modo Google Sheets (Google Drive)",
            index=0 if current_mode == "excel" else 1,
        )

        if new_mode != current_mode:
            if st.button("Aplicar Cambio de Modo"):
                cfg["app"]["storage_mode"] = new_mode
                save_config(cfg)
                st.success(f"Modo cambiado a {new_mode.upper()}.")
                st.rerun()

        if new_mode == "google_sheets":
            st.markdown("---")
            st.write("**Configuracion de Google Sheets**")
            cred_path = Path("credentials.json")
            if cred_path.exists():
                st.success("Archivo credentials.json presente.")
            else:
                st.warning("No se encontro credentials.json.")

            with st.expander("Guia de Conexion con Google Sheets", expanded=not cred_path.exists()):
                st.markdown("""
                1. Crear proyecto en Google Cloud Console.
                2. Habilitar Google Drive API y Google Sheets API.
                3. Crear una Cuenta de Servicio, generar clave en JSON y guardarla como `credentials.json` en la carpeta del proyecto.
                4. Crear una hoja en Google Drive llamada `Mis Finanzas Personales` y compartirla con el correo de la cuenta de servicio como Editor.
                """)

    with tab_general:
        st.write("**Moneda y Reglas de Visualizacion**")
        gen_cfg = cfg.get("general", {})

        with st.form("form_general_settings"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_sym = st.text_input("Simbolo de Moneda", value=gen_cfg.get("currency_symbol", "$"))
                new_code = st.text_input("Codigo ISO", value=gen_cfg.get("currency_code", "USD"))
            with c2:
                new_dec = st.selectbox("Separador Decimal", options=[".", ","], index=0 if gen_cfg.get("decimal_separator", ".") == "." else 1)
                new_thou = st.selectbox("Separador de Miles", options=[",", "."], index=0 if gen_cfg.get("thousands_separator", ",") == "," else 1)
            with c3:
                new_day = st.number_input("Dia de inicio del mes", min_value=1, max_value=31, value=int(gen_cfg.get("month_start_day", 1)))
                new_hormiga = st.number_input("Umbral de Gastos Menores", min_value=1.0, value=float(gen_cfg.get("gastos_hormiga_umbral", 15.0)))

            btn_save_gen = st.form_submit_button("Guardar Preferencias")

        if btn_save_gen:
            cfg["general"]["currency_symbol"] = new_sym
            cfg["general"]["currency_code"] = new_code
            cfg["general"]["decimal_separator"] = new_dec
            cfg["general"]["thousands_separator"] = new_thou
            cfg["general"]["month_start_day"] = new_day
            cfg["general"]["gastos_hormiga_umbral"] = new_hormiga
            save_config(cfg)
            st.success("Preferencias guardadas.")
            st.rerun()

    with tab_cats:
        st.write("**Catalogo de Categorias**")
        df_cats = provider.get_sheet("Categorias")
        st.dataframe(df_cats, use_container_width=True)

        with st.expander("Anadir Categoria o Subcategoria"):
            with st.form("form_nueva_cat"):
                c1, c2 = st.columns(2)
                with c1:
                    n_cat = st.text_input("Categoria", placeholder="Ej: Mascotas...")
                    n_sub = st.text_input("Subcategoria", placeholder="Ej: Alimento...")
                with c2:
                    n_tipo = st.selectbox("Tipo de gasto", ["Fijo", "Variable", "Discrecional"])
                    n_50 = st.selectbox("Clasificacion 50/30/20", ["Necesidad", "Deseo", "Ahorro"])
                btn_add_cat = st.form_submit_button("Guardar Categoria")
            if btn_add_cat and n_cat:
                provider.append_row("Categorias", {
                    "Categoria": n_cat,
                    "Subcategoria": n_sub,
                    "Tipo de gasto": n_tipo,
                    "Clasificacion 50/30/20": n_50,
                    "Codigo": n_cat[:3].upper(),
                })
                st.success(f"Categoria '{n_cat}' anadida a Excel.")
                st.rerun()

        st.markdown("---")
        st.write("**Cuentas y Metodos de Pago**")
        df_cue = provider.get_sheet("Cuentas_Metodos")
        st.dataframe(df_cue, use_container_width=True)

    with tab_backups:
        st.write("**Copias de Seguridad del Archivo Excel**")
        col_bk1, _ = st.columns([2, 3])
        with col_bk1:
            if st.button("Crear Respaldo Manual Ahora", type="primary"):
                bak = provider.create_backup(reason="manual")
                if bak:
                    st.success(f"Copia generada: {bak.name}")
                else:
                    st.error("Error al generar copia.")

        backups = list_backups()
        st.write(f"Respaldos en carpeta /backups ({len(backups)})")
        if backups:
            for name, dt, size, p in backups[:10]:
                c_nom, c_fec, c_btn = st.columns([3, 2, 2])
                with c_nom:
                    st.write(f"`{name}`")
                with c_fec:
                    st.caption(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} ({size // 1024} KB)")
                with c_btn:
                    if st.button("Restaurar", key=f"rst_{name}"):
                        if provider.restore_backup(p):
                            st.success(f"Copia {name} restaurada.")
                            st.rerun()
                        else:
                            st.error("Error al restaurar.")
        else:
            st.info("Sin respaldos previos.")

        st.markdown("---")
        with st.expander("Reiniciar Archivo Excel a Plantilla Limpia"):
            st.write("Vacia los datos demo de movimientos y deja el archivo finanzas.xlsx listo para tus datos reales.")
            conf_reset = st.checkbox("Confirmar reinicio de la hoja de calculo.")
            if st.button("Reiniciar a Hoja en Blanco", type="secondary"):
                if conf_reset:
                    provider.create_backup(reason="pre_reset")
                    excel_path = Path("finanzas.xlsx")
                    create_master_spreadsheet(excel_path, include_demo_data=False)
                    st.success("Hoja finanzas.xlsx reiniciada en blanco.")
                    st.rerun()
                else:
                    st.error("Debe marcar la confirmacion.")
