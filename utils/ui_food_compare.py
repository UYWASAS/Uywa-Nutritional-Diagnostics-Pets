
"""
UYWA Food Compare
Comparador nutricional 2.0 para pestaña Comparador.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.ui_cards import render_section_title, render_kpi_card, render_source_chip_group, render_badges
from utils.ui_theme import COLORS, NUTRIENT_COLORS
from utils.ui_food_charts import (
    plot_compare_radar,
    plot_compare_energy_stacked,
    plot_compare_energy_bullet,
)


def _short_name(food_name: str, data: dict) -> str:
    name = str(data.get("name", "") or "").strip()
    brand = str(data.get("brand", "") or "").strip()
    if name and brand:
        return f"{name} · {brand}"
    if name:
        return name
    parts = [p.strip() for p in str(food_name).split("|")]
    if len(parts) >= 3:
        return f"{parts[1]} · {parts[2]}"
    return food_name


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

        rows.append({
            "Alimento": food_name,
            "Alimento corto": _short_name(food_name, data),
            "Marca": data.get("brand", ""),
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
        })

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
    best_cov = None
    if mer and mer > 0 and df["Cobertura energética (%)"].notna().any():
        best_cov = df.sort_values("Cobertura energética (%)", ascending=False).iloc[0]

    cols = st.columns(4 if best_cov is not None else 3)
    with cols[0]:
        render_kpi_card("Mayor energía", best_me["Alimento corto"], f"{best_me['ME (kcal/100g)']:.1f} kcal/100g", tone="energy", icon="⚡")
    with cols[1]:
        render_kpi_card("Mayor proteína", best_pb["Alimento corto"], f"{best_pb['PB (%)']:.1f}% PB", tone="protein", icon="🥩")
    with cols[2]:
        render_kpi_card("Menor ENA", low_ena["Alimento corto"], f"{low_ena['ENA (%)']:.1f}% ENA", tone="carb", icon="🌽")
    if best_cov is not None:
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
                st.markdown(
                    f"""
                    <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};
                                border-radius:22px;padding:18px;box-shadow:0 8px 22px rgba(15,23,42,0.06);margin-bottom:14px;">
                        <div style="font-weight:950;font-size:1.05rem;color:{COLORS['ink']};line-height:1.15;">{row['Alimento corto']}</div>
                        <div style="color:{COLORS['muted']};font-size:0.82rem;font-weight:750;margin-top:3px;">{row.get('Marca','')}</div>
                        <hr style="border:0;border-top:1px solid {COLORS['border']};margin:12px 0;">
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.86rem;">
                            <div><b>ME</b><br>{row['ME (kcal/100g)']:.1f} kcal/100g</div>
                            <div><b>PB</b><br>{row['PB (%)']:.1f}%</div>
                            <div><b>EE</b><br>{row['EE (%)']:.1f}%</div>
                            <div><b>ENA</b><br>{row['ENA (%)']:.1f}%</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_compare_sources(df: pd.DataFrame) -> None:
    render_section_title(
        "Fuentes nutricionales",
        kicker="Ingredientes por alimento",
        subtitle="Materias primas principales agrupadas por proteína, grasa y carbohidratos/fibra.",
        icon="🌱",
    )

    selected = st.selectbox(
        "Revisar fuentes de:",
        list(df["Alimento corto"]),
        key="compare_sources_selector",
    )
    row = df[df["Alimento corto"] == selected].iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        render_source_chip_group("🥩 Proteína", row.get("Fuente PB", ""), color=NUTRIENT_COLORS["protein"])
    with c2:
        render_source_chip_group("🧈 Grasa", row.get("Fuente EE", ""), color=NUTRIENT_COLORS["fat"])
    with c3:
        render_source_chip_group("🌾 Carbohidratos/fibra", row.get("Fuente FC", ""), color=NUTRIENT_COLORS["fiber"])


def render_compare_table(df: pd.DataFrame) -> None:
    render_section_title(
        "Tabla comparativa",
        kicker="Datos técnicos",
        subtitle="Valores comparables por alimento. Puedes ordenar columnas desde la tabla.",
        icon="📋",
    )

    table_cols = [
        "Alimento corto",
        "PB (%)",
        "EE (%)",
        "FC (%)",
        "ENA (%)",
        "ME (kcal/100g)",
        "Aporte kcal/día",
        "Cobertura energética (%)",
    ]
    show_df = df[table_cols].copy()
    show_df = show_df.rename(columns={"Alimento corto": "Alimento"})

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

    default_foods = default_foods or available_foods[:3]

    def _display(food_name: str) -> str:
        return _short_name(food_name, foods.get(food_name, {}) or {})

    selected_foods = st.multiselect(
        "Selecciona alimentos para comparar",
        available_foods,
        default=[x for x in default_foods if x in available_foods][:3],
        max_selections=6,
        key="comparador_alimentos_avanzado_v2",
        format_func=_display,
    )

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

    df = build_compare_dataframe(
        selected_foods=selected_foods,
        foods=foods,
        calculate_energy_func=calculate_energy_func,
        calculate_ena_func=calculate_ena_func,
        calculate_energy_breakdown_func=calculate_energy_breakdown_func,
        species=species,
        mer=mer,
        grams=grams,
    )

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
