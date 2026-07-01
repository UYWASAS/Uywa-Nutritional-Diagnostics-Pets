"""
Componentes visuales reutilizables para las aplicaciones UYWA.

Este módulo concentra tarjetas, badges, KPIs y bloques de decisión para evitar
HTML repetido dentro de app.py o food_analysis.py.
"""

from __future__ import annotations

from typing import Iterable, Optional
import html

import streamlit as st

try:
    from utils.ui_theme import (
        COLORS,
        NUTRIENT_COLORS,
        STATUS_COLORS,
        SHADOWS,
        RADIUS,
        SPACING,
        FONT_FAMILY,
    )
except Exception:
    # Fallback para desarrollo local si el archivo ui_theme.py aún no está cargado.
    COLORS = {
        "primary": "#2563EB",
        "secondary": "#16A34A",
        "warning": "#F59E0B",
        "danger": "#DC2626",
        "muted": "#64748B",
        "dark": "#0F172A",
        "surface": "#FFFFFF",
        "border": "#E2E8F0",
        "soft": "#F8FAFC",
    }
    NUTRIENT_COLORS = {
        "protein": "#DC2626",
        "fat": "#F59E0B",
        "fiber": "#16A34A",
        "carbs": "#2563EB",
        "ash": "#64748B",
        "humidity": "#38BDF8",
    }
    STATUS_COLORS = {
        "low": "#2563EB",
        "ok": "#16A34A",
        "warning": "#F59E0B",
        "danger": "#DC2626",
        "neutral": "#64748B",
    }
    SHADOWS = {"sm": "0 4px 12px rgba(15,23,42,0.06)", "md": "0 10px 28px rgba(15,23,42,0.08)"}
    RADIUS = {"md": "14px", "lg": "18px", "xl": "24px", "pill": "999px"}
    SPACING = {"sm": "8px", "md": "14px", "lg": "20px"}
    FONT_FAMILY = "Inter, Montserrat, sans-serif"


def _esc(value) -> str:
    return html.escape(str(value or ""))


def _status_color(status: str | None) -> str:
    if not status:
        return STATUS_COLORS.get("neutral", "#64748B")
    return STATUS_COLORS.get(str(status).lower(), COLORS.get("muted", "#64748B"))


