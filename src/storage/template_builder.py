"""
Generador de la plantilla maestra finanzas.xlsx.
Estilo minimalista en blanco y negro, sin emojis, con encabezados sobrios,
validaciones de datos y formulas nativas de Excel.
"""
from datetime import date, datetime
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# Estilos en escala de grises / blanco y negro
HEADER_FILL = PatternFill(start_color="262626", end_color="262626", fill_type="solid")  # Negro suave / Antracita
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ROW_ALT_FILL = PatternFill(start_color="F7F7F7", end_color="F7F7F7", fill_type="solid")  # Gris muy suave
BORDER_THIN = Border(
    left=Side(style='thin', color='D4D4D4'),
    right=Side(style='thin', color='D4D4D4'),
    top=Side(style='thin', color='D4D4D4'),
    bottom=Side(style='thin', color='D4D4D4')
)
BORDER_HEADER = Border(
    left=Side(style='thin', color='171717'),
    right=Side(style='thin', color='171717'),
    top=Side(style='thin', color='171717'),
    bottom=Side(style='medium', color='171717')
)

CATEGORIAS_DATA = [
    # Categoria, Subcategoria, Tipo Gasto, Clasificacion 50/30/20, Codigo
    ("Vivienda", "Alquiler / Hipoteca", "Fijo", "Necesidad", "VIV-01"),
    ("Vivienda", "Mantenimiento / Reparaciones", "Variable", "Necesidad", "VIV-02"),
    ("Servicios", "Electricidad", "Fijo", "Necesidad", "SER-01"),
    ("Servicios", "Agua y Gas", "Fijo", "Necesidad", "SER-02"),
    ("Servicios", "Internet y Telefonia", "Fijo", "Necesidad", "SER-03"),
    ("Alimentacion", "Supermercado", "Fijo", "Necesidad", "ALI-01"),
    ("Alimentacion", "Restaurantes y Delivery", "Discrecional", "Deseo", "ALI-02"),
    ("Alimentacion", "Cafe y Snacks", "Discrecional", "Deseo", "ALI-03"),
    ("Transporte", "Combustible", "Variable", "Necesidad", "TRA-01"),
    ("Transporte", "Transporte Publico / Taxi", "Variable", "Necesidad", "TRA-02"),
    ("Transporte", "Mantenimiento Vehicular", "Variable", "Necesidad", "TRA-03"),
    ("Salud", "Farmacia y Medicamentos", "Variable", "Necesidad", "SAL-01"),
    ("Salud", "Consultas y Seguros", "Fijo", "Necesidad", "SAL-02"),
    ("Educacion", "Cursos y Libros", "Discrecional", "Deseo", "EDU-01"),
    ("Ocio y Salidas", "Cine, Conciertos y Salidas", "Discrecional", "Deseo", "OCI-01"),
    ("Ocio y Salidas", "Streaming y Suscripciones", "Fijo", "Deseo", "OCI-02"),
    ("Compras Personales", "Ropa y Calzado", "Discrecional", "Deseo", "COM-01"),
    ("Compras Personales", "Electronica y Hogar", "Discrecional", "Deseo", "COM-02"),
    ("Ahorro e Inversion", "Fondo de Emergencia", "Fijo", "Ahorro", "AHO-01"),
    ("Ahorro e Inversion", "Inversiones", "Variable", "Ahorro", "AHO-02"),
    ("Pago de Deudas", "Tarjeta de Credito", "Fijo", "Necesidad", "DEU-01"),
    ("Pago de Deudas", "Prestamo Personal", "Fijo", "Necesidad", "DEU-02"),
]

CUENTAS_DATA = [
    # Cuenta, Tipo, Saldo Inicial, Saldo Actual, Moneda
    ("Banco Principal (Debito)", "Banco", 1500.00, 1820.50, "USD"),
    ("Efectivo Billetera", "Efectivo", 150.00, 95.00, "USD"),
    ("Tarjeta Visa Platino", "Tarjeta de Credito", 0.00, -340.00, "USD"),
    ("Billetera Digital", "Billetera Digital", 300.00, 245.00, "USD"),
    ("Cuenta de Ahorros / Inversion", "Inversion", 4500.00, 5200.00, "USD"),
]

INGRESOS_ESPERADOS_DATA = [
    # Fuente, Monto, Frecuencia, Dia de cobro, Cuenta Destino
    ("Sueldo Principal", 3200.00, "Mensual", 1, "Banco Principal (Debito)"),
    ("Trabajo Freelance / Extra", 450.00, "Mensual", 15, "Billetera Digital"),
    ("Rendimiento Inversiones", 65.00, "Mensual", 28, "Cuenta de Ahorros / Inversion"),
]

