"""
Generador del Excel definitivo de Finanzas Personales: Control_Financiero.xlsx.
Diseno profesional en blanco y negro, sin emojis, con 3 hojas integradas:
1. Resumen (KPIs anuales y mensuales con formulas)
2. Presupuesto (Plan por categoria vs gasto real calculado por SUMIFS)
3. Registro_Diario (Tabla de captura diaria simple con listas desplegables)
"""
from datetime import date
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HEADER_FILL = PatternFill(start_color="1A1A1A", end_color="1A1A1A", fill_type="solid")  # Negro solido
SUBHEADER_FILL = PatternFill(start_color="404040", end_color="404040", fill_type="solid")  # Gris oscuro
ALT_ROW_FILL = PatternFill(start_color="F9F9F9", end_color="F9F9F9", fill_type="solid")  # Blanco tenue
CARD_FILL = PatternFill(start_color="F4F4F5", end_color="F4F4F5", fill_type="solid")

FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_TITLE = Font(name="Calibri", size=14, bold=True, color="111111")
FONT_CARD_TITLE = Font(name="Calibri", size=9, bold=True, color="52525B")
FONT_CARD_VAL = Font(name="Calibri", size=16, bold=True, color="09090B")
FONT_BOLD = Font(name="Calibri", size=11, bold=True, color="111111")

BORDER_THIN = Border(
    left=Side(style='thin', color='E4E4E7'),
    right=Side(style='thin', color='E4E4E7'),
    top=Side(style='thin', color='E4E4E7'),
    bottom=Side(style='thin', color='E4E4E7')
)
BORDER_HEADER = Border(
    left=Side(style='thin', color='1A1A1A'),
    right=Side(style='thin', color='1A1A1A'),
    top=Side(style='thin', color='1A1A1A'),
    bottom=Side(style='medium', color='1A1A1A')
)
BORDER_TOTAL = Border(
    top=Side(style='thin', color='1A1A1A'),
    bottom=Side(style='double', color='1A1A1A')
)

CATEGORIAS = [
    ("Ingreso", "Sueldo / Salario Principal"),
    ("Ingreso", "Ingresos Extra / Ventas"),
    ("Ingreso", "Rendimientos / Inversiones"),
    ("Gasto Fijo", "Alquiler / Hipoteca"),
    ("Gasto Fijo", "Servicios (Luz, Agua, Gas)"),
    ("Gasto Fijo", "Internet y Telefonia"),
    ("Gasto Fijo", "Seguros y Cuotas"),
    ("Gasto Variable", "Supermercado y Despensa"),
    ("Gasto Variable", "Transporte y Combustible"),
    ("Gasto Variable", "Salud y Medicamentos"),
    ("Gasto Variable", "Mantenimiento del Hogar"),
    ("Estilo de Vida", "Restaurantes y Salidas"),
    ("Estilo de Vida", "Cafeteria y Snacks"),
    ("Estilo de Vida", "Suscripciones (Streaming)"),
    ("Estilo de Vida", "Ropa y Compras Personales"),
    ("Ahorro", "Fondo de Emergencia"),
    ("Ahorro", "Inversiones y Futuro"),
    ("Deudas", "Pago de Tarjeta de Credito"),
    ("Deudas", "Cuota de Prestamo"),
]

METODOS_PAGO = ["Efectivo", "Tarjeta de Debito", "Tarjeta de Credito", "Transferencia", "Billetera Digital"]


