# ======================== ANÁLISIS NUTRICIONAL DE ALIMENTOS ========================
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
import textwrap

from food_database import (
    FOODS,
    calculate_energy,
    calculate_ena,
    calculate_energy_breakdown,
    get_food_names,
    get_food_data,
    infer_me_from_manufacturer_dog_10kg,
)

# ---- Paleta de colores corporativa ----
COLORS = {
    "PB": "#2176FF",
    "EE": "#FFB703",
    "Ash": "#8E9AAF",
    "Humidity": "#8ECAE6",
    "FC": "#52B788",
    "ENA": "#F4845F",
}

LABELS = {
    "PB": "Proteína Bruta",
    "EE": "Grasa (EE)",
    "Ash": "Cenizas",
    "Humidity": "Humedad",
    "FC": "Fibra Cruda",
    "ENA": "Carbohidratos (ENA)",
}

# Umbral de cobertura energética para alertas visuales (%)
ENERGY_COVERAGE_THRESHOLD = 110

# Íconos por clase de decisión nutricional
DECISION_COLORS = {
    "low": "🔵",       # < 90%
    "adequate": "🟢",  # 90-110%
    "moderate": "🟠",  # 110-130%
    "high": "🔴",      # > 130%
}


def get_clase_decision(cobertura_pct):
    """Devuelve la clase CSS según el porcentaje de cobertura energética."""
    if cobertura_pct < 90:
        return "low"
    elif cobertura_pct <= 110:
        return "adequate"
    elif cobertura_pct <= 130:
        return "moderate"
    else:
        return "high"


def get_resultado_cobertura(cobertura_pct):
    """Texto interpretativo de cobertura energética."""
    if cobertura_pct < 90:
        return "No cubre el requerimiento energético"
    elif cobertura_pct <= 110:
        return "Cubre adecuadamente el requerimiento energético"
    else:
        return "Excede el requerimiento energético"


def generar_interpretacion_alimento(nombre, cobertura, aporte, mer,
                                    gramos_act, gramos_rec, cob_pb, cob_ee):
    """
    Genera un párrafo interpretativo con el análisis nutricional completo del alimento.

    Parámetros:
        nombre (str)       : Nombre del alimento.
        cobertura (float)  : Cobertura energética en % (aporte/MER×100).
        aporte (float)     : Energía aportada (kcal/día).
        mer (float)        : Requerimiento energético del animal (kcal/día).
        gramos_act (float) : Gramos diarios actuales.
        gramos_rec (float) : Gramos diarios recomendados para cubrir MER.
        cob_pb (float|None): Cobertura de proteína en % (puede ser None).
        cob_ee (float|None): Cobertura de grasa en % (puede ser None).

    Retorna:
        str: Párrafo interpretativo.
    """
    template = f"{nombre} aporta {aporte:.0f} kcal/día con {gramos_act:.0f} g/día. "

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


def plot_macronutrients_pie(food_name, food_data):
    """
    Donut premium de composición proximal del alimento.
    Muestra proporción de PB, EE, Cenizas, Humedad, FC y ENA.
    """
    ENA = calculate_ena(food_data)

    ms = 100 - float(food_data.get("Humidity", 0) or 0)
    me = float(food_data.get("ME", 0) or 0)

    food_title = get_food_short_name(food_name) if "get_food_short_name" in globals() else food_name

    nutrient_data = [
        ("Proteína", float(food_data.get("PB", 0) or 0), "#DC2626"),
        ("Grasa", float(food_data.get("EE", 0) or 0), "#F59E0B"),
        ("Fibra", float(food_data.get("FC", 0) or 0), "#16A34A"),
        ("Cenizas", float(food_data.get("Ash", 0) or 0), "#64748B"),
        ("Humedad", float(food_data.get("Humidity", 0) or 0), "#38BDF8"),
        ("ENA", float(ENA or 0), "#2563EB"),
    ]

    labels = [x[0] for x in nutrient_data if x[1] > 0]
    values = [x[1] for x in nutrient_data if x[1] > 0]
    colors = [x[2] for x in nutrient_data if x[1] > 0]

    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.58,
            sort=False,
            direction="clockwise",
            marker=dict(
                colors=colors,
                line=dict(color="#FFFFFF", width=3),
            ),
            textinfo="percent",
            textposition="inside",
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        )
    )

    fig.add_annotation(
        text=f"<b>MS</b><br>{ms:.1f}%",
        x=0.5,
        y=0.54,
        font=dict(size=22, color="#0F172A"),
        showarrow=False,
    )

    fig.add_annotation(
        text=f"ENA {ENA:.1f}%",
        x=0.5,
        y=0.43,
        font=dict(size=13, color="#64748B"),
        showarrow=False,
    )

    fig.update_layout(
        title=dict(
            text=f"Composición proximal · {food_title}",
            font=dict(size=18, family="Inter, Montserrat, sans-serif", color="#0F172A"),
            x=0.02,
            xanchor="left",
        ),
        height=460,
        margin=dict(t=70, b=70, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color="#334155"),
        ),
        font=dict(family="Inter, Montserrat, sans-serif", color="#334155"),
    )

    return fig
    
