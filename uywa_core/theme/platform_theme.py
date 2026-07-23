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
    - tablas;
    - métricas;
    - preservación de íconos nativos de Streamlit.
    """

    st.markdown(
        f"""
        <style>
            /* =====================================================
               TIPOGRAFÍA GENERAL
               ===================================================== */

            html,
            body,
            p,
            li,
            h1,
            h2,
            h3,
            h4,
            h5,
            h6,
            label,
            input,
            textarea,
            select,
            button {{
                font-family: {FONT_FAMILY};
            }}

            html,
            body {{
                color: {COLOR_TEXT_PRIMARY};
            }}

            /*
            IMPORTANTE:
            Streamlit utiliza Material Symbols para varios íconos.
            No se debe sobrescribir su fuente con la tipografía general.
            */

            .material-symbols-rounded,
            .material-symbols-outlined,
            [data-testid="stIconMaterial"],
            [data-testid="stIconMaterial"] span,
            [class*="material-symbols"] {{
                font-family: "Material Symbols Rounded" !important;
                font-weight: normal !important;
                font-style: normal !important;
                font-size: inherit;
                line-height: 1;
                letter-spacing: normal;
                text-transform: none;
                white-space: nowrap;
                word-wrap: normal;
                direction: ltr;
                -webkit-font-feature-settings: "liga";
                -webkit-font-smoothing: antialiased;
                font-feature-settings: "liga";
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
                box-shadow:
                    6px 0 22px rgba(17, 27, 50, 0.12);
            }}

            [data-testid="stSidebar"] > div:first-child {{
                width: {SIDEBAR_WIDTH};
                padding-top: 1.15rem;
            }}

            [data-testid="stSidebar"] .block-container {{
                padding-left: 1.1rem;
                padding-right: 1.1rem;
            }}

            /*
            No usamos:
            [data-testid="stSidebar"] * {{ color:white; }}

            porque modifica también inputs, paneles y componentes internos.
            */

            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] h4,
            [data-testid="stSidebar"] h5,
            [data-testid="stSidebar"] h6 {{
                color: #FFFFFF;
            }}

            [data-testid="stSidebar"] hr {{
                border-color:
                    rgba(255, 255, 255, 0.24);
            }}

            [data-testid="stSidebar"]
            [data-testid="stImage"] {{
                background: transparent;
                border-radius: {RADIUS_MEDIUM};
                overflow: hidden;
            }}

            [data-testid="stSidebarCollapseButton"] button {{
                color: #FFFFFF;
            }}

            [data-testid="stSidebarCollapseButton"]
            [data-testid="stIconMaterial"] {{
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
               BOTONES GENERALES
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
                box-shadow:
                    0 5px 14px
                    rgba(40, 119, 126, 0.18);
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
                box-shadow:
                    0 8px 18px
                    rgba(23, 35, 63, 0.20);
            }}

            .stButton > button:focus,
            .stFormSubmitButton > button:focus {{
                color: #FFFFFF;
                box-shadow:
                    0 0 0 0.18rem
                    rgba(101, 190, 198, 0.25);
            }}

            .stButton > button:disabled,
            .stFormSubmitButton > button:disabled {{
                border-color: {COLOR_BORDER};
                background: #E8ECF2;
                color: #8791A0;
                box-shadow: none;
                transform: none;
                opacity: 0.82;
            }}

            .stButton > button p,
            .stFormSubmitButton > button p {{
                margin: 0;
                color: inherit;
                font-weight: inherit;
            }}

            /* =====================================================
               BOTONES DEL SIDEBAR
               ===================================================== */

            [data-testid="stSidebar"]
            .stButton > button {{
                border:
                    1px solid
                    rgba(255, 255, 255, 0.45);
                background:
                    rgba(255, 255, 255, 0.08);
                color: #FFFFFF;
                box-shadow: none;
            }}

            [data-testid="stSidebar"]
            .stButton > button:hover {{
                border-color: #FFFFFF;
                background:
                    rgba(255, 255, 255, 0.16);
                color: #FFFFFF;
            }}

            [data-testid="stSidebar"]
            .stButton > button p {{
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
                    0 0 0 0.18rem
                    rgba(101, 190, 198, 0.18);
            }}

            input,
            textarea {{
                color: {COLOR_TEXT_PRIMARY} !important;
                -webkit-text-fill-color:
                    {COLOR_TEXT_PRIMARY} !important;
            }}

            input::placeholder,
            textarea::placeholder {{
                color: {COLOR_TEXT_MUTED} !important;
                opacity: 1;
            }}

            [data-testid="stTextInput"]
            [data-testid="stIconMaterial"] {{
                color: {COLOR_TEXT_SECONDARY};
            }}

            /*
            El ícono de mostrar/ocultar contraseña debe conservar
            la fuente Material Symbols.
            */

            [data-testid="stTextInput"]
            button,
            [data-testid="stTextInput"]
            button span {{
                color: {COLOR_TEXT_PRIMARY};
            }}

            [data-testid="stTextInput"]
            button [data-testid="stIconMaterial"] {{
                font-family:
                    "Material Symbols Rounded" !important;
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

            [data-testid="stForm"] label {{
                color: {COLOR_TEXT_PRIMARY};
            }}

            /* =====================================================
               ALERTAS
               ===================================================== */

            [data-testid="stAlert"] {{
                border-radius: {RADIUS_MEDIUM};
                border-width: 1px;
                box-shadow: none;
            }}

            [data-testid="stAlert"] p {{
                margin: 0;
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

            [data-testid="stExpander"] summary {{
                color: {COLOR_TEXT_PRIMARY};
                font-weight: 650;
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
                border-radius:
                    {RADIUS_MEDIUM}
                    {RADIUS_MEDIUM}
                    0
                    0;
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
                min-height: 126px;
                padding: 1rem;
                border: 1px solid {COLOR_BORDER};
                border-radius: {RADIUS_MEDIUM};
                background: {COLOR_SURFACE};
                box-shadow: {SHADOW_SOFT};
            }}

            [data-testid="stMetricLabel"] {{
                color: {COLOR_TEXT_SECONDARY};
            }}

            [data-testid="stMetricValue"] {{
                color: {COLOR_TEXT_PRIMARY};
            }}

            /* =====================================================
               DIVISORES
               ===================================================== */

            [data-testid="stDivider"] {{
                border-color: {COLOR_BORDER};
            }}

            /* =====================================================
               BLOQUES DE CÓDIGO
               ===================================================== */

            /*
            No se altera el comportamiento de st.code.
            Esta regla solo evita desbordamientos.
            */

            [data-testid="stCodeBlock"] {{
                max-width: 100%;
                overflow-x: auto;
            }}

            /* =====================================================
               RESPONSIVE
               ===================================================== */

            @media (max-width: 900px) {{
                .block-container {{
                    padding-left: 1rem;
                    padding-right: 1rem;
                }}

                [data-testid="stSidebar"] {{
                    width: min(
                        {SIDEBAR_WIDTH},
                        88vw
                    );
                    min-width: min(
                        {SIDEBAR_WIDTH},
                        88vw
                    );
                }}
            }}

            @media (max-width: 600px) {{
                .block-container {{
                    padding-top: 1.25rem;
                    padding-bottom: 2rem;
                }}

                [data-testid="stMetric"] {{
                    min-height: auto;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
