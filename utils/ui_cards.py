
"""
UYWA UI Cards
Componentes visuales limpios para Streamlit.
No devuelve HTML. Todas las funciones renderizan directamente.
"""

from __future__ import annotations

from typing import Iterable
import html
import textwrap

import streamlit as st

from utils.ui_theme import (
    COLORS,
    NUTRIENT_COLORS,
    STATUS_COLORS,
    SHADOWS,
    RADIUS,
    FONT_FAMILY,
)


def _esc(value) -> str:
    return html.escape(str(value or ""))


def _tone_color(tone: str | None) -> str:
    if not tone:
        return COLORS["muted"]

    key = str(tone)
    key_l = key.lower()

    return (
        STATUS_COLORS.get(key_l)
        or STATUS_COLORS.get(key)
        or NUTRIENT_COLORS.get(key_l)
        or NUTRIENT_COLORS.get(key)
        or COLORS.get(key_l)
        or COLORS.get(key)
        or COLORS["muted"]
    )


def _render_html(raw_html: str) -> None:
    """Render seguro para evitar que Streamlit muestre HTML como bloque de código."""
    st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)


def render_section_title(
    title: str,
    kicker: str | None = None,
    subtitle: str | None = None,
    icon: str | None = None,
) -> None:
    icon_html = f"<span style='font-size:1.25rem;margin-right:8px;'>{_esc(icon)}</span>" if icon else ""
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

    _render_html(
        f"""
        <div style="margin:10px 0 18px 0;">
          {kicker_html}
          <div style="display:flex;align-items:center;font-family:{FONT_FAMILY};font-size:1.34rem;font-weight:900;color:{COLORS['ink']};">
            {icon_html}<span>{_esc(title)}</span>
          </div>
          {subtitle_html}
        </div>
        """
    )


render_section_header = render_section_title


def render_badge(label: str, status: str = "neutral", icon: str | None = None) -> None:
    color = _tone_color(status)
    icon_html = f"{_esc(icon)} " if icon else ""
    _render_html(
        f"""
        <span class="uywa-badge" style="color:{color};background:{color}12;border-color:{color}44;">
          {icon_html}{_esc(label)}
        </span>
        """
    )


def render_badges(labels: Iterable[str], status: str = "neutral") -> None:
    color = _tone_color(status)
    badges = "".join(
        f"<span class='uywa-badge' style='color:{color};background:{color}12;border-color:{color}44;'>{_esc(label)}</span>"
        for label in labels
    )
    _render_html(f"<div>{badges}</div>")


def render_kpi_card(
    title: str,
    value: str,
    unit: str | None = None,
    note: str | None = None,
    tone: str = "primary",
    icon: str | None = None,
) -> None:
    color = _tone_color(tone)
    unit_html = (
        f"<span style='font-size:0.82rem;color:{COLORS['muted']};font-weight:700;margin-left:4px;'>{_esc(unit)}</span>"
        if unit
        else ""
    )
    note_html = (
        f"<div style='font-size:0.78rem;color:{COLORS['muted']};margin-top:8px;line-height:1.35;'>{_esc(note)}</div>"
        if note
        else ""
    )
    icon_html = f"<div style='font-size:1.45rem;margin-bottom:6px;'>{_esc(icon)}</div>" if icon else ""

    _render_html(
        f"""
        <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};border-left:5px solid {color};
                    border-radius:{RADIUS['lg']};padding:16px 18px;box-shadow:{SHADOWS['sm']};
                    min-height:118px;margin-bottom:10px;">
          {icon_html}
          <div style="font-size:0.76rem;font-weight:850;letter-spacing:0.06em;text-transform:uppercase;color:{COLORS['muted']};">
            {_esc(title)}
          </div>
          <div style="margin-top:6px;font-size:1.45rem;font-weight:900;color:{COLORS['ink']};line-height:1.1;">
            {_esc(value)}{unit_html}
          </div>
          {note_html}
        </div>
        """
    )


