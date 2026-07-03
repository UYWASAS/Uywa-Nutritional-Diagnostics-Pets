"""
UYWA Food Dashboard
Componentes visuales limpios para análisis individual de alimentos.

Versión con soporte para imagen de empaque:
- Lee food_data["package_image"].
- Busca imágenes en assets/food_images/packages/ y assets/food_images/brands/.
- Tolera mayúsculas/minúsculas y nombres con o sin extensión.
- Muestra ícono genérico si no encuentra imagen.
"""

from __future__ import annotations

import html
import textwrap
from pathlib import Path

import streamlit as st

from utils.ui_theme import COLORS, NUTRIENT_COLORS, coverage_status
from utils.ui_cards import (
    render_section_title,
    render_kpi_card,
    render_progress_card,
    render_score_card,
    render_source_chip_group,
    render_badges,
)


PACKAGE_IMAGE_DIRS = [
    Path("assets") / "food_images" / "packages",
    Path("assets") / "food_images" / "brands",
]


def _esc(value) -> str:
    return html.escape(str(value or ""))


def _render_html(raw_html: str) -> None:
    st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)


def _clean(value) -> str:
    return str(value or "").strip()


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


# =============================================================================
# IMÁGENES DE EMPAQUE
# =============================================================================

def get_package_image_path(food_data: dict) -> Path | None:
    """
    Retorna la ruta local de la imagen del empaque si existe.

    Lee:
        food_data["package_image"]

    Busca en:
        assets/food_images/packages/
        assets/food_images/brands/

    La búsqueda es tolerante a:
    - Mayúsculas/minúsculas.
    - Nombre con o sin extensión.
    - Extensiones png, jpg, jpeg, webp.
    """
    image_name = _clean(food_data.get("package_image"))

    if not image_name:
        return None

    valid_exts = [".png", ".jpg", ".jpeg", ".webp"]
    candidates: list[Path] = []

    for folder in PACKAGE_IMAGE_DIRS:
        candidates.append(folder / image_name)

    if Path(image_name).suffix == "":
        for folder in PACKAGE_IMAGE_DIRS:
            for ext in valid_exts:
                candidates.append(folder / f"{image_name}{ext}")

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    image_stem = Path(image_name).stem.lower()
    image_suffix = Path(image_name).suffix.lower()

    for folder in PACKAGE_IMAGE_DIRS:
        if not folder.exists():
            continue

        for file in folder.iterdir():
            if not file.is_file():
                continue

            same_stem = file.stem.lower() == image_stem
            same_suffix = image_suffix == "" or file.suffix.lower() == image_suffix

            if same_stem and same_suffix:
                return file

    return None


