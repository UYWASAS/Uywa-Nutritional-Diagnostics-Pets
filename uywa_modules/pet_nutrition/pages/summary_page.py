"""
Página Resumen y Exportar para UYWA Pets.
"""

from __future__ import annotations

import datetime

import streamlit as st

from ..core.clinical_state import (
    clinical_state_is_ready,
    get_current_clinical_state,
)

from ..foods.food_database import (
    FOODS,
    calculate_energy as calc_energy_food,
    calculate_ena as calc_ena_food,
    calculate_energy_breakdown,
)
from ..exports.export_tools import (
    generar_diagnostico_resumen,
    generar_recomendaciones,
    generar_decision_resumen,
    exportar_a_html,
    exportar_ficha_maestra_excel,
)
from utils.nutrient_reference import (
    NUTRIENTES_REFERENCIA_PERRO,
    NUTRIENTES_REFERENCIA_GATO,
)
from .profile_page import get_estado_corporal

def show_summary_page() -> None:
    st.header("📋 Resumen y Exportación")

    ready, ready_message = clinical_state_is_ready(require_food=False)
    state = get_current_clinical_state()

    pet = state["pet"]
    energy = state["energy"]
    food = state["food"]

    _nombre3 = pet.get("nombre", "—")
    _especie3 = pet.get("especie", "perro")
    _edad3 = pet.get("edad", 0.0)
    _peso3 = pet.get("peso", 0.0)
    _etapa3 = pet.get("etapa", "adulto")
    _condicion3 = pet.get("condicion", "Castrado")
    _bcs3 = pet.get("bcs", 5)

    _mer_final3 = energy.get("mer_final", 0.0)
    _rer3 = energy.get("rer", 0.0)
    _mer_base3 = energy.get("mer_base", 0.0)
    _factor_fis3 = energy.get("factor_fisiologico", 0.0)
    _senior3 = energy.get("senior_aplicado", False)
    _estado_corp3 = energy.get("estado_corporal", get_estado_corporal(_bcs3))
    _riesgo3 = energy.get("riesgo_nutricional", "—")
    _prioridad3 = energy.get("prioridad_nutricional", "—")
    _aplicar_senior3 = pet.get("aplicar_ajuste_senior", False)

    _food_name3 = food.get("alimento", "—")
    _food_data3 = food.get("food_data_edited", {}) or {}

    if not _food_data3 and _food_name3 in FOODS:
        _food_data3 = FOODS.get(_food_name3, {})

    _gramos3 = food.get("gramos", 0.0)

    if _food_data3:
        _species_food3 = _food_data3.get("species", _especie3)

        _food_energy3 = calc_energy_food(
            _food_data3,
            species=_species_food3,
        )

        _food_ena3 = calc_ena_food(_food_data3)

        _food_eb3 = calculate_energy_breakdown(
            _food_data3,
            species=_species_food3,
        )
    else:
        _food_energy3 = {}
        _food_ena3 = 0.0
        _food_eb3 = {}

    _me3 = food.get("me", 0.0) or _food_energy3.get("ME", 0.0)
    _aporte3 = food.get("energia_aportada", 0.0)

    if not _aporte3 and _me3 > 0 and _gramos3 > 0:
        _aporte3 = (_me3 / 100.0) * _gramos3

    _req_pb3 = energy.get("req_pb_g", None)
    _req_ee3 = energy.get("req_ee_g", None)

    _gramos_pb3 = (_food_data3.get("PB", 0) / 100.0) * _gramos3 if _food_data3 else 0.0
    _gramos_ee3 = (_food_data3.get("EE", 0) / 100.0) * _gramos3 if _food_data3 else 0.0

    _datos_completos = (
        _mer_final3 is not None
        and _mer_final3 > 0
        and _food_name3 not in [None, "", "—"]
        and _me3 > 0
    )

    if _datos_completos:
        _cobertura3 = (_aporte3 / _mer_final3) * 100.0
        _gramos_rec3 = (_mer_final3 / (_me3 / 100.0)) if _me3 > 0 else 0.0
        _dif_g3 = _gramos_rec3 - _gramos3
        _cob_pb3 = (_gramos_pb3 / _req_pb3 * 100.0) if (_req_pb3 and _req_pb3 > 0) else None
        _cob_ee3 = (_gramos_ee3 / _req_ee3 * 100.0) if (_req_ee3 and _req_ee3 > 0) else None
    else:
        _cobertura3 = 0.0
        _gramos_rec3 = 0.0
        _dif_g3 = 0.0
        _cob_pb3 = None
        _cob_ee3 = None

    _diagnostico3 = generar_diagnostico_resumen(
        _nombre3,
        _bcs3,
        _estado_corp3,
        _mer_final3 or 0.0,
        _prioridad3,
        _condicion3,
        _edad3,
        _aplicar_senior3,
    )

    if _datos_completos:
        _resultado3, _dif_kcal3, _interpretacion3 = generar_decision_resumen(
            _cobertura3,
            _aporte3,
            _mer_final3 or 0.0,
            _gramos3,
            _gramos_rec3,
            _cob_pb3,
            _cob_ee3,
        )
    else:
        _resultado3, _dif_kcal3, _interpretacion3 = (
            "—",
            0.0,
            "Complete el perfil y el análisis de alimento.",
        )

    _recomendaciones3 = generar_recomendaciones(
        _estado_corp3,
        _bcs3,
        _edad3,
        _condicion3,
        _cobertura3 if _datos_completos else None,
        _cob_pb3,
        _cob_ee3,
    )

    st.subheader("👤 Resumen del Paciente")

    if ready:
        st.success("Perfil energético completo.")
    else:
        st.warning(ready_message)

    _rc1, _rc2 = st.columns(2)

    with _rc1:
        st.markdown(f"**Nombre:** {_nombre3}")
        st.markdown(f"**Especie:** {_especie3.capitalize()}")
        st.markdown(f"**Edad:** {_edad3:.1f} años")
        st.markdown(f"**Peso actual:** {_peso3:.1f} kg")

    with _rc2:
        st.markdown(f"**Etapa de vida:** {_etapa3.capitalize()}")
        st.markdown(f"**Condición fisiológica:** {_condicion3}")
        st.markdown(f"**BCS:** {_bcs3}/9")
        st.markdown(f"**Estado corporal:** {_estado_corp3}")
        st.markdown(f"**Riesgo nutricional:** {_riesgo3}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🩺 Diagnóstico Nutricional")
    st.info(_diagnostico3)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚡ Requerimiento Energético")

    if _mer_final3 and _mer_final3 > 0:
        _ec1, _ec2, _ec3, _ec4 = st.columns(4)

        with _ec1:
            st.metric("🔋 RER", f"{_rer3:.1f} kcal/día")

        with _ec2:
            st.metric("📊 MER base", f"{_mer_base3:.1f} kcal/día")

        with _ec3:
            st.metric("🎯 MER final", f"{_mer_final3:.1f} kcal/día")

        with _ec4:
            _sen_adj = "Sí" if _senior3 else "No"
            st.metric("👴 Senior aplicado", _sen_adj)

        with st.expander("Ver detalle energético", expanded=False):
            st.markdown(f"**Factor fisiológico:** {_factor_fis3:.2f}")
            st.markdown(f"**Ajuste senior:** {'Sí' if _senior3 else 'No'}")
            st.markdown(f"**Diagnóstico base:** {energy.get('diagnostico', '—')}")
    else:
        st.warning("Completa primero la pestaña Perfil de Mascota.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🍽️ Análisis del Alimento")

    if _food_name3 not in [None, "", "—"] and _food_data3:
        _fa1, _fa2 = st.columns(2)

        with _fa1:
            st.markdown(f"**Alimento seleccionado:** {_food_name3}")
            st.metric("⚡ ME", f"{_me3:.2f} kcal/100g")
            st.metric("🥣 Gramos evaluados", f"{_gramos3:.0f} g/día")
            st.metric("🔥 Energía aportada", f"{_aporte3:.1f} kcal/día")

        with _fa2:
            _comp_rows = [
                ("Proteína Bruta (PB %)", _food_data3.get("PB", 0)),
                ("Grasa (EE %)", _food_data3.get("EE", 0)),
                ("Cenizas (%)", _food_data3.get("Ash", 0)),
                ("Humedad (%)", _food_data3.get("Humidity", 0)),
                ("Fibra Cruda (FC %)", _food_data3.get("FC", 0)),
                ("ENA (%)", round(_food_ena3, 2)),
            ]

            for _n, _v in _comp_rows:
                st.markdown(f"**{_n}:** {_v:.2f}")

            if _food_data3.get("ingredients"):
                st.caption(f"Ingredientes: {_food_data3.get('ingredients')}")
    else:
        st.warning("Selecciona y analiza un alimento en la pestaña Análisis.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("✅ Decisión Nutricional")

    if _datos_completos:
        if _cobertura3 < 90:
            st.warning(_resultado3)
        elif _cobertura3 <= 110:
            st.success(_resultado3)
        else:
            st.error(_resultado3)

        st.markdown(_interpretacion3)

        _cq1, _cq2, _cq3 = st.columns(3)

        with _cq1:
            st.metric("Cobertura energética", f"{_cobertura3:.1f}%")

        with _cq2:
            st.metric("Gramos recomendados", f"{_gramos_rec3:.0f} g/día")

        with _cq3:
            _signo_g = "+" if _dif_g3 > 0 else ""
            st.metric("Diferencia vs evaluado", f"{_signo_g}{_dif_g3:.0f} g")
    else:
        st.info("Complete perfil y análisis del alimento para generar decisión nutricional.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💡 Recomendaciones del veterinario")

    _recs_default_text = "\n".join(_recomendaciones3) if _recomendaciones3 else ""

    _recs_signature = (
        f"{_food_name3}|{_gramos3}|{_me3}|{_aporte3}|{_cobertura3}|"
        f"{_cob_pb3}|{_cob_ee3}|{_bcs3}|{_condicion3}|{_edad3}|{_mer_final3}"
    )

    if st.session_state.get("recomendaciones_signature") != _recs_signature:
        st.session_state["recomendaciones_veterinario_texto"] = _recs_default_text
        st.session_state["recomendaciones_signature"] = _recs_signature

    _recomendaciones_editadas_texto = st.text_area(
        "Edita o agrega recomendaciones clínicas/nutricionales para el informe:",
        height=180,
        key="recomendaciones_veterinario_texto",
    )

    _recomendaciones_export = [
        rec.strip()
        for rec in _recomendaciones_editadas_texto.split("\n")
        if rec.strip()
    ]

    if _recomendaciones_export:
        st.markdown("**Vista previa:**")
        for _rec in _recomendaciones_export:
            st.markdown(f"✓ {_rec}")
    else:
        st.info("Agrega recomendaciones para incluirlas en el informe.")

    st.markdown("---")
    st.subheader("📥 Descargar Informes")

    _fecha3 = datetime.date.today()
    _nombre_archivo3 = _nombre3.replace(" ", "_") if _nombre3 != "—" else "Mascota"

    _datos_energeticos3 = {
        "edad": _edad3,
        "peso": _peso3,
        "bcs": _bcs3,
        "etapa": _etapa3,
        "estado_corporal": _estado_corp3,
        "riesgo_nutricional": _riesgo3,
        "condicion": _condicion3,
        "rer": _rer3 or 0.0,
        "mer_base": _mer_base3 or 0.0,
        "diagnostico": _diagnostico3,
        "recomendaciones": _recomendaciones_export,
    }

    _rng_min_exp = _gramos_rec3 * 0.9 if _datos_completos else 0.0
    _rng_max_exp = _gramos_rec3 * 1.1 if _datos_completos else 0.0

    _datos_alimento3 = {
        "alimento": _food_name3 or "—",
        "marca": _food_data3.get("brand", ""),
        "especie_comercial": _food_data3.get("species", ""),
        "etapa_comercial": _food_data3.get("life_stage", ""),
        "ingredientes": _food_data3.get("ingredients", ""),
        "fuente_pb": _food_data3.get("source_pb", ""),
        "fuente_ee": _food_data3.get("source_ee", ""),
        "fuente_fc": _food_data3.get("source_fc", ""),
        "fuente_me": food.get("fuente_me", "Fórmula Uywa"),
        "me": _me3,
        "gramos": _gramos3,
        "aporte": _aporte3,
        "cobertura": _cobertura3,
        "recomendados": _gramos_rec3,
        "rango_min": _rng_min_exp,
        "rango_max": _rng_max_exp,
        "decision": _resultado3,
        "interpretacion": _interpretacion3,
        "pb": _food_data3.get("PB", 0) if _food_data3 else 0,
        "ee": _food_data3.get("EE", 0) if _food_data3 else 0,
        "ash": _food_data3.get("Ash", 0) if _food_data3 else 0,
        "humidity": _food_data3.get("Humidity", 0) if _food_data3 else 0,
        "fc": _food_data3.get("FC", 0) if _food_data3 else 0,
        "ena": _food_ena3,
        "ms": _food_energy3.get("MS", 0) if _food_energy3 else 0,
        "ge": _food_eb3.get("GE", 0) if _food_eb3 else 0,
        "de_pct": _food_energy3.get("DE_pct", 0) if _food_energy3 else 0,
        "de": _food_energy3.get("DE", 0) if _food_energy3 else 0,
    }

    _mascota_export3 = {
        "nombre": _nombre3,
        "especie": _especie3,
    }

    if not _datos_completos:
        st.warning("Para descargar informes completos, primero completa Perfil y Análisis.")

    _col_xlsx, _col_html = st.columns(2)

    with _col_xlsx:
        try:
            _nutrientes_ref3 = (
                NUTRIENTES_REFERENCIA_PERRO
                if _especie3 == "perro"
                else NUTRIENTES_REFERENCIA_GATO
            )

            _xlsx_bytes = exportar_ficha_maestra_excel(
                mascota=_mascota_export3,
                datos_energeticos=_datos_energeticos3,
                datos_alimento=_datos_alimento3,
                mer_final=_mer_final3 or 0.0,
                senior_applied=_senior3,
                recomendaciones=_recomendaciones_export,
                nutrientes_ref=_nutrientes_ref3,
                cob_pb=_cob_pb3,
                cob_ee=_cob_ee3,
            )

            st.download_button(
                label="📥 Descargar ficha maestra de seguimiento (.xlsx)",
                data=_xlsx_bytes,
                file_name=f"UYWA_Ficha_Nutricional_{_nombre_archivo3}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_ficha_maestra",
                disabled=not _datos_completos,
            )

        except Exception as _e:
            st.error(f"Error al generar ficha maestra: {_e}")

    with _col_html:
        try:
            _html_str = exportar_a_html(
                _mascota_export3,
                _datos_energeticos3,
                _datos_alimento3,
                _mer_final3 or 0.0,
                _diagnostico3,
                _recomendaciones_export,
            )

            st.download_button(
                label="📄 Descargar informe visual de hoy (HTML)",
                data=_html_str,
                file_name=f"UYWA_Informe_{_nombre_archivo3}_{_fecha3.strftime('%d%m%Y')}.html",
                mime="text/html",
                use_container_width=True,
                key="download_html_informe",
                disabled=not _datos_completos,
            )

        except Exception as _e:
            st.error(f"Error al generar informe HTML: {_e}")
