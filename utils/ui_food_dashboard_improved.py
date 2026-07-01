"""
Componentes visuales para el dashboard de análisis de alimentos UYWA Pets.

Este módulo no calcula energía ni requerimientos. Solo renderiza UI.
"""

from __future__ import annotations

import streamlit as st

from utils.ui_theme import (
    COLOR_BORDER,
    COLOR_MUTED,
    COLOR_PANEL,
    COLOR_SOFT_BG,
    COLOR_TEXT,
    NUTRIENT_COLORS,
    STATUS_BG,
    STATUS_COLORS,
    card_style,
)


def normalize_life_stage_label(value: str) -> str:
    text = str(value or "").strip().replace("-", " · ")

    replacements = {
        "Adultos": "Adulto",
        "Cachorro Razas": "Cachorro · Razas",
        "Cachorro·Razas": "Cachorro · Razas",
        "Adulto todas las razas": "Adulto · Todas las razas",
        "Adultos Todas las razas": "Adulto · Todas las razas",
        "Adultos para todas las razas": "Adulto · Todas las razas",
        "Adultos-Todos los tamaños control de peso": "Adulto · Control de peso",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " · ".join([p.strip() for p in text.split("·") if p.strip()])


def get_food_card_fields(food_name: str, foods: dict) -> dict:
    data = foods.get(food_name, {}) or {}

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


def _render_badge(text: str, color: str = "#2563EB", bg: str = "#EFF6FF") -> str:
    return (
        f"<span style='background:{bg};color:{color};border:1px solid {color}33;"
        "border-radius:999px;padding:4px 9px;font-size:0.75rem;font-weight:750;'>"
        f"{text}</span>"
    )


def render_food_header(food_name: str, food_data: dict, food_title: str, food_display: str):
    """Encabezado visual del alimento seleccionado."""
    emoji = food_data.get("emoji", "🐾")
    description = food_data.get("description", "")
    category = food_data.get("category", "")

    category_badge = _render_badge(category, "#2563EB", "#EFF6FF") if category else ""

    st.markdown(
        f"""
        <div style="{card_style(border_color='#BFDBFE', background='#FFFFFF', radius=20, padding='18px 22px')} border-left:6px solid #2563EB;">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="font-size:2.2rem;">{emoji}</div>
                <div style="flex:1;">
                    <div style="font-size:1.35rem;font-weight:900;color:{COLOR_TEXT};line-height:1.15;">
                        {food_title}
                    </div>
                    <div style="font-size:0.86rem;color:{COLOR_MUTED};font-weight:650;margin-top:3px;">
                        {food_display}
                    </div>
                </div>
                <div>{category_badge}</div>
            </div>
            <div style="font-size:0.92rem;color:{COLOR_MUTED};margin-top:12px;line-height:1.4;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_food_selector_cards(
    alimentos: list[str],
    foods: dict,
    key_prefix: str = "food_card",
    page_size: int = 6,
) -> str | None:
    """
    Selector visual de alimentos por tarjetas con paginación.
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
            <div style="text-align:center;color:{COLOR_MUTED};font-weight:800;padding-top:0.62rem;">
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
            fields = get_food_card_fields(alimento, foods)
            selected = alimento == current

            border = "#2563EB" if selected else COLOR_BORDER
            bg = "#EFF6FF" if selected else COLOR_PANEL
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
                        border-radius:20px;
                        padding:16px 18px;
                        min-height:158px;
                        box-shadow:{shadow};
                        margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                            <div style="font-size:1.9rem;">{fields['emoji'] or '🐾'}</div>
                            <div>
                                <div style="font-size:1.05rem;font-weight:900;color:{COLOR_TEXT};line-height:1.15;">
                                    {fields['nombre']}
                                </div>
                                <div style="font-size:0.86rem;color:{COLOR_MUTED};font-weight:750;">
                                    {fields['marca']}
                                </div>
                            </div>
                        </div>
                        <div style="font-size:0.86rem;color:#1F2937;margin-top:8px;min-height:34px;">
                            {fields['etapa']}
                        </div>
                        <div style="margin-top:10px;">
                            {_render_badge(fields['especie'], '#475569', COLOR_SOFT_BG)}
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


def _coverage_status(aporte, req):
    if req is None or req <= 0:
        return None, "Sin referencia", "neutral"

    pct = (aporte / req) * 100.0

    if pct < 90:
        return pct, "Bajo", "low"
    if pct <= 110:
        return pct, "En rango", "ok"

    return pct, "Excedido", "high"


def render_requirement_coverage_cards(
    mer_animal,
    me_total_kcal,
    req_pb_g,
    gramos_pb,
    req_ee_g,
    gramos_ee,
):
    """
    Tarjetas de cobertura de requerimientos usando componentes nativos de Streamlit.
    """
    items = [
        {"title": "⚡ Energía", "req": mer_animal, "aporte": me_total_kcal, "unit": "kcal/día"},
        {"title": "🥩 Proteína", "req": req_pb_g, "aporte": gramos_pb, "unit": "g/día"},
        {"title": "🧈 Grasa", "req": req_ee_g, "aporte": gramos_ee, "unit": "g/día"},
    ]

    st.markdown("#### Cobertura de requerimientos")

    for item in items:
        pct, estado, status = _coverage_status(item["aporte"], item["req"])
        color = STATUS_COLORS[status]
        bg = STATUS_BG[status]

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
            delta_color = "normal"
        else:
            value_text = f"{pct:.0f}%"
            progress_value = min(pct / 140.0, 1.0)
            delta_text = f"{estado} · {pct - 100:+.0f}% vs req."
            delta_color = "inverse" if status == "high" else "normal"

        with st.container(border=True):
            c1, c2 = st.columns([2.4, 1])

            with c1:
                st.markdown(f"**{item['title']}**")
                st.caption(f"Requerimiento: **{req_text}** · Aporte: **{aporte_text}**")
                st.progress(progress_value)

            with c2:
                st.markdown(
                    f"<div style='background:{bg};border:1px solid {color}33;border-radius:16px;padding:4px 8px;'>",
                    unsafe_allow_html=True,
                )
                st.metric(
                    label="Cobertura",
                    value=value_text,
                    delta=delta_text,
                    delta_color=delta_color,
                )
                st.markdown("</div>", unsafe_allow_html=True)


def render_composition_metrics(edited_food_data: dict, ena: float, energy: dict):
    """Métricas de composición proximal y valores derivados."""
    st.markdown("#### 📊 Composición proximal")

    prox_col1, prox_col2 = st.columns(2)
    with prox_col1:
        st.metric("🥩 Proteína Bruta (PB)", f"{edited_food_data['PB']:.2f} %")
        st.metric("⚫ Cenizas", f"{edited_food_data['Ash']:.2f} %")
        st.metric("🌾 Fibra Cruda (FC)", f"{edited_food_data['FC']:.2f} %")
    with prox_col2:
        st.metric("🧈 Extracto Etéreo (EE)", f"{edited_food_data['EE']:.2f} %")
        st.metric("💧 Humedad", f"{edited_food_data['Humidity']:.2f} %")
        st.metric("🌽 Extracto No Nitrogenado (ENA)", f"{ena:.2f} %")

    st.markdown("#### 📈 Valores derivados")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔬 Materia Seca (MS)", f"{energy['MS']:.1f} %")
    with col2:
        st.metric("📐 FC en base MS", f"{energy['FC_MS']:.2f} %")


def render_technical_profile(
    edited_food_data: dict,
    ena: float,
    me_por_100g: float,
):
    """
    Panel derecho del perfil técnico del alimento.
    """
    st.markdown("#### Lectura rápida")

    pb_pct = float(edited_food_data.get("PB", 0) or 0)
    ee_pct = float(edited_food_data.get("EE", 0) or 0)
    fc_pct = float(edited_food_data.get("FC", 0) or 0)
    humidity_pct = float(edited_food_data.get("Humidity", 0) or 0)
    ena_pct = float(ena or 0)
    me_pct = float(me_por_100g or 0)

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

    try:
        st.pills(
            "Indicadores",
            perfil_tags,
            selection_mode="multi",
            default=perfil_tags,
            disabled=True,
            label_visibility="collapsed",
        )
    except Exception:
        st.caption(" · ".join(perfil_tags))

    m1, m2 = st.columns(2)

    with m1:
        st.metric("ME estimada", f"{me_pct:.1f} kcal/100g")
        st.metric("Proteína PB", f"{pb_pct:.1f}%")
        st.metric("Fibra FC", f"{fc_pct:.1f}%")

    with m2:
        st.metric("Grasa EE", f"{ee_pct:.1f}%")
        st.metric("ENA", f"{ena_pct:.1f}%")
        st.metric("Humedad", f"{humidity_pct:.1f}%")


def render_ingredient_sources(edited_food_data: dict):
    """Fuentes principales de proteína, grasa y carbohidratos/fibra."""
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
