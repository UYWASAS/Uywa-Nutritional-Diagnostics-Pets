
import html
import textwrap

import streamlit as st


UYWA_COLORS = {
    "blue": "#2563EB",
    "blue_dark": "#1D4ED8",
    "blue_soft": "#EFF6FF",
    "green": "#16A34A",
    "green_soft": "#ECFDF5",
    "orange": "#F97316",
    "orange_soft": "#FFF7ED",
    "red": "#DC2626",
    "red_soft": "#FEF2F2",
    "yellow": "#F59E0B",
    "yellow_soft": "#FFFBEB",
    "purple": "#7C3AED",
    "purple_soft": "#F5F3FF",
    "gray": "#64748B",
    "gray_soft": "#F8FAFC",
    "dark": "#0F172A",
    "text": "#1F2937",
    "muted": "#64748B",
    "border": "#E2E8F0",
    "white": "#FFFFFF",
}


RISK_CONFIG = {
    "Bajo": {
        "color": UYWA_COLORS["green"],
        "bg": UYWA_COLORS["green_soft"],
        "icon": "●",
    },
    "Moderado": {
        "color": UYWA_COLORS["yellow"],
        "bg": UYWA_COLORS["yellow_soft"],
        "icon": "●",
    },
    "Alto": {
        "color": UYWA_COLORS["red"],
        "bg": UYWA_COLORS["red_soft"],
        "icon": "●",
    },
}


TONE_CONFIG = {
    "blue": {
        "color": UYWA_COLORS["blue"],
        "bg": UYWA_COLORS["blue_soft"],
    },
    "green": {
        "color": UYWA_COLORS["green"],
        "bg": UYWA_COLORS["green_soft"],
    },
    "orange": {
        "color": UYWA_COLORS["orange"],
        "bg": UYWA_COLORS["orange_soft"],
    },
    "red": {
        "color": UYWA_COLORS["red"],
        "bg": UYWA_COLORS["red_soft"],
    },
    "purple": {
        "color": UYWA_COLORS["purple"],
        "bg": UYWA_COLORS["purple_soft"],
    },
    "gray": {
        "color": UYWA_COLORS["gray"],
        "bg": UYWA_COLORS["gray_soft"],
    },
}


def _esc(value) -> str:
    return html.escape(str(value or ""))


def _html(raw_html: str) -> None:
    """Render HTML de forma controlada para evitar que aparezca como texto."""
    st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)


