# ======================== ANÁLISIS NUTRICIONAL DE ALIMENTOS ========================

from __future__ import annotations

import pandas as pd
import streamlit as st

from food_database import (
    FOODS,
    calculate_energy,
    calculate_ena,
    calculate_energy_breakdown,
    get_food_names,
    get_food_data,
    infer_me_from_manufacturer_reference,
)

from utils.ui_theme import inject_uywa_theme
from utils.ui_cards import render_section_title, render_info_card
from utils.ui_food_dashboard import (
    render_food_selector_cards,
    render_food_header,
    render_food_composition_metrics,
    render_requirement_coverage_cards,
    render_technical_profile,
    render_ingredients_sources,
)
from utils.ui_food_charts import (
    plot_macronutrients_donut,
    plot_energy_sources_horizontal,
    plot_compare_energy_stacked,
)


ENERGY_COVERAGE_THRESHOLD = 110


def normalize_species(value):
    value = str(value or "").strip().lower()

    if value in ["perro", "canino", "canine", "dog"]:
        return "perro"

    if value in ["gato", "felino", "feline", "cat"]:
        return "gato"

    return value


def get_foods_by_species(species: str) -> list[str]:
    if not species or str(species).strip() == "":
        return sorted(list(FOODS.keys()))

    species_norm = normalize_species(species)
    alimentos_filtrados = []

    for nombre, datos in FOODS.items():
        food_species_norm = normalize_species(datos.get("species", ""))

        if food_species_norm == species_norm:
            alimentos_filtrados.append(nombre)

    return sorted(alimentos_filtrados, key=get_food_display_name)


def get_food_display_name(food_name: str) -> str:
    data = FOODS.get(food_name, {}) or {}

    nombre = str(data.get("name", "") or "").strip()
    marca = str(data.get("brand", "") or "").strip()
    etapa = str(data.get("life_stage", "") or "").strip()
    especie = str(data.get("species", "") or "").strip()

    if not nombre:
        partes = [p.strip() for p in str(food_name).split("|")]
        if len(partes) >= 5:
            nombre = partes[1]
            marca = partes[2]
            especie = partes[3]
            etapa = partes[4]
        else:
            nombre = food_name

    items = [x for x in [nombre, marca, especie.capitalize(), etapa] if x]
    return " · ".join(items)


def get_food_short_name(food_name: str) -> str:
    data = FOODS.get(food_name, {}) or {}
    nombre = str(data.get("name", "") or "").strip()
    marca = str(data.get("brand", "") or "").strip()

    if nombre and marca:
        return f"{nombre} · {marca}"

    if nombre:
        return nombre

    partes = [p.strip() for p in str(food_name).split("|")]

    if len(partes) >= 3:
        return f"{partes[1]} · {partes[2]}"

    return food_name


def get_food_search_text(food_name: str) -> str:
    data = FOODS.get(food_name, {}) or {}

    fields = [
        food_name,
        data.get("name", ""),
        data.get("brand", ""),
        data.get("species", ""),
        data.get("life_stage", ""),
        data.get("category", ""),
        data.get("description", ""),
        data.get("ingredients", ""),
        data.get("source_pb", ""),
        data.get("source_ee", ""),
        data.get("source_fc", ""),
    ]

    return " ".join(str(x) for x in fields if x).lower()


def filtrar_alimentos_por_busqueda(query: str, alimentos: list) -> list[str]:
    if not query or query.strip() == "":
        return sorted(alimentos, key=get_food_display_name)

    query_terms = query.lower().strip().split()

    resultados = []

    for alimento in alimentos:
        search_text = get_food_search_text(alimento)

        if all(term in search_text for term in query_terms):
            resultados.append(alimento)

    return sorted(resultados, key=get_food_display_name)


def get_clase_decision(cobertura_pct):
    if cobertura_pct < 90:
        return "low"
    if cobertura_pct <= 110:
        return "adequate"
    if cobertura_pct <= 130:
        return "moderate"
    return "high"


def get_resultado_cobertura(cobertura_pct):
    if cobertura_pct < 90:
        return "No cubre el requerimiento energético"
    if cobertura_pct <= 110:
        return "Cubre adecuadamente el requerimiento energético"
    return "Excede el requerimiento energético"


