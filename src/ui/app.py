"""
Punto de Entrada Principal de la Interfaz Streamlit.
Estilo simple, sobrio y en blanco y negro (B/N), sin emojis.
"""
import streamlit as st
from src.config import load_config
from src.storage import get_data_provider
from src.ui.style import apply_custom_style
from src.ui.views import (
    v01_dashboard,
    v02_registrar,
    v03_movimientos,
    v04_presupuesto,
    v05_analisis,
    v06_metas_deudas,
    v07_recurrentes,
    v08_configuracion,
)


def run_app():
    try:
        st.set_page_config(
            page_title="Control de Finanzas",
            layout="wide",
            initial_sidebar_state="expanded",
        )
    except Exception:
        pass

    apply_custom_style(st)

    cfg = load_config()
    provider = get_data_provider()

    # Menu Lateral Sobrio
    st.sidebar.markdown(
        """
        <div style="padding-bottom: 0.75rem; border-bottom: 1px solid #E5E7EB; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #111827; font-size: 1.1rem; letter-spacing: -0.02em;">Control de Finanzas</h3>
            <span style="font-size: 0.75rem; color: #6B7280;">Base de datos en Excel</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    SECCIONES = {
        "Dashboard": v01_dashboard,
        "Registrar Movimiento": v02_registrar,
        "Movimientos y Filtros": v03_movimientos,
        "Presupuesto": v04_presupuesto,
        "Analisis y Reportes": v05_analisis,
        "Metas y Deudas": v06_metas_deudas,
        "Recurrentes y Calendario": v07_recurrentes,
        "Configuracion y Respaldos": v08_configuracion,
    }

    modo_actual = cfg.get("app", {}).get("storage_mode", "excel")
    badge_modo = "Excel Local" if modo_actual == "excel" else "Google Sheets"

    st.sidebar.caption(f"Modo: {badge_modo}")

    seleccion = st.sidebar.radio(
        "Secciones:",
        options=list(SECCIONES.keys()),
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Hoja de calculo: finanzas.xlsx")

    vista_modulo = SECCIONES[seleccion]
    vista_modulo.render_view(provider)


if __name__ == "__main__":
    run_app()