def inject_global_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --uywa-blue: #2563EB;
            --uywa-blue-dark: #1D4ED8;
            --uywa-green: #16A34A;
            --uywa-orange: #F97316;
            --uywa-red: #DC2626;
            --uywa-purple: #7C3AED;
            --uywa-dark: #0F172A;
            --uywa-text: #1F2937;
            --uywa-muted: #64748B;
            --uywa-border: #E2E8F0;
            --uywa-bg: #F8FAFC;
            --uywa-card: #FFFFFF;
        }

        html, body, .stApp, .block-container {
            font-family: 'Inter', sans-serif !important;
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 30%),
                linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 55%, #EEF4FC 100%) !important;
            color: var(--uywa-text) !important;
        }

        .block-container {
            padding: 2rem 4rem 3rem 4rem;
            max-width: 1520px;
        }

        h1 {
            font-size: 2.25rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
            color: var(--uywa-dark) !important;
            margin-bottom: 0.75rem !important;
        }

        h2 {
            font-size: 1.65rem !important;
            font-weight: 750 !important;
            color: var(--uywa-dark) !important;
            letter-spacing: -0.02em !important;
        }

        h3 {
            font-size: 1.25rem !important;
            font-weight: 750 !important;
            color: var(--uywa-dark) !important;
        }

        p, div, span, label {
            font-size: 1rem;
        }

        hr {
            border: none !important;
            border-top: 1px solid var(--uywa-border) !important;
            margin: 1.4rem 0 !important;
        }

        footer {
            visibility: hidden !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255,255,255,0.70);
            border: 1px solid var(--uywa-border);
            padding: 8px;
            border-radius: 16px;
            box-shadow: 0 8px 28px rgba(15, 23, 42, 0.05);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            padding: 10px 16px;
            font-weight: 700;
            color: var(--uywa-muted);
        }

        .stTabs [aria-selected="true"] {
            background: var(--uywa-blue) !important;
            color: white !important;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top, rgba(37,99,235,0.28), transparent 35%),
                linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
            color: #fff !important;
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #fff !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--uywa-blue) 0%, var(--uywa-blue-dark) 100%) !important;
            color: #fff !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.7rem 1.1rem !important;
            font-size: 0.98rem !important;
            font-weight: 750 !important;
            box-shadow: 0 8px 18px rgba(37, 99, 235, 0.22);
            transition: all 0.18s ease-in-out;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.30);
        }

        .stDownloadButton > button {
            border-radius: 12px !important;
            font-weight: 750 !important;
            padding: 0.7rem 1.1rem !important;
        }

        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.82);
            border: 1px solid var(--uywa-border);
            border-radius: 16px;
            padding: 14px 16px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        [data-testid="stMetricLabel"] {
            color: var(--uywa-muted) !important;
            font-weight: 700 !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.55rem !important;
            font-weight: 800 !important;
            color: var(--uywa-dark) !important;
        }

        .stNumberInput, .stSelectbox, .stTextInput, .stTextArea, .stMultiSelect {
            background-color: transparent !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        textarea {
            border-radius: 12px !important;
            border: 1px solid var(--uywa-border) !important;
            background: rgba(255,255,255,0.95) !important;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 16px !important;
            overflow: hidden !important;
            border: 1px solid var(--uywa-border) !important;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        .streamlit-expanderHeader {
            font-weight: 750 !important;
            color: var(--uywa-dark) !important;
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--uywa-border) !important;
            border-radius: 16px !important;
            background: rgba(255,255,255,0.72) !important;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }

        .uywa-section-header {
            background: rgba(255,255,255,0.76);
            border: 1px solid var(--uywa-border);
            border-radius: 18px;
            padding: 18px 22px;
            margin: 12px 0 20px 0;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
        }

        .uywa-section-kicker {
            color: var(--uywa-blue);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .uywa-section-title {
            font-size: 1.35rem;
            line-height: 1.25;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--uywa-dark);
            margin-bottom: 4px;
        }

        .uywa-section-subtitle {
            color: var(--uywa-muted);
            font-size: 0.96rem;
            line-height: 1.45;
        }

        .uywa-kpi-card {
            position: relative;
            overflow: hidden;
            background: rgba(255,255,255,0.92);
            border: 1px solid var(--uywa-border);
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.07);
            min-height: 126px;
        }

        .uywa-kpi-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 6px;
            background: var(--accent-color);
        }

        .uywa-kpi-card::after {
            content: "";
            position: absolute;
            right: -30px;
            top: -30px;
            width: 110px;
            height: 110px;
            border-radius: 999px;
            background: var(--accent-bg);
        }

        .uywa-kpi-label {
            color: var(--uywa-muted);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 7px;
            position: relative;
            z-index: 2;
        }

        .uywa-kpi-value {
            color: var(--uywa-dark);
            font-size: 1.65rem;
            line-height: 1.1;
            font-weight: 850;
            letter-spacing: -0.03em;
            position: relative;
            z-index: 2;
        }

        .uywa-kpi-unit, .uywa-kpi-note {
            color: var(--uywa-muted);
            font-size: 0.86rem;
            margin-top: 4px;
            position: relative;
            z-index: 2;
        }

        .uywa-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            border: 1px solid var(--badge-color, #E2E8F0);
            color: var(--badge-color, #64748B);
            background: var(--badge-bg, #F8FAFC);
        }

        .uywa-alert-card {
            border-radius: 18px;
            padding: 20px 22px;
            border: 1px solid var(--alert-color);
            border-left: 7px solid var(--alert-color);
            background: var(--alert-bg);
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
            margin: 14px 0;
        }

        .uywa-alert-title {
            font-size: 1.1rem;
            font-weight: 850;
            color: var(--alert-color);
            margin-bottom: 8px;
        }

        .uywa-alert-line {
            color: var(--uywa-text);
            font-size: 0.95rem;
            line-height: 1.45;
            margin-bottom: 5px;
        }

        .uywa-alert-text {
            color: var(--uywa-text);
            font-size: 0.94rem;
            line-height: 1.55;
            margin-top: 12px;
            opacity: 0.96;
        }

        .profile-left {
            text-align: center;
            padding: 20px 10px;
        }

        .pet-photo-circle {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 5px solid #FFFFFF;
            box-shadow: 0 10px 30px rgba(37,99,235,0.25);
            margin: 0 auto 14px auto;
            display: block;
            outline: 3px solid rgba(37,99,235,0.22);
        }

        .pet-photo-placeholder {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background:
                radial-gradient(circle at 30% 20%, rgba(255,255,255,0.40), transparent 30%),
                linear-gradient(135deg, #2563EB 0%, #16A34A 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 58px;
            margin: 0 auto 14px auto;
            box-shadow: 0 10px 30px rgba(37,99,235,0.24);
        }

        .pet-name {
            font-size: 1.55rem;
            font-weight: 850;
            color: var(--uywa-dark);
            letter-spacing: -0.03em;
            margin: 8px 0 2px 0;
        }

        .stage-badge {
            display: inline-flex;
            padding: 5px 13px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            margin: 8px 0;
        }

        .stage-badge.cachorro {
            background-color: #FFF7ED;
            color: #C2410C;
            border: 1px solid #FDBA74;
        }

        .stage-badge.adulto {
            background-color: #ECFDF5;
            color: #15803D;
            border: 1px solid #86EFAC;
        }

        .vital-card {
            background: rgba(255,255,255,0.92);
            border-radius: 18px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.07);
            border: 1px solid var(--uywa-border);
            border-left: 6px solid #2563EB;
            min-height: 100px;
        }

        .vital-card .card-label {
            font-size: 0.74rem;
            color: var(--uywa-muted);
            text-transform: uppercase;
            letter-spacing: 0.07em;
            font-weight: 850;
            margin-bottom: 4px;
        }

        .vital-card .card-value {
            font-size: 1.28rem;
            font-weight: 850;
            color: var(--uywa-dark);
            letter-spacing: -0.02em;
        }

        .vital-card .card-icon {
            font-size: 1.35rem;
            float: right;
            margin-top: -2px;
        }

        .bcs-bar-container {
            background: #E2E8F0;
            border-radius: 999px;
            height: 9px;
            margin-top: 9px;
            overflow: hidden;
        }

        .bcs-bar-fill {
            height: 9px;
            border-radius: 999px;
        }

        .section-divider {
            border: none;
            border-top: 1px solid var(--uywa-border);
            margin: 24px 0 18px 0;
        }

        .energy-table, .nutrients-table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            margin-top: 20px;
            font-size: 0.94rem;
            text-align: left;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--uywa-border);
            box-shadow: 0 10px 28px rgba(15,23,42,0.05);
            background: #fff;
        }

        .energy-table th, .nutrients-table th {
            background-color: #0F172A;
            color: #fff;
            padding: 13px 14px;
            font-weight: 850;
            font-size: 0.83rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .energy-table td, .nutrients-table td {
            padding: 13px 14px;
            border-bottom: 1px solid #E2E8F0;
            color: var(--uywa-text);
        }

        .energy-table tr:nth-child(even), .nutrients-table tr:nth-child(even) {
            background-color: #F8FAFC;
        }

        .diagnostic-card {
            border-radius: 18px;
            padding: 22px 24px;
            margin: 20px 0;
            border: 1px solid;
            border-left: 7px solid;
            box-shadow: 0 12px 30px rgba(15,23,42,0.07);
        }

        .diagnostic-card.low-risk {
            background: #ECFDF5;
            border-color: #16A34A;
            color: #14532D;
        }

        .diagnostic-card.moderate-risk {
            background: #FFFBEB;
            border-color: #F59E0B;
            color: #78350F;
        }

        .diagnostic-card.high-risk {
            background: #FEF2F2;
            border-color: #DC2626;
            color: #7F1D1D;
        }

        @media (max-width: 900px) {
            .block-container {
                padding: 1.2rem 1.2rem 2rem 1.2rem;
            }

            h1 {
                font-size: 1.75rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title, subtitle=None, kicker=None):
    kicker_html = f"<div class='uywa-section-kicker'>{_esc(kicker)}</div>" if kicker else ""
    subtitle_html = f"<div class='uywa-section-subtitle'>{_esc(subtitle)}</div>" if subtitle else ""

    _html(
        f"""
        <div class="uywa-section-header">
            {kicker_html}
            <div class="uywa-section-title">{_esc(title)}</div>
            {subtitle_html}
        </div>
        """
    )


def render_kpi_card(title, value, unit="", note="", tone="blue"):
    cfg = TONE_CONFIG.get(tone, TONE_CONFIG["blue"])

    _html(
        f"""
        <div class="uywa-kpi-card" style="--accent-color:{cfg['color']}; --accent-bg:{cfg['bg']};">
            <div class="uywa-kpi-label">{_esc(title)}</div>
            <div class="uywa-kpi-value">{_esc(value)}</div>
            <div class="uywa-kpi-unit">{_esc(unit)}</div>
            <div class="uywa-kpi-note">{_esc(note)}</div>
        </div>
        """
    )


def render_badge(text, tone="blue"):
    cfg = TONE_CONFIG.get(tone, TONE_CONFIG["blue"])

    _html(
        f"""
        <span class="uywa-badge" style="--badge-color:{cfg['color']}; --badge-bg:{cfg['bg']};">
            {_esc(text)}
        </span>
        """
    )


def render_risk_card(risk, title, lines=None, text=None):
    cfg = RISK_CONFIG.get(risk, RISK_CONFIG["Bajo"])
    lines = lines or []

    lines_html = "".join(f"<div class='uywa-alert-line'>{_esc(line)}</div>" for line in lines)
    text_html = f"<div class='uywa-alert-text'>{_esc(text)}</div>" if text else ""

    _html(
        f"""
        <div class="uywa-alert-card" style="--alert-color:{cfg['color']}; --alert-bg:{cfg['bg']};">
            <div class="uywa-alert-title">{cfg['icon']} {_esc(title)}</div>
            {lines_html}
            {text_html}
        </div>
        """
    )


def render_pet_identity_card(nombre, especie, etapa, especie_icon, foto_b64=None):
    """
    Tarjeta visual del paciente.
    Esta versión evita que el HTML interno se muestre como texto.
    """
    nombre = _esc(nombre or "Mascota")
    especie = _esc(str(especie or "").capitalize())
    etapa_raw = str(etapa or "").lower()
    etapa_label = _esc(etapa_raw.capitalize())
    etapa_class = "cachorro" if etapa_raw == "cachorro" else "adulto"

    if foto_b64:
        photo_html = f'<img src="data:image/png;base64,{foto_b64}" class="pet-photo-circle" alt="foto mascota"/>'
    else:
        photo_html = f'<div class="pet-photo-placeholder">{_esc(especie_icon)}</div>'

    _html(
        f"""
        <div class="profile-left">
            {photo_html}
            <div class="pet-name">{nombre}</div>
            <div style="font-size:13px; color:#718096; margin:2px 0;">
                {especie}
            </div>
            <span class="stage-badge {etapa_class}">{etapa_label}</span>
        </div>
        """
    )


def render_vital_card(title, value, icon="", color="#2563EB", extra_html=""):
    _html(
        f"""
        <div class="vital-card" style="border-left-color:{color};">
            <span class="card-icon">{_esc(icon)}</span>
            <div class="card-label">{_esc(title)}</div>
            <div class="card-value">{_esc(value)}</div>
            {extra_html}
        </div>
        """
    )


def render_bcs_card(bcs, bcs_pct, bcs_color):
    render_vital_card(
        title="Condición Corporal (BCS)",
        value=f"{bcs} / 9",
        icon="📏",
        color=bcs_color,
        extra_html=f"""
        <div class="bcs-bar-container">
            <div class="bcs-bar-fill" style="width:{bcs_pct}%; background:{bcs_color};"></div>
        </div>
        """,
    )


def render_energy_kpi_grid(
    energia_basal_actual,
    mer_actual,
    mer_final,
    factor_fisiologico,
    factor_condicion_val,
    senior_aplicado,
    fmt_func,
):
    senior_label = "×0.85 aplicado" if senior_aplicado else "No aplicado"

    ec1, ec2, ec3, ec4 = st.columns(4)

    with ec1:
        render_kpi_card(
            title="RER actual",
            value=fmt_func(energia_basal_actual),
            unit="kcal/día",
            note="Energía en reposo",
            tone="blue",
        )

    with ec2:
        render_kpi_card(
            title="MER fisiológico",
            value=fmt_func(mer_actual),
            unit="kcal/día",
            note=f"Factor {factor_fisiologico}",
            tone="green",
        )

    with ec3:
        render_kpi_card(
            title="MER ajustado final",
            value=fmt_func(mer_final),
            unit="kcal/día",
            note="Después de BCS/senior",
            tone="orange",
        )

    with ec4:
        render_kpi_card(
            title="Factor final",
            value=factor_condicion_val,
            unit="RER × factor",
            note=f"Senior: {senior_label}",
            tone="purple" if senior_aplicado else "gray",
        )


def render_profile_dashboard(
    nombre,
    especie,
    etapa,
    peso,
    edad,
    bcs,
    estado_preview,
    riesgo_preview,
    mer_final,
    senior_aplicado,
    fmt_func,
):
    dash1, dash2, dash3 = st.columns(3)

    with dash1:
        render_kpi_card(
            title="Paciente",
            value=nombre,
            unit=f"{str(especie).capitalize()} · {str(etapa).capitalize()}",
            note=f"{fmt_func(peso)} kg · {fmt_func(edad)} años",
            tone="blue",
        )

    with dash2:
        risk_tone = {
            "Bajo": "green",
            "Moderado": "orange",
            "Alto": "red",
        }.get(riesgo_preview, "green")

        render_kpi_card(
            title="Estado corporal",
            value=f"BCS {bcs}/9",
            unit=estado_preview,
            note=f"Riesgo {riesgo_preview}",
            tone=risk_tone,
        )

    with dash3:
        render_kpi_card(
            title="Energía final",
            value=f"{fmt_func(mer_final)}",
            unit="kcal/día",
            note=f"Senior: {'Sí' if senior_aplicado else 'No'}",
            tone="orange",
        )
def render_app_title(
    title="UYWA PET NUTRITION STUDIO",
    subtitle="Sistema de apoyo a la decisión clínica en nutrición de animales de compañia",
):
    st.markdown(
        f"""
        <div style="
            font-size:100px !important;
            font-weight:900 !important;
            color:#0F172A !important;
            line-height:0.95 !important;
            margin:0 0 10px 0 !important;
            letter-spacing:-3px !important;
            font-family:Inter, Montserrat, sans-serif !important;
        ">
            {html.escape(str(title))}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="
            font-size:26px !important;
            color:#64748B !important;
            line-height:1.35 !important;
            font-weight:500 !important;
            margin:0 0 28px 0 !important;
            font-family:Inter, Montserrat, sans-serif !important;
        ">
            {html.escape(str(subtitle))}
        </div>
        """,
        unsafe_allow_html=True,
    )