def generar_interpretacion_alimento(nombre, cobertura, aporte, mer, gramos_act, gramos_rec, cob_pb, cob_ee):
    template = f"{get_food_short_name(nombre)} aporta {aporte:.0f} kcal/día con {gramos_act:.0f} g/día. "

    if cobertura < 90:
        template += f"Cubre solo el {cobertura:.0f}% del requerimiento energético. "
        template += f"Se recomienda aumentar a {gramos_rec:.0f} g/día. "
    elif cobertura <= 110:
        template += f"Cubre adecuadamente el {cobertura:.0f}% del requerimiento energético. "
    else:
        template += f"Excede al {cobertura:.0f}% el requerimiento energético. "
        template += f"Se recomienda reducir a {gramos_rec:.0f} g/día. "

    if cob_pb is not None:
        if cob_pb < 90:
            template += f"Proteína insuficiente ({cob_pb:.0f}% del requerimiento). "
        elif cob_pb <= 110:
            template += f"Proteína adecuada ({cob_pb:.0f}% del requerimiento). "
        else:
            template += f"Proteína elevada ({cob_pb:.0f}% del requerimiento). "

    if cob_ee is not None:
        if cob_ee < 90:
            template += f"Grasa insuficiente ({cob_ee:.0f}% del requerimiento). "
        elif cob_ee <= 110:
            template += f"Grasa adecuada ({cob_ee:.0f}% del requerimiento). "
        else:
            template += f"Grasa elevada ({cob_ee:.0f}% del requerimiento). "

    template += "Se recomienda monitoreo de peso y condición corporal regularmente."
    return template


# Compatibilidad con imports antiguos de app.py
def build_energy_breakdown_table_with_edits(selected_foods, edited_values_map=None):
    rows = []

    for fname in selected_foods:
        fdata = get_food_data(fname)

        if not fdata:
            continue

        edited_fdata = dict(fdata)

        if edited_values_map and fname in edited_values_map:
            edited_fdata.update(edited_values_map[fname])

        species_food = edited_fdata.get("species", st.session_state.get("especie_mascota", "perro"))
        bd = calculate_energy_breakdown(edited_fdata, species=species_food)

        rows.append(
            {
                "Alimento": f"{edited_fdata.get('emoji','')} {get_food_short_name(fname)}",
                "Proteína (kcal/100g)": bd["kcal_pb"],
                "Grasa (kcal/100g)": bd["kcal_ee"],
                "Carbohidratos (kcal/100g)": bd["kcal_cho"],
                "GE Total (kcal/100g)": bd["GE"],
                "DE Total (kcal/100g)": bd["DE"],
                "ME Total (kcal/100g)": bd["ME"],
            }
        )

    return pd.DataFrame(rows)


def plot_energy_breakdown_stacked_with_edits(selected_foods, edited_values_map=None):
    rows = []

    for fname in selected_foods:
        fdata = get_food_data(fname)

        if not fdata:
            continue

        edited_fdata = dict(fdata)

        if edited_values_map and fname in edited_values_map:
            edited_fdata.update(edited_values_map[fname])

        species_food = edited_fdata.get("species", st.session_state.get("especie_mascota", "perro"))
        bd = calculate_energy_breakdown(edited_fdata, species=species_food)

        rows.append(
            {
                "Alimento corto": get_food_short_name(fname),
                "ME proteína": bd.get("me_pb", 0),
                "ME grasa": bd.get("me_ee", 0),
                "ME carbohidratos": bd.get("me_cho", 0),
            }
        )

    return plot_compare_energy_stacked(pd.DataFrame(rows))


def show_energy_breakdown_cards(selected_foods):
    for row_start in range(0, len(selected_foods), 3):
        cols = st.columns(3)

        for i, fname in enumerate(selected_foods[row_start:row_start + 3]):
            fdata = get_food_data(fname)

            if not fdata:
                continue

            species_food = fdata.get("species", st.session_state.get("especie_mascota", "perro"))
            bd = calculate_energy_breakdown(fdata, species=species_food)

            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{get_food_short_name(fname)}**")
                    st.caption(f"ME: {bd['ME']:.1f} kcal/100g")
                    st.progress(min(bd["pct_pb"] / 100, 1.0))
                    st.caption(f"Proteína: {bd['pct_pb']:.1f}%")
                    st.progress(min(bd["pct_ee"] / 100, 1.0))
                    st.caption(f"Grasa: {bd['pct_ee']:.1f}%")
                    st.progress(min(bd["pct_cho"] / 100, 1.0))
                    st.caption(f"Carbohidratos: {bd['pct_cho']:.1f}%")


