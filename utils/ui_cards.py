
"""
UYWA UI Cards
==============
Componentes visuales reutilizables para las aplicaciones UYWA.

Este módulo centraliza:
- encabezados de sección;
- tarjetas KPI;
- badges/chips;
- cards informativas;
- barras de progreso;
- score cards;
- grupos de fuentes nutricionales.

Compatible con:
- utils/ui_theme.py
- utils/ui_food_dashboard.py
- utils/ui_food_compare.py
"""

from __future__ import annotations

from typing import Iterable
import html

import streamlit as st

try:
    from utils.ui_theme import (
        COLORS,
        NUTRIENT_COLORS,
        STATUS_COLORS,
        SHADOWS,
        RADIUS,
        FONT_FAMILY,
    )
except Exception:
    # Fallback defensivo para evitar caída si ui_theme.py no está cargado.
    FONT_FAMILY = "Inter, Montserrat, sans-serif"

    COLORS = {
        "primary": "#2563EB",
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
        "surface": "#FFFFFF",
        "surface_soft": "#F8FAFC",
        "surface_alt": "#F1F5F9",
    }

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
        "Humidity": "#38BDF8",
        "humidity": "#38BDF8",
        "energy": "#7C3AED",
        "ME": "#7C3AED",
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
        "protein": "#DC2626",
        "fat": "#F59E0B",
        "fiber": "#16A34A",
        "carb": "#2563EB",
        "carbs": "#2563EB",
        "energy": "#7C3AED",
        "ash": "#64748B",
        "humidity": "#38BDF8",
    }

    SHADOWS = {
        "sm": "0 4px 12px rgba(15,23,42,0.06)",
        "md": "0 10px 28px rgba(15,23,42,0.08)",
        "lg": "0 18px 44px rgba(15,23,42,0.12)",
    }

    RADIUS = {
        "sm": "10px",
        "md": "14px",
        "lg": "18px",
        "xl": "24px",
        "pill": "999px",
    }


# =============================================================================
# UTILIDADES INTERNAS
# =============================================================================

def _esc(value) -> str:
    """Escapa texto antes de insertarlo en HTML."""
    return html.escape(str(value or ""))


def _tone_color(tone: str | None) -> str:
    """Devuelve color según tono semántico, nutriente o clave de paleta."""
    if not tone:
        return COLORS.get("muted", "#64748B")

    key = str(tone)
    key_lower = key.lower()

    return (
        STATUS_COLORS.get(key_lower)
        or STATUS_COLORS.get(key)
        or NUTRIENT_COLORS.get(key_lower)
        or NUTRIENT_COLORS.get(key)
        or COLORS.get(key_lower)
        or COLORS.get(key)
        or COLORS.get("muted", "#64748B")
    )


def _soft_bg(color: str) -> str:
    """Genera color translúcido para fondos."""
    return f"{color}12"


def _soft_border(color: str) -> str:
    """Genera color translúcido para bordes."""
    return f"{color}44"


# =============================================================================
# ENCABEZADOS
# =============================================================================