GASTOS_RECURRENTES_DATA = [
    # Nombre, Monto, Frecuencia, Dia de cobro, Categoria, Cuenta Debito, Auto registrar
    ("Alquiler Departamento", 850.00, "Mensual", 5, "Vivienda", "Banco Principal (Debito)", "Si"),
    ("Internet Fibra Optica", 45.00, "Mensual", 10, "Servicios", "Banco Principal (Debito)", "Si"),
    ("Plan Movil", 25.00, "Mensual", 12, "Servicios", "Tarjeta Visa Platino", "Si"),
    ("Netflix y Spotify", 22.00, "Mensual", 16, "Ocio y Salidas", "Tarjeta Visa Platino", "Si"),
    ("Gimnasio", 40.00, "Mensual", 2, "Salud", "Tarjeta Visa Platino", "Si"),
]

METAS_AHORRO_DATA = [
    # Nombre, Monto Objetivo, Fecha Limite, Aportes Acumulados
    ("Fondo de Emergencia (6 meses)", 6000.00, "2027-12-31", 3800.00),
    ("Vacaciones Fin de Ano", 1500.00, "2027-11-30", 900.00),
    ("Renovacion Portatil", 1200.00, "2027-08-31", 500.00),
]

DEUDAS_DATA = [
    # Acreedor, Monto Original, Saldo, Tasa Interes Anual (%), Cuota Mensual, Fecha Vencimiento
    ("Tarjeta Visa Platino", 1200.00, 340.00, 24.5, 120.00, "2027-03-15"),
    ("Prestamo Vehicular", 8000.00, 3100.00, 9.8, 220.00, "2028-06-30"),
]

CONFIG_SHEET_DATA = [
    ("moneda_simbolo", "$", "Simbolo principal para visualizacion"),
    ("moneda_codigo", "USD", "Codigo ISO de la moneda"),
    ("dia_inicio_mes", 1, "Dia calendario de inicio del mes financiero"),
    ("alerta_amarilla_pct", 80, "Porcentaje para alerta preventiva"),
    ("alerta_roja_pct", 100, "Porcentaje que indica presupuesto excedido"),
    ("gastos_hormiga_umbral", 15, "Monto maximo considerado como gasto menor"),
]


def create_master_spreadsheet(output_path: Path, include_demo_data: bool = True) -> None:
    """Crea el archivo Excel sobrio con las 10 pestanas formateadas en blanco y negro."""
    wb = openpyxl.Workbook()
    default_sheet = wb.active

    # 1. MOVIMIENTOS
    ws_mov = wb.create_sheet("Movimientos")
    headers_mov = [
        "ID", "Fecha", "Tipo", "Categoria", "Subcategoria", "Descripcion",
        "Comercio/Lugar", "Monto", "Metodo de pago", "Cuenta", "Etiquetas", "Recurrente", "Nota"
    ]
    ws_mov.append(headers_mov)

    # 2. PRESUPUESTO
    ws_pres = wb.create_sheet("Presupuesto")
    headers_pres = ["Mes", "Categoria", "Monto Presupuestado"]
    ws_pres.append(headers_pres)

    # 3. CATEGORIAS
    ws_cat = wb.create_sheet("Categorias")
    headers_cat = ["Categoria", "Subcategoria", "Tipo de gasto", "Clasificacion 50/30/20", "Codigo"]
    ws_cat.append(headers_cat)
    for row in CATEGORIAS_DATA:
        ws_cat.append(list(row))

    # 4. INGRESOS ESPERADOS
    ws_ing = wb.create_sheet("Ingresos_Esperados")
    headers_ing = ["Fuente", "Monto", "Frecuencia", "Dia de cobro", "Cuenta destino"]
    ws_ing.append(headers_ing)
    for row in INGRESOS_ESPERADOS_DATA:
        ws_ing.append(list(row))

    # 5. GASTOS RECURRENTES
    ws_rec = wb.create_sheet("Gastos_Recurrentes")
    headers_rec = ["Nombre", "Monto", "Frecuencia", "Dia de cobro", "Categoria", "Cuenta debito", "Auto registrar"]
    ws_rec.append(headers_rec)
    for row in GASTOS_RECURRENTES_DATA:
        ws_rec.append(list(row))

    # 6. CUENTAS Y METODOS DE PAGO
    ws_cue = wb.create_sheet("Cuentas_Metodos")
    headers_cue = ["Cuenta", "Tipo", "Saldo inicial", "Saldo actual", "Moneda"]
    ws_cue.append(headers_cue)
    for row in CUENTAS_DATA:
        ws_cue.append(list(row))

    # 7. METAS DE AHORRO
    ws_met = wb.create_sheet("Metas_Ahorro")
    headers_met = ["Nombre", "Monto objetivo", "Fecha limite", "Aportes acumulados"]
    ws_met.append(headers_met)
    for row in METAS_AHORRO_DATA:
        ws_met.append(list(row))

    # 8. DEUDAS
    ws_deu = wb.create_sheet("Deudas")
    headers_deu = ["Acreedor", "Monto original", "Saldo actual", "Tasa de interes (%)", "Cuota mensual", "Fecha vencimiento"]
    ws_deu.append(headers_deu)
    for row in DEUDAS_DATA:
        ws_deu.append(list(row))

    # 9. CONFIGURACION
    ws_cfg = wb.create_sheet("Configuracion")
    headers_cfg = ["Parametro", "Valor", "Descripcion"]
    ws_cfg.append(headers_cfg)
    for row in CONFIG_SHEET_DATA:
        ws_cfg.append(list(row))

    # 10. RESUMEN MENSUAL
    ws_res = wb.create_sheet("Resumen_Mensual")
    headers_res = ["Mes", "Categoria", "Presupuesto", "Gasto Real", "Diferencia", "% Ejecucion", "Estado"]
    ws_res.append(headers_res)

    if default_sheet in wb.worksheets:
        wb.remove(default_sheet)

    if include_demo_data:
        _populate_demo_data(ws_mov, ws_pres, ws_res)

    _apply_formatting_and_validations(wb)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)


