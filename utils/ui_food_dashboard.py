import streamlit as st
import pandas as pd


def normalize_life_stage_label(value: str) -> str:
    text = str(value or "").strip().replace("-", " · ")

    replacements = {
        "Adultos": "Adulto",
        "Cachorro Razas": "Cachorro · Razas",
        "Cachorro·Razas": "Cachorro · Razas",
        "Adulto todas las razas": "Adulto · Todas las razas",
        "Adultos Todas las razas": "Adulto · Todas las razas",
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
            fields = get_food_card_fields(alimento, foods)
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
