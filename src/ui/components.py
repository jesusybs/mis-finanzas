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
    cards = []
    for label, val, sub in items:
        sub_html = f'<div class="kpi-caption">{sub}</div>' if sub else ''
        cards.append(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-number">{val}</div>'
            f'{sub_html}'
            f'</div>'
        )

    full_html = f'<div class="kpi-grid-responsive">{"".join(cards)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)


def render_insight_card(titulo: str, mensaje: str) -> None:
    card_html = (
        f'<div class="insight-item">'
        f'<div class="insight-item-title">{titulo}</div>'
        f'<div class="insight-item-desc">{mensaje}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
