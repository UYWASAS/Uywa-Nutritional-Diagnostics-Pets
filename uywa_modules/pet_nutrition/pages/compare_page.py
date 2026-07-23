"""
Página Comparador nutricional.
"""

from __future__ import annotations

import streamlit as st

from ..core.clinical_state import get_current_clinical_state
from food_analysis import get_foods_by_species
from ..foods.food_database import (
    FOODS,
    calculate_energy as calc_energy_food,
    calculate_ena as calc_ena_food,
    calculate_energy_breakdown,
)
from utils.ui_food_compare import render_food_comparison_dashboard


def show_compare_page() -> None:
    state_comp = get_current_clinical_state()
    pet_comp = state_comp["pet"]
    energy_comp = state_comp["energy"]

    especie_comp = pet_comp.get("especie", "perro")
    mer_comp = energy_comp.get("mer_final", 0)

    alimentos_disponibles_comp = get_foods_by_species(especie_comp)

    render_food_comparison_dashboard(
        foods=FOODS,
        available_foods=alimentos_disponibles_comp,
        species=especie_comp,
        mer=mer_comp,
        calculate_energy_func=calc_energy_food,
        calculate_ena_func=calc_ena_food,
        calculate_energy_breakdown_func=calculate_energy_breakdown,
        default_foods=alimentos_disponibles_comp[:3],
    )
