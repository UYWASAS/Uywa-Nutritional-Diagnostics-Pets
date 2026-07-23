
"""
clinical_state.py

Módulo centralizado para leer el estado clínico actual de la aplicación UYWA.

Versión corregida:
- Lee las claves nuevas generadas por food_analysis.py v2/v3.
- Mantiene compatibilidad con claves antiguas.
- Recupera correctamente alimento, gramos, ME, fuente energética y coberturas.
"""

from __future__ import annotations

import streamlit as st


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if value == "" or value.lower() == "nan":
                return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        return int(round(safe_float(value, default)))
    except Exception:
        return default


def _first_session_value(keys, default=None):
    for key in keys:
        if key in st.session_state:
            value = st.session_state.get(key)
            if value not in [None, ""]:
                return value
    return default


def get_current_profile_raw():
    return st.session_state.get("profile", {}) or {}


def get_current_pet_profile():
    profile = get_current_profile_raw()
    mascota = profile.get("mascota", {}) or {}

    bcs = safe_int(st.session_state.get("bcs_mascota", mascota.get("bcs", 5)), 5)
    bcs = max(1, min(9, bcs))

    return {
        "nombre": st.session_state.get("nombre_mascota", mascota.get("nombre", "—")) or "—",
        "especie": st.session_state.get("especie_mascota", mascota.get("especie", "perro")),
        "edad": safe_float(st.session_state.get("edad_mascota", mascota.get("edad", 0)), 0),
        "peso": safe_float(st.session_state.get("peso_mascota", mascota.get("peso", 0)), 0),
        "etapa": st.session_state.get("etapa_mascota", mascota.get("etapa", "adulto")),
        "condicion": st.session_state.get("condicion_mascota", mascota.get("condicion", "Castrado")),
        "bcs": bcs,
        "aplicar_ajuste_senior": bool(
            st.session_state.get(
                "aplicar_ajuste_senior_mascota",
                mascota.get("aplicar_ajuste_senior", False),
            )
        ),
    }


def get_current_energy_state():
    return {
        "rer": safe_float(st.session_state.get("rer_actual", 0)),
        "mer_base": safe_float(st.session_state.get("mer_base_actual", 0)),
        "mer_final": safe_float(st.session_state.get("energia_actual", 0)),
        "factor_fisiologico": safe_float(st.session_state.get("factor_fisiologico_actual", 0)),
        "senior_aplicado": bool(st.session_state.get("senior_aplicado_actual", False)),
        "estado_corporal": st.session_state.get("estado_corporal_tab1", "—"),
        "riesgo_nutricional": st.session_state.get("riesgo_nutricional_tab1", "—"),
        "prioridad_nutricional": st.session_state.get("prioridad_nutricional_tab1", "—"),
        "diagnostico": st.session_state.get("interpretacion_diagnostico_tab1", "—"),
        "req_pb_g": st.session_state.get("req_pb_g", None),
        "req_ee_g": st.session_state.get("req_ee_g", None),
    }


def _resolve_food_name():
    return _first_session_value(
        [
            "analysis_food_name_edited",
            "alimento_seleccionado",
            "food_name",
            "analysis_food_selector",
            "analysis_food_selector_card",
        ],
        "—",
    )


def _resolve_food_grams(food_name):
    direct_value = _first_session_value(
        [
            "gramos_alimento_actual",
            "gramos_actual",
            "food_grams_actual",
        ],
        None,
    )

    if direct_value is not None:
        return safe_float(direct_value, 0)

    if food_name and food_name != "—":
        safe_key = "".join(c if c.isalnum() else "_" for c in str(food_name))
        dynamic_key = f"gramos_alimento_{safe_key}"

        if dynamic_key in st.session_state:
            return safe_float(st.session_state.get(dynamic_key), 0)

        raw_key = f"gramos_alimento_{food_name}"
        if raw_key in st.session_state:
            return safe_float(st.session_state.get(raw_key), 0)

    return 0.0


def get_current_food_state():
    food_name = _resolve_food_name()
    gramos = _resolve_food_grams(food_name)

    food_data_edited = _first_session_value(
        [
            "analysis_food_data_edited",
            "food_data_edited",
        ],
        {},
    ) or {}

    return {
        "alimento": food_name,
        "gramos": gramos,
        "me": safe_float(
            _first_session_value(
                [
                    "me_alimento_actual",
                    "analysis_me_alimento",
                    "food_me_actual",
                ],
                0,
            )
        ),
        "fuente_me": _first_session_value(
            [
                "fuente_me_actual",
                "analysis_fuente_me",
            ],
            "Fórmula Uywa",
        ),
        "me_formula_uywa": safe_float(st.session_state.get("me_formula_uywa_actual", 0)),
        "me_manufacturer": safe_float(st.session_state.get("me_manufacturer_actual", 0)),
        "me_inferred_manufacturer": safe_float(st.session_state.get("me_inferred_manufacturer_actual", 0)),
        "energia_aportada": safe_float(
            _first_session_value(
                [
                    "energia_aportada_actual",
                    "analysis_energia_aportada",
                    "food_energy_intake_actual",
                ],
                0,
            )
        ),
        "cobertura_energia": safe_float(
            _first_session_value(
                [
                    "cobertura_energia_actual",
                    "analysis_cobertura_energia",
                ],
                0,
            )
        ),
        "gramos_recomendados": safe_float(
            _first_session_value(
                [
                    "gramos_recomendados_actual",
                    "analysis_gramos_recomendados",
                ],
                0,
            )
        ),
        "cobertura_proteina": _first_session_value(
            [
                "cobertura_proteina_actual",
                "analysis_cobertura_proteina",
            ],
            None,
        ),
        "cobertura_grasa": _first_session_value(
            [
                "cobertura_grasa_actual",
                "analysis_cobertura_grasa",
            ],
            None,
        ),
        "food_data_edited": food_data_edited,
        "proximal_sum": safe_float(st.session_state.get("analysis_food_proximal_sum", 0)),
    }


def get_current_clinical_state():
    return {
        "pet": get_current_pet_profile(),
        "energy": get_current_energy_state(),
        "food": get_current_food_state(),
    }


def clinical_state_is_ready(require_food=True):
    pet = get_current_pet_profile()
    energy = get_current_energy_state()
    food = get_current_food_state()

    if not pet.get("nombre") or pet.get("nombre") == "—":
        return False, "Falta el nombre de la mascota."

    if pet.get("peso", 0) <= 0:
        return False, "Falta un peso válido de la mascota."

    if energy.get("mer_final", 0) <= 0:
        return False, "Falta calcular el requerimiento energético."

    if require_food:
        if not food.get("alimento") or food.get("alimento") == "—":
            return False, "Falta seleccionar un alimento."

        if food.get("me", 0) <= 0:
            return False, "Falta calcular la energía metabolizable del alimento."

        if not food.get("food_data_edited"):
            return False, "Falta información del alimento analizado."

    return True, "Estado clínico completo."
