# ======================== UYWA UI FOOD CHARTS ========================
# Gráficos Plotly reutilizables para análisis y comparación de alimentos.

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from utils.ui_theme import (
    COLOR_PROTEIN,
    COLOR_FAT,
    COLOR_FIBER,
    COLOR_ENA,
    COLOR_ASH,
    COLOR_HUMIDITY,
    COLOR_BLUE,
    COLOR_TEXT,
    COLOR_MUTED,
    COLOR_GRID,
    FONT_FAMILY,
)


def plot_macronutrients_donut(food_name: str, food_data: dict, ena: float, food_title: str | None = None):
    """
    Donut premium de composición proximal del alimento.
    No calcula ENA; lo recibe desde food_analysis para mantener lógica centralizada.
    """
    humidity = float(food_data.get("Humidity", 0) or 0)
    ms = 100 - humidity

    title = food_title or food_name

    nutrient_data = [
        ("Proteína", float(food_data.get("PB", 0) or 0), COLOR_PROTEIN),
        ("Grasa", float(food_data.get("EE", 0) or 0), COLOR_FAT),
        ("Fibra", float(food_data.get("FC", 0) or 0), COLOR_FIBER),
        ("Cenizas", float(food_data.get("Ash", 0) or 0), COLOR_ASH),
        ("Humedad", humidity, COLOR_HUMIDITY),
        ("ENA", float(ena or 0), COLOR_ENA),
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
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=3)),
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
        font=dict(size=22, color=COLOR_TEXT),
        showarrow=False,
    )

    fig.add_annotation(
        text=f"ENA {float(ena or 0):.1f}%",
        x=0.5,
        y=0.43,
        font=dict(size=13, color=COLOR_MUTED),
        showarrow=False,
    )

    fig.update_layout(
        title=dict(
            text=f"Composición proximal · {title}",
            font=dict(size=18, family=FONT_FAMILY, color=COLOR_TEXT),
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
        font=dict(family=FONT_FAMILY, color="#334155"),
    )

    return fig


def plot_energy_sources_horizontal(bd_single: dict):
    """
    Barras horizontales para origen de energía metabolizable del alimento seleccionado.
    """
    energy_sources = pd.DataFrame([
        {
            "Fuente": "Proteína",
            "kcal": float(bd_single.get("me_pb", 0) or 0),
            "pct": float(bd_single.get("pct_pb", 0) or 0),
            "color": COLOR_PROTEIN,
        },
        {
            "Fuente": "Grasa",
            "kcal": float(bd_single.get("me_ee", 0) or 0),
            "pct": float(bd_single.get("pct_ee", 0) or 0),
            "color": COLOR_FAT,
        },
        {
            "Fuente": "Carbohidratos",
            "kcal": float(bd_single.get("me_cho", 0) or 0),
            "pct": float(bd_single.get("pct_cho", 0) or 0),
            "color": COLOR_ENA,
        },
    ])

    fig = go.Figure()

    fig.add_trace(
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

    fig.update_layout(
        title=dict(
            text="Distribución energética estimada",
            font=dict(size=17, family=FONT_FAMILY, color=COLOR_TEXT),
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
        font=dict(family=FONT_FAMILY, color="#334155"),
        showlegend=False,
    )

    fig.update_xaxes(showgrid=True, gridcolor=COLOR_GRID, zeroline=False)
    fig.update_yaxes(showgrid=False)

    return fig


def plot_compare_radar(compare_df: pd.DataFrame):
    """
    Radar nutricional comparativo.
    Espera columnas: Alimento corto, PB (%), EE (%), FC (%), ENA (%), ME (kcal/100g)
    """
    if compare_df.empty:
        return go.Figure()

    categories = ["PB (%)", "EE (%)", "FC (%)", "ENA (%)", "ME normalizada"]

    df = compare_df.copy()
    max_me = max(float(df["ME (kcal/100g)"].max()), 1.0)
    df["ME normalizada"] = (df["ME (kcal/100g)"] / max_me) * 100.0

    fig = go.Figure()

    palette = [COLOR_BLUE, COLOR_PROTEIN, COLOR_FAT, COLOR_FIBER, COLOR_ENA, COLOR_ASH]

    for idx, row in df.iterrows():
        values = [
            float(row.get("PB (%)", 0) or 0),
            float(row.get("EE (%)", 0) or 0),
            float(row.get("FC (%)", 0) or 0),
            float(row.get("ENA (%)", 0) or 0),
            float(row.get("ME normalizada", 0) or 0),
        ]

        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=str(row.get("Alimento corto", row.get("Alimento", f"Alimento {idx+1}"))),
                line=dict(color=palette[idx % len(palette)], width=2),
                opacity=0.72,
            )
        )

    fig.update_layout(
        title=dict(
            text="Radar nutricional comparativo",
            font=dict(size=17, family=FONT_FAMILY, color=COLOR_TEXT),
            x=0.02,
            xanchor="left",
        ),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=COLOR_GRID,
                tickfont=dict(size=10, color=COLOR_MUTED),
            ),
            angularaxis=dict(
                gridcolor=COLOR_GRID,
                tickfont=dict(size=11, color=COLOR_TEXT),
            ),
        ),
        height=460,
        margin=dict(t=70, b=70, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
    )

    return fig


