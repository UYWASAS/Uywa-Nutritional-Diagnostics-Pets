"""
UI dashboard module for UYWA Nutrition.
Version 2.0 - Base structure.
"""

import streamlit as st

from utils.ui_cards import (
    render_section_header,
    render_kpi_card,
    render_info_card,
)

from utils.ui_theme import COLORS


def render_food_header(food_name:str, brand:str="", species:str="", stage:str=""):
    render_section_header(
        title=food_name,
        kicker="Alimento balanceado",
        subtitle=f"{brand} • {species} • {stage}"
    )


def render_food_composition_metrics(pb, ee, fc, ena, me):
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        render_kpi_card("PB", f"{pb:.1f}", "%", tone="protein")
    with c2:
        render_kpi_card("EE", f"{ee:.1f}", "%", tone="fat")
    with c3:
        render_kpi_card("FC", f"{fc:.1f}", "%", tone="fiber")
    with c4:
        render_kpi_card("ENA", f"{ena:.1f}", "%", tone="carb")
    with c5:
        render_kpi_card("ME", f"{me:.0f}", "kcal/kg", tone="energy")


def render_energy_decision_card(status:str, message:str):
    render_info_card(
        title="Decisión nutricional",
        body=message,
        tone=status,
    )
