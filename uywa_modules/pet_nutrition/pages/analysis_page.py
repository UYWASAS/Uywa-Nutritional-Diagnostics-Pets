"""
Página de análisis nutricional de Uywa Pet Nutrition.
"""

from __future__ import annotations

import streamlit as st

from food_analysis import show_food_analysis


PROFILE_SESSION_KEY = "profile"
ANALYSIS_SPECIES_KEY = "analysis_species_active"

SUPPORTED_SPECIES = {
    "perro",
    "gato",
}

SPECIES_ALIASES = {
    "canino": "perro",
    "dog": "perro",
    "felino": "gato",
    "cat": "gato",
}


def _get_species_from_profile() -> str:
    """
    Obtiene la especie activa desde el perfil almacenado
    en session_state.

    Mantiene compatibilidad con los nombres:

    - perro
    - gato
    - canino
    - felino
    - dog
    - cat
    """

    profile = st.session_state.get(
        PROFILE_SESSION_KEY,
        {},
    )

    if not isinstance(profile, dict):
        return "perro"

    pet_data = profile.get(
        "mascota",
        {},
    )

    if not isinstance(pet_data, dict):
        return "perro"

    species = str(
        pet_data.get(
            "especie",
            "perro",
        )
        or "perro"
    ).strip().lower()

    species = SPECIES_ALIASES.get(
        species,
        species,
    )

    if species not in SUPPORTED_SPECIES:
        return "perro"

    return species


def _configure_species_dependent_keys(
    species: str,
) -> None:
    """
    Configura las claves de session_state utilizadas por
    la página de análisis y por food_analysis.py.
    """

    st.session_state[
        ANALYSIS_SPECIES_KEY
    ] = species

    if species == "gato":
        st.session_state[
            "food_search_input_active"
        ] = "food_search_input_gato"

        st.session_state[
            "analysis_food_card_active_page_key"
        ] = "analysis_food_card_gato_page"

        return

    st.session_state[
        "food_search_input_active"
    ] = "food_search_input_perro"

    st.session_state[
        "analysis_food_card_active_page_key"
    ] = "analysis_food_card_perro_page"


def show_analysis_page() -> None:
    """
    Renderiza la página de análisis nutricional para
    la especie registrada en el perfil activo.
    """

    active_species = (
        _get_species_from_profile()
    )

    _configure_species_dependent_keys(
        active_species
    )

    show_food_analysis()
