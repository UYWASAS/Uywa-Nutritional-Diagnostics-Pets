"""
Página Perfil de Mascota para UYWA Pets.
Extraída desde app.py para evitar que otros módulos se rendericen al mismo tiempo.
"""

from __future__ import annotations

import base64

import pandas as pd
import streamlit as st

from energy_requirements import calcular_rer
from clinical_state import safe_float
from utils.fmt_tools import fmt2
from utils.ui_components import (
    render_section_header,
    render_risk_card,
    render_pet_identity_card,
    render_vital_card,
    render_bcs_card,
    render_energy_kpi_grid,
    render_profile_dashboard,
)
from utils.nutrient_reference import (
    NUTRIENTES_REFERENCIA_PERRO,
    NUTRIENTES_REFERENCIA_GATO,
)

# ======================== CONSTANTES GENERALES ========================

ENERGY_COVERAGE_THRESHOLD = 110
SENIOR_FACTOR = 0.85

RADAR_CHART_COLORS = [
    "#2176FF",
    "#FFB703",
    "#52B788",
    "#F4845F",
    "#8E9AAF",
    "#E74C3C",
]

RIESGO_COLORES = {
    "Bajo": "#52B788",
    "Moderado": "#FFB703",
    "Alto": "#F4845F",
}

RIESGO_ICONS = {
    "Bajo": "🟢",
    "Moderado": "🟠",
    "Alto": "🔴",
}


# ======================== FUNCIONES DE DIAGNÓSTICO ========================

def get_estado_corporal(bcs):
    """Devuelve el estado corporal textual según BCS 1–9."""
    if 1 <= bcs <= 3:
        return "Bajo peso"
    if bcs == 4:
        return "Ligeramente bajo"
    if bcs == 5:
        return "Condición ideal"
    if bcs == 6:
        return "Ligeramente sobrepeso"
    if bcs == 7:
        return "Sobrepeso"
    if 8 <= bcs <= 9:
        return "Obesidad"
    return "Desconocido"


def calcular_riesgo_nutricional(bcs, edad, condicion, etapa, aplicar_senior):
    """Calcula el nivel de riesgo nutricional del paciente."""
    if bcs == 5:
        riesgo = "Bajo"
    elif bcs in [4, 6]:
        riesgo = "Moderado"
    else:
        riesgo = "Alto"

    if aplicar_senior and bcs >= 6:
        riesgo = "Alto"

    if condicion == "Castrado" and bcs >= 6:
        riesgo = "Alto"

    if etapa == "cachorro" and condicion == "Destete a 4 meses":
        riesgo = "Moderado"

    if condicion in ["Gestación (Segunda mitad)", "Gestación (Final)", "Lactancia"]:
        riesgo = "Alto"

    return riesgo


def calcular_prioridad_nutricional(bcs, etapa, condicion, edad):
    """Devuelve prioridad nutricional y recomendación inicial."""
    if etapa == "cachorro":
        return "Sostener crecimiento", "Maximizar aporte nutricional balanceado"

    if condicion in ["Gestación (Segunda mitad)", "Gestación (Final)", "Lactancia"]:
        return "Cubrir alta demanda energética", "Aumentar frecuencia de alimentación y calidad"

    if bcs < 5:
        return "Recuperar condición corporal", "Aumentar gradualmente el aporte energético"

    if bcs > 5:
        return "Controlar peso y energía", "Reducir calorías y aumentar monitoreo"

    if edad >= 7:
        return "Mantener masa magra y prevenir sobrepeso", "Monitoreo frecuente cada 4–8 semanas"

    return "Mantener condición corporal", "Monitoreo regular cada 2–4 semanas"