def create_control_financiero(output_path: Path) -> None:
    wb = openpyxl.Workbook()
    default_sheet = wb.active

    # =========================================================================
    # HOJA 1: RESUMEN
    # =========================================================================
    ws_res = wb.create_sheet("Resumen")
    ws_res.views.sheetView[0].showGridLines = True

    # Titulo
    ws_res["A1"] = "CONTROL FINANCIERO PERSONAL"
    ws_res["A1"].font = FONT_TITLE
    ws_res["A2"] = "Panel de Control y Resumen de Flujo de Caja"
    ws_res["A2"].font = Font(name="Calibri", size=10, italic=True, color="71717A")

    # Tarjetas KPI (Fila 4 a 6)
    cards = [
        ("B4", "C4", "B5", "C5", "TOTAL INGRESOS DEL ANO", '=SUM(D10:D21)'),
        ("D4", "E4", "D5", "E5", "TOTAL GASTOS DEL ANO", '=SUM(E10:E21)'),
        ("F4", "G4", "F5", "G5", "SALDO DISPONIBLE / AHORRO", '=B5-D5'),
    ]
    for top_l, top_r, bot_l, bot_r, label, formula in cards:
        ws_res.merge_cells(f"{top_l}:{top_r}")
        ws_res[top_l] = label
        ws_res[top_l].font = FONT_CARD_TITLE
        ws_res[top_l].alignment = Alignment(horizontal="center", vertical="center")
        ws_res[top_l].fill = CARD_FILL

        ws_res.merge_cells(f"{bot_l}:{bot_r}")
        ws_res[bot_l] = formula
        ws_res[bot_l].font = FONT_CARD_VAL
        ws_res[bot_l].alignment = Alignment(horizontal="center", vertical="center")
        ws_res[bot_l].number_format = '"Bs. "#,##0.00'
        ws_res[bot_l].fill = CARD_FILL

    # Tabla Anual Mes a Mes (Fila 9)
    headers_res = ["Mes", "Nombre Mes", "Total Ingresos", "Total Gastos", "Balance Neto", "% Ahorro"]
    for col_idx, h in enumerate(headers_res, start=2):
        cell = ws_res.cell(row=9, column=col_idx, value=h)
        cell.fill = HEADER_FILL
        cell.font = FONT_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER_HEADER
    ws_res.row_dimensions[9].height = 24

    meses = [
        ("01", "Enero"), ("02", "Febrero"), ("03", "Marzo"), ("04", "Abril"),
        ("05", "Mayo"), ("06", "Junio"), ("07", "Julio"), ("08", "Agosto"),
        ("09", "Septiembre"), ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre")
    ]

    for idx, (cod, nom) in enumerate(meses, start=10):
        # Fórmulas SUMIFS dinámicas que leen de Registro_Diario
        # Fecha en columna B, Tipo en columna C, Monto en columna F
        f_ing = f'=SUMIFS(Registro_Diario!F:F, Registro_Diario!C:C, "Ingreso", Registro_Diario!B:B, ">="&DATE(YEAR(TODAY()),{int(cod)},1), Registro_Diario!B:B, "<="&EOMONTH(DATE(YEAR(TODAY()),{int(cod)},1),0))'
        f_gas = f'=SUMIFS(Registro_Diario!F:F, Registro_Diario!C:C, "Gasto", Registro_Diario!B:B, ">="&DATE(YEAR(TODAY()),{int(cod)},1), Registro_Diario!B:B, "<="&EOMONTH(DATE(YEAR(TODAY()),{int(cod)},1),0))'
        f_bal = f'=D{idx}-E{idx}'
        f_pct = f'=IF(D{idx}>0, F{idx}/D{idx}, 0)'

        row_vals = [cod, nom, f_ing, f_gas, f_bal, f_pct]
        for col_idx, val in enumerate(row_vals, start=2):
            c = ws_res.cell(row=idx, column=col_idx, value=val)
            c.border = BORDER_THIN
            if col_idx in [2, 3]:
                c.alignment = Alignment(horizontal="center")
            elif col_idx in [4, 5, 6]:
                c.alignment = Alignment(horizontal="right")
                c.number_format = '"Bs. "#,##0.00'
            elif col_idx == 7:
                c.alignment = Alignment(horizontal="right")
                c.number_format = '0.0%'

    # Fila de Totales Anuales (Fila 22)
    ws_res.cell(row=22, column=2, value="TOTAL").font = FONT_BOLD
    ws_res.cell(row=22, column=3, value="")
    cell_tot_ing = ws_res.cell(row=22, column=4, value='=SUM(D10:D21)')
    cell_tot_gas = ws_res.cell(row=22, column=5, value='=SUM(E10:E21)')
    cell_tot_bal = ws_res.cell(row=22, column=6, value='=SUM(F10:F21)')
    cell_tot_pct = ws_res.cell(row=22, column=7, value='=IF(D22>0, F22/D22, 0)')

    for c in [cell_tot_ing, cell_tot_gas, cell_tot_bal]:
        c.font = FONT_BOLD
        c.alignment = Alignment(horizontal="right")
        c.number_format = '"Bs. "#,##0.00'
        c.border = BORDER_TOTAL
    cell_tot_pct.font = FONT_BOLD
    cell_tot_pct.alignment = Alignment(horizontal="right")
    cell_tot_pct.number_format = '0.0%'
    cell_tot_pct.border = BORDER_TOTAL

    # =========================================================================
    # HOJA 2: PRESUPUESTO
    # =========================================================================
    ws_pre = wb.create_sheet("Presupuesto")
    ws_pre.views.sheetView[0].showGridLines = True

    ws_pre["A1"] = "PLAN DE PRESUPUESTO MENSUAL"
    ws_pre["A1"].font = FONT_TITLE
    ws_pre["A2"] = "Define tu presupuesto estimado y compara contra tus gastos reales"
    ws_pre["A2"].font = Font(name="Calibri", size=10, italic=True, color="71717A")

    headers_pre = ["Grupo", "Categoria", "Presupuesto Planificado", "Gasto Real Acumulado", "Diferencia Disponible", "% Utilizado", "Estado"]
    for col_idx, h in enumerate(headers_pre, start=1):
        cell = ws_pre.cell(row=4, column=col_idx, value=h)
        cell.fill = HEADER_FILL
        cell.font = FONT_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER_HEADER
    ws_pre.row_dimensions[4].height = 24

    # Poblar categorias
    pre_row = 5
    # Presupuestos sugeridos de ejemplo
    montos_base = {
        "Sueldo / Salario Principal": 3000.00,
        "Ingresos Extra / Ventas": 400.00,
        "Rendimientos / Inversiones": 50.00,
        "Alquiler / Hipoteca": 800.00,
        "Servicios (Luz, Agua, Gas)": 150.00,
        "Internet y Telefonia": 50.00,
        "Seguros y Cuotas": 70.00,
        "Supermercado y Despensa": 450.00,
        "Transporte y Combustible": 180.00,
        "Salud y Medicamentos": 80.00,
        "Mantenimiento del Hogar": 60.00,
        "Restaurantes y Salidas": 150.00,
        "Cafeteria y Snacks": 40.00,
        "Suscripciones (Streaming)": 25.00,
        "Ropa y Compras Personales": 100.00,
        "Fondo de Emergencia": 300.00,
        "Inversiones y Futuro": 250.00,
        "Pago de Tarjeta de Credito": 120.00,
        "Cuota de Prestamo": 150.00,
    }

    for grupo, cat_name in CATEGORIAS:
        val_plan = montos_base.get(cat_name, 0.0)
        # Formula SUMIFS para calcular lo realmente gastado de Registro_Diario
        f_real = f'=SUMIFS(Registro_Diario!F:F, Registro_Diario!D:D, B{pre_row})'
        # Diferencia = Planificado - Real
        f_dif = f'=C{pre_row}-D{pre_row}'
        # % Utilizado
        f_pct = f'=IF(C{pre_row}>0, D{pre_row}/C{pre_row}, 0)'
        # Estado simple en texto
        f_est = f'=IF(F{pre_row}>1, "EXCEDIDO", IF(F{pre_row}>=0.8, "LIMITE", "OK"))'

        vals = [grupo, cat_name, val_plan, f_real, f_dif, f_pct, f_est]
        for col_idx, v in enumerate(vals, start=1):
            c = ws_pre.cell(row=pre_row, column=col_idx, value=v)
            c.border = BORDER_THIN
            if col_idx in [1, 2]:
                c.alignment = Alignment(horizontal="left", vertical="center")
            elif col_idx in [3, 4, 5]:
                c.alignment = Alignment(horizontal="right", vertical="center")
                c.number_format = '"Bs. "#,##0.00'
            elif col_idx == 6:
                c.alignment = Alignment(horizontal="right", vertical="center")
                c.number_format = '0.0%'
            elif col_idx == 7:
                c.alignment = Alignment(horizontal="center", vertical="center")
        pre_row += 1

    # Totales Presupuesto
    ws_pre.cell(row=pre_row, column=1, value="TOTAL GASTOS").font = FONT_BOLD
    ws_pre.cell(row=pre_row, column=2, value="")
    c_tot_plan = ws_pre.cell(row=pre_row, column=3, value=f'=SUM(C8:C{pre_row-1})')
    c_tot_real = ws_pre.cell(row=pre_row, column=4, value=f'=SUM(D8:D{pre_row-1})')
    c_tot_dif = ws_pre.cell(row=pre_row, column=5, value=f'=C{pre_row}-D{pre_row}')
    c_tot_pct = ws_pre.cell(row=pre_row, column=6, value=f'=IF(C{pre_row}>0, D{pre_row}/C{pre_row}, 0)')

    for c in [c_tot_plan, c_tot_real, c_tot_dif]:
        c.font = FONT_BOLD
        c.alignment = Alignment(horizontal="right")
        c.number_format = '"Bs. "#,##0.00'
        c.border = BORDER_TOTAL
    c_tot_pct.font = FONT_BOLD
    c_tot_pct.alignment = Alignment(horizontal="right")
    c_tot_pct.number_format = '0.0%'
    c_tot_pct.border = BORDER_TOTAL

    # =========================================================================
    # HOJA 3: REGISTRO DIARIO (El Libro Diario de Movimientos)
    # =========================================================================
    ws_reg = wb.create_sheet("Registro_Diario")
    ws_reg.views.sheetView[0].showGridLines = True

    ws_reg["A1"] = "REGISTRO DIARIO DE INGRESOS Y GASTOS"
    ws_reg["A1"].font = FONT_TITLE
    ws_reg["A2"] = "Anota aqui cada movimiento. El Presupuesto y el Resumen se calculan automaticamente."
    ws_reg["A2"].font = Font(name="Calibri", size=10, italic=True, color="71717A")

    headers_reg = ["ID", "Fecha", "Tipo", "Categoria", "Concepto / Descripcion", "Monto", "Forma de Pago", "Nota"]
    for col_idx, h in enumerate(headers_reg, start=1):
        cell = ws_reg.cell(row=4, column=col_idx, value=h)
        cell.fill = HEADER_FILL
        cell.font = FONT_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER_HEADER
    ws_reg.row_dimensions[4].height = 24

    # Datos iniciales de ejemplo sobrios
    demo_registros = [
        ("001", "2026-11-01", "Ingreso", "Sueldo / Salario Principal", "Cobro de nomina mensual", 3000.00, "Transferencia", "Puntual"),
        ("002", "2026-11-02", "Gasto", "Alquiler / Hipoteca", "Pago mensual vivienda", 800.00, "Transferencia", "Vivienda"),
        ("003", "2026-11-03", "Gasto", "Servicios (Luz, Agua, Gas)", "Factura de electricidad", 55.40, "Tarjeta de Debito", "Edenor"),
        ("004", "2026-11-05", "Gasto", "Supermercado y Despensa", "Compra semanal de alimentos", 124.80, "Tarjeta de Debito", "Supermercado"),
        ("005", "2026-11-07", "Gasto", "Transporte y Combustible", "Carga de combustible", 45.00, "Tarjeta de Credito", "Nafta"),
        ("006", "2026-11-08", "Gasto", "Cafeteria y Snacks", "Cafe y desayuno trabajo", 6.50, "Efectivo", ""),
        ("007", "2026-11-10", "Gasto", "Internet y Telefonia", "Abono internet fibra", 38.00, "Tarjeta de Debito", ""),
        ("008", "2026-11-12", "Gasto", "Restaurantes y Salidas", "Cena fin de semana", 42.00, "Tarjeta de Credito", ""),
        ("009", "2026-11-14", "Gasto", "Salud y Medicamentos", "Farmacia analgesicos", 18.20, "Efectivo", ""),
        ("010", "2026-11-15", "Ingreso", "Ingresos Extra / Ventas", "Venta de articulo usado", 150.00, "Transferencia", "Extra"),
        ("011", "2026-11-16", "Gasto", "Supermercado y Despensa", "Segunda compra quincenal", 132.50, "Tarjeta de Debito", ""),
        ("012", "2026-11-18", "Gasto", "Transporte y Combustible", "Carga de combustible", 45.00, "Tarjeta de Credito", ""),
        ("013", "2026-11-20", "Gasto", "Fondo de Emergencia", "Aporte mensual ahorro", 300.00, "Transferencia", "Ahorro"),
        ("014", "2026-11-22", "Gasto", "Pago de Tarjeta de Credito", "Pago cuota mensual tarjeta", 120.00, "Transferencia", "Deuda"),
    ]

    for row_idx, r in enumerate(demo_registros, start=5):
        for col_idx, val in enumerate(r, start=1):
            cell = ws_reg.cell(row=row_idx, column=col_idx, value=val)
            cell.border = BORDER_THIN
            if col_idx in [1, 2, 3]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in [4, 5, 7, 8]:
                cell.alignment = Alignment(horizontal="left")
            elif col_idx == 6:
                cell.alignment = Alignment(horizontal="right")
                cell.number_format = '"Bs. "#,##0.00'

    # Validacion desplegable de Tipo en Registro Diario (Columna C)
    dv_tipo = DataValidation(type="list", formula1='"Ingreso,Gasto"', allow_blank=True)
    ws_reg.add_data_validation(dv_tipo)
    dv_tipo.add("C5:C5000")

    # Validacion desplegable de Forma de Pago (Columna G)
    dv_pago = DataValidation(type="list", formula1=f'"{",".join(METODOS_PAGO)}"', allow_blank=True)
    ws_reg.add_data_validation(dv_pago)
    dv_pago.add("G5:G5000")

    # Ajustar anchos de columnas en todas las hojas
    for ws in [ws_res, ws_pre, ws_reg]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if not val_str.startswith("="):
                    max_len = max(max_len, len(val_str))
                else:
                    max_len = max(max_len, 14)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Remover hoja vacia por defecto
    if default_sheet in wb.worksheets:
        wb.remove(default_sheet)

    wb.save(output_path)


if __name__ == "__main__":
    out = Path("Control_Financiero.xlsx")
    create_control_financiero(out)
    print(f"Archivo generado con exito en: {out.resolve()}")
