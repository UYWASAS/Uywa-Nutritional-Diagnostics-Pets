
"""
UYWA UI Theme
Sistema visual base para aplicaciones UYWA.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import streamlit as st

FONT_FAMILY = "Inter, Montserrat, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

COLORS = {
    "primary": "#2563EB",
    "primary_dark": "#1D4ED8",
    "primary_soft": "#EFF6FF",
    "secondary": "#16A34A",
    "secondary_soft": "#ECFDF5",
    "accent": "#F59E0B",
    "accent_soft": "#FFFBEB",
    "success": "#16A34A",
    "success_soft": "#ECFDF5",
    "warning": "#F59E0B",
    "warning_soft": "#FFFBEB",
    "danger": "#DC2626",
    "danger_soft": "#FEF2F2",
    "info": "#0284C7",
    "info_soft": "#E0F2FE",
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
}

UYWA_COLORS = COLORS

NUTRIENT_COLORS = {
    "PB": "#DC2626",
    "protein": "#DC2626",
    "proteina": "#DC2626",
    "EE": "#F59E0B",
    "fat": "#F59E0B",
    "grasa": "#F59E0B",
    "FC": "#16A34A",
    "fiber": "#16A34A",
    "fibra": "#16A34A",
    "ENA": "#2563EB",
    "carb": "#2563EB",
    "carbs": "#2563EB",
    "cho": "#2563EB",
    "Ash": "#64748B",
    "ash": "#64748B",
    "cenizas": "#64748B",
    "Humidity": "#38BDF8",
    "humidity": "#38BDF8",
    "humedad": "#38BDF8",
    "energy": "#7C3AED",
    "ME": "#7C3AED",
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

STATUS_COLORS = {
    "low": "#2563EB",
    "ok": "#16A34A",
    "success": "#16A34A",
    "warning": "#F59E0B",
    "moderate": "#F59E0B",
    "danger": "#DC2626",
    "high": "#DC2626",
    "neutral": "#64748B",
    "protein": NUTRIENT_COLORS["protein"],
    "fat": NUTRIENT_COLORS["fat"],
    "fiber": NUTRIENT_COLORS["fiber"],
    "carb": NUTRIENT_COLORS["carbs"],
    "carbs": NUTRIENT_COLORS["carbs"],
    "energy": NUTRIENT_COLORS["energy"],
    "ash": NUTRIENT_COLORS["ash"],
    "humidity": NUTRIENT_COLORS["humidity"],
}

RADIUS = {"sm": "10px", "md": "14px", "lg": "18px", "xl": "24px", "pill": "999px"}
UI_RADIUS = RADIUS

SHADOWS = {
    "sm": "0 4px 12px rgba(15,23,42,0.06)",
    "md": "0 10px 28px rgba(15,23,42,0.08)",
    "lg": "0 18px 44px rgba(15,23,42,0.12)",
}
UI_SHADOWS = SHADOWS

SPACING = {"xs": "4px", "sm": "8px", "md": "14px", "lg": "20px", "xl": "28px"}
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


def coverage_status(pct: Optional[float], low_cut: float = 90, high_cut: float = 110) -> StatusStyle:
    if pct is None:
        return STATUS_STYLES["neutral"]
    if pct < low_cut:
        return STATUS_STYLES["low"]
    if pct <= high_cut:
        return STATUS_STYLES["ok"]
    if pct <= 130:
        return STATUS_STYLES["warning"]
    return STATUS_STYLES["danger"]


def risk_status(risk: str) -> StatusStyle:
    risk_norm = str(risk or "").lower()
    if "bajo" in risk_norm:
        return STATUS_STYLES["ok"]
    if "moderado" in risk_norm:
        return STATUS_STYLES["warning"]
    if "alto" in risk_norm:
        return STATUS_STYLES["danger"]
    return STATUS_STYLES["neutral"]


def get_nutrient_color(key: str, default: str = "#64748B") -> str:
    return NUTRIENT_COLORS.get(str(key), default)


def get_nutrient_label(key: str) -> str:
    return NUTRIENT_LABELS.get(str(key), str(key))


def get_nutrient_icon(key: str) -> str:
    return NUTRIENT_ICONS.get(str(key), "•")


def safe_pct(value: Any, digits: int = 1) -> str:
    try:
        return f"{float(value):.{digits}f}%"
    except Exception:
        return "—"


def safe_kcal(value: Any, digits: int = 1, suffix: str = "kcal") -> str:
    try:
        return f"{float(value):.{digits}f} {suffix}"
    except Exception:
        return "—"


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(float(value), max_value))


def apply_uywa_plotly_layout(fig, title: Optional[str] = None, height: int = 420):
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
        ),
    )
    return fig


def inject_uywa_theme() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --uywa-primary: {COLORS['primary']};
            --uywa-secondary: {COLORS['secondary']};
            --uywa-accent: {COLORS['accent']};
            --uywa-ink: {COLORS['ink']};
            --uywa-text: {COLORS['text']};
            --uywa-muted: {COLORS['muted']};
            --uywa-border: {COLORS['border']};
            --uywa-surface: {COLORS['surface']};
            --uywa-soft: {COLORS['surface_soft']};
            --uywa-font: {FONT_FAMILY};
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
        }}
        .uywa-divider {{
            border: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--uywa-border), transparent);
            margin: 24px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


__all__ = [
    "COLORS", "UYWA_COLORS", "NUTRIENT_COLORS", "NUTRIENT_LABELS", "NUTRIENT_ICONS",
    "FONT_FAMILY", "RADIUS", "UI_RADIUS", "SHADOWS", "UI_SHADOWS", "SPACING", "UI_SPACING",
    "STATUS_COLORS", "STATUS_STYLES", "StatusStyle", "coverage_status", "risk_status",
    "get_nutrient_color", "get_nutrient_label", "get_nutrient_icon",
    "safe_pct", "safe_kcal", "clamp", "apply_uywa_plotly_layout", "inject_uywa_theme",
]
