
"""
UYWA Food Compare
Comparador nutricional limpio para pestaña Comparador.

Versión corregida:
- nombres visibles únicos;
- selector con nombre completo;
- cards y gráficos con nombres cortos pero diferenciables;
- evita que alimentos distintos parezcan duplicados.
"""

from __future__ import annotations

from collections import Counter

import pandas as pd
import streamlit as st

from utils.ui_cards import render_section_title, render_kpi_card, render_source_chip_group
from utils.ui_theme import NUTRIENT_COLORS
from utils.ui_food_charts import (
    plot_compare_radar,
    plot_compare_energy_stacked,
    plot_compare_energy_bullet,
)


def _clean(value) -> str:
    return str(value or "").strip()


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

    return {
        "id": food_id,
        "name": name,
        "brand": brand,
        "species": species,
        "life_stage": life_stage,
        "category": category,
        "emoji": emoji,
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
        }

    second_counts = Counter(v["short"] for v in labels.values())

    for fname, item in labels.items():
        if second_counts[item["short"]] > 1:
            if item["id"]:
                item["short"] = f"{item['short']} · ID {item['id']}"
            else:
                item["short"] = item["full"]

    return labels


def sort_foods_for_compare(food_names: list[str], foods: dict) -> list[str]:
    labels = build_unique_labels(food_names, foods)
    return sorted(food_names, key=lambda x: labels[x]["full"].lower())


def build_compare_dataframe(
    selected_foods: list[str],
    foods: dict,
    calculate_energy_func,
    calculate_ena_func,
    calculate_energy_breakdown_func,
    species: str,
    mer: float,
    grams: float,
) -> pd.DataFrame:
    labels = build_unique_labels(selected_foods, foods)
    rows = []

    for food_name in selected_foods:
        data = foods.get(food_name, {}) or {}
        species_food = data.get("species", species)
        energy = calculate_energy_func(data, species=species_food)
        ena = calculate_ena_func(data)
        bd = calculate_energy_breakdown_func(data, species=species_food)

        me = float(energy.get("ME", 0) or 0)
        aporte = (me / 100.0) * grams
        cobertura = (aporte / mer * 100.0) if mer and mer > 0 else None
        label = labels[food_name]

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
                "PB (%)": round(float(data.get("PB", 0) or 0), 2),
                "EE (%)": round(float(data.get("EE", 0) or 0), 2),
                "FC (%)": round(float(data.get("FC", 0) or 0), 2),
                "ENA (%)": round(float(ena or 0), 2),
                "ME (kcal/100g)": round(me, 2),
                "Aporte kcal/día": round(aporte, 1),
                "Cobertura energética (%)": round(cobertura, 1) if cobertura is not None else None,
                "ME proteína": round(float(bd.get("me_pb", 0) or 0), 2),
                "ME grasa": round(float(bd.get("me_ee", 0) or 0), 2),
                "ME carbohidratos": round(float(bd.get("me_cho", 0) or 0), 2),
                "Fuente PB": data.get("source_pb", ""),
                "Fuente EE": data.get("source_ee", ""),
                "Fuente FC": data.get("source_fc", ""),
                "Ingredientes": data.get("ingredients", ""),
            }
        )

    return pd.DataFrame(rows)


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
        render_kpi_card("Mayor energía", best_me["Alimento corto"], f"{best_me['ME (kcal/100g)']:.1f} kcal/100g", tone="energy", icon="⚡")

    with cols[1]:
        render_kpi_card("Mayor proteína", best_pb["Alimento corto"], f"{best_pb['PB (%)']:.1f}% PB", tone="protein", icon="🥩")

    with cols[2]:
        render_kpi_card("Menor ENA", low_ena["Alimento corto"], f"{low_ena['ENA (%)']:.1f}% ENA", tone="carb", icon="🌽")

    if mer and mer > 0 and df["Cobertura energética (%)"].notna().any():
        best_cov = df.sort_values("Cobertura energética (%)", ascending=False).iloc[0]
        with cols[3]:
            render_kpi_card("Mayor cobertura", best_cov["Alimento corto"], f"{best_cov['Cobertura energética (%)']:.1f}% MER", tone="success", icon="🎯")


def render_compare_food_cards(df: pd.DataFrame) -> None:
    render_section_title(
        "Tarjetas nutricionales",
        kicker="Perfil por alimento",
        subtitle="Resumen compacto de composición, energía y fuentes declaradas.",
        icon="🃏",
    )

    for row_start in range(0, len(df), 3):
        cols = st.columns(3)

        for i, (_, row) in enumerate(df.iloc[row_start:row_start + 3].iterrows()):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{row['Alimento corto']}**")
                    st.caption(row["Alimento completo"])

                    m1, m2 = st.columns(2)

                    with m1:
                        st.metric("ME", f"{row['ME (kcal/100g)']:.1f}", "kcal/100g")

                    with m2:
                        cobertura = row.get("Cobertura energética (%)")
                        if pd.notna(cobertura):
                            st.metric("Cobertura", f"{cobertura:.1f}%")
                        else:
                            st.metric("Cobertura", "—")

                    st.markdown(
                        f"""
**PB:** {row['PB (%)']:.1f}% · **EE:** {row['EE (%)']:.1f}% · **FC:** {row['FC (%)']:.1f}%  
**ENA:** {row['ENA (%)']:.1f}% · **Etapa:** {row.get('Etapa', '—')}
                        """
                    )


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


def render_duplicate_audit(available_foods: list[str], foods: dict) -> None:
    labels = build_unique_labels(available_foods, foods)
    audit_rows = []

    for food_name in available_foods:
        data = foods.get(food_name, {}) or {}
        ident = get_food_identity(food_name, data)
        audit_rows.append(
            {
                "Clave": food_name,
                "ID": ident["id"],
                "Nombre": ident["name"],
                "Marca": ident["brand"],
                "Especie": ident["species"],
                "Etapa": ident["life_stage"],
                "Etiqueta corta": labels[food_name]["short"],
                "Etiqueta completa": labels[food_name]["full"],
            }
        )

    audit_df = pd.DataFrame(audit_rows)

    apparent_duplicates = (
        audit_df.groupby(["Nombre", "Marca"])
        .size()
        .reset_index(name="N")
        .query("N > 1")
        .sort_values("N", ascending=False)
    )

    with st.expander("Auditoría de nombres y duplicados aparentes", expanded=False):
        if apparent_duplicates.empty:
            st.success("No se detectaron nombres aparentes repetidos por Nombre + Marca.")
        else:
            st.warning(
                "Hay nombres aparentes repetidos por Nombre + Marca. "
                "Esto no necesariamente implica duplicados reales; pueden corresponder a etapas o IDs distintos."
            )
            st.dataframe(apparent_duplicates, use_container_width=True, hide_index=True)

        st.dataframe(audit_df, use_container_width=True, hide_index=True)


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

    grams = st.number_input(
        "Gramos diarios para estimar aporte y cobertura",
        min_value=1.0,
        max_value=5000.0,
        value=100.0,
        step=10.0,
        key="comparador_gramos_avanzado_v2",
    )