def render_section_title(
    title: str,
    kicker: str | None = None,
    subtitle: str | None = None,
    icon: str | None = None,
) -> None:
    """
    Encabezado visual uniforme para secciones.

    Parámetros:
        title: título principal.
        kicker: texto superior corto.
        subtitle: descripción breve.
        icon: icono opcional.
    """
    icon_html = (
        f"<span style='font-size:1.35rem;margin-right:8px;'>{_esc(icon)}</span>"
        if icon
        else ""
    )

    kicker_html = (
        f"""
        <div style="font-size:0.74rem;font-weight:850;letter-spacing:0.08em;
                    text-transform:uppercase;color:{COLORS['primary']};margin-bottom:4px;">
            {_esc(kicker)}
        </div>
        """
        if kicker
        else ""
    )

    subtitle_html = (
        f"""
        <div style="font-size:0.92rem;color:{COLORS['muted']};
                    margin-top:4px;line-height:1.45;">
            {_esc(subtitle)}
        </div>
        """
        if subtitle
        else ""
    )

    st.markdown(
        f"""
        <div style="margin: 10px 0 18px 0;">
            {kicker_html}
            <div style="display:flex;align-items:center;font-family:{FONT_FAMILY};
                        font-size:1.35rem;font-weight:900;color:{COLORS['ink']};">
                {icon_html}<span>{_esc(title)}</span>
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Alias requerido por módulos previos/nuevos
render_section_header = render_section_title


# =============================================================================
# BADGES / CHIPS
# =============================================================================

def render_badge(
    label: str,
    status: str = "neutral",
    icon: str | None = None,
) -> None:
    """Renderiza un badge individual."""
    color = _tone_color(status)
    icon_html = f"{_esc(icon)} " if icon else ""

    st.markdown(
        f"""
        <span class="uywa-badge"
              style="color:{color};background:{_soft_bg(color)};
                     border-color:{_soft_border(color)};">
            {icon_html}{_esc(label)}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_badges(labels: Iterable[str], status: str = "neutral") -> None:
    """Renderiza múltiples badges en una sola línea."""
    color = _tone_color(status)
    html_badges = ""

    for label in labels:
        html_badges += (
            f"""
            <span class="uywa-badge"
                  style="color:{color};background:{_soft_bg(color)};
                         border-color:{_soft_border(color)};">
                {_esc(label)}
            </span>
            """
        )

    st.markdown(html_badges, unsafe_allow_html=True)


# =============================================================================
# KPI CARDS
# =============================================================================

def render_kpi_card(
    title: str,
    value: str,
    unit: str | None = None,
    note: str | None = None,
    tone: str = "primary",
    icon: str | None = None,
) -> None:
    """
    Tarjeta KPI premium.

    Parámetros:
        title: título del indicador.
        value: valor principal.
        unit: unidad.
        note: nota inferior.
        tone: color semántico o nutriente.
        icon: icono opcional.
    """
    color = _tone_color(tone)

    unit_html = (
        f"""
        <span style="font-size:0.82rem;color:{COLORS['muted']};
                     font-weight:700;margin-left:4px;">
            {_esc(unit)}
        </span>
        """
        if unit
        else ""
    )

    note_html = (
        f"""
        <div style="font-size:0.78rem;color:{COLORS['muted']};
                    margin-top:8px;line-height:1.35;">
            {_esc(note)}
        </div>
        """
        if note
        else ""
    )

    icon_html = (
        f"<div style='font-size:1.45rem;margin-bottom:6px;'>{_esc(icon)}</div>"
        if icon
        else ""
    )

    st.markdown(
        f"""
        <div style="background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-left:5px solid {color};
                    border-radius:{RADIUS['lg']};
                    padding:16px 18px;
                    box-shadow:{SHADOWS['sm']};
                    min-height:118px;
                    margin-bottom:10px;">
            {icon_html}
            <div style="font-size:0.76rem;font-weight:850;letter-spacing:0.06em;
                        text-transform:uppercase;color:{COLORS['muted']};">
                {_esc(title)}
            </div>
            <div style="margin-top:6px;font-size:1.45rem;font-weight:900;
                        color:{COLORS['ink']};line-height:1.1;">
                {_esc(value)}{unit_html}
            </div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_grid(items: list[dict], columns: int = 3) -> None:
    """
    Renderiza una grilla de tarjetas KPI.

    Cada item puede incluir:
    title, value, unit, note, tone, icon.
    """
    if not items:
        return

    columns = max(1, int(columns))
    cols = st.columns(columns)

    for i, item in enumerate(items):
        with cols[i % columns]:
            render_kpi_card(
                title=item.get("title", ""),
                value=item.get("value", "—"),
                unit=item.get("unit"),
                note=item.get("note"),
                tone=item.get("tone", "primary"),
                icon=item.get("icon"),
            )


# =============================================================================
# INFO / ALERT CARDS
# =============================================================================

def render_info_card(
    title: str,
    body: str,
    tone: str = "neutral",
    icon: str | None = None,
) -> None:
    """Card informativa con borde semántico."""
    color = _tone_color(tone)

    icon_html = (
        f"<span style='font-size:1.25rem;margin-right:8px;'>{_esc(icon)}</span>"
        if icon
        else ""
    )

    st.markdown(
        f"""
        <div style="background:{_soft_bg(color)};
                    border:1px solid {_soft_border(color)};
                    border-left:6px solid {color};
                    border-radius:{RADIUS['lg']};
                    padding:16px 18px;
                    margin:10px 0;
                    box-shadow:{SHADOWS['sm']};">
            <div style="font-size:1.05rem;font-weight:900;
                        color:{COLORS['ink']};margin-bottom:6px;">
                {icon_html}{_esc(title)}
            </div>
            <div style="font-size:0.92rem;color:{COLORS['text']};line-height:1.45;">
                {_esc(body)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# PROGRESS / COVERAGE CARDS
# =============================================================================

def render_progress_card(
    title: str,
    pct: float | None,
    req_text: str,
    aporte_text: str,
    status_label: str = "",
    tone: str = "primary",
) -> None:
    """Tarjeta de cobertura con barra de progreso."""
    color = _tone_color(tone)

    if pct is None:
        width = 0
        pct_text = "—"
    else:
        pct_float = float(pct)
        width = min(max(pct_float, 0), 140) / 140 * 100
        pct_text = f"{pct_float:.0f}%"

    label_text = status_label or "Estado"

    st.markdown(
        f"""
        <div style="background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-radius:{RADIUS['lg']};
                    padding:16px 18px;
                    margin-bottom:12px;
                    box-shadow:{SHADOWS['sm']};">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;gap:12px;">
                <div>
                    <div style="font-size:0.95rem;font-weight:900;
                                color:{COLORS['ink']};">
                        {_esc(title)}
                    </div>
                    <div style="font-size:0.82rem;color:{COLORS['muted']};
                                margin-top:4px;">
                        {_esc(req_text)} · {_esc(aporte_text)}
                    </div>
                </div>
                <div style="color:{color};font-weight:900;background:{_soft_bg(color)};
                            border:1px solid {_soft_border(color)};
                            border-radius:999px;padding:5px 10px;font-size:0.82rem;
                            white-space:nowrap;">
                    {_esc(label_text)} · {pct_text}
                </div>
            </div>

            <div style="background:{COLORS['border']};height:10px;border-radius:999px;
                        overflow:hidden;margin-top:14px;">
                <div style="width:{width:.1f}%;background:{color};height:10px;
                            border-radius:999px;"></div>
            </div>

            <div style="display:flex;justify-content:space-between;
                        color:{COLORS['muted']};font-size:0.72rem;
                        font-weight:700;margin-top:6px;">
                <span>0%</span>
                <span>90%</span>
                <span>100%</span>
                <span>110%</span>
                <span>140%+</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# SCORE CARDS
# =============================================================================

def render_score_card(
    title: str,
    score: float,
    subtitle: str = "",
    tone: str = "primary",
) -> None:
    """Tarjeta de score visual 0–100."""
    color = _tone_color(tone)

    try:
        score_val = max(0.0, min(float(score), 100.0))
    except Exception:
        score_val = 0.0

    st.markdown(
        f"""
        <div style="background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-radius:{RADIUS['xl']};
                    padding:20px;
                    box-shadow:{SHADOWS['md']};
                    text-align:center;
                    margin-bottom:12px;">
            <div style="font-size:0.78rem;color:{COLORS['muted']};
                        font-weight:850;text-transform:uppercase;
                        letter-spacing:0.06em;">
                {_esc(title)}
            </div>
            <div style="font-size:2.4rem;font-weight:950;color:{color};
                        line-height:1;margin-top:8px;">
                {score_val:.0f}
            </div>
            <div style="font-size:0.9rem;color:{COLORS['text']};
                        font-weight:700;margin-top:4px;">
                {_esc(subtitle)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# SOURCE CHIP GROUPS
# =============================================================================

def render_source_chip_group(
    title: str,
    items: str | Iterable[str] | None,
    color: str | None = None,
) -> None:
    """Grupo de chips para fuentes nutricionales."""
    color = color or COLORS["primary"]

    if items is None:
        items_list = []
    elif isinstance(items, str):
        items_list = [x.strip() for x in items.split(";") if x.strip()]
    else:
        items_list = [str(x).strip() for x in items if str(x).strip()]

    if not items_list:
        items_list = ["No especificado"]

    html_items = "".join(
        f"""
        <span class="uywa-badge"
              style="color:{color};background:{_soft_bg(color)};
                     border-color:{_soft_border(color)};">
            {_esc(item)}
        </span>
        """
        for item in items_list
    )

    st.markdown(
        f"""
        <div style="background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-radius:{RADIUS['lg']};
                    padding:14px 16px;
                    box-shadow:{SHADOWS['sm']};
                    margin-bottom:12px;">
            <div style="font-size:0.86rem;font-weight:900;
                        color:{COLORS['ink']};margin-bottom:8px;">
                {_esc(title)}
            </div>
            {html_items}
        </div>
        """,
        unsafe_allow_html=True,
    )


__all__ = [
    "_esc",
    "render_section_title",
    "render_section_header",
    "render_badge",
    "render_badges",
    "render_kpi_card",
    "render_metric_grid",
    "render_info_card",
    "render_progress_card",
    "render_score_card",
    "render_source_chip_group",
]