def render_section_title(
    title: str,
    kicker: str | None = None,
    subtitle: str | None = None,
    icon: str | None = None,
) -> None:
    """Encabezado visual uniforme para secciones."""
    icon_html = f"<span style='font-size:1.35rem;margin-right:8px;'>{_esc(icon)}</span>" if icon else ""
    kicker_html = (
        f"<div style='font-size:0.74rem;font-weight:850;letter-spacing:0.08em;text-transform:uppercase;color:{COLORS['primary']};margin-bottom:4px;'>{_esc(kicker)}</div>"
        if kicker
        else ""
    )
    subtitle_html = (
        f"<div style='font-size:0.92rem;color:{COLORS['muted']};margin-top:4px;line-height:1.45;'>{_esc(subtitle)}</div>"
        if subtitle
        else ""
    )

    st.markdown(
        f"""
        <div style="margin: 10px 0 18px 0;">
            {kicker_html}
            <div style="display:flex;align-items:center;font-family:{FONT_FAMILY};font-size:1.35rem;font-weight:900;color:{COLORS['dark']};">
                {icon_html}<span>{_esc(title)}</span>
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(
    label: str,
    status: str = "neutral",
    icon: str | None = None,
    soft: bool = True,
) -> None:
    """Badge individual."""
    color = _status_color(status)
    bg = f"{color}18" if soft else color
    fg = color if soft else "#FFFFFF"
    border = f"1px solid {color}33" if soft else f"1px solid {color}"
    icon_html = f"{_esc(icon)} " if icon else ""
    st.markdown(
        f"""
        <span style="display:inline-flex;align-items:center;gap:4px;background:{bg};color:{fg};border:{border};
                     border-radius:{RADIUS['pill']};padding:5px 10px;font-size:0.78rem;font-weight:800;margin:2px 4px 2px 0;">
            {icon_html}{_esc(label)}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_badges(labels: Iterable[str], status: str = "neutral") -> None:
    labels = [str(x) for x in labels if str(x).strip()]
    if not labels:
        return
    spans = []
    color = _status_color(status)
    for label in labels:
        spans.append(
            f"<span style='display:inline-flex;background:{color}18;color:{color};border:1px solid {color}33;"
            f"border-radius:{RADIUS['pill']};padding:5px 10px;font-size:0.78rem;font-weight:800;margin:2px 4px 2px 0;'>{_esc(label)}</span>"
        )
    st.markdown("".join(spans), unsafe_allow_html=True)


def render_kpi_card(
    title: str,
    value: str | int | float,
    unit: str | None = None,
    note: str | None = None,
    icon: str | None = None,
    status: str = "neutral",
    delta: str | None = None,
) -> None:
    """Tarjeta KPI premium."""
    color = _status_color(status)
    unit_html = f"<span style='font-size:0.85rem;color:{COLORS['muted']};font-weight:700;margin-left:4px;'>{_esc(unit)}</span>" if unit else ""
    note_html = f"<div style='font-size:0.78rem;color:{COLORS['muted']};margin-top:8px;line-height:1.35;'>{_esc(note)}</div>" if note else ""
    delta_html = f"<div style='font-size:0.8rem;color:{color};font-weight:850;margin-top:6px;'>{_esc(delta)}</div>" if delta else ""
    icon_html = f"<div style='font-size:1.35rem;'>{_esc(icon)}</div>" if icon else ""

    st.markdown(
        f"""
        <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};border-left:6px solid {color};
                    border-radius:{RADIUS['lg']};padding:16px 18px;box-shadow:{SHADOWS['sm']};min-height:128px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;">
                <div>
                    <div style="font-size:0.76rem;color:{COLORS['muted']};font-weight:850;text-transform:uppercase;letter-spacing:0.06em;">
                        {_esc(title)}
                    </div>
                    <div style="margin-top:8px;font-size:1.62rem;color:{COLORS['dark']};font-weight:950;line-height:1.05;">
                        {_esc(value)}{unit_html}
                    </div>
                </div>
                {icon_html}
            </div>
            {delta_html}
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_grid(items: list[dict], columns: int = 3) -> None:
    """Renderiza una grilla de KPIs desde diccionarios."""
    if not items:
        return
    cols = st.columns(columns)
    for i, item in enumerate(items):
        with cols[i % columns]:
            render_kpi_card(
                title=item.get("title", ""),
                value=item.get("value", "—"),
                unit=item.get("unit"),
                note=item.get("note"),
                icon=item.get("icon"),
                status=item.get("status", "neutral"),
                delta=item.get("delta"),
            )


def render_info_card(
    title: str,
    body: str,
    icon: str | None = None,
    status: str = "neutral",
) -> None:
    color = _status_color(status)
    icon_html = f"<span style='font-size:1.45rem;margin-right:8px;'>{_esc(icon)}</span>" if icon else ""
    st.markdown(
        f"""
        <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};border-left:6px solid {color};
                    border-radius:{RADIUS['lg']};padding:16px 18px;box-shadow:{SHADOWS['sm']};margin-bottom:12px;">
            <div style="display:flex;align-items:center;color:{COLORS['dark']};font-weight:900;font-size:1.02rem;">
                {icon_html}<span>{_esc(title)}</span>
            </div>
            <div style="font-size:0.9rem;color:{COLORS['muted']};line-height:1.5;margin-top:8px;">
                {_esc(body)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_card(
    title: str,
    value_pct: float | None,
    left_label: str,
    right_label: str,
    status: str = "neutral",
    icon: str | None = None,
    cap_pct: float = 140.0,
) -> None:
    """Tarjeta con barra de progreso y porcentaje."""
    color = _status_color(status)
    if value_pct is None:
        pct_text = "—"
        progress = 0
    else:
        pct_text = f"{value_pct:.0f}%"
        progress = max(0, min(value_pct / cap_pct, 1))

    with st.container(border=True):
        c1, c2 = st.columns([2.4, 1])
        with c1:
            icon_prefix = f"{icon} " if icon else ""
            st.markdown(f"**{icon_prefix}{title}**")
            st.caption(f"{left_label} · {right_label}")
            st.progress(progress)
        with c2:
            st.metric("Cobertura", pct_text)


def render_score_card(
    title: str,
    score: float,
    max_score: float = 100,
    subtitle: str | None = None,
    status: str | None = None,
) -> None:
    """Tarjeta de score nutricional o clínico."""
    pct = (score / max_score * 100) if max_score else 0
    if status is None:
        status = "ok" if pct >= 80 else ("warning" if pct >= 60 else "danger")
    color = _status_color(status)
    subtitle_html = f"<div style='font-size:0.85rem;color:{COLORS['muted']};margin-top:6px;'>{_esc(subtitle)}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,{color}18,#FFFFFF);border:1px solid {color}33;
                    border-radius:{RADIUS['xl']};padding:20px;box-shadow:{SHADOWS['md']};text-align:center;">
            <div style="font-size:0.78rem;color:{COLORS['muted']};font-weight:850;text-transform:uppercase;letter-spacing:0.06em;">
                {_esc(title)}
            </div>
            <div style="font-size:2.7rem;font-weight:950;color:{color};line-height:1;margin-top:10px;">
                {score:.0f}<span style="font-size:1.1rem;color:{COLORS['muted']};">/{max_score:.0f}</span>
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_chip_group(title: str, items: str | Iterable[str] | None, color: str | None = None) -> None:
    """Muestra materias primas/fuentes nutricionales como chips."""
    color = color or COLORS.get("primary", "#2563EB")
    if isinstance(items, str):
        parsed = [x.strip() for x in items.replace(",", ";").split(";") if x.strip()]
    elif items:
        parsed = [str(x).strip() for x in items if str(x).strip()]
    else:
        parsed = []

    st.markdown(f"**{_esc(title)}**")
    if not parsed:
        st.caption("No especificado")
        return

    chips = "".join(
        f"<span style='display:inline-flex;background:{color}14;color:{color};border:1px solid {color}30;"
        f"border-radius:{RADIUS['pill']};padding:5px 10px;font-size:0.78rem;font-weight:800;margin:3px 4px 3px 0;'>{_esc(x)}</span>"
        for x in parsed
    )
    st.markdown(chips, unsafe_allow_html=True)