def generar_interpretacion_diagnostico(
    nombre,
    bcs,
    estado,
    mer_final,
    prioridad,
    condicion,
    edad,
    aplicar_senior,
):
    """Genera diagnóstico textual automático."""
    texto = f"{nombre} presenta condición corporal {estado.lower()} (BCS {bcs}/9). "
    texto += f"Su requerimiento energético final estimado es {mer_final:.0f} kcal/día. "

    if bcs < 5:
        texto += (
            "La prioridad nutricional es recuperar condición corporal. "
            "Se recomienda aumentar gradualmente el aporte energético y monitorear peso cada 2–3 semanas."
        )
    elif bcs > 5:
        texto += (
            "La prioridad nutricional es controlar peso y energía. "
            "Se recomienda reducir calorías gradualmente y monitorear peso cada 1–2 semanas."
        )
    else:
        if edad >= 7 and aplicar_senior:
            texto += (
                "Como animal senior, la prioridad es mantener masa magra y prevenir sobrepeso. "
                "Se recomienda monitoreo frecuente cada 4–8 semanas."
            )
        elif condicion in ["Gestación (Segunda mitad)", "Gestación (Final)", "Lactancia"]:
            texto += (
                "La prioridad nutricional es cubrir la alta demanda energética. "
                "Se recomienda aumentar frecuencia de alimentación y monitoreo semanal."
            )
        else:
            texto += (
                "La prioridad es mantener la condición corporal actual. "
                "Se recomienda monitoreo regular cada 2–4 semanas."
            )

    return texto


# ======================== FACTORES ENERGÉTICOS ========================

FACTORES_CONDICION = {
    "perro": {
        "adulto": {
            "Castrado": 1.6,
            "Entero": 1.8,
            "Tendencia obesidad o inactivo": [1.2, 1.4],
            "Obeso": 1.0,
            "Bajo peso": [1.4, 1.6],
            "Gestación (Primera mitad)": 1.2,
            "Gestación (Segunda mitad)": 1.6,
            "Lactancia": [3.0, 6.0],
        },
        "cachorro": {
            "Destete a 4 meses": 3.0,
            "5 meses hasta adulto": 2.0,
        },
    },
    "gato": {
        "adulto": {
            "Castrado": 1.2,
            "Entero": 1.4,
            "Indoor": 1.0,
            "Tendencia obesidad": 1.0,
            "Obeso": 0.8,
            "Bajo peso": [1.2, 1.4],
            "Gestación (Inicio)": 1.6,
            "Gestación (Final)": 2.0,
            "Lactancia": [2.0, 6.0],
        },
        "cachorro": {
            "Destete a 4 meses": 3.0,
            "5 meses hasta adulto": 2.0,
        },
    },
}

CONDICIONES_GESTACION = {
    "Gestación (Primera mitad)",
    "Gestación (Segunda mitad)",
    "Gestación (Inicio)",
    "Gestación (Final)",
}

CONDICIONES_GESTACION_INICIAL = {
    "Gestación (Primera mitad)",
    "Gestación (Inicio)",
}

CONDICIONES_GESTACION_FINAL = {
    "Gestación (Segunda mitad)",
    "Gestación (Final)",
}


