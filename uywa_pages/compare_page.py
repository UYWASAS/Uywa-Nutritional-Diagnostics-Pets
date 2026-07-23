"""
Página de comparación nutricional de Uywa Pet Nutrition.
"""

from __future__ import annotations

from clinical_state import (
    get_current_clinical_state,
)
from food_analysis import (
    get_foods_by_species,
)
from food_database import (
    FOODS,
    calculate_ena as calc_ena_food,
    calculate_energy as calc_energy_food,
    calculate_energy_breakdown,
)
from utils.ui_food_compare import (
    render_food_comparison_dashboard,
)


def show_compare_page() -> None:
    """
    Renderiza el comparador de alimentos para la especie
    y el requerimiento energético del paciente activo.
    """

    clinical_state = (
        get_current_clinical_state()
    )

    pet_state = clinical_state.get(
        "pet",
        {},
    )

    energy_state = clinical_state.get(
        "energy",
        {},
    )

    species = str(
        pet_state.get(
            "especie",
            "perro",
        )
        or "perro"
    ).strip().lower()

    if species not in {
        "perro",
        "gato",
    }:
        species = "perro"

    mer = energy_state.get(
        "mer_final",
        0,
    )

    available_foods = (
        get_foods_by_species(
            species
        )
    )

    render_food_comparison_dashboard(
        foods=FOODS,
        available_foods=available_foods,
        species=species,
        mer=mer,
        calculate_energy_func=(
            calc_energy_food
        ),
        calculate_ena_func=(
            calc_ena_food
        ),
        calculate_energy_breakdown_func=(
            calculate_energy_breakdown
        ),
        default_foods=(
            available_foods[:3]
        ),
    )