def _render_editable_composition(food_name: str, food_data: dict) -> dict:
    edit_cols = {
        "PB (%)": "PB",
        "EE (%)": "EE",
        "Cenizas (%)": "Ash",
        "Humedad (%)": "Humidity",
        "FC (%)": "FC",
    }

    safe_key = "".join(c if c.isalnum() else "_" for c in food_name)
    session_key = f"comp_data_{safe_key}"

    if session_key not in st.session_state:
        st.session_state[session_key] = {
            col: float(food_data.get(key, 0.0) or 0.0)
            for col, key in edit_cols.items()
        }

    with st.expander("✏️ Editar valores", expanded=False):
        edit_df = pd.DataFrame([st.session_state[session_key]])
        edited = st.data_editor(
            edit_df,
            use_container_width=True,
            hide_index=True,
            key=f"comp_editor_{safe_key}",
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    format="%.1f",
                )
                for col in edit_cols
            },
        )

        for col in edit_cols:
            st.session_state[session_key][col] = float(edited[col].iloc[0])

    edited_food_data = dict(food_data)

    for col, key in edit_cols.items():
        edited_food_data[key] = st.session_state[session_key][col]

    return edited_food_data


def _get_energy_source_options(edited_food_data: dict, energy: dict, safe_key: str):
    me_formula_kcal_100g = float(energy.get("ME", 0.0) or 0.0)

    me_manufacturer_kcal_kg = float(edited_food_data.get("ME_manufacturer_kcal_kg", 0.0) or 0.0)
    me_manufacturer_kcal_100g = me_manufacturer_kcal_kg / 10.0 if me_manufacturer_kcal_kg > 0 else 0.0

    manufacturer_g_day_ref = float(edited_food_data.get("manufacturer_g_day_ref", 0.0) or 0.0)

    me_inferred_kcal_kg = infer_me_from_manufacturer_reference(
        manufacturer_g_day_ref,
        species=edited_food_data.get("species", "perro"),
    )
    
    me_inferred_kcal_100g = me_inferred_kcal_kg / 10.0 if me_inferred_kcal_kg > 0 else 0.0

    opciones_me = ["Fórmula Uywa"]

    if me_manufacturer_kcal_100g > 0:
        opciones_me.append("ME declarada fabricante")

    if me_inferred_kcal_100g > 0:
        opciones_me.append("ME inferida desde gramaje fabricante")

    with st.expander("🏷️ Fuente energética usada para dosis", expanded=False):
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("ME fórmula Uywa", f"{me_formula_kcal_100g:.1f} kcal/100g")

        with c2:
            st.metric(
                "ME declarada fabricante",
                f"{me_manufacturer_kcal_100g:.1f} kcal/100g" if me_manufacturer_kcal_100g > 0 else "No disponible",
            )

        with c3:
            st.metric(
                "ME inferida por gramaje",
                f"{me_inferred_kcal_100g:.1f} kcal/100g" if me_inferred_kcal_100g > 0 else "No disponible",
            )

        fuente_me = st.selectbox(
            "Fuente energética para calcular la dosis",
            opciones_me,
            key=f"fuente_me_{safe_key}",
        )

    if fuente_me == "ME declarada fabricante":
        return fuente_me, me_manufacturer_kcal_100g, me_formula_kcal_100g, me_manufacturer_kcal_100g, me_inferred_kcal_100g

    if fuente_me == "ME inferida desde gramaje fabricante":
        return fuente_me, me_inferred_kcal_100g, me_formula_kcal_100g, me_manufacturer_kcal_100g, me_inferred_kcal_100g

    return fuente_me, me_formula_kcal_100g, me_formula_kcal_100g, me_manufacturer_kcal_100g, me_inferred_kcal_100g


