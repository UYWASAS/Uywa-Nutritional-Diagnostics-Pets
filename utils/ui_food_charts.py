"""
UYWA Food Charts
Gráficos Plotly limpios para análisis y comparación de alimentos.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from utils.ui_theme import COLORS, NUTRIENT_COLORS, FONT_FAMILY, apply_uywa_plotly_layout


def plot_macronutrients_donut(food_name: str, food_data: dict, ena: float, short_name: str | None = None):
    ms = 100 - float(food_data.get("Humidity", 0) or 0)
    title = short_name or food_name

    data = [
        ("Proteína", float(food_data.get("PB", 0) or 0), NUTRIENT_COLORS["protein"]),
        ("Grasa", float(food_data.get("EE", 0) or 0), NUTRIENT_COLORS["fat"]),
        ("Fibra", float(food_data.get("FC", 0) or 0), NUTRIENT_COLORS["fiber"]),
        ("Cenizas", float(food_data.get("Ash", 0) or 0), NUTRIENT_COLORS["ash"]),
        ("Humedad", float(food_data.get("Humidity", 0) or 0), NUTRIENT_COLORS["humidity"]),
        ("ENA", float(ena or 0), NUTRIENT_COLORS["carbs"]),
    ]

    labels = [x[0] for x in data if x[1] > 0]
    values = [x[1] for x in data if x[1] > 0]
    colors = [x[2] for x in data if x[1] > 0]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            sort=False,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=3)),
            textinfo="percent",
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        )
    )

    fig.add_annotation(
        text=f"<b>MS</b><br>{ms:.1f}%",
        x=0.5,
        y=0.54,
        showarrow=False,
        font=dict(size=22, color=COLORS["ink"], family=FONT_FAMILY),
    )
    fig.add_annotation(
        text=f"ENA {float(ena or 0):.1f}%",
        x=0.5,
        y=0.43,
        showarrow=False,
        font=dict(size=13, color=COLORS["muted"], family=FONT_FAMILY),
    )

    apply_uywa_plotly_layout(fig, title=f"Composición proximal · {title}", height=460)
    fig.update_layout(margin=dict(t=70, b=70, l=20, r=20))
    return fig


def plot_energy_sources_horizontal(bd_single: dict, title: str = "Distribución energética estimada"):
    sources = pd.DataFrame(
        [
            {"Fuente": "Proteína", "kcal": bd_single.get("me_pb", 0), "pct": bd_single.get("pct_pb", 0), "color": NUTRIENT_COLORS["protein"]},
            {"Fuente": "Grasa", "kcal": bd_single.get("me_ee", 0), "pct": bd_single.get("pct_ee", 0), "color": NUTRIENT_COLORS["fat"]},
            {"Fuente": "Carbohidratos", "kcal": bd_single.get("me_cho", 0), "pct": bd_single.get("pct_cho", 0), "color": NUTRIENT_COLORS["carbs"]},
        ]
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=sources["Fuente"],
            x=sources["kcal"],
            orientation="h",
            marker=dict(color=sources["color"]),
            text=[f"{row.kcal:.1f} kcal/100g · {row.pct:.1f}%" for row in sources.itertuples()],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>%{x:.1f} kcal/100g<extra></extra>",
        )
    )

    apply_uywa_plotly_layout(fig, title=title, height=350)
    fig.update_layout(showlegend=False, margin=dict(t=60, b=35, l=20, r=20), xaxis_title="kcal/100 g", yaxis_title="")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.25)", zeroline=False)
    return fig


def plot_compare_radar(df: pd.DataFrame, title: str = "Radar nutricional comparativo"):
    metrics = ["PB (%)", "EE (%)", "FC (%)", "ENA (%)", "ME (kcal/100g)"]
    fig = go.Figure()

    for _, row in df.iterrows():
        values = []
        for m in metrics:
            max_val = df[m].max() if m in df and df[m].max() else 1
            val = row.get(m, 0)
            values.append((float(val) / float(max_val)) * 100 if max_val else 0)

        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=metrics + [metrics[0]],
                fill="toself",
                name=str(row.get("Alimento corto", row.get("Alimento", "Alimento"))),
                opacity=0.65,
            )
        )

    apply_uywa_plotly_layout(fig, title=title, height=520)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(148,163,184,0.25)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )
    return fig


def plot_compare_energy_stacked(df: pd.DataFrame, title: str = "Origen de la energía metabolizable"):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Proteína",
        x=df["Alimento corto"],
        y=df["ME proteína"],
        marker_color=NUTRIENT_COLORS["protein"],
        hovertemplate="<b>Proteína</b><br>%{y:.1f} kcal/100g<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="Grasa",
        x=df["Alimento corto"],
        y=df["ME grasa"],
        marker_color=NUTRIENT_COLORS["fat"],
        hovertemplate="<b>Grasa</b><br>%{y:.1f} kcal/100g<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="Carbohidratos",
        x=df["Alimento corto"],
        y=df["ME carbohidratos"],
        marker_color=NUTRIENT_COLORS["carbs"],
        hovertemplate="<b>Carbohidratos</b><br>%{y:.1f} kcal/100g<extra></extra>",
    ))

    apply_uywa_plotly_layout(fig, title=title, height=460)
    fig.update_layout(barmode="stack", yaxis_title="kcal/100 g", xaxis_tickangle=-15)
    return fig


def plot_compare_energy_bullet(df: pd.DataFrame, mer: float, grams: float, title: str = "Cobertura energética por alimento"):
    fig = go.Figure()

    if mer and mer > 0 and "Cobertura energética (%)" in df:
        x = df["Cobertura energética (%)"]
        text = [f"{float(v):.1f}%" if pd.notna(v) else "—" for v in x]
        x_title = "Cobertura (%)"
    else:
        x = df["Aporte kcal/día"]
        text = [f"{float(v):.0f} kcal" for v in x]
        x_title = "kcal/día"

    fig.add_trace(
        go.Bar(
            y=df["Alimento corto"],
            x=x,
            orientation="h",
            marker_color=COLORS["primary"],
            text=text,
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>%{x:.1f}<extra></extra>",
        )
    )

    if mer and mer > 0:
        fig.add_vline(
            x=100,
            line_width=2,
            line_dash="dash",
            line_color=COLORS["success"],
            annotation_text="100% MER",
            annotation_position="top right",
        )
        fig.add_vrect(x0=90, x1=110, fillcolor=COLORS["success"], opacity=0.08, line_width=0)

    apply_uywa_plotly_layout(fig, title=title, height=420)
    fig.update_layout(showlegend=False, xaxis_title=x_title, yaxis_title="")
    fig.update_yaxes(autorange="reversed")
    return fig
