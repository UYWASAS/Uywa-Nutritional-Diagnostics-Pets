import streamlit as st


def safe_float(value, default=0.0):
    try:
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
    except Exception:
        return default


def get_current_pet_profile():
    profile = st.session_state.get("profile", {})
    mascota = profile.get("mascota", {})

    return {
        "nombre": st.session_state.get("nombre_mascota", mascota.get("nombre", "—")) or "—",
        "especie": st.session_state.get("especie_mascota", mascota.get("especie", "perro")),
        "edad": safe_float(st.session_state.get("edad_mascota", mascota.get("edad", 0))),
        "peso": safe_float(st.session_state.get("peso_mascota", mascota.get("peso", 0))),
        "etapa": st.session_state.get("etapa_mascota", mascota.get("etapa", "adulto")),
        "condicion": st.session_state.get("condicion_mascota", mascota.get("condicion", "Castrado")),
        "bcs": int(safe_float(st.session_state.get("bcs_mascota", mascota.get("bcs", 5)), 5)),
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
    }


def get_current_food_state():
    return {
        "alimento": st.session_state.get("analysis_food_selector", "—"),
        "me": safe_float(st.session_state.get("me_alimento_actual", 0)),
        "energia_aportada": safe_float(st.session_state.get("energia_aportada_actual", 0)),
        "cobertura_energia": safe_float(st.session_state.get("cobertura_energia_actual", 0)),
        "gramos_recomendados": safe_float(st.session_state.get("gramos_recomendados_actual", 0)),
        "cobertura_proteina": st.session_state.get("cobertura_proteina_actual", None),
        "cobertura_grasa": st.session_state.get("cobertura_grasa_actual", None),
    }