def reset_food_analysis_state_on_species_change(species: str) -> None:
    species_norm = normalize_species(species)
    last_species = st.session_state.get("_food_analysis_last_species")

    if last_species is None:
        st.session_state["_food_analysis_last_species"] = species_norm
        return

    if last_species == species_norm:
        return

    st.session_state["_food_analysis_last_species"] = species_norm

    exact_keys = [
        "analysis_food_selector_card",
        "alimento_seleccionado",
        "food_name",
        "analysis_food_name_edited",
        "analysis_food_data_edited",
        "analysis_food_proximal_sum",
        "me_alimento_actual",
        "energia_aportada_actual",
        "fuente_me_actual",
        "me_formula_uywa_actual",
        "me_manufacturer_actual",
        "me_inferred_manufacturer_actual",
        "cobertura_energia_actual",
        "gramos_recomendados_actual",
        "cobertura_proteina_actual",
        "cobertura_grasa_actual",

        # keys por especie
        "food_search_input_perro",
        "food_search_input_gato",
        "analysis_food_card_perro_page",
        "analysis_food_card_gato_page",
    ]

    prefixes = [
        "comp_data_",
        "comp_editor_",
        "gramos_alimento_",
        "fuente_me_",
        "analysis_food_card_",
    ]

    for key in exact_keys:
        st.session_state.pop(key, None)

    for key in list(st.session_state.keys()):
        if any(key.startswith(prefix) for prefix in prefixes):
            del st.session_state[key]

    st.rerun()

