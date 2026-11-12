"""Shared Line Check visual styling and logo."""

import streamlit as st

LOGO = """
<svg viewBox="0 0 64 64" role="img" aria-label="Line Check basketball logo">
  <circle cx="32" cy="32" r="27" fill="#e87524" stroke="#f6bd60" stroke-width="2"/>
  <path d="M8 32h48M32 5c-10 9-10 45 0 54M32 5c10 9 10 45 0 54M13 13l38 38M51 13 13 51"
        fill="none" stroke="#30231b" stroke-width="2"/>
  <path d="m23 32 6 6 13-14" fill="none" stroke="#fff4df" stroke-width="4"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def apply_global_styles() -> None:
    """Apply the shared dark hardwood theme and typography."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Oswald:wght@500;600;700&display=swap');
        :root { --court-orange: #e87524; --court-gold: #f6bd60; --court-cream: #fff4df; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        h1, h2, h3, [data-testid="stMetricValue"] {
            font-family: 'Oswald', sans-serif !important;
            letter-spacing: .02em;
        }
        [data-testid="stAppViewContainer"] {
            background:
              radial-gradient(ellipse at 50% 100%, rgba(232,117,36,.12), transparent 55%),
              repeating-linear-gradient(0deg, rgba(255,255,255,.012) 0 1px, transparent 1px 5px),
              linear-gradient(135deg, #111315 0%, #17191b 55%, #1d1713 100%);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #17191b, #211a15);
            border-right: 1px solid rgba(246,189,96,.18);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #e5dfd5;
        }
        .lc-brand { display:flex; align-items:center; gap:.7rem; margin:.25rem 0 1rem; }
        .lc-brand svg { width:48px; height:48px; flex:none; }
        .lc-brand span { font:600 1.55rem 'Oswald',sans-serif; color:#fff4df; letter-spacing:.04em; }
        .lc-kicker { color:#f6bd60; text-transform:uppercase; letter-spacing:.14em;
                     font-size:.78rem; font-weight:700; }
        .lc-card { border:1px solid rgba(246,189,96,.22); border-radius:14px;
                   padding:1.15rem 1.3rem; background:rgba(255,255,255,.035); }
        .lc-disclaimer { color:#c8c0b5; font-size:.78rem; line-height:1.45; }
        div.stButton > button[kind="primary"] {
            background:#e87524; border-color:#e87524; color:#151515; font-weight:700;
        }
        div.stButton > button[kind="primary"]:hover {
            background:#f6bd60; border-color:#f6bd60; color:#151515;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_logo() -> None:
    """Render the inline logo beside the app name."""
    st.markdown(
        f'<div class="lc-brand">{LOGO}<span>LINE CHECK</span></div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Show the shared brand, username control, and responsible-use note."""
    with st.sidebar:
        render_logo()
        st.caption("NBA odds & research")
        st.text_input(
            "Username",
            value="guest",
            key="username",
            help="Tags your saved bets. This is not a login or security feature.",
        )
        st.divider()
        st.markdown(
            '<p class="lc-disclaimer"><strong>Responsible use</strong><br>'
            "Line Check is for education and analysis only. It does not guarantee "
            "outcomes. Please bet responsibly and only where it is legal for you. "
            "You must be of legal betting age.</p>",
            unsafe_allow_html=True,
        )


def render_page_footer() -> None:
    """Display the shared educational disclaimer on the active page."""
    st.divider()
    st.caption(
        "Line Check is for education and analysis only. It does not guarantee "
        "outcomes. Please bet responsibly, only where legal, and only if you are "
        "of legal betting age."
    )