def _populate_demo_data(ws_mov, ws_pres, ws_res) -> None:
    today = date.today()
    year, month = today.year, today.month
    months = []
    for offset in [2, 1, 0]:
        m = month - offset
        y = year
        if m <= 0:
            m += 12
            y -= 1
        months.append(f"{y:04d}-{m:02d}")

    cats = sorted(list(set(c[0] for c in CATEGORIAS_DATA)))

    budget_map = {
        "Vivienda": 950.00,
        "Servicios": 180.00,
        "Alimentacion": 500.00,
        "Transporte": 220.00,
        "Salud": 120.00,
        "Educacion": 80.00,
        "Ocio y Salidas": 200.00,
        "Compras Personales": 150.00,
        "Ahorro e Inversion": 600.00,
        "Pago de Deudas": 340.00,
    }

    for m in months:
        for cat, amount in budget_map.items():
            ws_pres.append([m, cat, amount])

    demo_movs = []
    mov_id = 1001

    for m_str in months:
        y_int, m_int = int(m_str.split("-")[0]), int(m_str.split("-")[1])

        # Ingresos
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-01", "Ingreso", "Ingreso", "Salario",
            "Pago nomina empresa", "Empleador Corp", 3200.00, "Transferencia", "Banco Principal (Debito)",
            "nomina,fijo", "si", "Deposito mensual puntual"
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-15", "Ingreso", "Ingreso", "Freelance",
            "Proyecto consultoria web", "Cliente Tech", 450.00, "Transferencia", "Billetera Digital",
            "extra,variable", "no", "Consultoria freelance"
        ))
        mov_id += 1

        # Gastos
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-05", "Gasto", "Vivienda", "Alquiler / Hipoteca",
            "Pago mensual de renta", "Inmobiliaria Central", 850.00, "Transferencia", "Banco Principal (Debito)",
            "vivienda,fijo", "si", "Alquiler departamento"
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-08", "Gasto", "Servicios", "Electricidad",
            "Factura de luz", "Compania Electrica", 62.50, "Debito Automatico", "Banco Principal (Debito)",
            "servicios,hogar", "si", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-10", "Gasto", "Servicios", "Internet y Telefonia",
            "Internet fibra optica hogar", "FibraNet", 45.00, "Tarjeta de Credito", "Tarjeta Visa Platino",
            "servicios,internet", "si", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-06", "Gasto", "Alimentacion", "Supermercado",
            "Compra quincenal despensa", "Supermercado Mayorista", 185.40, "Tarjeta de Debito", "Banco Principal (Debito)",
            "mercado,comida", "no", "Despensa y articulos de aseo"
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-19", "Gasto", "Alimentacion", "Supermercado",
            "Segunda compra de viveres", "Mercado Local", 142.10, "Tarjeta de Debito", "Banco Principal (Debito)",
            "mercado,frescos", "no", "Frutas, verduras y carnes"
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-12", "Gasto", "Alimentacion", "Restaurantes y Delivery",
            "Cena fin de semana", "Restaurante La Parrilla", 68.00, "Tarjeta de Credito", "Tarjeta Visa Platino",
            "social,salidas", "no", "Cena grupal"
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-14", "Gasto", "Alimentacion", "Cafe y Snacks",
            "Cafe y desayuno", "Cafeteria Aroma", 8.50, "Efectivo", "Efectivo Billetera",
            "menor,cafe", "no", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-07", "Gasto", "Transporte", "Combustible",
            "Carga de combustible", "Estacion de Servicio", 65.00, "Tarjeta de Credito", "Tarjeta Visa Platino",
            "auto,nafta", "no", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-18", "Gasto", "Transporte", "Transporte Publico / Taxi",
            "Viaje en taxi", "Uber", 16.50, "Billetera Digital", "Billetera Digital",
            "transporte,taxi", "no", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-16", "Gasto", "Ocio y Salidas", "Streaming y Suscripciones",
            "Suscripcion mensual", "Netflix y Spotify", 22.00, "Tarjeta de Credito", "Tarjeta Visa Platino",
            "suscripcion,ocio", "si", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-11", "Gasto", "Salud", "Farmacia y Medicamentos",
            "Medicamentos farmacia", "Farmacia Central", 24.30, "Tarjeta de Debito", "Banco Principal (Debito)",
            "salud,farmacia", "no", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-02", "Ahorro", "Ahorro e Inversion", "Fondo de Emergencia",
            "Aporte mensual fondo de emergencia", "Cuenta de Ahorros", 350.00, "Transferencia", "Cuenta de Ahorros / Inversion",
            "ahorro,emergencia", "si", "Aporte regular"
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-03", "Ahorro", "Ahorro e Inversion", "Inversiones",
            "Inversion fondos indexados", "Broker de Inversion", 250.00, "Transferencia", "Cuenta de Ahorros / Inversion",
            "inversion,largo plazo", "si", ""
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-05", "Pago de deuda", "Pago de Deudas", "Prestamo Personal",
            "Cuota mensual vehicular", "Banco Automotor", 220.00, "Debito Automatico", "Banco Principal (Debito)",
            "deuda,auto", "si", "Cuota vehicular"
        ))
        mov_id += 1
        demo_movs.append((
            f"MOV-{mov_id}", f"{y_int}-{m_int:02d}-15", "Pago de deuda", "Pago de Deudas", "Tarjeta de Credito",
            "Pago saldo tarjeta de credito", "Banco Emisor", 120.00, "Transferencia", "Banco Principal (Debito)",
            "deuda,tarjeta", "si", "Pago resumen tarjeta"
        ))
        mov_id += 1

    for row in demo_movs:
        ws_mov.append(list(row))

    res_row = 2
    for m in months:
        for cat in cats:
            f_pres = f'=SUMIFS(Presupuesto!C:C, Presupuesto!A:A, A{res_row}, Presupuesto!B:B, B{res_row})'
            f_real = f'=SUMIFS(Movimientos!H:H, Movimientos!B:B, A{res_row}&"-*", Movimientos!D:D, B{res_row}, Movimientos!C:C, "Gasto")'
            f_dif = f'=C{res_row}-D{res_row}'
            f_pct = f'=IF(C{res_row}>0, D{res_row}/C{res_row}, 0)'
            f_est = f'=IF(F{res_row}>1, "EXCEDIDO", IF(F{res_row}>=0.8, "ALERTA", "OK"))'
            ws_res.append([m, cat, f_pres, f_real, f_dif, f_pct, f_est])
            res_row += 1


