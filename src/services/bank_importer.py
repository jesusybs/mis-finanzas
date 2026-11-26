"""
Servicio para importar extractos bancarios desde archivos CSV y Excel.
Incluye mapeo inteligente de columnas, normalización de montos y deduplicación.
"""
from datetime import datetime
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from src.services.transactions import get_next_mov_id, suggest_category, check_possible_duplicates


DATE_COLUMN_CANDIDATES = ["fecha", "date", "f. valor", "fecha operacion", "fecha transacción", "fec"]
DESC_COLUMN_CANDIDATES = ["descripcion", "descripción", "concepto", "detalle", "comercio", "description", "movimiento"]
AMOUNT_COLUMN_CANDIDATES = ["monto", "importe", "amount", "valor", "debito", "cargo"]


def detect_column_mappings(columns: List[str]) -> Dict[str, Optional[str]]:
    """Intenta detectar automáticamente qué columna corresponde a Fecha, Descripción y Monto."""
    col_map = {"Fecha": None, "Descripción": None, "Monto": None}
    cols_clean = {c: c.lower().strip() for c in columns}

    for orig, clean in cols_clean.items():
        if not col_map["Fecha"] and any(cand in clean for cand in DATE_COLUMN_CANDIDATES):
            col_map["Fecha"] = orig
        elif not col_map["Descripción"] and any(cand in clean for cand in DESC_COLUMN_CANDIDATES):
            col_map["Descripción"] = orig
        elif not col_map["Monto"] and any(cand in clean for cand in AMOUNT_COLUMN_CANDIDATES):
            col_map["Monto"] = orig

    return col_map


def parse_bank_file(file_bytes: bytes, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Lee el archivo subido en CSV o Excel y devuelve un DataFrame preliminar."""
    name = filename.lower()
    try:
        if name.endswith(".csv"):
            try:
                # Intentar utf-8 primero
                df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine='python', encoding='utf-8')
            except Exception:
                df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine='python', encoding='latin1')
        elif name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            return None, "Formato no soportado. Por favor sube un archivo .CSV o .XLSX"

        df.dropna(how="all", inplace=True)
        return df, None
    except Exception as e:
        return None, f"Error al procesar el archivo: {str(e)}"


def prepare_import_candidates(
    provider,
    df_raw: pd.DataFrame,
    col_fecha: str,
    col_desc: str,
    col_monto: str,
    default_cuenta: str = "Banco Principal (Débito)",
) -> List[Dict[str, Any]]:
    """Transforma el extracto bancario en movimientos candidatos enriquecidos."""
    df_movs = provider.get_sheet("Movimientos")
    candidates = []

    for idx, row in df_raw.iterrows():
        try:
            # 1. Parsear Fecha
            raw_fecha = row[col_fecha]
            if isinstance(raw_fecha, datetime):
                fecha_clean = raw_fecha.strftime("%Y-%m-%d")
            else:
                # Normalizar fechas estilo DD/MM/AAAA o AAAA-MM-DD
                dt_obj = pd.to_datetime(raw_fecha, errors='coerce', dayfirst=True)
                fecha_clean = dt_obj.strftime("%Y-%m-%d") if pd.notnull(dt_obj) else datetime.today().strftime("%Y-%m-%d")

            # 2. Parsear Descripción
            desc_clean = str(row[col_desc]).strip()

            # 3. Parsear Monto
            raw_monto = row[col_monto]
            if isinstance(raw_monto, str):
                cleaned_num = raw_monto.replace("$", "").replace(" ", "").replace(".", "").replace(",", ".")
                monto_val = float(cleaned_num)
            else:
                monto_val = float(raw_monto)

            tipo = "Gasto" if monto_val < 0 else "Ingreso"
            monto_abs = abs(monto_val)

            # Sugerencia de categoría
            cat_sug = suggest_category(desc_clean)
            cat = cat_sug[0] if cat_sug else ("Alimentación" if tipo == "Gasto" else "Ingreso")
            subcat = cat_sug[1] if cat_sug else ""

            # Verificar posibles duplicados
            pos_dup = check_possible_duplicates(provider, fecha_clean, monto_abs, desc_clean)

            candidates.append({
                "Fecha": fecha_clean,
                "Tipo": tipo,
                "Categoría": cat,
                "Subcategoría": subcat,
                "Descripción": desc_clean,
                "Comercio/Lugar": desc_clean[:40],
                "Monto": monto_abs,
                "Método de pago": "Tarjeta de Débito",
                "Cuenta": default_cuenta,
                "Etiquetas": "importado_banco",
                "¿Recurrente?": "no",
                "Nota": f"Fila original {idx+1}",
                "Es_Duplicado": len(pos_dup) > 0,
            })
        except Exception:
            continue

    return candidates
