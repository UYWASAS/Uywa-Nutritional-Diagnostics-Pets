from __future__ import annotations

import streamlit as st

from uywa_core.theme.tokens import (
    COLOR_AQUA_PALE,
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_BORDER_STRONG,
    COLOR_NAVY,
    COLOR_NAVY_DARK,
    COLOR_NAVY_LIGHT,
    COLOR_SURFACE,
    COLOR_SURFACE_SOFT,
    COLOR_TEAL,
    COLOR_TEAL_DARK,
    COLOR_TEAL_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    FONT_FAMILY,
    RADIUS_LARGE,
    RADIUS_MEDIUM,
    SHADOW_SOFT,
    SIDEBAR_WIDTH,
)


def inject_platform_theme() -> None:
    """
    Aplica la identidad visual global de Uywa Platform.

    Incluye:
    - tipografía;
    - fondo general;
    - barra lateral;
    - botones;
    - formularios;
    - alertas;
    - expansores;
    - pestañas;
    - tablas.
    """

    st.markdown(
        f"""
        <style>
            /* =====================================================
               TIPOGRAFÍA GENERAL
               ===================================================== */

            html,
            body,
            [class*="css"],
            [class*="st-"],
            button,
            input,
            textarea,
            select {{
                font-family: {FONT_FAMILY};
            }}

            html,
            body {{
                color: {COLOR_TEXT_PRIMARY};
            }}

            /* =====================================================
               CONTENEDOR PRINCIPAL
               ===================================================== */

            [data-testid="stAppViewContainer"] {{
                background:
                    radial-gradient(
                        circle at 90% 5%,
                        rgba(101, 190, 198, 0.10),
                        transparent 25rem
                    ),
                    {COLOR_BACKGROUND};
            }}

            [data-testid="stMain"] {{
                background: transparent;
            }}

            .block-container {{
                max-width: 1380px;
                padding-top: 2rem;
                padding-bottom: 3rem;
                padding-left: 2.4rem;
                padding-right: 2.4rem;
            }}

            /* =====================================================
               ENCABEZADO NATIVO DE STREAMLIT
               ===================================================== */

            [data-testid="stHeader"] {{
                background: transparent;
            }}

            [data-testid="stToolbar"] {{
                right: 1rem;
            }}

            /* =====================================================
               BARRA LATERAL
               ===================================================== */

            [data-testid="stSidebar"] {{
                width: {SIDEBAR_WIDTH};
                min-width: {SIDEBAR_WIDTH};
                background:
                    linear-gradient(
                        180deg,
                        {COLOR_NAVY} 0%,
                        {COLOR_NAVY_DARK} 100%
                    );
                border-right: none;
                box-shadow: 6px 0 22px rgba(17, 27, 50, 0.12);
            }}

            [data-testid="stSidebar"] > div:first-child {{
                width: {SIDEBAR_WIDTH};
                padding-top: 1.15rem;
            }}

            [data-testid="stSidebar"] .block-container {{
                padding-left: 1.1rem;
                padding-right: 1.1rem;
            }}

            [data-testid="stSidebar"] * {{
                color: #FFFFFF;
            }}

            [data-testid="stSidebar"] hr {{
                border-color: rgba(255, 255, 255, 0.24);
            }}

            [data-testid="stSidebar"] [data-testid="stImage"] {{
                background: transparent;
                border-radius: {RADIUS_MEDIUM};
                overflow: hidden;
            }}

            [data-testid="stSidebarCollapseButton"] button {{
                color: #FFFFFF;
            }}

            /* =====================================================
               TÍTULOS Y TEXTO
               ===================================================== */

            h1,
            h2,
            h3,
            h4,
            h5,
            h6 {{
                color: {COLOR_TEXT_PRIMARY};
                letter-spacing: -0.02em;
            }}

            h1 {{
                font-weight: 800;
            }}

            h2,
            h3 {{
                font-weight: 750;
            }}

            p,
            li {{
                color: {COLOR_TEXT_SECONDARY};
                line-height: 1.6;
            }}

            [data-testid="stCaptionContainer"] {{
                color: {COLOR_TEXT_MUTED};
            }}

            /* =====================================================
               BOTONES
               ===================================================== */

            .stButton > button,
            .stFormSubmitButton > button {{
                min-height: 2.8rem;
                border: 1px solid {COLOR_TEAL};
                border-radius: {RADIUS_MEDIUM};
                background:
                    linear-gradient(
                        135deg,
                        {COLOR_TEAL},
                        {COLOR_TEAL_DARK}
                    );
                color: #FFFFFF;
                font-weight: 700;
                letter-spacing: 0.01em;
                box-shadow: 0 5px 14px rgba(40, 119, 126, 0.18);
                transition:
                    transform 0.16s ease,
                    box-shadow 0.16s ease,
                    border-color 0.16s ease;
            }}

            .stButton > button:hover,
            .stFormSubmitButton > button:hover {{
                border-color: {COLOR_TEAL_DARK};
                background:
                    linear-gradient(
                        135deg,
                        {COLOR_TEAL_DARK},
                        {COLOR_NAVY_LIGHT}
                    );
                color: #FFFFFF;
                transform: translateY(-1px);
                box-shadow: 0 8px 18px rgba(23, 35, 63, 0.20);
            }}

            .stButton > button:focus,
            .stFormSubmitButton > button:focus {{
                color: #FFFFFF;
                box-shadow:
                    0 0 0 0.18rem rgba(101, 190, 198, 0.25);
            }}

            .stButton > button:disabled,
            .stFormSubmitButton > button:disabled {{
                border-color: {COLOR_BORDER};
                background: #E8ECF2;
                color: #8791A0;
                box-shadow: none;
                transform: none;
            }}

            /* Botones dentro del sidebar */

            [data-testid="stSidebar"] .stButton > button {{
                border: 1px solid rgba(255, 255, 255, 0.45);
                background: rgba(255, 255, 255, 0.08);
                color: #FFFFFF;
                box-shadow: none;
            }}

            [data-testid="stSidebar"] .stButton > button:hover {{
                border-color: #FFFFFF;
                background: rgba(255, 255, 255, 0.16);
                color: #FFFFFF;
            }}

            /* =====================================================
               CAMPOS DE FORMULARIO
               ===================================================== */

            [data-baseweb="input"] > div,
            [data-baseweb="textarea"] > div,
            [data-baseweb="select"] > div {{
                border-color: {COLOR_BORDER_STRONG};
                border-radius: {RADIUS_MEDIUM};
                background: {COLOR_SURFACE};
            }}

            [data-baseweb="input"] > div:focus-within,
            [data-baseweb="textarea"] > div:focus-within,
            [data-baseweb="select"] > div:focus-within {{
                border-color: {COLOR_TEAL_LIGHT};
                box-shadow:
                    0 0 0 0.18rem rgba(101, 190, 198, 0.18);
            }}

            /* =====================================================
               FORMULARIOS
               ===================================================== */

            [data-testid="stForm"] {{
                padding: 1.5rem;
                border: 1px solid {COLOR_BORDER};
                border-radius: {RADIUS_LARGE};
                background: {COLOR_SURFACE};
                box-shadow: {SHADOW_SOFT};
            }}

            /* =====================================================
               ALERTAS
               ===================================================== */

            [data-testid="stAlert"] {{
                border-radius: {RADIUS_MEDIUM};
                border-width: 1px;
                box-shadow: none;
            }}

            /* =====================================================
               EXPANSORES
               ===================================================== */

            [data-testid="stExpander"] {{
                border: 1px solid {COLOR_BORDER};
                border-radius: {RADIUS_MEDIUM};
                background: {COLOR_SURFACE};
                overflow: hidden;
            }}

            /* =====================================================
               PESTAÑAS
               ===================================================== */

            [data-baseweb="tab-list"] {{
                gap: 0.4rem;
                border-bottom: 1px solid {COLOR_BORDER};
            }}

            [data-baseweb="tab"] {{
                min-height: 2.8rem;
                padding-left: 1rem;
                padding-right: 1rem;
                border-radius: {RADIUS_MEDIUM} {RADIUS_MEDIUM} 0 0;
                color: {COLOR_TEXT_SECONDARY};
                font-weight: 650;
            }}

            [aria-selected="true"][data-baseweb="tab"] {{
                background: {COLOR_AQUA_PALE};
                color: {COLOR_TEAL_DARK};
            }}

            /* =====================================================
               DATAFRAMES Y TABLAS
               ===================================================== */

            [data-testid="stDataFrame"] {{
                border: 1px solid {COLOR_BORDER};
                border-radius: {RADIUS_MEDIUM};
                overflow: hidden;
                background: {COLOR_SURFACE};
            }}

            /* =====================================================
               MÉTRICAS
               ===================================================== */

            [data-testid="stMetric"] {{
                padding: 1rem;
                border: 1px solid {COLOR_BORDER};
                border-radius: {RADIUS_MEDIUM};
                background: {COLOR_SURFACE};
                box-shadow: {SHADOW_SOFT};
            }}

            /* =====================================================
               DIVISORES
               ===================================================== */

            [data-testid="stDivider"] {{
                border-color: {COLOR_BORDER};
            }}

            /* =====================================================
               RESPONSIVE
               ===================================================== */

            @media (max-width: 900px) {{
                .block-container {{
                    padding-left: 1rem;
                    padding-right: 1rem;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
