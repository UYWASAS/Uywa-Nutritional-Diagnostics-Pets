"""
clinical_state.py

Módulo centralizado para leer el estado clínico actual de la aplicación UYWA.

Objetivo:
- Evitar duplicación de lecturas desde st.session_state.
- Unificar datos de mascota, energía y alimento.
- Preparar la app para seguimiento clínico, exportación y futuras mejoras.
"""

import streamlit as st


def safe_float(value, default=0.0):
    """
    Convierte valores a float de forma segura.
    Acepta coma decimal como entrada.
    """
    try:
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    """
    Convierte valores a int de forma segura.
    """
    try:
        return int(round(safe_float(value, default)))
    except Exception:
        return default


def get_current_profile_raw():
    """
    Devuelve el perfil completo almacenado en session_state.
    """
    return st.session_state.get("profile", {}) or {}


def get_current_pet_profile():
    """
    Devuelve los datos actuales de la mascota/paciente.

    Prioridad:
    1. Valores actuales de widgets en session_state.
    2. Valores guardados en profile["mascota"].
    3. Valores por defecto.
    """
    profile = get_current_profile_raw()
    mascota = profile.get("mascota", {}) or {}

    bcs = safe_int(
        st.session_state.get("bcs_mascota", mascota.get("bcs", 5)),
        5,
    )
    bcs = max(1, min(9, bcs))

    return {
        "nombre": st.session_state.get(
            "nombre_mascota",
            mascota.get("nombre", "—"),
        ) or "—",
        "especie": st.session_state.get(
            "especie_mascota",
            mascota.get("especie", "perro"),
        ),
        "edad": safe_float(
            st.session_state.get("edad_mascota", mascota.get("edad", 0)),
            0,
        ),
        "peso": safe_float(
            st.session_state.get("peso_mascota", mascota.get("peso", 0)),
            0,
        ),
        "etapa": st.session_state.get(
            "etapa_mascota",
            mascota.get("etapa", "adulto"),
        ),
        "condicion": st.session_state.get(
            "condicion_mascota",
            mascota.get("condicion", "Castrado"),
        ),
        "bcs": bcs,
        "aplicar_ajuste_senior": bool(
            st.session_state.get(
                "aplicar_ajuste_senior_mascota",
                mascota.get("aplicar_ajuste_senior", False),
            )
        ),
    }


def get_current_energy_state():
    """
    Devuelve el estado energético calculado en la pestaña Perfil.
    """
    return {
        "rer": safe_float(st.session_state.get("rer_actual", 0)),
        "mer_base": safe_float(st.session_state.get("mer_base_actual", 0)),
        "mer_final": safe_float(st.session_state.get("energia_actual", 0)),
        "factor_fisiologico": safe_float(
            st.session_state.get("factor_fisiologico_actual", 0)
        ),
        "senior_aplicado": bool(
            st.session_state.get("senior_aplicado_actual", False)
        ),
        "estado_corporal": st.session_state.get(
            "estado_corporal_tab1",
            "—",
        ),
        "riesgo_nutricional": st.session_state.get(
            "riesgo_nutricional_tab1",
            "—",
        ),
        "prioridad_nutricional": st.session_state.get(
            "prioridad_nutricional_tab1",
            "—",
        ),
        "diagnostico": st.session_state.get(
            "interpretacion_diagnostico_tab1",
            "—",
        ),
        "req_pb_g": st.session_state.get("req_pb_g", None),
        "req_ee_g": st.session_state.get("req_ee_g", None),
    }


def get_current_food_state():
    """
    Devuelve el estado actual del alimento analizado.
    """
    food_name = st.session_state.get("analysis_food_selector", "—")

    gramos = safe_float(
        st.session_state.get(f"gramos_alimento_{food_name}", 0),
        0,
    )

    return {
        "alimento": food_name,
        "gramos": gramos,
        "me": safe_float(st.session_state.get("me_alimento_actual", 0)),
        "energia_aportada": safe_float(
            st.session_state.get("energia_aportada_actual", 0)
        ),
        "cobertura_energia": safe_float(
            st.session_state.get("cobertura_energia_actual", 0)
        ),
        "gramos_recomendados": safe_float(
            st.session_state.get("gramos_recomendados_actual", 0)
        ),
        "cobertura_proteina": st.session_state.get(
            "cobertura_proteina_actual",
            None,
        ),
        "cobertura_grasa": st.session_state.get(
            "cobertura_grasa_actual",
            None,
        ),
        "food_data_edited": st.session_state.get(
            "analysis_food_data_edited",
            {},
        ),
    }


def get_current_clinical_state():
    """
    Devuelve un paquete completo con:
    - perfil de mascota
    - energía
    - alimento
    """
    return {
        "pet": get_current_pet_profile(),
        "energy": get_current_energy_state(),
        "food": get_current_food_state(),
    }


def clinical_state_is_ready(require_food=True):
    """
    Verifica si existe información suficiente para exportar o registrar visita.

    Parámetros:
        require_food (bool): si True, exige también alimento analizado.

    Retorna:
        tuple(bool, str)
    """
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

    return True, "Estado clínico completo."
