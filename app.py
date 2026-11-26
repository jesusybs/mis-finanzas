"""
Punto de entrada principal para Streamlit Cloud y ejecución directa.
Estilo simple, sobrio y en blanco y negro (B/N), sin emojis.
"""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import src.ui.app
