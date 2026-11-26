"""
Pruebas unitarias para el motor de insights y score de salud financiera.
"""
from pathlib import Path
import pytest
from src.storage.excel_provider import ExcelProvider
from src.storage.template_builder import create_master_spreadsheet
from src.services.insights import compute_financial_health_score, generate_automated_insights


@pytest.fixture
def test_provider(tmp_path):
    test_excel = tmp_path / "test_finanzas.xlsx"
    create_master_spreadsheet(test_excel, include_demo_data=True)
    return ExcelProvider(filepath=str(test_excel))


def test_health_score_bounds(test_provider):
    df_movs = test_provider.get_sheet("Movimientos")
    first_month = str(df_movs["Fecha"].iloc[0])[:7]

    health = compute_financial_health_score(test_provider, first_month)
    assert 0 <= health["Score_Total"] <= 100
    assert health["Nivel"] in ["Excelente", "Bueno", "Regular", "Crítico"]
    assert "Color" in health
    assert "Desglose" in health


def test_automated_insights_generation(test_provider):
    df_movs = test_provider.get_sheet("Movimientos")
    first_month = str(df_movs["Fecha"].iloc[0])[:7]

    insights = generate_automated_insights(test_provider, first_month)
    assert isinstance(insights, list)
    for ins in insights:
        assert "tipo" in ins
        assert "icono" in ins
        assert "titulo" in ins
        assert "mensaje" in ins
