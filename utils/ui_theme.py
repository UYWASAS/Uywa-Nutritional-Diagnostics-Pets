
"""
UYWA UI Theme
==============
Sistema visual base para aplicaciones UYWA.

Este módulo centraliza:
- paleta cromática corporativa;
- colores por nutriente;
- tipografía;
- estilos Plotly;
- utilidades para estados, coberturas y formato;
- CSS global reutilizable para dashboards Streamlit.

Compatible con:
- utils/ui_cards.py
- utils/ui_food_dashboard.py
- utils/ui_food_charts.py
- utils/ui_food_compare.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import streamlit as st


# =============================================================================
# 1. TIPOGRAFÍA
# =============================================================================

FONT_FAMILY = (
    "Inter, Montserrat, system-ui, -apple-system, BlinkMacSystemFont, "
    "'Segoe UI', sans-serif"
)


# =============================================================================
# 2. PALETA CORPORATIVA PRINCIPAL
# =============================================================================

COLORS = {
    # Brand
    "primary": "#2563EB",
    "primary_dark": "#1D4ED8",
    "primary_soft": "#EFF6FF",
    "secondary": "#16A34A",
    "secondary_dark": "#15803D",
    "secondary_soft": "#ECFDF5",
    "accent": "#F59E0B",
    "accent_dark": "#D97706",
    "accent_soft": "#FFFBEB",

    # Semantic
    "success": "#16A34A",
    "success_soft": "#ECFDF5",
    "warning": "#F59E0B",
    "warning_soft": "#FFFBEB",
    "danger": "#DC2626",
    "danger_soft": "#FEF2F2",
    "info": "#0284C7",
    "info_soft": "#E0F2FE",

    # Neutral
    "ink": "#0F172A",
    "dark": "#0F172A",
    "text": "#334155",
    "muted": "#64748B",
    "muted_soft": "#94A3B8",
    "border": "#E2E8F0",
    "border_dark": "#CBD5E1",
    "surface": "#FFFFFF",
    "surface_soft": "#F8FAFC",
    "surface_alt": "#F1F5F9",
    "background": "#F8FAFC",

    # Extra chart colors
    "purple": "#7C3AED",
    "purple_soft": "#F3E8FF",
    "cyan": "#38BDF8",
    "cyan_soft": "#E0F2FE",
}

# Alias histórico/corporativo
UYWA_COLORS = COLORS


# =============================================================================
# 3. PALETA POR NUTRIENTE
# =============================================================================

NUTRIENT_COLORS = {
    # Proteína
    "PB": "#DC2626",
    "pb": "#DC2626",
    "protein": "#DC2626",
    "proteina": "#DC2626",
    "proteína": "#DC2626",

    # Grasa
    "EE": "#F59E0B",
    "ee": "#F59E0B",
    "fat": "#F59E0B",
    "grasa": "#F59E0B",

    # Fibra
    "FC": "#16A34A",
    "fc": "#16A34A",
    "fiber": "#16A34A",
    "fibra": "#16A34A",

    # Carbohidratos / ENA
    "ENA": "#2563EB",
    "ena": "#2563EB",
    "carb": "#2563EB",
    "carbs": "#2563EB",
    "cho": "#2563EB",
    "carbohidratos": "#2563EB",

    # Minerales / cenizas
    "Ash": "#64748B",
    "ash": "#64748B",
    "cenizas": "#64748B",

    # Humedad
    "Humidity": "#38BDF8",
    "humidity": "#38BDF8",
    "humedad": "#38BDF8",

    # Energía
    "ME": "#7C3AED",
    "me": "#7C3AED",
    "energy": "#7C3AED",
    "energia": "#7C3AED",
    "energía": "#7C3AED",
}

NUTRIENT_LABELS = {
    "PB": "Proteína",
    "EE": "Grasa",
    "FC": "Fibra",
    "ENA": "Carbohidratos",
    "Ash": "Cenizas",
    "Humidity": "Humedad",
    "ME": "Energía metabolizable",
}

NUTRIENT_ICONS = {
    "PB": "🥩",
    "EE": "🧈",
    "FC": "🌾",
    "ENA": "🌽",
    "Ash": "⚫",
    "Humidity": "💧",
    "ME": "⚡",
}


# =============================================================================
# 4. ESTADOS Y SEMÁFOROS
# =============================================================================

STATUS_COLORS = {
    "low": COLORS["primary"],
    "ok": COLORS["success"],
    "success": COLORS["success"],
    "adequate": COLORS["success"],
    "warning": COLORS["warning"],
    "moderate": COLORS["warning"],
    "danger": COLORS["danger"],
    "high": COLORS["danger"],
    "neutral": COLORS["muted"],
    "info": COLORS["info"],

    # Tonos por nutriente para tarjetas
    "protein": NUTRIENT_COLORS["protein"],
    "fat": NUTRIENT_COLORS["fat"],
    "fiber": NUTRIENT_COLORS["fiber"],
    "carb": NUTRIENT_COLORS["carbs"],
    "carbs": NUTRIENT_COLORS["carbs"],
    "energy": NUTRIENT_COLORS["energy"],
    "ash": NUTRIENT_COLORS["ash"],
    "humidity": NUTRIENT_COLORS["humidity"],

    # Tonos corporativos
    "primary": COLORS["primary"],
    "secondary": COLORS["secondary"],
    "accent": COLORS["accent"],
}


RADIUS = {
    "sm": "10px",
    "md": "14px",
    "lg": "18px",
    "xl": "24px",
    "pill": "999px",
}
UI_RADIUS = RADIUS

SHADOWS = {
    "none": "none",
    "sm": "0 4px 12px rgba(15,23,42,0.06)",
    "md": "0 10px 28px rgba(15,23,42,0.08)",
    "lg": "0 18px 44px rgba(15,23,42,0.12)",
}
UI_SHADOWS = SHADOWS

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "14px",
    "lg": "20px",
    "xl": "28px",
}
UI_SPACING = SPACING


@dataclass(frozen=True)
class StatusStyle:
    key: str
    label: str
    color: str
    soft: str
    icon: str


STATUS_STYLES = {
    "low": StatusStyle("low", "Bajo", COLORS["primary"], COLORS["primary_soft"], "🔵"),
    "ok": StatusStyle("ok", "En rango", COLORS["success"], COLORS["success_soft"], "🟢"),
    "warning": StatusStyle("warning", "Moderado", COLORS["warning"], COLORS["warning_soft"], "🟠"),
    "danger": StatusStyle("danger", "Alto", COLORS["danger"], COLORS["danger_soft"], "🔴"),
    "neutral": StatusStyle("neutral", "Sin referencia", COLORS["muted"], COLORS["surface_alt"], "⚪"),
}


# =============================================================================
# 5. UTILIDADES DE ESTADO
# =============================================================================

def coverage_status(
    pct: Optional[float],
    low_cut: float = 90,
    high_cut: float = 110,
) -> StatusStyle:
    """
    Devuelve estilo visual para una cobertura porcentual.

    - < low_cut: bajo
    - low_cut–high_cut: adecuado
    - high_cut–130: moderado
    - >130: alto
    """
    if pct is None:
        return STATUS_STYLES["neutral"]

    try:
        pct_val = float(pct)
    except Exception:
        return STATUS_STYLES["neutral"]

    if pct_val < low_cut:
        return STATUS_STYLES["low"]
    if pct_val <= high_cut:
        return STATUS_STYLES["ok"]
    if pct_val <= 130:
        return STATUS_STYLES["warning"]
    return STATUS_STYLES["danger"]


def risk_status(risk: str) -> StatusStyle:
    """Devuelve estilo visual para riesgo bajo/moderado/alto."""
    risk_norm = str(risk or "").lower()

    if "bajo" in risk_norm:
        return STATUS_STYLES["ok"]
    if "moderado" in risk_norm:
        return STATUS_STYLES["warning"]
    if "alto" in risk_norm:
        return STATUS_STYLES["danger"]

    return STATUS_STYLES["neutral"]


def get_nutrient_color(key: str, default: str = "#64748B") -> str:
    """Color por nutriente o clave equivalente."""
    return NUTRIENT_COLORS.get(str(key), default)


def get_nutrient_label(key: str) -> str:
    """Etiqueta legible por nutriente."""
    key_str = str(key)
    return NUTRIENT_LABELS.get(key_str, key_str)


def get_nutrient_icon(key: str) -> str:
    """Icono por nutriente."""
    return NUTRIENT_ICONS.get(str(key), "•")


def safe_pct(value: Any, digits: int = 1) -> str:
    """Formatea porcentaje seguro."""
    try:
        return f"{float(value):.{digits}f}%"
    except Exception:
        return "—"


def safe_kcal(value: Any, digits: int = 1, suffix: str = "kcal") -> str:
    """Formatea kcal seguro."""
    try:
        return f"{float(value):.{digits}f} {suffix}"
    except Exception:
        return "—"


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """Limita un valor numérico entre min y max."""
    try:
        value_float = float(value)
    except Exception:
        value_float = min_value

    return max(min_value, min(value_float, max_value))


# =============================================================================
# 6. PLOTLY
# =============================================================================

def apply_uywa_plotly_layout(
    fig,
    title: Optional[str] = None,
    height: int = 420,
):
    """
    Aplica formato visual UYWA a figuras Plotly.
    """
    fig.update_layout(
        title=dict(
            text=title or "",
            font=dict(size=18, family=FONT_FAMILY, color=COLORS["ink"]),
            x=0.02,
            xanchor="left",
        ),
        height=height,
        margin=dict(t=65 if title else 30, b=45, l=35, r=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color=COLORS["text"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=COLORS["text"]),
        ),
    )

    try:
        fig.update_xaxes(
            showgrid=True,
            gridcolor="rgba(148,163,184,0.25)",
            zeroline=False,
            linecolor="rgba(148,163,184,0.35)",
        )
        fig.update_yaxes(
            showgrid=False,
            zeroline=False,
            linecolor="rgba(148,163,184,0.35)",
        )
    except Exception:
        pass

    return fig


# =============================================================================
# 7. CSS GLOBAL
# =============================================================================

def inject_uywa_theme() -> None:
    """
    Inyecta CSS global del sistema visual UYWA.
    Puede convivir con inject_global_css() existente.
    """
    st.markdown(
        f"""
        <style>
        :root {{
            --uywa-primary: {COLORS['primary']};
            --uywa-secondary: {COLORS['secondary']};
            --uywa-accent: {COLORS['accent']};
            --uywa-success: {COLORS['success']};
            --uywa-warning: {COLORS['warning']};
            --uywa-danger: {COLORS['danger']};
            --uywa-ink: {COLORS['ink']};
            --uywa-text: {COLORS['text']};
            --uywa-muted: {COLORS['muted']};
            --uywa-border: {COLORS['border']};
            --uywa-surface: {COLORS['surface']};
            --uywa-soft: {COLORS['surface_soft']};
            --uywa-font: {FONT_FAMILY};
        }}

        html, body, [class*="css"] {{
            font-family: var(--uywa-font);
        }}

        .uywa-card {{
            background: var(--uywa-surface);
            border: 1px solid var(--uywa-border);
            border-radius: 18px;
            padding: 18px;
            box-shadow: {SHADOWS['sm']};
        }}

        .uywa-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border-radius: 999px;
            border: 1px solid var(--uywa-border);
            padding: 4px 10px;
            font-size: 0.76rem;
            font-weight: 800;
            margin: 2px 4px 2px 0;
            line-height: 1.25;
        }}

        .uywa-divider {{
            border: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--uywa-border), transparent);
            margin: 24px 0;
        }}

        .uywa-small-label {{
            color: var(--uywa-muted);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .uywa-value {{
            color: var(--uywa-ink);
            font-weight: 900;
            font-size: 1.35rem;
            line-height: 1.1;
        }}

        .uywa-caption {{
            color: var(--uywa-muted);
            font-size: 0.82rem;
            line-height: 1.35;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Alias opcional para compatibilidad semántica
inject_theme = inject_uywa_theme


__all__ = [
    "COLORS",
    "UYWA_COLORS",
    "NUTRIENT_COLORS",
    "NUTRIENT_LABELS",
    "NUTRIENT_ICONS",
    "FONT_FAMILY",
    "RADIUS",
    "UI_RADIUS",
    "SHADOWS",
    "UI_SHADOWS",
    "SPACING",
    "UI_SPACING",
    "STATUS_COLORS",
    "STATUS_STYLES",
    "StatusStyle",
    "coverage_status",
    "risk_status",
    "get_nutrient_color",
    "get_nutrient_label",
    "get_nutrient_icon",
    "safe_pct",
    "safe_kcal",
    "clamp",
    "apply_uywa_plotly_layout",
    "inject_uywa_theme",
    "inject_theme",
]