def show_food_analysis():
    inject_uywa_theme()

    especie = st.session_state.get("especie_mascota", "")
    especie_norm = normalize_species(especie)

    reset_food_analysis_state_on_species_change(especie_norm)

    render_section_title(
        "Análisis nutricional de alimentos",
        kicker="Uywa Pets",
        subtitle="Selecciona un alimento, ajusta su composición proximal y evalúa aporte energético y cobertura nutricional.",
        icon="🍽️",
    )

    if especie_norm:
        st.caption(f"Especie activa: **{especie_norm.capitalize()}**")

    alimentos_disponibles = get_foods_by_species(especie_norm)
    col_search, col_info = st.columns([3, 1])

    with col_search:
        query_busqueda = st.text_input(
            "🔍 Busca un alimento (nombre o marca):",
            placeholder="Ej: Pro Plan, Purina, Royal Canin...",
            key=f"food_search_input_{especie_norm}",
        )

    with col_info:
        plural = {"perro": "perros", "gato": "gatos"}.get(str(especie).lower(), "")
        st.metric("Disponibles", len(alimentos_disponibles), f"para {plural}" if plural else None)

    alimentos_filtrados = filtrar_alimentos_por_busqueda(query_busqueda, alimentos_disponibles)

    if query_busqueda:
        st.caption(f"{len(alimentos_filtrados)} resultado(s) encontrado(s)")

    if not alimentos_filtrados:
        st.warning(f"No se encontraron alimentos con '{query_busqueda}'.")
        return

    food_name = render_food_selector_cards(
        alimentos_filtrados,
        foods=FOODS,
        key_prefix=f"analysis_food_card_{especie_norm}",
        page_size=6,
    )

    if not food_name:
        st.warning("Selecciona un alimento para continuar.")
        return

    st.session_state["alimento_seleccionado"] = food_name
    st.session_state["food_name"] = food_name

    food_data = get_food_data(food_name)

    if food_data is None:
        st.error("No se encontraron datos para el alimento seleccionado.")
        return

    food_title = get_food_short_name(food_name)
    food_display = get_food_display_name(food_name)

    render_food_header(
        food_name=food_name,
        food_data=food_data,
        short_name=food_title,
        display_name=food_display,
    )

    edited_food_data = _render_editable_composition(food_name, food_data)

    suma_proximal = (
        edited_food_data.get("PB", 0.0)
        + edited_food_data.get("EE", 0.0)
        + edited_food_data.get("Ash", 0.0)
        + edited_food_data.get("Humidity", 0.0)
        + edited_food_data.get("FC", 0.0)
    )

    if suma_proximal > 100:
        st.error(
            f"La suma de PB + EE + Cenizas + Humedad + FC es {suma_proximal:.1f}%. "
            "Debe ser ≤ 100% para calcular correctamente el ENA."
        )
        st.stop()

    if suma_proximal < 40:
        st.warning(
            f"La suma proximal actual es baja ({suma_proximal:.1f}%). "
            "Verifica que los valores estén expresados en porcentaje sobre alimento tal como se ofrece."
        )

    ena = calculate_ena(edited_food_data)
    species_energy = edited_food_data.get("species", st.session_state.get("especie_mascota", "perro"))

    energy = calculate_energy(
        edited_food_data,
        species=species_energy,
    )

    safe_key = "".join(c if c.isalnum() else "_" for c in food_name)

    fuente_me, me_por_100g, me_formula, me_manufacturer, me_inferred = _get_energy_source_options(
        edited_food_data,
        energy,
        safe_key,
    )

    render_food_composition_metrics(edited_food_data, ena, me_por_100g)

    st.plotly_chart(
        plot_macronutrients_donut(food_name, edited_food_data, ena, short_name=food_title),
        use_container_width=True,
    )

    st.markdown("---")
    render_section_title(
        "Cálculo de aporte energético",
        kicker="Dosificación diaria",
        subtitle="Ingresa los gramos diarios del alimento seleccionado para estimar aporte y cobertura.",
        icon="🧮",
    )

    gramos_key = f"gramos_alimento_{safe_key}"

    gramos_input = st.number_input(
        f"Gramos diarios de {food_title}",
        min_value=0.0,
        max_value=5000.0,
        value=float(st.session_state.get(gramos_key, 100.0)),
        step=10.0,
        key=gramos_key,
    )

    me_total_kcal = (me_por_100g / 100.0) * gramos_input

    mer_animal = st.session_state.get("energia_actual", None)
    gramos_pb = (edited_food_data.get("PB", 0) / 100.0) * gramos_input
    gramos_ee = (edited_food_data.get("EE", 0) / 100.0) * gramos_input

    req_pb_g = st.session_state.get("req_pb_g", None)
    req_ee_g = st.session_state.get("req_ee_g", None)

    cobertura_energetica_pct = (me_total_kcal / mer_animal * 100.0) if mer_animal and mer_animal > 0 else 0.0
    gramos_recomendados = (mer_animal / (me_por_100g / 100.0)) if mer_animal and mer_animal > 0 and me_por_100g > 0 else 0.0
    cob_pb = (gramos_pb / req_pb_g * 100.0) if req_pb_g and req_pb_g > 0 else None
    cob_ee = (gramos_ee / req_ee_g * 100.0) if req_ee_g and req_ee_g > 0 else None

    st.session_state["analysis_food_data_edited"] = edited_food_data.copy()
    st.session_state["analysis_food_name_edited"] = food_name
    st.session_state["analysis_food_proximal_sum"] = suma_proximal
    st.session_state["me_alimento_actual"] = me_por_100g
    st.session_state["energia_aportada_actual"] = me_total_kcal
    st.session_state["fuente_me_actual"] = fuente_me
    st.session_state["me_formula_uywa_actual"] = me_formula
    st.session_state["me_manufacturer_actual"] = me_manufacturer
    st.session_state["me_inferred_manufacturer_actual"] = me_inferred
    st.session_state["cobertura_energia_actual"] = cobertura_energetica_pct
    st.session_state["gramos_recomendados_actual"] = gramos_recomendados
    st.session_state["cobertura_proteina_actual"] = cob_pb
    st.session_state["cobertura_grasa_actual"] = cob_ee

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Energía aportada", f"{me_total_kcal:.1f} kcal/día")

    with c2:
        st.metric("MER del animal", f"{mer_animal:.1f} kcal/día" if mer_animal else "No calculado")

    with c3:
        st.metric(
            "Cobertura energética",
            f"{cobertura_energetica_pct:.1f}%" if mer_animal else "—",
            f"{cobertura_energetica_pct - 100:.1f}% vs req." if mer_animal else None,
            delta_color="inverse" if cobertura_energetica_pct > ENERGY_COVERAGE_THRESHOLD else "normal",
        )

    if mer_animal and mer_animal > 0:
        resultado = get_resultado_cobertura(cobertura_energetica_pct)
        diferencia_kcal = me_total_kcal - mer_animal
        diferencia_g = gramos_recomendados - gramos_input

        tone = get_clase_decision(cobertura_energetica_pct)

        render_info_card(
            "Decisión nutricional del alimento",
            f"{resultado}. Aporte: {me_total_kcal:.0f} kcal/día; requerimiento: {mer_animal:.0f} kcal/día; diferencia: {diferencia_kcal:+.0f} kcal/día. "
            f"Cantidad recomendada estimada: {gramos_recomendados:.0f} g/día; diferencia frente a la cantidad actual: {diferencia_g:+.0f} g.",
            tone="success" if tone == "adequate" else "warning" if tone == "moderate" else "danger" if tone == "high" else "low",
            icon="🩺",
        )

        st.info(
            generar_interpretacion_alimento(
                food_name,
                cobertura_energetica_pct,
                me_total_kcal,
                mer_animal,
                gramos_input,
                gramos_recomendados,
                cob_pb,
                cob_ee,
            )
        )

        render_requirement_coverage_cards(
            mer_animal=mer_animal,
            me_total_kcal=me_total_kcal,
            req_pb_g=req_pb_g,
            gramos_pb=gramos_pb,
            req_ee_g=req_ee_g,
            gramos_ee=gramos_ee,
        )
    else:
        st.info("Completa el perfil de la mascota para obtener el MER y la cobertura energética.")

    st.markdown("---")
    render_section_title(
        "Perfil técnico del alimento seleccionado",
        kicker="Energía e ingredientes",
        subtitle="Distribución del origen energético y lectura técnica del alimento.",
        icon="🔬",
    )

    bd_single = calculate_energy_breakdown(
        edited_food_data,
        species=species_energy,
    )
    bd_single["ME"] = me_por_100g
    bd_single["me_pb"] = round(me_por_100g * bd_single["pct_pb"] / 100.0, 2)
    bd_single["me_ee"] = round(me_por_100g * bd_single["pct_ee"] / 100.0, 2)
    bd_single["me_cho"] = round(me_por_100g * bd_single["pct_cho"] / 100.0, 2)

    tec_col1, tec_col2 = st.columns([1.2, 1])

    with tec_col1:
        st.plotly_chart(
            plot_energy_sources_horizontal(bd_single),
            use_container_width=True,
        )

    with tec_col2:
        render_technical_profile(
            edited_food_data=edited_food_data,
            ena=ena,
            me_por_100g=me_por_100g,
        )

    render_ingredients_sources(edited_food_data)

    with st.expander("📋 Ver cálculo energético detallado", expanded=False):
        equation_species = energy.get("equation_species", "perro")

        if equation_species == "gato":
            de_formula_text = "%DE = 87.9 - (0.88×FC_MS)"
            me_formula_text = "ME = DE - (0.77×PB)"
            species_label = "Gato"
        else:
            de_formula_text = "%DE = 91.2 - (1.43×FC_MS)"
            me_formula_text = "ME = DE - (1.04×PB)"
            species_label = "Perro"

        st.markdown(f"**Ecuaciones FEDIAF/NRC — {species_label}:**")
        st.markdown(f"1. `GE = (5.7×PB) + (9.4×EE) + [4.1×(ENA+FC)]`")
        st.markdown(f"2. `{de_formula_text}`")
        st.markdown(f"3. `DE = GE × (%DE/100)`")
        st.markdown(f"4. `{me_formula_text}`")

        energy_calc_rows = [
            ("Materia Seca (MS)", energy["MS"], "%"),
            ("FC en base MS (FC_MS)", energy["FC_MS"], "%"),
            ("Energía Bruta (GE)", energy["GE"], "kcal/100g"),
            ("Digestibilidad Energética (DE%)", energy["DE_pct"], "%"),
            ("Energía Digestible (DE)", energy["DE"], "kcal/100g"),
            ("Energía Metabolizable (ME)", energy["ME"], "kcal/100g"),
        ]

        st.dataframe(
            pd.DataFrame(energy_calc_rows, columns=["Parámetro", "Valor", "Unidad"]),
            use_container_width=True,
            hide_index=True,
        )