def show_profile_page(profile: dict, update_and_save_profile, reset_species_dependent_state) -> None:
    render_section_header(
        title="Perfil clínico-nutricional",
        kicker="Paciente y requerimiento energético",
        subtitle=(
            "Registra los datos del paciente, estima sus requerimientos energéticos "
            "y genera una interpretación nutricional inicial."
        ),
    )

    # --- Formulario de edición en expander ---
    mascota = profile.get("mascota", {})

    with st.expander("✏️ Editar perfil clínico del paciente", expanded=True):

        st.markdown("### 1. Datos básicos del paciente")

        ef_col1, ef_col2 = st.columns(2)

        with ef_col1:
            nombre_mascota = st.text_input(
                "Nombre de la mascota",
                value=mascota.get("nombre", "Mascota"),
                key="nombre_mascota",
            )

            especie = st.selectbox(
                "Especie",
                ["perro", "gato"],
                index=["perro", "gato"].index(
                    mascota.get("especie", "perro").lower()
                ),
                key="especie_mascota",
            )

            edad = st.number_input(
                "Edad en años",
                min_value=0.1,
                max_value=20.0,
                value=max(0.1, safe_float(mascota.get("edad", 1.0), 1.0)),
                step=0.1,
                key="edad_mascota",
            )

        with ef_col2:
            peso = st.number_input(
                "Peso en kg",
                min_value=0.1,
                max_value=200.0,
                value=max(0.1, safe_float(mascota.get("peso", 12.0), 12.0)),
                step=0.1,
                key="peso_mascota",
            )

            etapa = st.selectbox(
                "Etapa de vida",
                ["adulto", "cachorro"],
                index=["adulto", "cachorro"].index(
                    mascota.get("etapa", "adulto").lower()
                ),
                key="etapa_mascota",
            )

        st.markdown("---")
        st.markdown("### 2. Condición fisiológica")

        _especie_form_cond = st.session_state.get(
            "especie_mascota",
            mascota.get("especie", "perro"),
        )

        _etapa_actual_form = st.session_state.get(
            "etapa_mascota",
            mascota.get("etapa", "adulto"),
        )

        if _etapa_actual_form == "adulto":
            if _especie_form_cond == "perro":
                opciones_condicion = [
                    "Castrado",
                    "Entero",
                    "Gestación (Primera mitad)",
                    "Gestación (Segunda mitad)",
                    "Lactancia",
                ]
            else:
                opciones_condicion = [
                    "Castrado",
                    "Entero",
                    "Indoor",
                    "Tendencia obesidad",
                    "Obeso",
                    "Bajo peso",
                    "Gestación (Inicio)",
                    "Gestación (Final)",
                    "Lactancia",
                ]
        else:
            opciones_condicion = [
                "Destete a 4 meses",
                "5 meses hasta adulto",
            ]

        condicion_predeterminada = mascota.get("condicion", "Castrado")

        if condicion_predeterminada not in opciones_condicion:
            condicion_predeterminada = opciones_condicion[0]

        condicion = st.selectbox(
            "Condición fisiológica/productiva",
            opciones_condicion,
            index=opciones_condicion.index(condicion_predeterminada),
            key="condicion_mascota",
        )

        st.markdown("---")
        st.markdown("### 3. Estado corporal")

        bcs_disabled = (
            st.session_state.get(
                "etapa_mascota",
                mascota.get("etapa", "adulto"),
            ) == "cachorro"
            and condicion == "Destete a 4 meses"
        )

        bcs_val = max(
            1,
            min(
                9,
                int(safe_float(mascota.get("bcs", 5), 5)),
            ),
        )

        bcs = st.slider(
            "Condición Corporal (BCS 1–9)",
            min_value=1,
            max_value=9,
            value=bcs_val,
            key="bcs_mascota",
            disabled=bcs_disabled,
        )

        if bcs_disabled:
            st.info(
                "En cachorros destete a 4 meses, el BCS puede no ser el criterio principal "
                "para ajustar el requerimiento energético."
            )

        _edad_form = safe_float(
            st.session_state.get(
                "edad_mascota",
                mascota.get("edad", 1.0),
            ),
            1.0,
        )

        if _etapa_actual_form == "adulto" and _especie_form_cond in ("perro", "gato"):
            _stored_senior = mascota.get("aplicar_ajuste_senior")
            _senior_default = (
                bool(_stored_senior)
                if _stored_senior is not None
                else (_edad_form >= 7)
            )

            aplicar_ajuste_senior_form = st.checkbox(
                "👴 Aplicar ajuste energético Senior (-15%)",
                value=_senior_default,
                key="aplicar_ajuste_senior_mascota",
                help=(
                    "Reduce el MER en un 15% para mascotas adultas senior. "
                    "Puede aplicarse adicionalmente al ajuste por condición corporal bajo criterio veterinario."
                ),
            )

            if _edad_form >= 7:
                st.info("Recomendado para mascotas adultas mayores de 7 años.")
        else:
            aplicar_ajuste_senior_form = False

            if "aplicar_ajuste_senior_mascota" in st.session_state:
                del st.session_state["aplicar_ajuste_senior_mascota"]

        st.markdown("---")
        st.markdown("### 4. Foto del paciente")

        foto_upload = st.file_uploader(
            "Foto de la mascota (opcional)",
            type=["png", "jpg", "jpeg"],
            key="foto_mascota_upload",
        )

        if foto_upload is not None:
            st.session_state["mascota_foto_bytes"] = foto_upload.getvalue()

        if st.session_state.get("mascota_foto_bytes"):
            col_prev, col_del = st.columns([1, 3])

            with col_prev:
                st.image(
                    st.session_state["mascota_foto_bytes"],
                    width=120,
                    caption="Vista previa",
                )

            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("🗑️ Eliminar foto", key="del_foto_perfil"):
                    del st.session_state["mascota_foto_bytes"]
                    st.rerun()

        st.markdown("---")

        if st.button(
            "💾 Guardar perfil de mascota",
            key="guardar_perfil_btn",
            use_container_width=True,
        ):
            mascota_actualizada = {
                "nombre": st.session_state["nombre_mascota"],
                "especie": st.session_state["especie_mascota"].lower(),
                "edad": st.session_state["edad_mascota"],
                "peso": st.session_state["peso_mascota"],
                "etapa": st.session_state["etapa_mascota"].lower(),
                "condicion": condicion,
                "bcs": st.session_state.get("bcs_mascota", 5),
                "aplicar_ajuste_senior": st.session_state.get(
                    "aplicar_ajuste_senior_mascota",
                    False,
                ),
            }

            profile["mascota"] = mascota_actualizada
            update_and_save_profile(profile)
            st.success("✅ Perfil actualizado correctamente.")

    # Leer valores actuales (del estado de sesión si fueron modificados, o del perfil guardado)
    especie = st.session_state.get("especie_mascota", mascota.get("especie", "perro"))
    _last_species = st.session_state.get("_last_species_rendered")

    if _last_species is None:
        st.session_state["_last_species_rendered"] = especie

    elif _last_species != especie:
        st.session_state["_last_species_rendered"] = especie
        reset_species_dependent_state()
        st.rerun()
    etapa = st.session_state.get("etapa_mascota", mascota.get("etapa", "adulto"))
    condicion = st.session_state.get("condicion_mascota", mascota.get("condicion", "Castrado"))
    bcs = max(1, min(9, int(safe_float(st.session_state.get("bcs_mascota", mascota.get("bcs", 5)), 5))))
    peso = max(0.1, safe_float(st.session_state.get("peso_mascota", mascota.get("peso", 12.0)), 12.0))
    edad = safe_float(st.session_state.get("edad_mascota", mascota.get("edad", 1.0)), 1.0)
    bcs_disabled = etapa == "cachorro" and condicion == "Destete a 4 meses"

    # Leer ajuste senior: desde session_state (widget) o desde perfil guardado
    if etapa == "adulto" and especie in ("perro", "gato"):
        _stored_senior = mascota.get("aplicar_ajuste_senior")
        _senior_profile_default = bool(_stored_senior) if _stored_senior is not None else (edad >= 7)
        aplicar_ajuste_senior = bool(st.session_state.get("aplicar_ajuste_senior_mascota", _senior_profile_default))
    else:
        aplicar_ajuste_senior = False

    # --- Cálculo del RER y MER (necesario antes del layout) ---
    try:
        energia_basal_actual = calcular_rer(peso)
        factores_etapa = FACTORES_CONDICION.get(especie, {}).get(etapa, {}).get(condicion, None)
        if factores_etapa is None:
            raise ValueError(f"Condición desconocida para '{especie}'.")
        factor_fisiologico = factores_etapa if isinstance(factores_etapa, (int, float)) else factores_etapa[0]
        mer_actual = energia_basal_actual * factor_fisiologico

        factores_bcs = {6: 0.9, 7: 0.8, 8: 0.7, 9: 0.6, 4: 1.1, 3: 1.2, 2: 1.3, 1: 1.4}

        # Determine if condition is gestación
        es_gestacion = condicion in CONDICIONES_GESTACION

        if es_gestacion and not bcs_disabled:
            # For gestating animals, BCS adjustment is only applied at extreme values (≤3 or ≥7).
            # BCS 4–6 is considered an acceptable range for a gestante; no adjustment is needed
            # because moderate variation in body condition is normal during pregnancy.
            bcs_gestacion_extremo = bcs <= 3 or bcs >= 7
            if bcs_gestacion_extremo:
                # BCS extreme: apply adjustment
                peso_objetivo = peso * factores_bcs.get(bcs, 1.0)
                energia_basal_objetivo = calcular_rer(peso_objetivo)
                mer_final = energia_basal_objetivo * factor_fisiologico
            else:
                # BCS 4–6: acceptable range for gestante, no BCS adjustment
                peso_objetivo = "-"
                energia_basal_objetivo = "-"
                mer_final = mer_actual
        elif not es_gestacion and bcs != 5 and not bcs_disabled:
            peso_objetivo = peso * factores_bcs.get(bcs, 1.0)
            energia_basal_objetivo = calcular_rer(peso_objetivo)
            mer_final = energia_basal_objetivo * factor_fisiologico
            bcs_gestacion_extremo = False
        else:
            peso_objetivo = "-"
            energia_basal_objetivo = "-"
            mer_final = mer_actual
            bcs_gestacion_extremo = False
        factor_condicion_val = round(mer_final / energia_basal_actual, 2) if energia_basal_actual > 1e-6 else "-"

        # --- Ajuste senior (paso final, después de todos los cálculos de BCS) ---
        senior_aplicado = False
        if (etapa == "adulto"
                and aplicar_ajuste_senior
                and not bcs_disabled):
            mer_final = mer_final * SENIOR_FACTOR
            senior_aplicado = True

        st.session_state["energia_actual"] = mer_final
        # Almacenar valores intermedios para Pestaña 3
        st.session_state["rer_actual"] = energia_basal_actual
        st.session_state["mer_base_actual"] = mer_actual
        st.session_state["factor_fisiologico_actual"] = factor_fisiologico
        st.session_state["senior_aplicado_actual"] = senior_aplicado

    except Exception as e:
        st.error(f"Error en cálculos energéticos: {str(e)}")
        st.stop()

    # ===================== LAYOUT DE 2 COLUMNAS =====================
    col_left, col_right = st.columns([3, 7])

    with col_left:
        especie_icon = "🐕" if especie == "perro" else "🐈"

        nombre_display = st.session_state.get(
            "nombre_mascota",
            mascota.get("nombre", "Mascota")
        ) or "Mascota"

        foto_bytes = st.session_state.get("mascota_foto_bytes")
        foto_b64 = base64.b64encode(foto_bytes).decode("utf-8") if foto_bytes else None

        render_pet_identity_card(
            nombre=nombre_display,
            especie=especie,
            etapa=etapa,
            especie_icon=especie_icon,
            foto_b64=foto_b64,
        )

    with col_right:
        # --- Datos Vitales en cards (2 por fila) ---
        edad_display = max(0.0, safe_float(st.session_state.get("edad_mascota", mascota.get("edad", 1.0)), 1.0))
        bcs_pct = int((bcs / 9) * 100)
        bcs_color = "#52b788" if 4 <= bcs <= 6 else ("#f4845f" if bcs > 6 else "#fbbf24")

    with col_right:
        edad_display = max(
            0.0,
            safe_float(
                st.session_state.get("edad_mascota", mascota.get("edad", 1.0)),
                1.0,
            ),
        )

        bcs_pct = int((bcs / 9) * 100)
        bcs_color = "#52b788" if 4 <= bcs <= 6 else ("#f4845f" if bcs > 6 else "#fbbf24")

        vc1, vc2 = st.columns(2)

        with vc1:
            render_vital_card(
                title="Edad",
                value=f"{fmt2(edad_display)} años",
                icon="🎂",
                color="#2563EB",
            )

        with vc2:
            render_vital_card(
                title="Peso",
                value=f"{fmt2(peso)} kg",
                icon="⚖️",
                color="#16A34A",
            )

        vc3, vc4 = st.columns(2)

        with vc3:
            render_bcs_card(
                bcs=bcs,
                bcs_pct=bcs_pct,
                bcs_color=bcs_color,
            )

        with vc4:
            render_vital_card(
                title="Condición fisiológica",
                value=condicion,
                icon="🛠️",
                color="#64748B",
            )
    # ===================== DASHBOARD EJECUTIVO DEL PERFIL =====================
    _estado_preview = get_estado_corporal(bcs)
    _riesgo_preview = calcular_riesgo_nutricional(
        bcs, edad, condicion, etapa, aplicar_ajuste_senior
    )

    render_profile_dashboard(
        nombre=nombre_display,
        especie=especie,
        etapa=etapa,
        peso=peso,
        edad=edad,
        bcs=bcs,
        estado_preview=_estado_preview,
        riesgo_preview=_riesgo_preview,
        mer_final=mer_final,
        senior_aplicado=senior_aplicado,
        fmt_func=fmt2,
    )

    # ===================== DIAGNÓSTICO NUTRICIONAL INICIAL (ANCHO COMPLETO) =====================
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    render_section_header(
        title="Estado corporal y diagnóstico inicial",
        kicker="Interpretación clínica",
        subtitle="Interpretación automática basada en BCS, edad, etapa de vida y condición fisiológica.",
    )

    _estado_corporal = get_estado_corporal(bcs)
    _riesgo = calcular_riesgo_nutricional(bcs, edad, condicion, etapa, aplicar_ajuste_senior)
    _prioridad, _recomendacion = calcular_prioridad_nutricional(bcs, etapa, condicion, edad)
    _interpretacion = generar_interpretacion_diagnostico(
        nombre_display, bcs, _estado_corporal, mer_final,
        _prioridad, condicion, edad, aplicar_ajuste_senior
    )

    _riesgo_class = {"Bajo": "low-risk", "Moderado": "moderate-risk", "Alto": "high-risk"}.get(_riesgo, "low-risk")
    _riesgo_icon = RIESGO_ICONS.get(_riesgo, "🟢")

    # Almacenar diagnóstico para Pestaña 3
    st.session_state["estado_corporal_tab1"] = _estado_corporal
    st.session_state["riesgo_nutricional_tab1"] = _riesgo
    st.session_state["prioridad_nutricional_tab1"] = _prioridad
    st.session_state["interpretacion_diagnostico_tab1"] = _interpretacion

    render_risk_card(
        risk=_riesgo,
        title=f"Riesgo {_riesgo.upper()}",
        lines=[
            f"Estado corporal: {_estado_corporal} (BCS {bcs}/9)",
            f"Prioridad: {_prioridad}",
            f"Recomendación: {_recomendacion}",
        ],
        text=_interpretacion,
    )

    # ===================== SECCIÓN ENERGÍA (ANCHO COMPLETO) =====================
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    render_section_header(
        title="Requerimiento energético",
        kicker="Cálculo RER / MER",
        subtitle="Resumen del requerimiento energético basal, fisiológico y ajustado del paciente.",
    )

    render_energy_kpi_grid(
        energia_basal_actual=energia_basal_actual,
        mer_actual=mer_actual,
        mer_final=mer_final,
        factor_fisiologico=factor_fisiologico,
        factor_condicion_val=factor_condicion_val,
        senior_aplicado=senior_aplicado,
        fmt_func=fmt2,
    )

    # Aviso cuando ajuste senior no se aplica por BCS ≠ 5
    if aplicar_ajuste_senior and not senior_aplicado and etapa == "adulto" and especie in ("perro", "gato"):
        st.warning("⚠️ Ajuste senior no aplicado porque el requerimiento fue priorizado por corrección de condición corporal.")

    # Mensajes informativos para gestación
    if es_gestacion and not bcs_disabled:
        if not bcs_gestacion_extremo:
            st.info("ℹ️ Ajuste BCS no aplicado: La gestante se encuentra en condición corporal aceptable. "
                    "El requerimiento se basa únicamente en el factor de gestación.")
        else:
            st.warning("⚠️ Condición corporal fuera de rango ideal. Se aplicará corrección adicional por BCS.")

    # Botón de edición
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    if st.button("✏️ Editar perfil", key="btn_editar_perfil_shortcut"):
        st.info("Usa el panel **✏️ Editar Perfil de la Mascota** en la parte superior para modificar los datos.")

    # ===================== TABLAS DETALLADAS (ANCHO COMPLETO) =====================
    try:
        # Descripción condicional para MER Actual según gestación
        if condicion in CONDICIONES_GESTACION_INICIAL:
            _desc_mer_actual = "Incremento energético asociado al desarrollo embrionario inicial y adaptación metabólica materna."
        elif condicion in CONDICIONES_GESTACION_FINAL:
            _desc_mer_actual = "Incremento energético elevado por crecimiento fetal acelerado y preparación para la lactancia."
        else:
            _desc_mer_actual = "Energía diaria necesaria según la condición productiva y fisiológica."

        # Tabla de energías calculadas
        _senior_valor = "Aplicado: ×0.85" if senior_aplicado else "No aplicado"
        energia_data = [
            {"Tipo": "RER Actual", "Valor": f"{fmt2(energia_basal_actual)} kcal/día", "Descripción": "Energía necesaria en reposo para mantener funciones básicas como respirar y digerir."},
            {"Tipo": "MER Actual (RER × Factor Fisiológico)", "Valor": f"{fmt2(mer_actual)} kcal/día", "Descripción": _desc_mer_actual},
            {"Tipo": "Peso Objetivo", "Valor": f"{fmt2(peso_objetivo)} kg" if peso_objetivo != "-" else "-", "Descripción": "Peso estimado para ajustar según la condición corporal (BCS)."},
            {"Tipo": "RER Objetivo", "Valor": f"{fmt2(energia_basal_objetivo)} kcal/día" if energia_basal_objetivo != "-" else "-", "Descripción": "Energía en reposo recalculada con el peso objetivo."},
            {"Tipo": "Ajuste senior", "Valor": _senior_valor, "Descripción": "Corrección energética opcional (-15%, ×0.85) para animales adultos senior (7+ años), usada solo cuando la condición corporal es ideal."},
            {"Tipo": "MER Ajustada Final", "Valor": f"{fmt2(mer_final)} kcal/día", "Descripción": "Energía total diaria necesaria tras ajustes por BCS y condición."},
        ]

        with st.expander("📋 Ver detalle del cálculo energético", expanded=False):
            html_table = "<table class='energy-table'><thead><tr><th>Tipo de Energía</th><th>Valor</th><th>Descripción</th></tr></thead><tbody>"
            for entry in energia_data:
                html_table += f"<tr><td>{entry['Tipo']}</td><td>{entry['Valor']}</td><td>{entry['Descripción']}</td></tr>"
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)

        # Tabla de nutrientes ajustados
        nutrientes_ref = NUTRIENTES_REFERENCIA_PERRO if especie == "perro" else NUTRIENTES_REFERENCIA_GATO
        nutrientes_especie_etapa = nutrientes_ref.get(etapa, {})
        kg_dieta_necesaria = mer_final / 4000.0

        requerimientos_ajustados = []
        _req_pb_g = None
        _req_ee_g = None
        for nutriente, valores in nutrientes_especie_etapa.items():
            unidad = valores.get("unit", "")
            min_valor = valores.get("min", None)
            max_valor = valores.get("max", None)

            if unidad == "%":
                min_ajustado = (min_valor / 100.0) * kg_dieta_necesaria * 1000 if min_valor is not None else None
                max_ajustado = (max_valor / 100.0) * kg_dieta_necesaria * 1000 if max_valor is not None else None
                nueva_unidad = "g"
                if nutriente == "Proteína" and min_ajustado is not None:
                    _req_pb_g = min_ajustado
                elif nutriente == "Grasa" and min_ajustado is not None:
                    _req_ee_g = min_ajustado
            elif unidad in ["mg/kg", "UI/kg", "IU/kg", "µg/kg"]:
                unidad_base = unidad.replace("/kg", "")
                min_ajustado = min_valor * kg_dieta_necesaria if min_valor is not None else None
                max_ajustado = max_valor * kg_dieta_necesaria if max_valor is not None else None
                nueva_unidad = unidad_base
            else:
                min_ajustado = min_valor
                max_ajustado = max_valor
                nueva_unidad = unidad if unidad else "-"

            requerimientos_ajustados.append({
                "Nutriente": nutriente,
                "Min Ajustado": fmt2(min_ajustado) if min_ajustado is not None else "-",
                "Max Ajustado": fmt2(max_ajustado) if max_ajustado is not None else "-",
                "Unidad": nueva_unidad,
            })

        st.session_state["req_pb_g"] = _req_pb_g
        st.session_state["req_ee_g"] = _req_ee_g

        df_nutrientes_ajustados = pd.DataFrame(requerimientos_ajustados)
        st.session_state["tabla_requerimientos_base"] = df_nutrientes_ajustados.copy()

        with st.expander("📋 Ver requerimientos nutricionales ajustados", expanded=False):
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption(
                "Los requerimientos se ajustan según especie, etapa de vida y MER final estimado."
            )
            html_nutrientes = "<table class='nutrients-table'><thead><tr><th>Nutriente</th><th>Min Ajustado</th><th>Max Ajustado</th><th>Unidad</th></tr></thead><tbody>"
            for req in requerimientos_ajustados:
                html_nutrientes += f"<tr><td>{req['Nutriente']}</td><td>{req['Min Ajustado']}</td><td>{req['Max Ajustado']}</td><td>{req['Unidad']}</td></tr>"
            html_nutrientes += "</tbody></table>"
            st.markdown(html_nutrientes, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error en cálculos y ajustes: {str(e)}")
        st.stop()