def show_energy_breakdown_cards(selected_foods):
    """
    Renderiza cards individuales por alimento con el desglose energético porcentual
    e información de las fuentes principales de cada nutriente.

    Parámetros:
        selected_foods (list[str]): Lista de nombres de alimentos a mostrar.
    """
    cols = st.columns(min(len(selected_foods), 3))
    for idx, fname in enumerate(selected_foods):
        fdata = get_food_data(fname)
        if not fdata:
            continue
        species_food = fdata.get("species", st.session_state.get("especie_mascota", "perro"))
        bd = calculate_energy_breakdown(fdata, species=species_food)
        col = cols[idx % 3]

        source_pb = fdata.get("source_pb", "")
        source_ee = fdata.get("source_ee", "")
        source_fc = fdata.get("source_fc", "")

        source_pb_html = (
            f'<div style="font-size:0.75rem;color:#4a5568;margin-top:2px;margin-bottom:6px;">'
            f'Proviene de: {source_pb}</div>'
            if source_pb else ""
        )
        source_ee_html = (
            f'<div style="font-size:0.75rem;color:#4a5568;margin-top:2px;margin-bottom:6px;">'
            f'Proviene de: {source_ee}</div>'
            if source_ee else ""
        )
        source_fc_html = (
            f'<div style="font-size:0.75rem;color:#4a5568;margin-top:2px;margin-bottom:6px;">'
            f'Proviene de: {source_fc}</div>'
            if source_fc else ""
        )

        with col:
            st.markdown(
                f"""
                <div style="background:#fff;border:1px solid #e0e7ef;border-radius:12px;
                            padding:16px;margin-bottom:12px;box-shadow:0 2px 8px #0001;">
                    <div style="font-size:1.6rem;text-align:center;">{fdata.get('emoji','')}</div>
                    <div style="font-weight:700;font-size:0.95rem;text-align:center;
                                color:#2C3E50;margin:6px 0 10px 0;line-height:1.3;">{fname}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                margin-bottom:5px;">
                        <span style="color:#2176FF;font-weight:600;font-size:0.85rem;">🥩 Proteína</span>
                        <span style="background:#2176FF22;color:#2176FF;border-radius:8px;
                                     padding:2px 8px;font-size:0.88rem;font-weight:700;">
                            {bd['pct_pb']:.1f}%
                        </span>
                    </div>
                    <div style="background:#2176FF;height:6px;border-radius:4px;
                                width:{bd['pct_pb']:.1f}%;margin-bottom:2px;"></div>
                    {source_pb_html}
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                margin-bottom:5px;">
                        <span style="color:#FFB703;font-weight:600;font-size:0.85rem;">🧈 Grasa</span>
                        <span style="background:#FFB70322;color:#b57d00;border-radius:8px;
                                     padding:2px 8px;font-size:0.88rem;font-weight:700;">
                            {bd['pct_ee']:.1f}%
                        </span>
                    </div>
                    <div style="background:#FFB703;height:6px;border-radius:4px;
                                width:{bd['pct_ee']:.1f}%;margin-bottom:2px;"></div>
                    {source_ee_html}
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                margin-bottom:5px;">
                        <span style="color:#52B788;font-weight:600;font-size:0.85rem;">🌾 Carbohidratos</span>
                        <span style="background:#52B78822;color:#1b7a53;border-radius:8px;
                                     padding:2px 8px;font-size:0.88rem;font-weight:700;">
                            {bd['pct_cho']:.1f}%
                        </span>
                    </div>
                    <div style="background:#52B788;height:6px;border-radius:4px;
                                width:{bd['pct_cho']:.1f}%;margin-bottom:2px;"></div>
                    {source_fc_html}
                    <div style="font-size:0.8rem;color:#5a6e8c;text-align:center;margin-top:6px;">
                        ME: <b>{bd['ME']:.1f} kcal/100g</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def build_energy_breakdown_table_with_edits(selected_foods, edited_values_map=None):
    """
    Construye tabla energética considerando valores editados por el usuario.

    Parámetros:
        selected_foods (list[str]): Nombres de alimentos a comparar
        edited_values_map (dict): Mapa {nombre_alimento: {columna: valor_editado}}
                                 Si None, usa valores originales de FOODS

    Retorna:
        pandas.DataFrame con desglose energético (considera ediciones)
    """
    rows = []
    for fname in selected_foods:
        fdata = get_food_data(fname)
        if not fdata:
            continue

        # Si hay valores editados para este alimento, usarlos
        if edited_values_map and fname in edited_values_map:
            edited_fdata = dict(fdata)
            for col_key, col_val in edited_values_map[fname].items():
                edited_fdata[col_key] = col_val
        else:
            edited_fdata = fdata

        species_food = edited_fdata.get("species", st.session_state.get("especie_mascota", "perro"))
        bd = calculate_energy_breakdown(edited_fdata, species=species_food)
        rows.append({
            "Alimento": f"{edited_fdata.get('emoji','')} {fname}",
            "Proteína (kcal/100g)": bd["kcal_pb"],
            "Grasa (kcal/100g)": bd["kcal_ee"],
            "Carbohidratos (kcal/100g)": bd["kcal_cho"],
            "GE Total (kcal/100g)": bd["GE"],
            "DE Total (kcal/100g)": bd["DE"],
            "ME Total (kcal/100g)": bd["ME"],
        })
    return pd.DataFrame(rows)


def plot_energy_breakdown_stacked_with_edits(selected_foods, edited_values_map=None):
    """
    Gráfico apilado considerando valores editados.

    Parámetros:
        selected_foods (list[str]): Alimentos a comparar
        edited_values_map (dict): Mapa de ediciones {nombre: {col: valor}}

    Retorna:
        plotly Figure
    """
    emoji_names = []
    me_pb_vals = []
    me_ee_vals = []
    me_cho_vals = []

    for fname in selected_foods:
        fdata = get_food_data(fname)
        if not fdata:
            continue

        # Aplicar ediciones si existen
        if edited_values_map and fname in edited_values_map:
            edited_fdata = dict(fdata)
            for col_key, col_val in edited_values_map[fname].items():
                edited_fdata[col_key] = col_val
        else:
            edited_fdata = fdata

        species_food = edited_fdata.get("species", st.session_state.get("especie_mascota", "perro"))
        bd = calculate_energy_breakdown(edited_fdata, species=species_food)
        emoji_names.append(f"{edited_fdata.get('emoji', '')} {fname}")
        me_pb_vals.append(bd["me_pb"])
        me_ee_vals.append(bd["me_ee"])
        me_cho_vals.append(bd["me_cho"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Proteína (PB)",
        x=emoji_names,
        y=me_pb_vals,
        marker_color="#2176FF",
        hovertemplate="<b>Proteína</b><br>%{y:.1f} kcal/100g<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Grasa (EE)",
        x=emoji_names,
        y=me_ee_vals,
        marker_color="#FFB703",
        hovertemplate="<b>Grasa</b><br>%{y:.1f} kcal/100g<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Carbohidratos + Fibra",
        x=emoji_names,
        y=me_cho_vals,
        marker_color="#52B788",
        hovertemplate="<b>Carbohidratos + Fibra</b><br>%{y:.1f} kcal/100g<extra></extra>",
    ))

    fig.update_layout(
        barmode="stack",
        title=dict(
            text="Origen de la Energía Metabolizable por Alimento",
            font=dict(size=16, family="Montserrat, sans-serif"),
        ),
        yaxis_title="Energía Metabolizable (kcal / 100 g)",
        xaxis_tickangle=-25,
        legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="center", x=0.5),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=480,
        margin=dict(t=60, b=140, l=60, r=40),
    )
    return fig


def plot_nutrient_comparison(mer_animal, me_total_kcal, req_pb_g, gramos_pb, req_ee_g, gramos_ee):
    """
    Crea un gráfico de subplots (3 paneles) comparando Requerimiento vs Aporte
    para Energía, Proteína y Grasa, con colores que indican el estado de cobertura.

    Colores:
        - 🔵 Azul  (#2176FF) : Aporte < 90% del requerimiento (bajo)
        - 🟢 Verde (#52B788) : Aporte entre 90-110% (en rango)
        - 🟠 Naranja (#FF6B35): Aporte > 110% (excedido)

    Parámetros:
        mer_animal (float)   : Requerimiento energético diario (kcal/día).
        me_total_kcal (float): Energía aportada por la ración (kcal/día).
        req_pb_g (float|None): Requerimiento mínimo de proteína (g/día).
        gramos_pb (float)    : Proteína aportada por la ración (g/día).
        req_ee_g (float|None): Requerimiento mínimo de grasa (g/día).
        gramos_ee (float)    : Grasa aportada por la ración (g/día).

    Retorna:
        plotly.graph_objects.Figure
    """
    def _coverage_color(aporte, req):
        if req is None or req <= 0:
            return "#2176FF"
        pct = (aporte / req) * 100.0
        if pct < 90.0:
            return "#2176FF"   # Azul — bajo
        elif pct <= 110.0:
            return "#52B788"   # Verde — en rango
        else:
            return "#FF6B35"   # Naranja — excedido

    def _coverage_label(aporte, req):
        if req is None or req <= 0:
            return "Sin referencia"
        pct = (aporte / req) * 100.0
        if pct < 90.0:
            return f"🔵 Bajo ({pct:.0f}%)"
        elif pct <= 110.0:
            return f"🟢 En rango ({pct:.0f}%)"
        else:
            return f"🟠 Excedido ({pct:.0f}%)"

    panels = [
        {
            "title": "⚡ Energía",
            "unit": "kcal/día",
            "req": mer_animal,
            "aporte": me_total_kcal,
        },
        {
            "title": "🥩 Proteína (PB)",
            "unit": "g/día",
            "req": req_pb_g if req_pb_g else 0.0,
            "aporte": gramos_pb,
        },
        {
            "title": "🧈 Grasa (EE)",
            "unit": "g/día",
            "req": req_ee_g if req_ee_g else 0.0,
            "aporte": gramos_ee,
        },
    ]

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[p["title"] for p in panels],
        horizontal_spacing=0.12,
    )

    for i, panel in enumerate(panels, start=1):
        aporte_color = _coverage_color(panel["aporte"], panel["req"])
        show_legend = (i == 1)

        fig.add_trace(
            go.Bar(
                name="🎯 Requerimiento",
                x=["Requerimiento"],
                y=[panel["req"]],
                marker_color="#8E9AAF",
                text=[f"{panel['req']:.1f}"],
                textposition="outside",
                hovertemplate=f"<b>Requerimiento</b><br>%{{y:.2f}} {panel['unit']}<extra></extra>",
                showlegend=show_legend,
                legendgroup="req",
            ),
            row=1,
            col=i,
        )
        fig.add_trace(
            go.Bar(
                name="📦 Aporte del Alimento",
                x=["Aporte"],
                y=[panel["aporte"]],
                marker_color=aporte_color,
                text=[f"{panel['aporte']:.1f}"],
                textposition="outside",
                hovertemplate=(
                    f"<b>Aporte</b><br>%{{y:.2f}} {panel['unit']}<br>"
                    f"{_coverage_label(panel['aporte'], panel['req'])}<extra></extra>"
                ),
                showlegend=show_legend,
                legendgroup="aporte",
            ),
            row=1,
            col=i,
        )
        fig.update_yaxes(title_text=panel["unit"], row=1, col=i)

    fig.update_layout(
        barmode="group",
        title=dict(
            text="Requerimiento vs Aporte por Nutriente",
            font=dict(size=15, family="Montserrat, sans-serif"),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=430,
        margin=dict(t=80, b=80, l=50, r=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        font=dict(family="Montserrat, sans-serif"),
    )
    return fig
def render_requirement_coverage_cards(
    mer_animal,
    me_total_kcal,
    req_pb_g,
    gramos_pb,
    req_ee_g,
    gramos_ee,
):
    """
    Renderiza tarjetas de cobertura usando componentes nativos de Streamlit.
    Evita problemas de HTML interpretado como texto.
    """

    def _status(aporte, req):
        if req is None or req <= 0:
            return None, "Sin referencia", "normal"

        pct = (aporte / req) * 100.0

        if pct < 90:
            return pct, "Bajo", "normal"
        if pct <= 110:
            return pct, "En rango", "normal"

        return pct, "Excedido", "inverse"

    items = [
        {
            "title": "⚡ Energía",
            "req": mer_animal,
            "aporte": me_total_kcal,
            "unit": "kcal/día",
        },
        {
            "title": "🥩 Proteína",
            "req": req_pb_g,
            "aporte": gramos_pb,
            "unit": "g/día",
        },
        {
            "title": "🧈 Grasa",
            "req": req_ee_g,
            "aporte": gramos_ee,
            "unit": "g/día",
        },
    ]

    st.markdown("#### Cobertura de requerimientos")

    for item in items:
        pct, estado, delta_color = _status(item["aporte"], item["req"])

        req_text = (
            f"{item['req']:.1f} {item['unit']}"
            if item["req"] is not None and item["req"] > 0
            else "Sin referencia"
        )

        aporte_text = f"{item['aporte']:.1f} {item['unit']}"

        if pct is None:
            value_text = "—"
            progress_value = 0.0
            delta_text = estado
        else:
            value_text = f"{pct:.0f}%"
            progress_value = min(pct / 140.0, 1.0)
            delta_text = f"{estado} · {pct - 100:+.0f}% vs req."

        with st.container(border=True):
            c1, c2 = st.columns([2.3, 1])

            with c1:
                st.markdown(f"**{item['title']}**")
                st.caption(f"Requerimiento: **{req_text}** · Aporte: **{aporte_text}**")
                st.progress(progress_value)

            with c2:
                st.metric(
                    label="Cobertura",
                    value=value_text,
                    delta=delta_text,
                    delta_color=delta_color,
                )
def normalize_species(value):
    value = str(value or "").strip().lower()

    if value in ["perro", "canino", "canine", "dog"]:
        return "perro"

    if value in ["gato", "felino", "feline", "cat"]:
        return "gato"

    return value


def get_foods_by_species(species: str) -> list[str]:
    """
    Filtra alimentos por especie del diccionario FOODS.
    Acepta equivalencias: perro/canino y gato/felino.
    """

    if not species or str(species).strip() == "":
        return sorted(list(FOODS.keys()))

    species_norm = normalize_species(species)
    alimentos_filtrados = []

    for nombre, datos in FOODS.items():
        food_species_norm = normalize_species(datos.get("species", ""))

        if food_species_norm == species_norm:
            alimentos_filtrados.append(nombre)

    return sorted(alimentos_filtrados)

def filtrar_alimentos_por_busqueda(query: str, alimentos: list) -> list[str]:
    """
    Filtra alimentos por búsqueda extendida:
    nombre, marca, especie, etapa, categoría, ingredientes y fuentes nutricionales.
    """
    if not query or query.strip() == "":
        return sorted(alimentos, key=get_food_display_name)

    query_terms = query.lower().strip().split()

    resultados = []
    for alimento in alimentos:
        search_text = get_food_search_text(alimento)

        if all(term in search_text for term in query_terms):
            resultados.append(alimento)

    return sorted(resultados, key=get_food_display_name)

def get_food_display_name(food_name: str) -> str:
    """
    Devuelve una etiqueta limpia para mostrar alimentos en selectbox/multiselect.
    No cambia la clave real del alimento.
    """
    data = FOODS.get(food_name, {}) or {}

    nombre = str(data.get("name", "") or "").strip()
    marca = str(data.get("brand", "") or "").strip()
    etapa = str(data.get("life_stage", "") or "").strip()
    especie = str(data.get("species", "") or "").strip()

    # Si no existen campos separados, limpia el nombre original.
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
    """
    Nombre corto para títulos y encabezados.
    """
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

def normalize_life_stage_label(value: str) -> str:
    text = str(value or "").strip()
    text = text.replace("-", " · ")

    replacements = {
        "Adultos": "Adulto",
        "Cachorro Razas": "Cachorro · Razas",
        "Cachorro·Razas": "Cachorro · Razas",
        "Adulto todas las razas": "Adulto · Todas las razas",
        "Adultos Todas las razas": "Adulto · Todas las razas",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = " · ".join([p.strip() for p in text.split("·") if p.strip()])
    return text


def get_food_card_fields(food_name: str) -> dict:
    data = FOODS.get(food_name, {}) or {}

    nombre = str(data.get("name", "") or "").strip()
    marca = str(data.get("brand", "") or "").strip()
    etapa = str(data.get("life_stage", "") or "").strip()
    especie = str(data.get("species", "") or "").strip()
    categoria = str(data.get("category", "") or "").strip()
    emoji = str(data.get("emoji", "") or "").strip()

    if not nombre:
        partes = [p.strip() for p in str(food_name).split("|")]
        if len(partes) >= 5:
            nombre = partes[1]
            marca = partes[2]
            especie = partes[3]
            etapa = partes[4]
        else:
            nombre = food_name

    return {
        "key": food_name,
        "nombre": nombre,
        "marca": marca,
        "etapa": normalize_life_stage_label(etapa),
        "especie": especie.capitalize(),
        "categoria": categoria,
        "emoji": emoji,
    }


def render_food_selector_cards(alimentos: list[str], key_prefix: str = "food_card", page_size: int = 6) -> str | None:
    """
    Selector visual por tarjetas con paginación.
    Retorna la clave real del alimento seleccionado.
    """
    if not alimentos:
        return None

    page_key = f"{key_prefix}_page"
    selected_key = "analysis_food_selector_card"

    total = len(alimentos)
    total_pages = max(1, (total + page_size - 1) // page_size)

    current_page = int(st.session_state.get(page_key, 0))
    current_page = max(0, min(current_page, total_pages - 1))
    st.session_state[page_key] = current_page

    current = st.session_state.get(selected_key, alimentos[0])

    if current not in alimentos:
        current = alimentos[0]
        st.session_state[selected_key] = current

    st.markdown("#### Selecciona un alimento balanceado")

    nav1, nav2, nav3 = st.columns([1, 2, 1])

    with nav1:
        if st.button(
            "◀ Anterior",
            key=f"{key_prefix}_prev",
            use_container_width=True,
            disabled=current_page <= 0,
        ):
            st.session_state[page_key] = current_page - 1
            st.rerun()

    with nav2:
        start_item = current_page * page_size + 1
        end_item = min((current_page + 1) * page_size, total)
        st.markdown(
            f"""
            <div style="text-align:center;color:#64748B;font-weight:700;padding-top:0.6rem;">
                Mostrando {start_item}-{end_item} de {total} alimentos · Página {current_page + 1}/{total_pages}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav3:
        if st.button(
            "Siguiente ▶",
            key=f"{key_prefix}_next",
            use_container_width=True,
            disabled=current_page >= total_pages - 1,
        ):
            st.session_state[page_key] = current_page + 1
            st.rerun()

    page_start = current_page * page_size
    page_end = page_start + page_size
    alimentos_pagina = alimentos[page_start:page_end]

    for row_start in range(0, len(alimentos_pagina), 3):
        cols = st.columns(3)

        for i, alimento in enumerate(alimentos_pagina[row_start:row_start + 3]):
            fields = get_food_card_fields(alimento)
            selected = alimento == current

            border = "#2563EB" if selected else "#E2E8F0"
            bg = "#EFF6FF" if selected else "#FFFFFF"
            shadow = (
                "0 12px 28px rgba(37,99,235,0.16)"
                if selected
                else "0 8px 22px rgba(15,23,42,0.06)"
            )

            global_index = page_start + row_start + i

            with cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        background:{bg};
                        border:2px solid {border};
                        border-radius:18px;
                        padding:16px 18px;
                        min-height:150px;
                        box-shadow:{shadow};
                        margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                            <div style="font-size:1.8rem;">{fields['emoji'] or '🐾'}</div>
                            <div>
                                <div style="font-size:1.05rem;font-weight:850;color:#0F172A;line-height:1.15;">
                                    {fields['nombre']}
                                </div>
                                <div style="font-size:0.86rem;color:#64748B;font-weight:700;">
                                    {fields['marca']}
                                </div>
                            </div>
                        </div>
                        <div style="font-size:0.86rem;color:#1F2937;margin-top:8px;">
                            {fields['etapa']}
                        </div>
                        <div style="margin-top:10px;">
                            <span style="
                                background:#F8FAFC;
                                color:#475569;
                                border:1px solid #E2E8F0;
                                border-radius:999px;
                                padding:4px 9px;
                                font-size:0.75rem;
                                font-weight:750;">
                                {fields['especie']}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Seleccionar" if not selected else "Seleccionado",
                    key=f"{key_prefix}_select_{global_index}",
                    use_container_width=True,
                    disabled=selected,
                ):
                    st.session_state[selected_key] = alimento
                    st.rerun()

    return st.session_state.get(selected_key, current)

def get_food_search_text(food_name: str) -> str:
    """
    Texto ampliado para búsqueda por nombre, marca, especie, etapa, categoría e ingredientes.
    """
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

def show_food_analysis():
    """
    Renderiza la interfaz de análisis nutricional en el Tab de Análisis de Streamlit.
    """
    st.markdown(
        """
        <style>
        .energy-table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
            font-size: 16.5px;
            text-align: center;
            border-radius: 8px;
            overflow: hidden;
        }
        .energy-table th {
            background-color: #4A5568;
            color: #fff;
            padding: 10px;
            font-weight: bold;
        }
        .energy-table td {
            padding: 10px;
        }
        .energy-table tr:nth-child(even) {
            background-color: #edf2f7;
        }
        .energy-table tr:nth-child(odd) {
            background-color: #ffffff;
        }
        .decision-card {
            border-radius: 12px;
            padding: 20px 24px;
            margin: 20px 0;
            border-left: 6px solid;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
        }
        .decision-card.low {
            background: rgba(33, 118, 255, 0.08);
            border-left-color: #2176FF;
            color: #1254d1;
        }
        .decision-card.adequate {
            background: rgba(82, 183, 136, 0.08);
            border-left-color: #52B788;
            color: #1b7a53;
        }
        .decision-card.moderate {
            background: rgba(255, 183, 3, 0.08);
            border-left-color: #FFB703;
            color: #92400e;
        }
        .decision-card.high {
            background: rgba(244, 132, 95, 0.08);
            border-left-color: #F4845F;
            color: #933b1a;
        }
        .decision-icon { font-size: 32px; margin-bottom: 8px; }
        .decision-status { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
        .decision-percentage { font-size: 28px; font-weight: 700; margin: 8px 0; }
        .decision-details { font-size: 15px; opacity: 0.85; margin: 8px 0; }
        .decision-diff { font-size: 15.5px; font-weight: 600; margin-top: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.header("Análisis Nutricional de Alimentos")
    st.markdown(
        "Selecciona un alimento para ver su composición proximal y el cálculo de "
        "energía metabolizable según el modelo **NRC**."
    )

    # Full list kept for the comparison multiselect later in this function
    food_names = get_food_names()

    # ── Especie desde Pestaña 1 ───────────────────────────────────────────────
    especie = st.session_state.get("especie_mascota", "")
    if especie:
        st.markdown(f"**🐾 Especie:** {especie.capitalize()}")
        st.markdown("---")

    # ── Filtrar alimentos por especie ─────────────────────────────────────────
    alimentos_disponibles = get_foods_by_species(especie)

    col_search, col_info = st.columns([3, 1])
    with col_search:
        query_busqueda = st.text_input(
            "🔍 Busca un alimento (nombre o marca):",
            placeholder="Ej: Pro Plan, Purina, Royal Canin...",
            key="food_search_input",
            help="Escribe para filtrar alimentos disponibles",
        )
    with col_info:
        _plural_especie = {"perro": "perros", "gato": "gatos"}.get(especie.lower(), "")
        st.metric(
            "Disponibles",
            len(alimentos_disponibles),
            f"para {_plural_especie}" if _plural_especie else None,
        )

    # ── Filtrar dinámicamente por búsqueda ────────────────────────────────────
    alimentos_filtrados = filtrar_alimentos_por_busqueda(query_busqueda, alimentos_disponibles)

    if query_busqueda:
        st.caption(f"📌 {len(alimentos_filtrados)} resultado(s) encontrado(s)")

    if not alimentos_filtrados:
        st.warning(f"❌ No se encontraron alimentos con '{query_busqueda}'")
        especie_info = f" para {_plural_especie}" if _plural_especie else ""
        st.info(f"💡 **Alimentos disponibles{especie_info}:**")
        cols = st.columns(2)
        for idx, alim in enumerate(alimentos_disponibles[:10]):
            with cols[idx % 2]:
                st.write(f"• {alim}")
        if len(alimentos_disponibles) > 10:
            st.caption(f"...y {len(alimentos_disponibles) - 10} más")
        return

    food_name = render_food_selector_cards(
        alimentos_filtrados,
        key_prefix="analysis_food_card",
        page_size=6,
    )
    
    if not food_name:
        st.warning("Selecciona un alimento para continuar.")
        return

    # Guardar en session_state para otras pestañas
    st.session_state["alimento_seleccionado"] = food_name
    st.session_state["food_name"] = food_name

    food_data = get_food_data(food_name)
    if food_data is None:
        st.error("No se encontraron datos para el alimento seleccionado.")
        return

    food_title = get_food_short_name(food_name)
    food_display = get_food_display_name(food_name)
    
    # ---- Encabezado del alimento ----
    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,#2176ff11,#eef4fc);
                    border-left:5px solid #2176FF;border-radius:10px;padding:16px 20px;margin-bottom:16px;">
            <span style="font-size:2rem;">{food_data.get('emoji','')}</span>
            <span style="font-size:1.4rem;font-weight:700;color:#2C3E50;margin-left:10px;">{food_title}</span>
            <span style="color:#5a6e8c;font-size:0.85rem;">{food_display}</span><br>
            <br>
            <span style="color:#5a6e8c;font-size:0.95rem;">{food_data.get('description','')}</span>
            &nbsp;&nbsp;<span style="background:#2176FF22;color:#2176FF;border-radius:6px;
                                     padding:2px 10px;font-size:0.85rem;font-weight:600;">
                {food_data.get('category','')}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Tabla de composición proximal (editable) ----
    st.subheader("📊 Composición Proximal")
    st.markdown(
        "<small style='color:#5a6e8c;'>Edita los valores para recalcular automáticamente la energía y los gráficos.</small>",
        unsafe_allow_html=True,
    )

    # Column mapping: display name → food_data key
    EDIT_COLS = {
        "PB (%)": "PB",
        "EE (%)": "EE",
        "Cenizas (%)": "Ash",
        "Humedad (%)": "Humidity",
        "FC (%)": "FC",
    }

    # Sanitize food_name for use as a widget key
    safe_key = "".join(c if c.isalnum() else "_" for c in food_name)

    # Initialise session_state with original food values (only on first load for this food)
    session_key = f"comp_data_{safe_key}"
    if session_key not in st.session_state:
        st.session_state[session_key] = {col: food_data[key] for col, key in EDIT_COLS.items()}

    with st.expander("✏️ Editar Valores", expanded=False):
        edit_df = pd.DataFrame([st.session_state[session_key]])
        edited = st.data_editor(
            edit_df,
            use_container_width=True,
            hide_index=True,
            key=f"comp_editor_{safe_key}",
            column_config={
                "PB (%)": st.column_config.NumberColumn("PB (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
                "EE (%)": st.column_config.NumberColumn("EE (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
                "Cenizas (%)": st.column_config.NumberColumn("Cenizas (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
                "Humedad (%)": st.column_config.NumberColumn("Humedad (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
                "FC (%)": st.column_config.NumberColumn("FC (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
            },
        )
        # Persist edits into session_state so they survive re-runs
        for col in EDIT_COLS:
            st.session_state[session_key][col] = float(edited[col].iloc[0])

    # Build updated food_data from session_state (always up-to-date)
    edited_food_data = dict(food_data)
    for col, key in EDIT_COLS.items():
        edited_food_data[key] = st.session_state[session_key][col]
    
    # ── Validación de composición proximal editada ───────────────────────────
    suma_proximal = (
        edited_food_data.get("PB", 0.0)
        + edited_food_data.get("EE", 0.0)
        + edited_food_data.get("Ash", 0.0)
        + edited_food_data.get("Humidity", 0.0)
        + edited_food_data.get("FC", 0.0)
    )

    st.session_state["analysis_food_data_edited"] = edited_food_data.copy()
    st.session_state["analysis_food_name_edited"] = food_name
    st.session_state["analysis_food_proximal_sum"] = suma_proximal

    if suma_proximal > 100:
        st.error(
            f"⚠️ La suma de PB + EE + Cenizas + Humedad + FC es {suma_proximal:.1f}%. "
            "Debe ser ≤ 100% para calcular correctamente el ENA."
        )
        st.stop()

    if suma_proximal < 40:
        st.warning(
            f"⚠️ La suma proximal actual es baja ({suma_proximal:.1f}%). "
            "Verifica que los valores estén expresados en porcentaje sobre alimento tal como se ofrece."
        )
    # Recalculate derived values from edited data
    ENA = calculate_ena(edited_food_data)
    species_energy = edited_food_data.get(
        "species",
        st.session_state.get("especie_mascota", "perro"),
    )
    
    energy = calculate_energy(
        edited_food_data,
        species=species_energy,
    )

    # ── Energías alternativas del fabricante ────────────────────────────────
    me_formula_kcal_100g = float(energy.get("ME", 0.0) or 0.0)

    me_manufacturer_kcal_kg = float(
        edited_food_data.get("ME_manufacturer_kcal_kg", 0.0) or 0.0
    )
    me_manufacturer_kcal_100g = (
        me_manufacturer_kcal_kg / 10.0
        if me_manufacturer_kcal_kg > 0
        else 0.0
    )

    manufacturer_g_day_10kg = float(
        edited_food_data.get("manufacturer_g_day_dog_10kg", 0.0) or 0.0
    )

    me_inferred_kcal_kg = infer_me_from_manufacturer_dog_10kg(
        manufacturer_g_day_10kg
    )
    me_inferred_kcal_100g = (
        me_inferred_kcal_kg / 10.0
        if me_inferred_kcal_kg > 0
        else 0.0
    )
    # ---- Métricas de nutrientes proximales ----
    st.markdown("#### 📊 Composición Proximal")

    prox_col1, prox_col2 = st.columns(2)
    with prox_col1:
        st.metric("🥩 Proteína Bruta (PB)", f"{edited_food_data['PB']:.2f} %",
                  help="PB: Proteína Bruta (base tal como está)")
        st.metric("⚫ Cenizas", f"{edited_food_data['Ash']:.2f} %",
                  help="Contenido de cenizas (minerales totales)")
        st.metric("🌾 Fibra Cruda (FC)", f"{edited_food_data['FC']:.2f} %",
                  help="Fibra Cruda (base tal como está)")
    with prox_col2:
        st.metric("🧈 Extracto Etéreo (EE)", f"{edited_food_data['EE']:.2f} %",
                  help="EE: Grasa o Extracto Etéreo (base tal como está)")
        st.metric("💧 Humedad", f"{edited_food_data['Humidity']:.2f} %",
                  help="Contenido de humedad del alimento")
        st.metric("🌽 Extracto No Nitrogenado (ENA)", f"{ENA:.2f} %",
                  help="ENA calculado por diferencia: 100 − PB − EE − Ash − Humedad − FC")

    st.markdown("#### 📈 Valores Derivados")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔬 Materia Seca (MS)", f"{energy['MS']:.1f} %",
                  help="MS = 100 − Humedad")
    with col2:
        st.metric("📐 FC en base MS", f"{energy['FC_MS']:.2f} %",
                  help="FC_MS = (FC / MS) × 100")

    # ── Datos energéticos del fabricante ─────────────────────────────────────
    st.markdown("---")
    st.subheader("🏷️ Datos energéticos del fabricante")

    fab_col1, fab_col2, fab_col3 = st.columns(3)

    with fab_col1:
        st.metric(
            "ME fórmula Uywa",
            f"{me_formula_kcal_100g:.1f} kcal/100g",
            help="Energía metabolizable estimada desde composición proximal.",
        )

    with fab_col2:
        if me_manufacturer_kcal_100g > 0:
            st.metric(
                "ME declarada fabricante",
                f"{me_manufacturer_kcal_100g:.1f} kcal/100g",
                help="Energía declarada en etiqueta o ficha técnica del fabricante.",
            )
        else:
            st.metric("ME declarada fabricante", "No disponible")

    with fab_col3:
        if me_inferred_kcal_100g > 0:
            st.metric(
                "ME inferida por gramaje",
                f"{me_inferred_kcal_100g:.1f} kcal/100g",
                help="Estimación inversa desde la dosis declarada para perro adulto entero de 10 kg.",
            )
        else:
            st.metric("ME inferida por gramaje", "No disponible")

    opciones_me = ["Fórmula Uywa"]

    if me_manufacturer_kcal_100g > 0:
        opciones_me.append("ME declarada fabricante")

    if me_inferred_kcal_100g > 0:
        opciones_me.append("ME inferida desde gramaje fabricante")

    fuente_me = st.selectbox(
        "Fuente energética para calcular la dosis",
        opciones_me,
        key=f"fuente_me_{safe_key}",
        help="Selecciona qué valor de energía metabolizable se usará para calcular aporte y gramos recomendados.",
    )

    if fuente_me == "ME declarada fabricante":
        me_usada_kcal_100g = me_manufacturer_kcal_100g
    elif fuente_me == "ME inferida desde gramaje fabricante":
        me_usada_kcal_100g = me_inferred_kcal_100g
    else:
        me_usada_kcal_100g = me_formula_kcal_100g

    st.caption(
        f"ME usada para el cálculo de dosis: **{me_usada_kcal_100g:.1f} kcal/100g** "
        f"({fuente_me})."
    )
    
    # ---- Cálculo de Aporte Energético ----
    st.subheader("🧮 Cálculo de Aporte Energético")
    st.markdown(
        "Ingresa los **gramos diarios** del alimento seleccionado para calcular el aporte energético "
        "y compararlo con el requerimiento diario de la mascota (MER)."
    )

    gramos_key = f"gramos_alimento_{food_name}"
    gramos_input = st.number_input(
        f"Gramos diarios de **{get_food_short_name(food_name)}**",
        min_value=0.0,
        max_value=5000.0,
        value=float(st.session_state.get(gramos_key, 100.0)),
        step=10.0,
        key=gramos_key,
    )

    # Energía metabolizable aportada
    me_por_100g = me_usada_kcal_100g
    me_total_kcal = (me_por_100g / 100.0) * gramos_input

    # ── Guardar resultados actuales para resumen, exportación y seguimiento ──
    st.session_state["me_alimento_actual"] = me_por_100g
    st.session_state["energia_aportada_actual"] = me_total_kcal

    # Fuente energética utilizada en el análisis
    st.session_state["fuente_me_actual"] = fuente_me
    st.session_state["me_formula_uywa_actual"] = me_formula_kcal_100g
    st.session_state["me_manufacturer_actual"] = me_manufacturer_kcal_100g
    st.session_state["me_inferred_manufacturer_actual"] = me_inferred_kcal_100g

    if st.session_state.get("energia_actual", None):
        mer_tmp = st.session_state.get("energia_actual")
        st.session_state["cobertura_energia_actual"] = (
            (me_total_kcal / mer_tmp) * 100.0 if mer_tmp > 0 else 0.0
        )
        st.session_state["gramos_recomendados_actual"] = (
            mer_tmp / (me_por_100g / 100.0) if me_por_100g > 0 else 0.0
        )
    else:
        st.session_state["cobertura_energia_actual"] = 0.0
        st.session_state["gramos_recomendados_actual"] = 0.0
    
    # MER del animal desde sesión (calculado en Tab 1)
    mer_animal = st.session_state.get("energia_actual", None)

    # Gramos de nutrientes aportados (siempre calculados)
    gramos_pb = (edited_food_data["PB"] / 100.0) * gramos_input
    gramos_ee = (edited_food_data["EE"] / 100.0) * gramos_input

    # Requerimientos de proteína y grasa del perfil de la mascota (Tab 1)
    req_pb_g = st.session_state.get("req_pb_g", None)
    req_ee_g = st.session_state.get("req_ee_g", None)

    # ── 🩺 DECISIÓN NUTRICIONAL DEL ALIMENTO ──────────────────────────────────
    st.markdown("---")
    st.subheader("🩺 Decisión Nutricional del Alimento")

    if mer_animal and mer_animal > 0:
        cobertura_energetica_pct = (me_total_kcal / mer_animal) * 100.0
        diferencia_kcal = me_total_kcal - mer_animal
        gramos_recomendados = (mer_animal / (me_por_100g / 100.0)) if me_por_100g > 0 else 0.0
        diferencia_g = gramos_recomendados - gramos_input

        clase = get_clase_decision(cobertura_energetica_pct)
        resultado = get_resultado_cobertura(cobertura_energetica_pct)
        icono = DECISION_COLORS[clase]
        signo = "+" if diferencia_kcal > 0 else ""

        st.markdown(
            f"""
            <div class="decision-card {clase}">
                <div class="decision-icon">{icono}</div>
                <div class="decision-status">{resultado.upper()}</div>
                <div class="decision-percentage">{cobertura_energetica_pct:.1f}%</div>
                <div class="decision-details">
                    Aporte: {me_total_kcal:.0f} kcal/día &nbsp;·&nbsp; Requerimiento: {mer_animal:.0f} kcal/día
                </div>
                <div class="decision-diff">{signo}{diferencia_kcal:.0f} kcal/día</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric(
                "📌 Recomendado",
                f"{gramos_recomendados:.0f} g/día",
                help="Gramos necesarios para cubrir exactamente el MER del animal.",
            )
        with col_r2:
            st.metric(
                "📊 Actual",
                f"{gramos_input:.0f} g/día",
                help="Gramos diarios que actualmente ingresa el animal.",
            )
        with col_r3:
            if abs(diferencia_g) < 5:
                estado_g = "✓ En rango aceptable"
            elif diferencia_g > 0:
                estado_g = f"↑ Faltan {diferencia_g:.0f} g"
            else:
                estado_g = f"↓ Exceso {abs(diferencia_g):.0f} g"
            st.metric(
                "📏 Diferencia",
                estado_g,
                help="Diferencia entre la cantidad recomendada y la actual.",
            )

                # Diagnóstico proteína y grasa
        cob_pb = (gramos_pb / req_pb_g * 100.0) if req_pb_g and req_pb_g > 0 else None
        cob_ee = (gramos_ee / req_ee_g * 100.0) if req_ee_g and req_ee_g > 0 else None

        # Guardar coberturas reales para seguimiento del paciente
        st.session_state["cobertura_proteina_actual"] = cob_pb
        st.session_state["cobertura_grasa_actual"] = cob_ee
        st.session_state["cobertura_energia_actual"] = cobertura_energetica_pct
        st.session_state["gramos_recomendados_actual"] = gramos_recomendados

        if cob_pb is not None or cob_ee is not None:
            col_p, col_e_diag = st.columns(2)

            if cob_pb is not None:
                pb_estado = (
                    "✓ Adecuada" if 90 <= cob_pb <= 110
                    else ("⚠ Insuficiente" if cob_pb < 90 else "⚠ Excedida")
                )
                with col_p:
                    st.metric(
                        "🥩 Proteína",
                        f"{cob_pb:.0f}%",
                        pb_estado,
                        help=f"Proteína aportada: {gramos_pb:.1f} g vs requerimiento: {req_pb_g:.1f} g",
                    )

            if cob_ee is not None:
                ee_estado = (
                    "✓ Adecuada" if 90 <= cob_ee <= 110
                    else ("⚠ Insuficiente" if cob_ee < 90 else "⚠ Excedida")
                )
                with col_e_diag:
                    st.metric(
                        "🧈 Grasa",
                        f"{cob_ee:.0f}%",
                        ee_estado,
                        help=f"Grasa aportada: {gramos_ee:.1f} g vs requerimiento: {req_ee_g:.1f} g",
                    )
        else:
            cob_pb = None
            cob_ee = None
            
        # Párrafo interpretativo
        interpretacion = generar_interpretacion_alimento(
            food_name, cobertura_energetica_pct, me_total_kcal, mer_animal,
            gramos_input, gramos_recomendados, cob_pb, cob_ee,
        )
        st.info(interpretacion)
    else:
        st.info(
            "💡 Completa el perfil de la mascota en la pestaña **Perfil de Mascota** "
            "para obtener el MER y ver la decisión nutricional."
        )

    st.markdown("---")

    # ── Cards de energía ─────────────────────────────────────────────────────
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.metric(
            label="⚡ Energía Aportada",
            value=f"{me_total_kcal:.1f} kcal",
            help="Energía Metabolizable total aportada por los gramos ingresados.",
        )
    with col_e2:
        mer_display = f"{mer_animal:.1f} kcal/día" if mer_animal else "No calculado"
        st.metric(
            label="🎯 MER del Animal",
            value=mer_display,
            help="Requerimiento Energético Metabolizable diario del animal (calculado en Tab 1).",
        )
    with col_e3:
        if mer_animal and mer_animal > 0:
            cobertura_pct = (me_total_kcal / mer_animal) * 100.0
            delta_color = "normal" if cobertura_pct <= ENERGY_COVERAGE_THRESHOLD else "inverse"
            st.metric(
                label="📊 Cobertura Energética",
                value=f"{cobertura_pct:.1f}%",
                delta=f"{cobertura_pct - 100:.1f}% vs requerimiento",
                delta_color=delta_color,
                help="Porcentaje del requerimiento energético diario cubierto.",
            )
        else:
            st.metric(label="📊 Cobertura Energética", value="—", help="Completa el perfil en Tab 1 para obtener el MER.")

    # ── Expander: Cálculo energético detallado (NRC) ──────────────────────────
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

        st.markdown(
            f"""
            <div style="background:#fffbe6;border-left:4px solid #FFB703;border-radius:8px;
                        padding:12px 18px;margin-bottom:16px;font-size:0.93rem;">
                <b>Ecuaciones utilizadas FEDIAF/NRC — {species_label}:</b><br>
                1. <code>GE = (5.7×PB) + (9.4×EE) + [4.1×(ENA+FC)]</code><br>
                2. <code>{de_formula_text}</code><br>
                3. <code>DE = GE × (%DE/100)</code><br>
                4. <code>{me_formula_text}</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 📋 Cálculo Paso a Paso (NRC)")
        energy_calc_rows = [
            ("Materia Seca (MS)", energy["MS"], "%"),
            ("FC en base MS (FC_MS)", energy["FC_MS"], "%"),
            ("Energía Bruta (GE)", energy["GE"], "kcal/100g"),
            ("Digestibilidad Energética (DE%)", energy["DE_pct"], "%"),
            ("Energía Digestible (DE)", energy["DE"], "kcal/100g"),
            ("Energía Metabolizable (ME)", energy["ME"], "kcal/100g"),
        ]
        html_energy_calc = "<table class='energy-table'><thead><tr><th>Parámetro</th><th>Valor</th><th>Unidad</th></tr></thead><tbody>"
        for param, val, unit in energy_calc_rows:
            html_energy_calc += f"<tr><td>{param}</td><td>{val:.2f}</td><td>{unit}</td></tr>"
        html_energy_calc += "</tbody></table>"
        st.markdown(html_energy_calc, unsafe_allow_html=True)

        me_por_kg = energy["ME"] * 10.0
        st.markdown(
            f"""
            <div style="background:linear-gradient(90deg,#2176ff,#52B788);
                        border-radius:10px;padding:16px;text-align:center;margin:10px 0 20px 0;">
                <span style="color:#fff;font-size:1.1rem;">Energía Metabolizable</span><br>
                <span style="color:#fff;font-size:2.5rem;font-weight:700;">{energy['ME']:.1f}</span>
                <span style="color:#ffffffcc;font-size:1.2rem;"> kcal / 100 g</span>
                &nbsp;&nbsp;
                <span style="color:#ffffffcc;font-size:1rem;">({me_por_kg:.0f} kcal / kg)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 📊 Desglose del Aporte Energético")
        base_rows = [
            {"Concepto": "ME del alimento (kcal/100g)", "Valor": f"{me_por_100g:.2f} kcal/100g"},
            {"Concepto": f"Gramos diarios de {food_name}", "Valor": f"{gramos_input:.1f} g/día"},
            {"Concepto": "Gramos de Proteína Bruta (PB)", "Valor": f"{gramos_pb:.2f} g/día"},
            {"Concepto": "Gramos de Grasa (EE)", "Valor": f"{gramos_ee:.2f} g/día"},
            {"Concepto": "Energía Metabolizable aportada", "Valor": f"{me_total_kcal:.2f} kcal/día"},
        ]
        if mer_animal and mer_animal > 0:
            _cob = (me_total_kcal / mer_animal) * 100.0
            base_rows += [
                {"Concepto": "MER del animal", "Valor": f"{mer_animal:.2f} kcal/día"},
                {"Concepto": "Cobertura energética", "Valor": f"{_cob:.1f}%"},
            ]
        aporte_df = pd.DataFrame(base_rows)
        html_aporte = "<table class='energy-table'><thead><tr><th>Concepto</th><th>Valor</th></tr></thead><tbody>"
        for _, row in aporte_df.iterrows():
            html_aporte += f"<tr><td>{row['Concepto']}</td><td>{row['Valor']}</td></tr>"
        html_aporte += "</tbody></table>"
        st.markdown(html_aporte, unsafe_allow_html=True)
 
    # ── Gráfico de composición (torta/donut) ──────────────────────────────────
    st.markdown("#### 📈 Composición del Alimento")
    st.plotly_chart(plot_macronutrients_pie(food_name, edited_food_data), use_container_width=True)

    # Gráfico comparativo mejorado (solo cuando MER disponible)
    if mer_animal and mer_animal > 0:
        render_requirement_coverage_cards(
            mer_animal=mer_animal,
            me_total_kcal=me_total_kcal,
            req_pb_g=req_pb_g,
            gramos_pb=gramos_pb,
            req_ee_g=req_ee_g,
            gramos_ee=gramos_ee,
        )
    # ── Perfil técnico del alimento seleccionado ─────────────────────────────
    st.markdown("---")
    st.subheader("🔬 Perfil técnico del alimento seleccionado")

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
        st.markdown("#### Origen de la energía metabolizable")
    
        energy_sources = pd.DataFrame([
            {
                "Fuente": "Proteína",
                "kcal": bd_single["me_pb"],
                "pct": bd_single["pct_pb"],
                "color": "#DC2626",
            },
            {
                "Fuente": "Grasa",
                "kcal": bd_single["me_ee"],
                "pct": bd_single["pct_ee"],
                "color": "#F59E0B",
            },
            {
                "Fuente": "Carbohidratos",
                "kcal": bd_single["me_cho"],
                "pct": bd_single["pct_cho"],
                "color": "#2563EB",
            },
        ])
    
        fig_single_energy = go.Figure()
    
        fig_single_energy.add_trace(
            go.Bar(
                y=energy_sources["Fuente"],
                x=energy_sources["kcal"],
                orientation="h",
                marker=dict(color=energy_sources["color"]),
                text=[
                    f"{row.kcal:.1f} kcal/100g · {row.pct:.1f}%"
                    for row in energy_sources.itertuples()
                ],
                textposition="auto",
                hovertemplate="<b>%{y}</b><br>%{x:.1f} kcal/100g<extra></extra>",
            )
        )
    
        fig_single_energy.update_layout(
            title=dict(
                text="Distribución energética estimada",
                font=dict(size=17, family="Inter, Montserrat, sans-serif", color="#0F172A"),
                x=0.02,
                xanchor="left",
            ),
            height=340,
            margin=dict(t=60, b=35, l=20, r=20),
            xaxis_title="kcal/100 g",
            yaxis_title="",
            yaxis=dict(autorange="reversed"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, Montserrat, sans-serif", color="#334155"),
            showlegend=False,
        )
    
        fig_single_energy.update_xaxes(
            showgrid=True,
            gridcolor="rgba(148,163,184,0.25)",
            zeroline=False,
        )
    
        fig_single_energy.update_yaxes(
            showgrid=False,
        )
    
        st.plotly_chart(fig_single_energy, use_container_width=True)

   with tec_col2:
        st.markdown("#### Lectura rápida")
    
        pb_pct = float(edited_food_data.get("PB", 0))
        ee_pct = float(edited_food_data.get("EE", 0))
        fc_pct = float(edited_food_data.get("FC", 0))
        ena_pct = float(ENA)
        me_pct = float(me_por_100g)
    
        perfil_tags = []
    
        if pb_pct >= 28:
            perfil_tags.append("Alta proteína")
        elif pb_pct >= 20:
            perfil_tags.append("Proteína moderada")
        else:
            perfil_tags.append("Proteína baja")
    
        if ee_pct >= 18:
            perfil_tags.append("Alta grasa")
        elif ee_pct <= 10:
            perfil_tags.append("Grasa controlada")
        else:
            perfil_tags.append("Grasa moderada")
    
        if ena_pct >= 45:
            perfil_tags.append("ENA elevado")
        elif ena_pct <= 30:
            perfil_tags.append("ENA bajo/moderado")
        else:
            perfil_tags.append("ENA moderado")
    
        if me_pct >= 380:
            perfil_tags.append("Alta densidad energética")
        elif me_pct <= 310:
            perfil_tags.append("Baja densidad energética")
        else:
            perfil_tags.append("Densidad energética media")
    
        st.write("Perfil técnico")
        st.pills(
            "Indicadores",
            perfil_tags,
            selection_mode="multi",
            default=perfil_tags,
            disabled=True,
            label_visibility="collapsed",
        )
    
        st.markdown("")
    
        m1, m2 = st.columns(2)
    
        with m1:
            st.metric("ME estimada", f"{me_pct:.1f} kcal/100g")
            st.metric("Proteína PB", f"{pb_pct:.1f}%")
            st.metric("Fibra FC", f"{fc_pct:.1f}%")
    
        with m2:
            st.metric("Grasa EE", f"{ee_pct:.1f}%")
            st.metric("ENA", f"{ena_pct:.1f}%")
            st.metric("Humedad", f"{edited_food_data.get('Humidity', 0):.1f}%")

    st.markdown("#### 🌱 Principales materias primas identificadas")

    source_pb = edited_food_data.get("source_pb", "")
    source_ee = edited_food_data.get("source_ee", "")
    source_fc = edited_food_data.get("source_fc", "")
    
    col_pb, col_ee, col_fc = st.columns(3)
    
    with col_pb:
        st.markdown("##### 🥩 Proteína")
    
        if source_pb:
            for item in source_pb.split(";"):
                st.markdown(f"• {item.strip()}")
        else:
            st.caption("No especificado")
    
    with col_ee:
        st.markdown("##### 🧈 Grasa")
    
        if source_ee:
            for item in source_ee.split(";"):
                st.markdown(f"• {item.strip()}")
        else:
            st.caption("No especificado")
    
    with col_fc:
        st.markdown("##### 🌾 Carbohidratos y fibra")
    
        if source_fc:
            for item in source_fc.split(";"):
                st.markdown(f"• {item.strip()}")
        else:
            st.caption("No especificado")
