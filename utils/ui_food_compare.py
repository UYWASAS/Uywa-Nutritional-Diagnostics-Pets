"""
UYWA Food Compare
Comparador nutricional para pestaña Comparador.

Versión con:
- Selección de fuente energética.
- Exclusión explícita de alimentos sin datos para la fuente seleccionada.
- Etiquetas únicas y limpias.
- Tarjetas visuales con miniatura del empaque.
- Mantiene gráficos comparativos: energía apilada, cobertura y radar.

Requiere que cada alimento pueda incluir opcionalmente:
    package_image: nombre del archivo de imagen del empaque.

Ruta esperada:
    assets/food_images/packages/<package_image>
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.ui_cards import render_section_title, render_kpi_card, render_source_chip_group
from utils.ui_theme import NUTRIENT_COLORS
from utils.ui_food_charts import (
    plot_compare_radar,
    plot_compare_energy_stacked,
    plot_compare_energy_bullet,
)


ENERGY_SOURCE_FORMULA = "Fórmula Uywa"
ENERGY_SOURCE_MANUFACTURER = "ME declarada fabricante"
ENERGY_SOURCE_INFERRED = "ME inferida desde gramaje fabricante"

ENERGY_SOURCE_OPTIONS = [
    ENERGY_SOURCE_FORMULA,
    ENERGY_SOURCE_MANUFACTURER,
    ENERGY_SOURCE_INFERRED,
]

PACKAGE_IMAGE_DIR = Path("assets") / "food_images" / "packages"


# =============================================================================
# UTILIDADES BASE
# =============================================================================

def _clean(value) -> str:
    return str(value or "").strip()


def _safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        value_txt = str(value).strip().replace(",", ".")

        if value_txt == "" or value_txt.lower() == "nan":
            return default

        return float(value_txt)

    except Exception:
        return default


def _short_text(value: str, max_len: int = 42) -> str:
    value = str(value or "").strip()
    if len(value) <= max_len:
        return value
    return value[: max_len - 1].rstrip() + "…"


def _normalize_species(value: str) -> str:
    v = str(value or "").strip().lower()
    if v in ("perro", "canino", "canine", "dog"):
        return "perro"
    if v in ("gato", "felino", "feline", "cat"):
        return "gato"
    return v


def _parse_key_parts(food_name: str) -> dict:
    parts = [p.strip() for p in str(food_name).split("|")]
    parsed = {"id": "", "name": "", "brand": "", "species": "", "life_stage": ""}

    if len(parts) >= 5:
        parsed["id"] = parts[0]
        parsed["name"] = parts[1]
        parsed["brand"] = parts[2]
        parsed["species"] = parts[3]
        parsed["life_stage"] = parts[4]
    elif len(parts) >= 4:
        parsed["name"] = parts[0]
        parsed["brand"] = parts[1]
        parsed["species"] = parts[2]
        parsed["life_stage"] = parts[3]
    elif len(parts) >= 2:
        parsed["name"] = parts[0]
        parsed["brand"] = parts[1]
    else:
        parsed["name"] = str(food_name)

    return parsed


def get_food_identity(food_name: str, data: dict) -> dict:
    parsed = _parse_key_parts(food_name)

    food_id = _clean(data.get("id")) or parsed["id"]
    name = _clean(data.get("name")) or parsed["name"] or str(food_name)
    brand = _clean(data.get("brand")) or parsed["brand"]
    species = _clean(data.get("species")) or parsed["species"]
    life_stage = _clean(data.get("life_stage")) or parsed["life_stage"]
    category = _clean(data.get("category")) or life_stage
    emoji = _clean(data.get("emoji")) or "🐾"
    package_image = _clean(data.get("package_image"))

    return {
        "id": food_id,
        "name": name,
        "brand": brand,
        "species": species,
        "life_stage": life_stage,
        "category": category,
        "emoji": emoji,
        "package_image": package_image,
    }


def food_full_label(food_name: str, data: dict) -> str:
    ident = get_food_identity(food_name, data)
    items = [ident["id"], ident["name"], ident["brand"], ident["species"], ident["life_stage"]]
    return " | ".join([x for x in items if x])


def food_medium_label(food_name: str, data: dict, include_id: bool = False) -> str:
    ident = get_food_identity(food_name, data)
    items = [ident["name"], ident["brand"], ident["species"], ident["life_stage"]]

    if include_id and ident["id"]:
        items.insert(0, ident["id"])

    return " · ".join([x for x in items if x])


def food_short_label(food_name: str, data: dict) -> str:
    ident = get_food_identity(food_name, data)
    items = [ident["name"], ident["brand"]]
    return " · ".join([x for x in items if x]) or str(food_name)


def build_unique_labels(food_names: list[str], foods: dict) -> dict[str, dict]:
    base_short = {
        fname: food_short_label(fname, foods.get(fname, {}) or {})
        for fname in food_names
    }

    counts = Counter(base_short.values())
    labels = {}

    for fname in food_names:
        data = foods.get(fname, {}) or {}
        ident = get_food_identity(fname, data)
        short = base_short[fname]

        if counts[short] > 1:
            with_stage = " · ".join(
                [x for x in [ident["name"], ident["brand"], ident["life_stage"]] if x]
            )
            if with_stage:
                short = with_stage

        labels[fname] = {
            "short": short,
            "medium": food_medium_label(fname, data, include_id=False),
            "full": food_full_label(fname, data),
            "id": ident["id"],
            "name": ident["name"],
            "brand": ident["brand"],
            "species": ident["species"],
            "life_stage": ident["life_stage"],
            "emoji": ident["emoji"],
            "package_image": ident["package_image"],
        }

    second_counts = Counter(v["short"] for v in labels.values())

    for _, item in labels.items():
        if second_counts[item["short"]] > 1:
            if item["id"]:
                item["short"] = f"{item['short']} · ID {item['id']}"
            else:
                item["short"] = item["full"]

    return labels


def sort_foods_for_compare(food_names: list[str], foods: dict) -> list[str]:
    labels = build_unique_labels(food_names, foods)
    return sorted(food_names, key=lambda x: labels[x]["full"].lower())


# =============================================================================
# IMÁGENES DE EMPAQUE
# =============================================================================

def get_package_image_path(food_data: dict) -> Path | None:
    image_name = _clean(food_data.get("package_image"))

    if not image_name:
        return None

    search_dirs = [
        Path("assets") / "food_images" / "packages",
        Path("assets") / "food_images" / "brands",
    ]

    valid_exts = [".png", ".jpg", ".jpeg", ".webp"]
    candidates = []

    for folder in search_dirs:
        candidates.append(folder / image_name)

    if Path(image_name).suffix == "":
        for folder in search_dirs:
            for ext in valid_exts:
                candidates.append(folder / f"{image_name}{ext}")

    for path in candidates:
        if path.exists() and path.is_file():
            return path

    image_stem = Path(image_name).stem.lower()
    image_suffix = Path(image_name).suffix.lower()

    for folder in search_dirs:
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


# =============================================================================
# FUENTE DE ENERGÍA
# =============================================================================

def infer_me_from_manufacturer_dog_10kg(grams_day: float) -> float:
    """
    Estima ME kcal/kg desde gramaje recomendado para perro adulto de 10 kg.
    """
    grams_day = _safe_float(grams_day, 0.0)
    if grams_day <= 0:
        return 0.0

    peso_ref = 10.0
    rer = 70.0 * (peso_ref ** 0.75)
    mer = rer * 1.8
    return round((mer / grams_day) * 1000.0, 2)


def infer_me_from_manufacturer_cat_5kg(grams_day: float) -> float:
    """
    Estima ME kcal/kg desde gramaje recomendado para gato adulto de 5 kg.
    """
    grams_day = _safe_float(grams_day, 0.0)
    if grams_day <= 0:
        return 0.0

    peso_ref = 5.0
    rer = 70.0 * (peso_ref ** 0.75)
    mer = rer * 1.2
    return round((mer / grams_day) * 1000.0, 2)


def _get_first_positive(data: dict, candidate_keys: list[str]) -> float:
    for k in candidate_keys:
        v = _safe_float(data.get(k, 0.0), 0.0)
        if v > 0:
            return v
    return 0.0


def _manufacturer_grams_ref(data: dict, species: str) -> float:
    """
    Obtiene gramaje de referencia del fabricante con tolerancia a múltiples nombres de campo.
    """
    species_norm = _normalize_species(species)

    dog_keys = [
        "manufacturer_g_day_dog_10kg",
        "manufacturer_g_day_ref_dog_10kg",
        "manufacturer_g_day_ref_dog",
        "manufacturer_g_day_ref",
        "dog_10kg_g_day",
        "g_day_dog_10kg",
    ]

    cat_keys = [
        "manufacturer_g_day_cat_5kg",
        "manufacturer_g_day_ref_cat_5kg",
        "manufacturer_g_day_ref_cat",
        "manufacturer_g_day_ref",
        "cat_5kg_g_day",
        "g_day_cat_5kg",
    ]

    if species_norm == "gato":
        return _get_first_positive(data, cat_keys)

    return _get_first_positive(data, dog_keys)


def get_me_for_compare(data: dict, energy: dict, energy_source: str, species: str) -> tuple[float | None, str]:
    """
    Retorna ME en kcal/100g según fuente seleccionada.
    """
    species_norm = _normalize_species(species)
    me_formula_100g = _safe_float(energy.get("ME", 0.0), 0.0)

    if energy_source == ENERGY_SOURCE_FORMULA:
        if me_formula_100g > 0:
            return me_formula_100g, ""
        return None, "sin ME calculada por fórmula Uywa"

    if energy_source == ENERGY_SOURCE_MANUFACTURER:
        me_manufacturer_kg = _safe_float(data.get("ME_manufacturer_kcal_kg", 0.0), 0.0)
        me_manufacturer_100g = me_manufacturer_kg / 10.0 if me_manufacturer_kg > 0 else 0.0

        if me_manufacturer_100g > 0:
            return me_manufacturer_100g, ""

        return None, "sin ME declarada por fabricante"

    if energy_source == ENERGY_SOURCE_INFERRED:
        grams_ref = _manufacturer_grams_ref(data, species_norm)

        if grams_ref <= 0:
            if species_norm == "gato":
                return None, "sin gramaje de fabricante para gato de 5 kg"
            return None, "sin gramaje de fabricante para perro de 10 kg"

        if species_norm == "gato":
            me_inferred_kg = infer_me_from_manufacturer_cat_5kg(grams_ref)
        else:
            me_inferred_kg = infer_me_from_manufacturer_dog_10kg(grams_ref)

        me_inferred_100g = me_inferred_kg / 10.0 if me_inferred_kg > 0 else 0.0

        if me_inferred_100g > 0:
            return me_inferred_100g, ""

        return None, "no fue posible inferir ME desde gramaje fabricante"

    return None, "fuente energética no reconocida"


# =============================================================================
# DATAFRAME
# =============================================================================

def build_compare_dataframe(
    selected_foods: list[str],
    foods: dict,
    calculate_energy_func,
    calculate_ena_func,
    calculate_energy_breakdown_func,
    species: str,
    mer: float,
    grams: float,
    energy_source: str,
) -> tuple[pd.DataFrame, list[dict]]:
    labels = build_unique_labels(selected_foods, foods)
    rows = []
    excluded = []

    species_global = _normalize_species(species)

    for food_name in selected_foods:
        data = foods.get(food_name, {}) or {}
        species_food = _normalize_species(data.get("species", species_global) or species_global)

        try:
            energy = calculate_energy_func(data, species=species_food)
        except Exception as exc:
            excluded.append(
                {
                    "Alimento": labels.get(food_name, {}).get("full", food_name),
                    "Motivo": f"error al calcular energía: {exc}",
                }
            )
            continue

        me, reason = get_me_for_compare(data, energy, energy_source, species_food)

        if me is None or me <= 0:
            excluded.append(
                {
                    "Alimento": labels.get(food_name, {}).get("full", food_name),
                    "Motivo": reason or f"sin datos para {energy_source}",
                }
            )
            continue

        try:
            ena = calculate_ena_func(data)
            bd = calculate_energy_breakdown_func(data, species=species_food)
        except Exception as exc:
            excluded.append(
                {
                    "Alimento": labels.get(food_name, {}).get("full", food_name),
                    "Motivo": f"error al calcular composición: {exc}",
                }
            )
            continue

        aporte = (me / 100.0) * grams
        cobertura = (aporte / mer * 100.0) if mer and mer > 0 else None
        label = labels[food_name]

        bd_pb = _safe_float(bd.get("pct_pb", 0), 0.0)
        bd_ee = _safe_float(bd.get("pct_ee", 0), 0.0)
        bd_cho = _safe_float(bd.get("pct_cho", 0), 0.0)

        rows.append(
            {
                "Alimento": food_name,
                "Alimento corto": label["short"],
                "Alimento completo": label["full"],
                "ID": label["id"],
                "Nombre": label["name"],
                "Marca": label["brand"],
                "Especie": label["species"],
                "Etapa": label["life_stage"],
                "Emoji": label["emoji"],
                "Package image": label["package_image"],
                "Fuente energética": energy_source,
                "PB (%)": round(float(data.get("PB", 0) or 0), 2),
                "EE (%)": round(float(data.get("EE", 0) or 0), 2),
                "FC (%)": round(float(data.get("FC", 0) or 0), 2),
                "ENA (%)": round(float(ena or 0), 2),
                "ME (kcal/100g)": round(float(me), 2),
                "Aporte kcal/día": round(aporte, 1),
                "Cobertura energética (%)": round(cobertura, 1) if cobertura is not None else None,
                "ME proteína": round(float(me) * bd_pb / 100.0, 2),
                "ME grasa": round(float(me) * bd_ee / 100.0, 2),
                "ME carbohidratos": round(float(me) * bd_cho / 100.0, 2),
                "Fuente PB": data.get("source_pb", ""),
                "Fuente EE": data.get("source_ee", ""),
                "Fuente FC": data.get("source_fc", ""),
                "Ingredientes": data.get("ingredients", ""),
                "_data": data,
            }
        )

    return pd.DataFrame(rows), excluded


# =============================================================================
# COMPONENTES DEL COMPARADOR
# =============================================================================

def render_excluded_foods(excluded_foods: list[dict], energy_source: str) -> None:
    if not excluded_foods:
        return

    with st.expander(
        f"Alimentos excluidos por falta de datos para: {energy_source}",
        expanded=True,
    ):
        st.warning(
            "Estos alimentos no se incluyeron en la comparación porque no tienen "
            "la fuente energética seleccionada o no fue posible calcularla."
        )

        excluded_df = pd.DataFrame(excluded_foods)
        st.dataframe(excluded_df, use_container_width=True, hide_index=True)


def render_package_image(food_data: dict, size: int = 96) -> None:
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


def render_compare_summary_cards(df: pd.DataFrame, mer: float) -> None:
    if df.empty:
        return

    render_section_title(
        "Resumen ejecutivo",
        kicker="Ranking rápido",
        subtitle="Indicadores principales para comparar densidad energética y perfil proximal.",
        icon="🏆",
    )

    best_me = df.sort_values("ME (kcal/100g)", ascending=False).iloc[0]
    best_pb = df.sort_values("PB (%)", ascending=False).iloc[0]
    low_ena = df.sort_values("ENA (%)", ascending=True).iloc[0]

    cols = st.columns(4 if mer and mer > 0 else 3)

    with cols[0]:
        render_kpi_card(
            "Mayor energía",
            best_me["Alimento corto"],
            f"{best_me['ME (kcal/100g)']:.1f} kcal/100g",
            tone="energy",
            icon="⚡",
        )

    with cols[1]:
        render_kpi_card(
            "Mayor proteína",
            best_pb["Alimento corto"],
            f"{best_pb['PB (%)']:.1f}% PB",
            tone="protein",
            icon="🥩",
        )

    with cols[2]:
        render_kpi_card(
            "Menor ENA",
            low_ena["Alimento corto"],
            f"{low_ena['ENA (%)']:.1f}% ENA",
            tone="carb",
            icon="🌽",
        )

    if mer and mer > 0 and df["Cobertura energética (%)"].notna().any():
        best_cov = df.sort_values("Cobertura energética (%)", ascending=False).iloc[0]

        with cols[3]:
            render_kpi_card(
                "Mayor cobertura",
                best_cov["Alimento corto"],
                f"{best_cov['Cobertura energética (%)']:.1f}% MER",
                tone="success",
                icon="🎯",
            )


def render_food_identity_line(row: pd.Series) -> None:
    meta = " · ".join(
        [
            str(row.get("Marca", "") or ""),
            str(row.get("Especie", "") or ""),
            str(row.get("Etapa", "") or ""),
        ]
    )
    meta = meta.strip(" ·")
    if meta:
        st.caption(meta)


def render_compare_food_cards(df: pd.DataFrame) -> None:
    render_section_title(
        "Tarjetas nutricionales",
        kicker="Perfil por alimento",
        subtitle="Resumen visual con empaque, composición proximal, energía y cobertura estimada.",
        icon="🃏",
    )

    for row_start in range(0, len(df), 3):
        cols = st.columns(3)

        for i, (_, row) in enumerate(df.iloc[row_start:row_start + 3].iterrows()):
            with cols[i]:
                with st.container(border=True):
                    img_col, text_col = st.columns([1, 2.7])

                    with img_col:
                        render_package_image(row.get("_data", {}) or {}, size=88)

                    with text_col:
                        title = _short_text(row.get("Alimento corto", "Alimento"), 48)
                        st.markdown(f"**{title}**")
                        render_food_identity_line(row)
                        st.caption(f"Fuente energética: {row['Fuente energética']}")

                    st.markdown(
                        """
                        <div style="height:6px;"></div>
                        """,
                        unsafe_allow_html=True,
                    )

                    m1, m2 = st.columns(2)

                    with m1:
                        st.metric("ME", f"{row['ME (kcal/100g)']:.1f}", "kcal/100g")

                    with m2:
                        cobertura = row.get("Cobertura energética (%)")
                        st.metric(
                            "Cobertura",
                            f"{cobertura:.1f}%" if pd.notna(cobertura) else "—",
                        )

                    p1, p2, p3 = st.columns(3)

                    with p1:
                        st.markdown(
                            f"<span style='color:{NUTRIENT_COLORS['protein']};font-weight:800;'>🥩 PB</span><br><b>{row['PB (%)']:.1f}%</b>",
                            unsafe_allow_html=True,
                        )

                    with p2:
                        st.markdown(
                            f"<span style='color:{NUTRIENT_COLORS['fat']};font-weight:800;'>🧈 EE</span><br><b>{row['EE (%)']:.1f}%</b>",
                            unsafe_allow_html=True,
                        )

                    with p3:
                        st.markdown(
                            f"<span style='color:{NUTRIENT_COLORS['carbs']};font-weight:800;'>🌽 ENA</span><br><b>{row['ENA (%)']:.1f}%</b>",
                            unsafe_allow_html=True,
                        )

                    with st.expander("Ver detalle", expanded=False):
                        st.markdown(f"**Alimento completo:** {row['Alimento completo']}")
                        st.markdown(f"**Fibra cruda:** {row['FC (%)']:.1f}%")
                        st.markdown(f"**Aporte estimado:** {row['Aporte kcal/día']:.1f} kcal/día")
                        ingredientes = row.get("Ingredientes", "")
                        if ingredientes:
                            st.caption(f"Ingredientes: {ingredientes}")


def render_compare_sources(df: pd.DataFrame) -> None:
    render_section_title(
        "Fuentes nutricionales",
        kicker="Ingredientes por alimento",
        subtitle="Materias primas principales agrupadas por proteína, grasa y carbohidratos/fibra.",
        icon="🌱",
    )

    options = list(df["Alimento completo"])

    selected = st.selectbox(
        "Revisar fuentes de:",
        options,
        key="compare_sources_selector",
    )

    row = df[df["Alimento completo"] == selected].iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        render_source_chip_group("🥩 Proteína", row.get("Fuente PB", ""), color=NUTRIENT_COLORS["protein"])

    with c2:
        render_source_chip_group("🧈 Grasa", row.get("Fuente EE", ""), color=NUTRIENT_COLORS["fat"])

    with c3:
        render_source_chip_group("🌾 Carbohidratos/fibra", row.get("Fuente FC", ""), color=NUTRIENT_COLORS["fiber"])

    ingredientes = row.get("Ingredientes", "")
    if ingredientes:
        with st.expander("Ver ingredientes declarados", expanded=False):
            st.write(ingredientes)


def render_compare_table(df: pd.DataFrame) -> None:
    render_section_title(
        "Tabla comparativa",
        kicker="Datos técnicos",
        subtitle="Valores comparables por alimento. Puedes ordenar columnas desde la tabla.",
        icon="📋",
    )

    table_cols = [
        "ID",
        "Nombre",
        "Marca",
        "Especie",
        "Etapa",
        "Package image",
        "Fuente energética",
        "PB (%)",
        "EE (%)",
        "FC (%)",
        "ENA (%)",
        "ME (kcal/100g)",
        "Aporte kcal/día",
        "Cobertura energética (%)",
    ]

    show_df = df[table_cols].copy()

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "PB (%)": st.column_config.NumberColumn("PB (%)", format="%.2f"),
            "EE (%)": st.column_config.NumberColumn("EE (%)", format="%.2f"),
            "FC (%)": st.column_config.NumberColumn("FC (%)", format="%.2f"),
            "ENA (%)": st.column_config.NumberColumn("ENA (%)", format="%.2f"),
            "ME (kcal/100g)": st.column_config.NumberColumn("ME (kcal/100g)", format="%.2f"),
            "Aporte kcal/día": st.column_config.NumberColumn("Aporte kcal/día", format="%.1f"),
            "Cobertura energética (%)": st.column_config.NumberColumn("Cobertura energética (%)", format="%.1f"),
        },
    )


def render_food_comparison_dashboard(
    foods: dict,
    available_foods: list[str],
    species: str,
    mer: float,
    calculate_energy_func,
    calculate_ena_func,
    calculate_energy_breakdown_func,
    default_foods: list[str] | None = None,
):
    render_section_title(
        "Comparador nutricional de alimentos",
        kicker="Dashboard comparativo",
        subtitle="Compara composición proximal, energía metabolizable, cobertura del MER y fuentes nutricionales.",
        icon="⚖️",
    )

    if not available_foods:
        st.warning("No hay alimentos disponibles para la especie activa.")
        return

    available_foods = sort_foods_for_compare(available_foods, foods)
    labels = build_unique_labels(available_foods, foods)

    default_foods = default_foods or available_foods[:3]
    default_foods = [x for x in default_foods if x in available_foods][:3]

    def _display(food_name: str) -> str:
        return labels[food_name]["full"]

    selected_foods = st.multiselect(
        "Selecciona alimentos para comparar",
        available_foods,
        default=default_foods,
        max_selections=6,
        key="comparador_alimentos_avanzado_v2",
        format_func=_display,
        placeholder="Busca por ID, nombre, marca, especie o etapa...",
    )

    col_energy, col_grams = st.columns([1.2, 1])

    with col_energy:
        energy_source = st.selectbox(
            "Fuente energética para comparar",
            ENERGY_SOURCE_OPTIONS,
            index=0,
            key="comparador_fuente_me",
            help=(
                "La fuente seleccionada se aplica a todos los alimentos. "
                "Los alimentos sin esa fuente energética serán excluidos de la comparación."
            ),
        )

    with col_grams:
        grams = st.number_input(
            "Gramos diarios para estimar aporte y cobertura",
            min_value=1.0,
            max_value=5000.0,
            value=100.0,
            step=10.0,
            key="comparador_gramos_avanzado_v2",
        )

    if not selected_foods:
        st.info("Selecciona al menos un alimento para iniciar la comparación.")
        return

    df, excluded_foods = build_compare_dataframe(
        selected_foods=selected_foods,
        foods=foods,
        calculate_energy_func=calculate_energy_func,
        calculate_ena_func=calculate_ena_func,
        calculate_energy_breakdown_func=calculate_energy_breakdown_func,
        species=species,
        mer=mer,
        grams=grams,
        energy_source=energy_source,
    )

    render_excluded_foods(excluded_foods, energy_source)

    if df.empty:
        st.error(
            "Ningún alimento seleccionado tiene datos disponibles para la fuente energética elegida. "
            "Selecciona otra fuente energética o elige alimentos con datos completos."
        )
        return

    render_compare_summary_cards(df, mer)

    st.markdown("<hr class='uywa-divider'>", unsafe_allow_html=True)

    g1, g2 = st.columns([1, 1])

    with g1:
        st.plotly_chart(plot_compare_energy_stacked(df), use_container_width=True)

    with g2:
        st.plotly_chart(plot_compare_energy_bullet(df, mer, grams), use_container_width=True)

    st.plotly_chart(plot_compare_radar(df), use_container_width=True)

    render_compare_food_cards(df)
    render_compare_sources(df)
    render_compare_table(df)

    if mer and mer > 0:
        st.success(f"Comparación ajustada al MER actual: {mer:.1f} kcal/día.")
    else:
        st.warning("No hay MER calculado. Completa el Perfil para estimar cobertura energética.")
