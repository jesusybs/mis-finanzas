"""
Componentes de UI responsivos en Blanco y Negro (B/N).
Adaptables automaticamente a pantallas moviles y de escritorio.
"""
from typing import List, Tuple
import streamlit as st


def render_kpi_grid(items: List[Tuple[str, str, str]]) -> None:
    """
    Renderiza una cuadricula fluida de tarjetas KPI que se adapta
    automaticamente a 2 columnas en celulares y 4-5 en monitores.
    items: lista de tuplas (Etiqueta, Valor, Subtitulo/Detalle)
    """
    cards_html = ""
    for label, val, sub in items:
        cards_html += f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-number">{val}</div>
            {f'<div class="kpi-caption">{sub}</div>' if sub else ''}
        </div>
        """

    st.markdown(
        f'<div class="kpi-grid-responsive">{cards_html}</div>',
        unsafe_allow_html=True,
    )


def render_insight_card(titulo: str, mensaje: str) -> None:
    st.markdown(
        f"""
        <div class="insight-item">
            <div class="insight-item-title">{titulo}</div>
            <div class="insight-item-desc">{mensaje}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