def _apply_formatting_and_validations(wb: openpyxl.Workbook) -> None:
    for ws in wb.worksheets:
        ws.views.sheetView[0].showGridLines = True

        for cell in ws[1]:
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = BORDER_HEADER
        ws.row_dimensions[1].height = 26

        for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
            fill = ROW_ALT_FILL if row_idx % 2 == 0 else PatternFill(fill_type=None)
            for cell in row:
                if cell.fill.fill_type is None:
                    cell.fill = fill
                cell.border = BORDER_THIN
                if isinstance(cell.value, (int, float)):
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    if ws.title in ["Movimientos", "Presupuesto", "Resumen_Mensual", "Cuentas_Metodos", "Deudas", "Metas_Ahorro"]:
                        cell.number_format = '$#,##0.00'
                elif isinstance(cell.value, str) and cell.value.startswith("="):
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    if "%" in ws.cell(row=1, column=cell.column).value or "Ejecucion" in str(ws.cell(row=1, column=cell.column).value):
                        cell.number_format = '0.0%'
                    else:
                        cell.number_format = '$#,##0.00'
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if val_str.startswith("="):
                    max_len = max(max_len, 14)
                else:
                    max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    ws_mov = wb["Movimientos"]
    dv_tipo = DataValidation(type="list", formula1='"Ingreso,Gasto,Ahorro,Pago de deuda"', allow_blank=True)
    ws_mov.add_data_validation(dv_tipo)
    dv_tipo.add("C2:C5000")

    dv_rec = DataValidation(type="list", formula1='"si,no"', allow_blank=True)
    ws_mov.add_data_validation(dv_rec)
    dv_rec.add("L2:L5000")