def plot_compare_energy_stacked(compare_df: pd.DataFrame):
    """
    Barras apiladas comparativas del origen energético.
    Espera columnas: Alimento corto, Proteína kcal/100g, Grasa kcal/100g, Carbohidratos kcal/100g.
    """
    if compare_df.empty:
        return go.Figure()

    x = compare_df["Alimento corto"] if "Alimento corto" in compare_df.columns else compare_df["Alimento"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Proteína",
            x=x,
            y=compare_df["Proteína kcal/100g"],
            marker_color=COLOR_PROTEIN,
            hovertemplate="<b>Proteína</b><br>%{y:.1f} kcal/100g<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Grasa",
            x=x,
            y=compare_df["Grasa kcal/100g"],
            marker_color=COLOR_FAT,
            hovertemplate="<b>Grasa</b><br>%{y:.1f} kcal/100g<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Carbohidratos",
            x=x,
            y=compare_df["Carbohidratos kcal/100g"],
            marker_color=COLOR_ENA,
            hovertemplate="<b>Carbohidratos</b><br>%{y:.1f} kcal/100g<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="stack",
        title=dict(
            text="Origen de la energía metabolizable",
            font=dict(size=17, family=FONT_FAMILY, color=COLOR_TEXT),
            x=0.02,
            xanchor="left",
        ),
        yaxis_title="kcal / 100 g",
        xaxis_title="",
        height=430,
        margin=dict(t=70, b=90, l=60, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color="#334155"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
        ),
    )

    fig.update_yaxes(showgrid=True, gridcolor=COLOR_GRID, zeroline=False)
    fig.update_xaxes(tickangle=-15)

    return fig


def plot_compare_energy_bullet(compare_df: pd.DataFrame, mer_animal: float | None = None, gramos_input: float | None = None):
    """
    Bullet chart simple para cobertura energética comparativa.
    Espera columnas: Alimento corto, Aporte kcal/día, Cobertura energética (%).
    """
    if compare_df.empty or "Cobertura energética (%)" not in compare_df.columns:
        return go.Figure()

    fig = go.Figure()

    df = compare_df.sort_values("Cobertura energética (%)", ascending=True)

    fig.add_trace(
        go.Bar(
            y=df["Alimento corto"] if "Alimento corto" in df.columns else df["Alimento"],
            x=df["Cobertura energética (%)"],
            orientation="h",
            marker_color=[
                "#16A34A" if 90 <= v <= 110 else ("#F59E0B" if v > 110 else COLOR_BLUE)
                for v in df["Cobertura energética (%)"]
            ],
            text=[f"{v:.1f}%" for v in df["Cobertura energética (%)"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Cobertura: %{x:.1f}%<extra></extra>",
        )
    )

    fig.add_vline(
        x=100,
        line_width=2,
        line_dash="dash",
        line_color=COLOR_TEXT,
        annotation_text="100%",
        annotation_position="top",
    )

    fig.update_layout(
        title=dict(
            text="Cobertura energética comparativa",
            font=dict(size=17, family=FONT_FAMILY, color=COLOR_TEXT),
            x=0.02,
            xanchor="left",
        ),
        xaxis_title="% del MER",
        yaxis_title="",
        height=max(330, 90 * len(df)),
        margin=dict(t=70, b=50, l=20, r=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color="#334155"),
        showlegend=False,
    )

    fig.update_xaxes(showgrid=True, gridcolor=COLOR_GRID, zeroline=False, range=[0, max(130, float(df["Cobertura energética (%)"].max()) + 15)])
    fig.update_yaxes(showgrid=False)

    return fig
