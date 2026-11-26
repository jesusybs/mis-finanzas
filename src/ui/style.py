"""
Estilos CSS responsivos, sobrios y de alta definicion (Minimalismo Blanco y Negro / Grises).
Disenado para verse impecable tanto en PC como en celulares y tablets.
"""

CUSTOM_CSS = """
<style>
    /* Reset y tipografia premium */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #18181B;
        -webkit-font-smoothing: antialiased;
    }

    /* Contenedor principal con respiracion responsiva */
    .main .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1140px;
    }

    /* Grid responsivo automatico para tarjetas KPI */
    .kpi-grid-responsive {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.85rem;
        margin-bottom: 1.5rem;
        width: 100%;
    }

    /* Tarjetas KPI de diseño moderno minimalista */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E4E4E7;
        border-radius: 8px;
        padding: 1rem 1.15rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #A1A1AA;
    }

    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #71717A;
        margin-bottom: 0.35rem;
    }

    .kpi-number {
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.15;
        color: #09090B;
        letter-spacing: -0.02em;
    }

    .kpi-caption {
        font-size: 0.75rem;
        color: #71717A;
        margin-top: 0.35rem;
    }

    /* Alertas e Insights sobrios */
    .insight-item {
        background-color: #FFFFFF;
        border: 1px solid #E4E4E7;
        border-left: 4px solid #18181B;
        border-radius: 6px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.75rem;
    }
    .insight-item-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #09090B;
    }
    .insight-item-desc {
        font-size: 0.82rem;
        color: #52525B;
        margin-top: 0.2rem;
        line-height: 1.4;
    }

    /* Botones limpios y faciles de presionar en celular */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        min-height: 42px !important;
        border: 1px solid #D4D4D8 !important;
        background-color: #FFFFFF !important;
        color: #18181B !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        border-color: #18181B !important;
        background-color: #F4F4F5 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #18181B !important;
        color: #FFFFFF !important;
        border-color: #18181B !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #27272A !important;
    }

    /* Entradas de formulario responsivas y comodas */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 6px !important;
        border: 1px solid #D4D4D8 !important;
        min-height: 42px !important;
        font-size: 0.9rem !important;
    }

    /* Tablas adaptables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E4E4E7;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Responsive: optimizaciones especificas para Celular */
    @media (max-width: 640px) {
        .main .block-container {
            padding-top: 0.75rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        .kpi-grid-responsive {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 0.5rem !important;
        }
        .kpi-card {
            padding: 0.75rem !important;
        }
        .kpi-number {
            font-size: 1.25rem !important;
        }
        .kpi-label {
            font-size: 0.68rem !important;
        }
        /* Ajustar columnas nativas de Streamlit a bloque vertical en pantalla chica */
        div[data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 0.5rem;
        }
    }
</style>
"""


def apply_custom_style(st) -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
