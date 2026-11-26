"""
Pruebas unitarias para calculos presupuestarios y regla 50/30/20.
"""
from pathlib import Path
import pytest
import pandas as pd
from src.storage.excel_provider import ExcelProvider
from src.storage.template_builder import create_master_spreadsheet
from src.services.budget import get_budget_vs_actual, calculate_50_30_20, get_budget_pace_projection


@pytest.fixture
def test_provider(tmp_path):
    test_excel = tmp_path / "test_finanzas.xlsx"
    create_master_spreadsheet(test_excel, include_demo_data=True)
    return ExcelProvider(filepath=str(test_excel))


def test_budget_vs_actual_structure(test_provider):
    df_movs = test_provider.get_sheet("Movimientos")
    assert not df_movs.empty
    first_month = str(df_movs["Fecha"].iloc[0])[:7]

    bva = get_budget_vs_actual(test_provider, first_month)
    assert not bva.empty
    assert "Categoria" in bva.columns or "Categoría" in bva.columns
    assert "Presupuesto" in bva.columns
    assert "Gasto_Real" in bva.columns
    assert "Diferencia" in bva.columns
    assert "Pct_Ejecucion" in bva.columns

    for _, r in bva.iterrows():
        assert round(r["Diferencia"], 2) == round(r["Presupuesto"] - r["Gasto_Real"], 2)


def test_50_30_20_calculation(test_provider):
    df_movs = test_provider.get_sheet("Movimientos")
    first_month = str(df_movs["Fecha"].iloc[0])[:7]

    dist = calculate_50_30_20(test_provider, first_month)
    assert dist["Ingresos_Totales"] > 0
    assert dist["Necesidades_Monto"] > 0
    assert dist["Total_Distribuido"] > 0
    assert dist["Necesidades_Pct"] + dist["Deseos_Pct"] + dist["Ahorro_Pct"] > 0


def test_budget_pace_projection(test_provider):
    df_movs = test_provider.get_sheet("Movimientos")
    first_month = str(df_movs["Fecha"].iloc[0])[:7]

    pace = get_budget_pace_projection(test_provider, first_month)
    assert pace["Dias_En_Mes"] in [28, 29, 30, 31]
    assert pace["Presupuesto_Total"] > 0
    assert pace["Gasto_Actual"] > 0
    assert pace["Ritmo_Diario_Real"] >= 0
