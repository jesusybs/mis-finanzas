"""
Generador de Reportes de Cierre de Mes en HTML/PDF (Estilo Sobrio B/N).
Sin emojis, con formato tabular clasico.
"""
from datetime import datetime
import pandas as pd
from src.config import load_config
from src.services.budget import get_budget_vs_actual, calculate_50_30_20
from src.services.insights import compute_financial_health_score, generate_automated_insights
from src.utils.formatting import format_currency


def generate_monthly_closing_html(provider, target_month: str) -> str:
    cfg = load_config()
    sym = cfg.get("general", {}).get("currency_symbol", "$")

    bva = get_budget_vs_actual(provider, target_month)
    dist = calculate_50_30_20(provider, target_month)
    health = compute_financial_health_score(provider, target_month)
    insights = generate_automated_insights(provider, target_month)

    total_pres = bva["Presupuesto"].sum() if not bva.empty else 0.0
    total_gasto = bva["Gasto_Real"].sum() if not bva.empty else 0.0
    ingresos = dist["Ingresos_Totales"]
    ahorros = dist["Ahorro_Monto"]

    rows_html = ""
    for _, r in bva.iterrows():
        cat = r["Categoria"]
        pres = format_currency(r["Presupuesto"], sym)
        real = format_currency(r["Gasto_Real"], sym)
        diff = format_currency(r["Diferencia"], sym)
        pct = f"{r['Pct_Ejecucion']:.1f}%"
        estado = r["Estado"]
        rows_html += f"""
        <tr>
            <td><strong>{cat}</strong></td>
            <td style="text-align: right;">{pres}</td>
            <td style="text-align: right;">{real}</td>
            <td style="text-align: right;">{diff}</td>
            <td style="text-align: right;">{pct}</td>
            <td style="text-align: center;">{estado}</td>
        </tr>
        """

    insights_html = ""
    for ins in insights:
        insights_html += f"""
        <div style="border-left: 3px solid #111827; padding-left: 10px; margin-bottom: 12px;">
            <strong>{ins['titulo']}</strong><br/>
            <span style="font-size: 13px; color: #4B5563;">{ins['mensaje']}</span>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe Financiero Mensual - {target_month}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #111827;
            background-color: #FFFFFF;
            margin: 0;
            padding: 30px;
        }}
        .header {{
            border-bottom: 2px solid #111827;
            padding-bottom: 15px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ margin: 0; font-size: 22px; text-transform: uppercase; letter-spacing: 0.05em; }}
        .header p {{ margin: 4px 0 0 0; color: #6B7280; font-size: 13px; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            border: 1px solid #D1D5DB;
            padding: 12px;
            text-align: center;
        }}
        .kpi-card .label {{ font-size: 11px; text-transform: uppercase; color: #6B7280; font-weight: 600; }}
        .kpi-card .value {{ font-size: 20px; font-weight: bold; margin-top: 4px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            font-size: 13px;
        }}
        th {{
            border-bottom: 2px solid #111827;
            padding: 8px;
            text-align: left;
            background: #F9FAFB;
        }}
        td {{
            padding: 8px;
            border-bottom: 1px solid #E5E7EB;
        }}
        @media print {{
            body {{ padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Informe Financiero</h1>
            <p>Periodo: {target_month} | Emision: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 24px; font-weight: bold;">{health['Score_Total']}/100</div>
            <div style="font-size: 12px; color: #6B7280;">Nivel: {health['Nivel']}</div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="label">Ingresos</div>
            <div class="value">{format_currency(ingresos, sym)}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Gastos</div>
            <div class="value">{format_currency(total_gasto, sym)}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Ahorro</div>
            <div class="value">{format_currency(ahorros, sym)}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Presupuesto</div>
            <div class="value">{format_currency(total_pres, sym)}</div>
        </div>
    </div>

    <h3 style="font-size: 15px; border-bottom: 1px solid #111827; padding-bottom: 4px;">Ejecucion por Categoria</h3>
    <table>
        <thead>
            <tr>
                <th>Categoria</th>
                <th style="text-align: right;">Presupuesto</th>
                <th style="text-align: right;">Gasto Real</th>
                <th style="text-align: right;">Diferencia</th>
                <th style="text-align: right;">% Ejecucion</th>
                <th style="text-align: center;">Estado</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <h3 style="font-size: 15px; border-bottom: 1px solid #111827; padding-bottom: 4px;">Observaciones</h3>
    {insights_html}
</body>
</html>"""
    return html
