"""
Pruebas de persistencia atomica, CRUD y respaldos en Excel.
"""
from pathlib import Path
import pytest
from src.storage.excel_provider import ExcelProvider
from src.storage.template_builder import create_master_spreadsheet


@pytest.fixture
def test_provider(tmp_path):
    test_excel = tmp_path / "test_finanzas.xlsx"
    create_master_spreadsheet(test_excel, include_demo_data=True)
    return ExcelProvider(filepath=str(test_excel))


def test_crud_operations(test_provider):
    df_movs = test_provider.get_sheet("Movimientos")
    cat_col = "Categoria" if "Categoria" in df_movs.columns else "Categoría"
    desc_col = "Descripcion" if "Descripcion" in df_movs.columns else "Descripción"

    nuevo_mov = {
        "ID": "MOV-9999",
        "Fecha": "2026-11-25",
        "Tipo": "Gasto",
        cat_col: "Alimentacion",
        "Subcategoria": "Cafe y Snacks",
        desc_col: "Cafe de prueba",
        "Comercio/Lugar": "Cafeteria Test",
        "Monto": 4.50,
        "Metodo de pago": "Efectivo",
        "Cuenta": "Efectivo Billetera",
        "Etiquetas": "test",
        "Recurrente": "no",
        "Nota": "Prueba unitaria",
    }
    test_provider.append_row("Movimientos", nuevo_mov)

    df_after = test_provider.get_sheet("Movimientos")
    assert "MOV-9999" in df_after["ID"].values

    updated_data = nuevo_mov.copy()
    updated_data["Monto"] = 8.50
    updated_data[desc_col] = "Cafe y Medialunas"
    ok = test_provider.update_row("Movimientos", "MOV-9999", updated_data)
    assert ok is True

    df_up = test_provider.get_sheet("Movimientos")
    row_up = df_up[df_up["ID"] == "MOV-9999"].iloc[0]
    assert float(row_up["Monto"]) == 8.50
    assert row_up[desc_col] == "Cafe y Medialunas"

    ok_del = test_provider.delete_row("Movimientos", "MOV-9999")
    assert ok_del is True
    df_del = test_provider.get_sheet("Movimientos")
    assert "MOV-9999" not in df_del["ID"].values
