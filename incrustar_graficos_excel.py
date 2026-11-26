"""
Agrega graficos nativos de Excel incrustados directamente dentro de Control_Financiero.xlsx.
Graficos sobrios en blanco y negro / escala de grises:
1. Hoja Resumen:
   - Grafico de Barras: Comparativa Mensual de Ingresos vs. Gastos (Enero a Diciembre).
2. Hoja Presupuesto:
   - Grafico de Barras Agrupadas: Presupuesto Planificado vs. Gasto Real por Categoria.
   - Grafico Circular (Pie): Distribucion del Gasto Real.
"""
from pathlib import Path
import openpyxl
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList

def add_native_charts_to_excel(excel_path: Path) -> None:
    wb = openpyxl.load_workbook(excel_path)

    # -------------------------------------------------------------------------
    # 1. GRAFICO EN HOJA 'Resumen': Ingresos vs Gastos Mensuales
    # -------------------------------------------------------------------------
    if "Resumen" in wb.sheetnames:
        ws_res = wb["Resumen"]

        chart_mensual = BarChart()
        chart_mensual.type = "col"
        chart_mensual.style = 13  # Estilo sobrio en escala de grises
        chart_mensual.title = "Ingresos vs. Gastos Mensuales"
        chart_mensual.y_axis.title = "Monto ($)"
        chart_mensual.x_axis.title = "Mes"
        chart_mensual.width = 18
        chart_mensual.height = 11

        # Datos: Columnas D (Ingresos) y E (Gastos) de fila 9 a 21
        data = Reference(ws_res, min_col=4, min_row=9, max_col=5, max_row=21)
        # Categorias / Etiquetas: Columna C (Nombre Mes) de fila 10 a 21
        cats = Reference(ws_res, min_col=3, min_row=10, max_row=21)

        chart_mensual.add_data(data, titles_from_data=True)
        chart_mensual.set_categories(cats)
        chart_mensual.legend.legendPos = "t"

        # Ubicar grafico al lado de la tabla en celda I4
        ws_res.add_chart(chart_mensual, "I4")

    # -------------------------------------------------------------------------
    # 2. GRAFICOS EN HOJA 'Presupuesto': Presupuesto vs Real y Distribucion
    # -------------------------------------------------------------------------
    if "Presupuesto" in wb.sheetnames:
        ws_pre = wb["Presupuesto"]

        # A) Grafico de Barras: Presupuesto vs Real por Categoria
        chart_pre = BarChart()
        chart_pre.type = "bar"  # Barras horizontales
        chart_pre.style = 13
        chart_pre.title = "Presupuesto Planificado vs. Gasto Real"
        chart_pre.x_axis.title = "Monto ($)"
        chart_pre.width = 18
        chart_pre.height = 15

        # Datos: Columna C (Presupuesto) y Columna D (Gasto Real) de fila 4 a 22
        # (Fila 8 a 22 son gastos, excluyendo ingresos)
        data_pre = Reference(ws_pre, min_col=3, min_row=4, max_col=4, max_row=22)
        cats_pre = Reference(ws_pre, min_col=2, min_row=5, max_row=22)

        chart_pre.add_data(data_pre, titles_from_data=True)
        chart_pre.set_categories(cats_pre)
        chart_pre.legend.legendPos = "t"

        ws_pre.add_chart(chart_pre, "I4")

        # B) Grafico Circular: Distribucion del Gasto
        chart_pie = PieChart()
        chart_pie.title = "Distribucion del Gasto Real"
        chart_pie.style = 2  # Tonos neutros / grises
        chart_pie.width = 14
        chart_pie.height = 11

        # Datos: Gasto Real (Columna D, filas 8 a 22)
        data_pie = Reference(ws_pre, min_col=4, min_row=7, max_row=22)
        cats_pie = Reference(ws_pre, min_col=2, min_row=8, max_row=22)

        chart_pie.add_data(data_pie, titles_from_data=True)
        chart_pie.set_categories(cats_pie)
        chart_pie.dataLabels = DataLabelList()
        chart_pie.dataLabels.showPercent = True

        ws_pre.add_chart(chart_pie, "I34")

    wb.save(excel_path)
    print(f"Graficos nativos incrustados exitosamente en: {excel_path}")

if __name__ == "__main__":
    p = Path("Control_Financiero.xlsx")
    add_native_charts_to_excel(p)