def render_package_image(food_data: dict, size: int = 96) -> None:
    """
    Renderiza imagen de empaque o un placeholder si no existe.
    """
    image_path = get_package_image_path(food_data)

    if image_path:
        st.image(str(image_path), width=size)
        return

    st.markdown(
        f"""
        <div style="
            width:{size}px;
            height:{size}px;
            border-radius:20px;
            background:linear-gradient(135deg,#EFF6FF 0%,#F8FAFC 100%);
            border:1px solid #DBEAFE;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:36px;
            box-shadow:0 8px 20px rgba(15,23,42,0.06);
        ">
            🥫
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_food_card_fields(food_name: str, foods: dict) -> dict:
    data = foods.get(food_name, {}) or {}

    nombre = str(data.get("name", "") or "").strip()
    marca = str(data.get("brand", "") or "").strip()
    etapa = str(data.get("life_stage", "") or "").strip()
    especie = str(data.get("species", "") or "").strip()
    categoria = str(data.get("category", "") or "").strip()
    emoji = str(data.get("emoji", "") or "").strip()
    package_image = str(data.get("package_image", "") or "").strip()

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
        "package_image": package_image,
        "description": str(data.get("description", "") or "").strip(),
        "data": data,
    }


def render_food_selector_cards(
    alimentos: list[str],
    foods: dict,
    key_prefix: str = "food_card",
    page_size: int = 6,
) -> str | None:
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

    render_section_title(
        "Selecciona un alimento balanceado",
        kicker="Base de alimentos",
        subtitle="Explora alimentos filtrados por especie y selecciona el producto a evaluar.",
        icon="🍽️",
    )

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
            <div style="text-align:center;color:{COLORS['muted']};font-weight:800;padding-top:0.6rem;">
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
    alimentos_pagina = alimentos[page_start:page_start + page_size]

    for row_start in range(0, len(alimentos_pagina), 3):
        cols = st.columns(3)

        for i, alimento in enumerate(alimentos_pagina[row_start:row_start + 3]):
            fields = get_food_card_fields(alimento, foods)
            selected = alimento == current
            global_index = page_start + row_start + i

            with cols[i]:
                with st.container(border=True):
                    img_col, info_col = st.columns([0.9, 2.6])

                    with img_col:
                        render_package_image(fields["data"], size=86)

                    with info_col:
                        st.markdown(f"**{fields['nombre']}**")
                        st.caption(fields["marca"])
                        st.markdown(fields["etapa"])

                        badge_text = fields["especie"]
                        if fields["categoria"]:
                            badge_text += f" · {fields['categoria']}"

                        st.caption(badge_text)

                if st.button(
                    "Seleccionar" if not selected else "Seleccionado",
                    key=f"{key_prefix}_select_{global_index}",
                    use_container_width=True,
                    disabled=selected,
                ):
                    st.session_state[selected_key] = alimento
                    st.rerun()

    return st.session_state.get(selected_key, current)
    
def render_food_header(
    food_name: str,
    food_data: dict,
    short_name: str | None = None,
    display_name: str | None = None,
) -> None:
    title = short_name or food_data.get("name") or food_name
    brand = food_data.get("brand", "")
    species = food_data.get("species", "")
    stage = normalize_life_stage_label(food_data.get("life_stage", ""))
    category = food_data.get("category", "")
    description = food_data.get("description", "")

    _render_html(
        f"""
        <div style="background:linear-gradient(135deg,{COLORS['primary_soft']},#ffffff);
                    border:1px solid {COLORS['border']};border-left:6px solid {COLORS['primary']};
                    border-radius:24px;padding:20px 22px;margin:12px 0 18px 0;
                    box-shadow:0 10px 30px rgba(15,23,42,0.08);">
        """
    )

    img_col, info_col = st.columns([0.8, 5])

    with img_col:
        render_package_image(food_data, size=112)

    with info_col:
        _render_html(
            f"""
            <div style="font-size:1.55rem;font-weight:950;color:{COLORS['ink']};line-height:1.1;">
                {_esc(title)}
            </div>
            <div style="font-size:0.9rem;color:{COLORS['muted']};font-weight:750;margin-top:4px;">
                {_esc(brand)} · {_esc(species).capitalize()} · {_esc(stage)}
            </div>
            <div style="margin-top:12px;color:{COLORS['text']};font-size:0.94rem;line-height:1.4;">
                {_esc(description)}
            </div>
            <div style="margin-top:12px;">
                {f"<span class='uywa-badge'>{_esc(category)}</span>" if category else ""}
                {f"<span class='uywa-badge'>{_esc(display_name)}</span>" if display_name else ""}
            </div>
            """
        )

    _render_html("</div>")


def render_food_composition_metrics(food_data: dict, ena: float, me_kcal_100g: float) -> None:
    render_section_title(
        "Composición proximal",
        kicker="Nutrientes",
        subtitle="Valores expresados sobre alimento tal como se ofrece.",
        icon="📊",
    )

    items = [
        {"title": "Proteína PB", "value": f"{float(food_data.get('PB', 0) or 0):.1f}", "unit": "%", "tone": "protein", "icon": "🥩"},
        {"title": "Grasa EE", "value": f"{float(food_data.get('EE', 0) or 0):.1f}", "unit": "%", "tone": "fat", "icon": "🧈"},
        {"title": "Fibra FC", "value": f"{float(food_data.get('FC', 0) or 0):.1f}", "unit": "%", "tone": "fiber", "icon": "🌾"},
        {"title": "ENA", "value": f"{float(ena or 0):.1f}", "unit": "%", "tone": "carb", "icon": "🌽"},
        {"title": "ME", "value": f"{float(me_kcal_100g or 0):.1f}", "unit": "kcal/100g", "tone": "energy", "icon": "⚡"},
    ]

    cols = st.columns(5)

    for col, item in zip(cols, items):
        with col:
            render_kpi_card(**item)


def render_requirement_coverage_cards(
    mer_animal,
    me_total_kcal,
    req_pb_g,
    gramos_pb,
    req_ee_g,
    gramos_ee,
):
    render_section_title(
        "Cobertura de requerimientos",
        kicker="Requerimiento vs aporte",
        subtitle="Evalúa si la cantidad diaria ingresada cubre energía, proteína y grasa.",
        icon="🎯",
    )

    items = [
        {"title": "⚡ Energía", "req": mer_animal, "aporte": me_total_kcal, "unit": "kcal/día"},
        {"title": "🥩 Proteína", "req": req_pb_g, "aporte": gramos_pb, "unit": "g/día"},
        {"title": "🧈 Grasa", "req": req_ee_g, "aporte": gramos_ee, "unit": "g/día"},
    ]

    for item in items:
        req = item["req"]
        aporte = item["aporte"]
        pct = None if req is None or req <= 0 else (aporte / req) * 100.0
        status = coverage_status(pct)

        req_text = f"Req.: {req:.1f} {item['unit']}" if req is not None and req > 0 else "Sin referencia"
        aporte_text = f"Aporte: {aporte:.1f} {item['unit']}"

        render_progress_card(
            title=item["title"],
            pct=pct,
            req_text=req_text,
            aporte_text=aporte_text,
            status_label=status.label,
            tone=status.key,
        )


def _technical_tags(pb_pct: float, ee_pct: float, ena_pct: float, me_pct: float) -> list[str]:
    tags = []

    if pb_pct >= 28:
        tags.append("Alta proteína")
    elif pb_pct >= 20:
        tags.append("Proteína moderada")
    else:
        tags.append("Proteína baja")

    if ee_pct >= 18:
        tags.append("Alta grasa")
    elif ee_pct <= 10:
        tags.append("Grasa controlada")
    else:
        tags.append("Grasa moderada")

    if ena_pct >= 45:
        tags.append("ENA elevado")
    elif ena_pct <= 30:
        tags.append("ENA bajo/moderado")
    else:
        tags.append("ENA moderado")

    if me_pct >= 380:
        tags.append("Alta densidad energética")
    elif me_pct <= 310:
        tags.append("Baja densidad energética")
    else:
        tags.append("Densidad energética media")

    return tags


def calculate_food_score(pb_pct: float, ee_pct: float, ena_pct: float, me_pct: float) -> float:
    score = 70.0

    if pb_pct >= 20:
        score += min((pb_pct - 20) * 1.2, 14)
    else:
        score -= (20 - pb_pct) * 1.5

    if 10 <= ee_pct <= 18:
        score += 8
    elif ee_pct < 7 or ee_pct > 22:
        score -= 6

    if ena_pct <= 45:
        score += 6
    else:
        score -= min((ena_pct - 45) * 0.6, 10)

    if 300 <= me_pct <= 420:
        score += 6

    return max(0, min(score, 100))


def render_technical_profile(edited_food_data: dict, ena: float, me_por_100g: float):
    pb_pct = float(edited_food_data.get("PB", 0) or 0)
    ee_pct = float(edited_food_data.get("EE", 0) or 0)
    fc_pct = float(edited_food_data.get("FC", 0) or 0)
    humidity_pct = float(edited_food_data.get("Humidity", 0) or 0)
    ena_pct = float(ena or 0)
    me_pct = float(me_por_100g or 0)

    tags = _technical_tags(pb_pct, ee_pct, ena_pct, me_pct)
    score = calculate_food_score(pb_pct, ee_pct, ena_pct, me_pct)

    render_section_title(
        "Lectura rápida",
        kicker="Perfil técnico",
        subtitle="Resumen visual del alimento seleccionado.",
        icon="🧾",
    )

    render_score_card(
        title="Score técnico visual",
        score=score,
        subtitle="Lectura orientativa del perfil proximal",
        tone="success" if score >= 80 else "warning" if score >= 65 else "danger",
    )

    render_badges(tags, status="neutral")

    c1, c2 = st.columns(2)

    with c1:
        render_kpi_card("ME estimada", f"{me_pct:.1f}", "kcal/100g", tone="energy", icon="⚡")
        render_kpi_card("Proteína PB", f"{pb_pct:.1f}", "%", tone="protein", icon="🥩")
        render_kpi_card("Fibra FC", f"{fc_pct:.1f}", "%", tone="fiber", icon="🌾")

    with c2:
        render_kpi_card("Grasa EE", f"{ee_pct:.1f}", "%", tone="fat", icon="🧈")
        render_kpi_card("ENA", f"{ena_pct:.1f}", "%", tone="carb", icon="🌽")
        render_kpi_card("Humedad", f"{humidity_pct:.1f}", "%", tone="humidity", icon="💧")


def render_ingredients_sources(food_data: dict) -> None:
    render_section_title(
        "Principales materias primas identificadas",
        kicker="Fuentes declaradas",
        subtitle="Agrupación de ingredientes asociados a proteína, grasa y carbohidratos/fibra.",
        icon="🌱",
    )

    col_pb, col_ee, col_fc = st.columns(3)

    with col_pb:
        render_source_chip_group(
            "🥩 Proteína",
            food_data.get("source_pb", ""),
            color=NUTRIENT_COLORS.get("protein", "#DC2626"),
        )

    with col_ee:
        render_source_chip_group(
            "🧈 Grasa",
            food_data.get("source_ee", ""),
            color=NUTRIENT_COLORS.get("fat", "#F59E0B"),
        )

    with col_fc:
        render_source_chip_group(
            "🌾 Carbohidratos y fibra",
            food_data.get("source_fc", ""),
            color=NUTRIENT_COLORS.get("fiber", "#16A34A"),
        )


__all__ = [
    "normalize_life_stage_label",
    "get_package_image_path",
    "render_package_image",
    "get_food_card_fields",
    "render_food_selector_cards",
    "render_food_header",
    "render_food_composition_metrics",
    "render_requirement_coverage_cards",
    "render_technical_profile",
    "render_ingredients_sources",
    "calculate_food_score",
]
