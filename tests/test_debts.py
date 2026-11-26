"""
Pruebas unitarias para los algoritmos de Bola de Nieve y Avalancha.
"""
import pytest
import pandas as pd
from src.services.debts_goals import simulate_debt_payoff


def test_simulate_debt_payoff():
    # Dos deudas: Deuda A (saldo bajo, tasa media), Deuda B (saldo alto, tasa alta)
    deudas_test = pd.DataFrame([
        {"Acreedor": "Tarjeta A", "Saldo actual": 500.0, "Cuota mensual": 50.0, "Tasa de interés (%)": 18.0},
        {"Acreedor": "Préstamo B", "Saldo actual": 2000.0, "Cuota mensual": 100.0, "Tasa de interés (%)": 30.0},
    ])

    sim = simulate_debt_payoff(deudas_test, extra_monthly_payment=50.0)

    assert sim["Total_Deuda"] == 2500.0
    assert sim["Total_Cuota_Minima"] == 150.0

    # Bola de nieve debe ordenar por menor saldo: Tarjeta A primero
    assert sim["Snowball"]["Orden"][0] == "Tarjeta A"

    # Avalancha debe ordenar por mayor tasa: Préstamo B primero
    assert sim["Avalanche"]["Orden"][0] == "Préstamo B"

    # Avalancha debe generar igual o menor interés total que Bola de Nieve
    assert sim["Avalanche"]["Intereses_Totales"] <= sim["Snowball"]["Intereses_Totales"]
    assert sim["Diferencia_Intereses"] >= 0.0
