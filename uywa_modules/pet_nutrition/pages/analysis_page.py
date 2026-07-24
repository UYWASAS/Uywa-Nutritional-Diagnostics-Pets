"""
Página Análisis nutricional.
"""

from __future__ import annotations

import streamlit as st

from ..foods.food_analysis import show_food_analysis


def _get_species_from_profile() -> str:
    profile = st.session_state.get("profile", {}) or {}
    mascota = profile.get("mascota", {}) or {}
    especie = str(mascota.get("especie", "perro")).strip().lower()

    if especie in ("canino", "dog"):
        return "perro"
    if especie in ("felino", "cat"):
        return "gato"
    if especie not in ("perro", "gato"):
        return "perro"
    return especie


def show_analysis_page() -> None:
    especie_activa = _get_species_from_profile()
    st.session_state["analysis_species_active"] = especie_activa

    # Mantiene compatibilidad con implementaciones que leen estas keys
    st.session_state["food_search_input_active"] = (
        "food_search_input_perro" if especie_activa == "perro" else "food_search_input_gato"
    )
    st.session_state["analysis_food_card_active_page_key"] = (
        "analysis_food_card_perro_page" if especie_activa == "perro" else "analysis_food_card_gato_page"
    )

    show_food_analysis()