def render_metric_grid(items: list[dict], columns: int = 3) -> None:
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


def render_info_card(title: str, body: str, tone: str = "neutral", icon: str | None = None) -> None:
    color = _tone_color(tone)
    icon_html = f"<span style='font-size:1.25rem;margin-right:8px;'>{_esc(icon)}</span>" if icon else ""

    _render_html(
        f"""
        <div style="background:{color}10;border:1px solid {color}44;border-left:6px solid {color};
                    border-radius:{RADIUS['lg']};padding:16px 18px;margin:10px 0;box-shadow:{SHADOWS['sm']};">
          <div style="font-size:1.05rem;font-weight:900;color:{COLORS['ink']};margin-bottom:6px;">
            {icon_html}{_esc(title)}
          </div>
          <div style="font-size:0.92rem;color:{COLORS['text']};line-height:1.45;">
            {_esc(body)}
          </div>
        </div>
        """
    )


def render_progress_card(
    title: str,
    pct: float | None,
    req_text: str,
    aporte_text: str,
    status_label: str = "",
    tone: str = "primary",
) -> None:
    """Usa componentes nativos para evitar HTML mostrado como texto."""
    color = _tone_color(tone)

    if pct is None:
        value_text = "—"
        progress = 0.0
        delta_text = status_label or "Sin referencia"
    else:
        pct_val = float(pct)
        value_text = f"{pct_val:.0f}%"
        progress = min(max(pct_val, 0.0) / 140.0, 1.0)
        delta_text = f"{status_label or 'Estado'} · {pct_val - 100:+.0f}% vs req."

    with st.container(border=True):
        left, right = st.columns([2.4, 1])
        with left:
            st.markdown(f"**{title}**")
            st.caption(f"{req_text} · {aporte_text}")
            st.progress(progress)
            st.caption("0% · 90% · 100% · 110% · 140%+")
        with right:
            st.metric("Cobertura", value_text, delta=delta_text, delta_color="inverse" if tone in ["danger", "warning"] else "normal")


def render_score_card(title: str, score: float, subtitle: str = "", tone: str = "primary") -> None:
    color = _tone_color(tone)
    try:
        score_val = max(0.0, min(float(score), 100.0))
    except Exception:
        score_val = 0.0

    _render_html(
        f"""
        <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};
                    border-radius:{RADIUS['xl']};padding:20px;box-shadow:{SHADOWS['md']};
                    text-align:center;margin-bottom:12px;">
          <div style="font-size:0.78rem;color:{COLORS['muted']};font-weight:850;text-transform:uppercase;letter-spacing:0.06em;">
            {_esc(title)}
          </div>
          <div style="font-size:2.4rem;font-weight:950;color:{color};line-height:1;margin-top:8px;">
            {score_val:.0f}
          </div>
          <div style="font-size:0.9rem;color:{COLORS['text']};font-weight:700;margin-top:4px;">
            {_esc(subtitle)}
          </div>
        </div>
        """
    )


def render_source_chip_group(title: str, items: str | Iterable[str] | None, color: str | None = None) -> None:
    color = color or COLORS["primary"]

    if items is None:
        items_list = []
    elif isinstance(items, str):
        items_list = [x.strip() for x in items.split(";") if x.strip()]
    else:
        items_list = [str(x).strip() for x in items if str(x).strip()]

    if not items_list:
        items_list = ["No especificado"]

    chips = "".join(
        f"<span class='uywa-badge' style='color:{color};background:{color}12;border-color:{color}44;'>{_esc(item)}</span>"
        for item in items_list
    )

    _render_html(
        f"""
        <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};
                    border-radius:{RADIUS['lg']};padding:14px 16px;box-shadow:{SHADOWS['sm']};
                    margin-bottom:12px;">
          <div style="font-size:0.86rem;font-weight:900;color:{COLORS['ink']};margin-bottom:8px;">
            {_esc(title)}
          </div>
          {chips}
        </div>
        """
    )


__all__ = [
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
