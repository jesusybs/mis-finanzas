"""
Servicio para simulación y planificación de Pago de Deudas (Bola de Nieve vs. Avalancha)
y seguimiento proyectado de Metas de Ahorro.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Tuple
import pandas as pd
from src.utils.formatting import format_currency


def simulate_debt_payoff(
    df_deudas: pd.DataFrame, extra_monthly_payment: float = 0.0
) -> Dict[str, Any]:
    """
    Simula y compara el pago de deudas mediante:
    1. Bola de Nieve (Prioridad: menor saldo actual primero)
    2. Avalancha (Prioridad: mayor tasa de interés anual primero)
    """
    if df_deudas.empty or "Saldo actual" not in df_deudas.columns:
        return {
            "Total_Deuda": 0.0,
            "Total_Cuota_Minima": 0.0,
            "Snowball": {"Meses": 0, "Intereses_Totales": 0.0, "Orden": []},
            "Avalanche": {"Meses": 0, "Intereses_Totales": 0.0, "Orden": []},
            "Diferencia_Intereses": 0.0,
        }

    valid_debts = []
    for _, r in df_deudas.iterrows():
        try:
            saldo = float(r.get("Saldo actual", 0.0) or 0.0)
            if saldo <= 0:
                continue
            cuota = float(r.get("Cuota mensual", 0.0) or 0.0)
            tasa = float(r.get("Tasa de interés (%)", 0.0) or 0.0)
            acreedor = str(r.get("Acreedor", "Deuda"))
            valid_debts.append({
                "Acreedor": acreedor,
                "Saldo": saldo,
                "Cuota": cuota,
                "Tasa_Anual": tasa,
                "Tasa_Mensual": (tasa / 100.0) / 12.0,
            })
        except Exception:
            continue

    if not valid_debts:
        return {
            "Total_Deuda": 0.0,
            "Total_Cuota_Minima": 0.0,
            "Snowball": {"Meses": 0, "Intereses_Totales": 0.0, "Orden": []},
            "Avalanche": {"Meses": 0, "Intereses_Totales": 0.0, "Orden": []},
            "Diferencia_Intereses": 0.0,
        }

    total_deuda = sum(d["Saldo"] for d in valid_debts)
    total_cuota = sum(d["Cuota"] for d in valid_debts)

    # Simular Bola de Nieve (Ordenar por Saldo ascendente)
    snowball_debts = sorted([d.copy() for d in valid_debts], key=lambda x: x["Saldo"])
    snowball_months, snowball_interest = _run_payoff_simulation(snowball_debts, extra_monthly_payment)

    # Simular Avalancha (Ordenar por Tasa Anual descendente)
    avalanche_debts = sorted([d.copy() for d in valid_debts], key=lambda x: x["Tasa_Anual"], reverse=True)
    avalanche_months, avalanche_interest = _run_payoff_simulation(avalanche_debts, extra_monthly_payment)

    dif_intereses = snowball_interest - avalanche_interest

    return {
        "Total_Deuda": total_deuda,
        "Total_Cuota_Minima": total_cuota,
        "Pago_Extra": extra_monthly_payment,
        "Snowball": {
            "Meses": snowball_months,
            "Intereses_Totales": round(snowball_interest, 2),
            "Orden": [d["Acreedor"] for d in snowball_debts],
        },
        "Avalanche": {
            "Meses": avalanche_months,
            "Intereses_Totales": round(avalanche_interest, 2),
            "Orden": [d["Acreedor"] for d in avalanche_debts],
        },
        "Diferencia_Intereses": round(dif_intereses, 2),
    }


def _run_payoff_simulation(debts: List[Dict[str, Any]], extra_payment: float) -> Tuple[int, float]:
    """Ejecuta la simulación mes a mes calculando amortización e intereses devengados."""
    month = 0
    total_interest = 0.0
    max_months = 360  # Limite de 30 años para evitar bucles infinitos

    while month < max_months:
        active_debts = [d for d in debts if d["Saldo"] > 0.01]
        if not active_debts:
            break

        month += 1
        available_extra = extra_payment

        # 1. Acumular interés mensual y cobrar cuota mínima
        for d in active_debts:
            monthly_interest = d["Saldo"] * d["Tasa_Mensual"]
            total_interest += monthly_interest
            d["Saldo"] += monthly_interest

            # Pago mínimo
            payment = min(d["Saldo"], d["Cuota"])
            d["Saldo"] -= payment

            # Si se liquidó, la cuota liberada se suma al efecto bola de nieve
            if d["Saldo"] <= 0.01:
                available_extra += (d["Cuota"] - payment)

        # 2. Aplicar el pago extra al foco prioritario (primera deuda activa)
        remaining_active = [d for d in debts if d["Saldo"] > 0.01]
        for d in remaining_active:
            if available_extra <= 0:
                break
            pay_extra = min(d["Saldo"], available_extra)
            d["Saldo"] -= pay_extra
            available_extra -= pay_extra

    return month, total_interest


def calculate_savings_goals_progress(
    df_metas: pd.DataFrame, monthly_savings_capacity: float = 0.0
) -> List[Dict[str, Any]]:
    """Calcula porcentaje de cumplimiento y proyección estimada de llegada a la meta."""
    if df_metas.empty or "Monto objetivo" not in df_metas.columns:
        return []

    results = []
    today = date.today()

    for _, r in df_metas.iterrows():
        try:
            nombre = str(r.get("Nombre", "Meta"))
            objetivo = float(r.get("Monto objetivo", 0.0) or 0.0)
            acumulado = float(r.get("Aportes acumulados", 0.0) or 0.0)
            fecha_limite_str = str(r.get("Fecha límite", ""))[:10]

            pct = (acumulado / objetivo * 100.0) if objetivo > 0 else 100.0
            remanente = max(0.0, objetivo - acumulado)

            # Meses estimados
            meses_faltantes = None
            fecha_estimada = None
            if remanente <= 0:
                estado = "ALCANZADA"
            elif monthly_savings_capacity > 0:
                meses_faltantes = int(remanente / monthly_savings_capacity) + (1 if remanente % monthly_savings_capacity > 0 else 0)
                # Proyectar fecha
                target_m = today.month + meses_faltantes
                target_y = today.year + (target_m - 1) // 12
                target_m = ((target_m - 1) % 12) + 1
                fecha_estimada = f"{target_y:04d}-{target_m:02d}-01"

                # Comparar con fecha límite
                if fecha_limite_str:
                    try:
                        lim_dt = datetime.strptime(fecha_limite_str, "%Y-%m-%d").date()
                        est_dt = date(target_y, target_m, 1)
                        estado = "A TIEMPO" if est_dt <= lim_dt else "RETRASADA"
                    except Exception:
                        estado = "EN PROCESO"
                else:
                    estado = "EN PROCESO"
            else:
                estado = "EN PROCESO"

            results.append({
                "Nombre": nombre,
                "Objetivo": objetivo,
                "Acumulado": acumulado,
                "Remanente": remanente,
                "Porcentaje": min(100.0, round(pct, 1)),
                "Fecha_Limite": fecha_limite_str,
                "Fecha_Estimada": fecha_estimada,
                "Meses_Faltantes": meses_faltantes,
                "Estado": estado,
            })
        except Exception:
            continue

    return results
