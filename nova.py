import streamlit as st
import streamlit.components.v1 as components

import json
import re
import random
import os
from datetime import datetime, timedelta

# =========================================
# 1. PAGE CONFIG  (siempre primero)
# =========================================
st.set_page_config(
    page_title="Nova 🚀", page_icon="🚀",
    layout="wide", initial_sidebar_state="expanded"
)

# =========================================
# 2. SESSION STATE  (antes de todo lo demás)
# =========================================
LEVEL_NAMES = {1:"Starter Student",2:"Focused Learner",3:"Knowledge Builder",
               4:"Quiz Champion",5:"Academic Hero",6:"Master Mind"}
LEVEL_ICONS = {1:"🌱",2:"📖",3:"🔥",4:"🏆",5:"⚡",6:"💎"}
XP_THRESHOLDS = {1:0,2:25,3:60,4:100,5:150,6:200}
AVATARS = ["🦁","🐯","🦊","🐺","🦝","🐻","🐼","🐨","🐸","🦄","🐉","🦋"]

_DEFAULTS = {
    "active_user": None,
    "xp": 0, "level": 1,
    "total_quizzes": 0, "battle_wins": 0,
    "badges": [], "quiz_history": [],
    "weak_topics": {}, "exam_date": None, "exam_subject": "",
    "quiz": None, "last_score": None, "last_topic": "",
    "study_plan_days": [], "flashcards": [], "flash_revealed": {},
    "battle_state": None, "dark_mode": True,
    "streak_days": 0, "last_study_date": None,
    "leaderboard": [
        {"name":"Valeria M.","xp":340,"level":6},
        {"name":"Sebastián R.","xp":290,"level":5},
        {"name":"Isabella T.","xp":210,"level":4},
        {"name":"Mateo G.","xp":160,"level":3},
        {"name":"Camila V.","xp":90,"level":2},
    ]
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# =========================================
# 3. ESTILOS  (después de session_state)
# =========================================
def inject_styles(dark: bool):
    # ── PREMIUM PALETTE ────────────────────────────────────────────────────
    # Inspired by Linear / Vercel / Arc — deep indigo base, glass surfaces
    if dark:
        # Backgrounds — layered depth
        BG   = "#070611"          # void — deepest base
        SB   = "#050410"          # sidebar slightly darker
        CB   = "rgba(255,255,255,0.045)"   # glass card surface
        CBR  = "rgba(255,255,255,0.08)"    # card border
        QBG  = "rgba(255,255,255,0.035)"   # quiz box bg
        HBG  = "rgba(255,255,255,0.03)"    # history items
        MBG  = "rgba(124,58,237,0.12)"     # metric tile bg
        TIPBG= "rgba(124,58,237,0.10)"     # tip card bg
        PROFBG="rgba(255,255,255,0.045)"
        PROFBR="rgba(124,58,237,0.3)"
        WBG  = "rgba(239,68,68,0.08)"
        # Accent — vivid purple
        AC   = "#8b5cf6"          # primary purple
        AC2  = "#06b6d4"          # cyan secondary
        # Text hierarchy
        TM   = "#f0eeff"          # headings — very slightly purple-tinted
        TS   = "#8b87b8"          # body — muted lavender
        # Component-specific
        NG   = "linear-gradient(135deg,#4f46e5 0%,#7c3aed 60%,#9333ea 100%)"
        QB   = "#7c3aed"
        LG   = "linear-gradient(135deg,#064e3b,#065f46)"
        CERTBG="linear-gradient(135deg,#1c1400,#2d1f00)"; CERTBR="#d97706"; CERTC="#fbbf24"
        FBG  = "linear-gradient(135deg,rgba(79,46,220,0.2),rgba(124,58,237,0.15))"
        FTX  = "#c4b5fd"
        BP1  = "linear-gradient(135deg,rgba(37,99,235,0.12),rgba(29,78,216,0.06))"
        BP2  = "linear-gradient(135deg,rgba(220,38,38,0.12),rgba(185,28,28,0.06))"
        CDBG = "linear-gradient(135deg,#0a0915,#110e2a)"
        TIPC = "#c4b5fd"
        TI="☀️"; TL="Light"
    else:
        BG   = "#fafaf9"
        SB   = "#1a1730"
        CB   = "#ffffff"
        CBR  = "rgba(0,0,0,0.07)"
        QBG  = "#ffffff"
        HBG  = "#f9f8ff"
        MBG  = "rgba(124,58,237,0.07)"
        TIPBG= "rgba(124,58,237,0.07)"
        PROFBG="#ffffff"
        PROFBR="rgba(124,58,237,0.25)"
        WBG  = "rgba(239,68,68,0.06)"
        AC   = "#7c3aed"
        AC2  = "#0891b2"
        TM   = "#0f0d1a"
        TS   = "#6b6b8a"
        NG   = "linear-gradient(135deg,#4f46e5 0%,#7c3aed 60%,#9333ea 100%)"
        QB   = "#7c3aed"
        LG   = "linear-gradient(135deg,#065f46,#059669)"
        CERTBG="linear-gradient(135deg,#fef3c7,#fde68a)"; CERTBR="#f59e0b"; CERTC="#78350f"
        FBG  = "linear-gradient(135deg,#ede9fe,#ddd6fe)"
        FTX  = "#4c1d95"
        BP1  = "linear-gradient(135deg,#dbeafe,#bfdbfe)"
        BP2  = "linear-gradient(135deg,#fee2e2,#fecaca)"
        CDBG = "linear-gradient(135deg,#0f0d1a,#1a1730)"
        TIPC = "#5b21b6"
        TI="🌙"; TL="Dark"

    st.markdown(f"""
    <style>
    /* ── FONTS ─────────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..700;1,14..32,300..700&family=Syne:wght@600;700;800;900&display=swap');

    /* ── BASE ───────────────────────────────────────────────────────────── */
    html,body,[class*="css"] {{
        font-family:'Inter',system-ui,-apple-system,sans-serif;
        -webkit-font-smoothing:antialiased;
        -moz-osx-font-smoothing:grayscale;
    }}
    .stApp {{ background:{BG}!important; color:{TM}; }}

    /* ── HIDE STREAMLIT CHROME ──────────────────────────────────────────── */
    #MainMenu {{ visibility:hidden; }}
    footer    {{ visibility:hidden; }}
    header    {{ visibility:hidden; }}
    [data-testid="stToolbar"] {{ display:none; }}
    .block-container {{ padding-top:2rem!important; max-width:1100px!important; }}

    /* ── CUSTOM SCROLLBAR ───────────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width:6px; height:6px; }}
    ::-webkit-scrollbar-track {{ background:transparent; }}
    ::-webkit-scrollbar-thumb {{ background:rgba(124,58,237,0.3); border-radius:999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background:rgba(124,58,237,0.55); }}

    /* ── SIDEBAR ────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background:{SB}!important;
        border-right:1px solid rgba(255,255,255,0.05)!important;
    }}
    [data-testid="stSidebar"] * {{ color:rgba(255,255,255,0.75)!important; }}
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,[data-testid="stSidebar"] strong {{
        color:rgba(255,255,255,0.95)!important;
    }}
    [data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        border-radius:8px!important;
        padding:7px 12px!important;
        font-size:13px!important;
        font-weight:500!important;
        letter-spacing:-0.01em!important;
        transition:all 0.15s ease!important;
    }}
    [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
        background:rgba(139,92,246,0.15)!important;
        color:rgba(255,255,255,0.95)!important;
    }}

    /* ── TYPOGRAPHY ─────────────────────────────────────────────────────── */
    h1,h2,h3 {{
        font-family:'Syne',sans-serif!important;
        color:{TM}!important;
        letter-spacing:-0.025em!important;
    }}
    h1 {{ font-size:22px!important; font-weight:800!important; }}
    h2 {{ font-size:18px!important; font-weight:700!important; }}
    h3 {{ font-size:15px!important; font-weight:600!important; }}
    p,li,span {{ color:{TS}; font-size:14px; line-height:1.6; }}

    /* ── ANIMATED TITLE ─────────────────────────────────────────────────── */
    .main-title {{
        font-family:'Syne',sans-serif;
        font-size:clamp(32px,5vw,56px);
        font-weight:900;
        text-align:center;
        background:linear-gradient(135deg,#f0eeff 0%,{AC} 50%,#06b6d4 100%);
        background-size:200% auto;
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        background-clip:text;
        animation:shine 5s linear infinite;
        letter-spacing:-0.03em;
        line-height:1.1;
        margin-bottom:4px;
    }}
    @keyframes shine {{ to {{ background-position:200% center; }} }}
    .subtitle {{
        font-size:15px;
        text-align:center;
        color:{TS};
        margin-bottom:28px;
        font-weight:400;
        letter-spacing:-0.01em;
    }}

    /* ── GLASS CARDS ────────────────────────────────────────────────────── */
    .card {{
        background:{CB};
        color:{TM};
        padding:24px 28px;
        border-radius:16px;
        border:1px solid {CBR};
        backdrop-filter:blur(12px) saturate(1.4);
        -webkit-backdrop-filter:blur(12px) saturate(1.4);
        margin-bottom:16px;
        transition:border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
        animation:fadeUp 0.4s cubic-bezier(0.16,1,0.3,1) both;
    }}
    .card:hover {{
        border-color:rgba(139,92,246,0.25);
        box-shadow:0 8px 32px rgba(124,58,237,0.12);
        transform:translateY(-1px);
    }}
    .card p,.card h2,.card h3,.card span,.card li {{ color:{TM}!important; }}
    @keyframes fadeUp {{
        from {{ opacity:0; transform:translateY(12px); }}
        to   {{ opacity:1; transform:translateY(0);    }}
    }}

    /* ── NOVA HERO CARD ─────────────────────────────────────────────────── */
    .nova-card {{
        background:{NG};
        color:white;
        padding:22px 26px;
        border-radius:20px;
        box-shadow:0 12px 40px rgba(124,58,237,0.35),
                   inset 0 1px 0 rgba(255,255,255,0.15);
        margin-bottom:16px;
        position:relative;
        overflow:hidden;
        border:1px solid rgba(255,255,255,0.1);
    }}
    .nova-card::before {{
        content:'';
        position:absolute;
        top:-60px;right:-60px;
        width:180px;height:180px;
        background:radial-gradient(circle,rgba(255,255,255,0.12),transparent 70%);
        border-radius:50%;
        pointer-events:none;
    }}
    .nova-card::after {{
        content:'';
        position:absolute;
        bottom:-40px;left:20%;
        width:140px;height:140px;
        background:radial-gradient(circle,rgba(6,182,212,0.15),transparent 70%);
        border-radius:50%;
        pointer-events:none;
    }}
    .nova-face {{
        font-size:68px;
        text-align:center;
        filter:drop-shadow(0 4px 16px rgba(0,0,0,0.3));
        animation:float 3.5s ease-in-out infinite;
    }}
    @keyframes float {{
        0%,100% {{ transform:translateY(0) rotate(-2deg); }}
        50%      {{ transform:translateY(-8px) rotate(2deg); }}
    }}
    .nova-text {{
        font-family:'Syne',sans-serif;
        font-size:12px;
        font-weight:700;
        text-align:center;
        letter-spacing:0.08em;
        text-transform:uppercase;
        opacity:0.75;
        margin-top:6px;
    }}

    /* ── TIP CARD ───────────────────────────────────────────────────────── */
    .tip-card {{
        background:{TIPBG};
        color:{TIPC};
        padding:14px 18px;
        border-radius:12px;
        margin-bottom:16px;
        border-left:3px solid {AC};
        font-size:13px;
        line-height:1.6;
        font-weight:450;
        letter-spacing:-0.005em;
        backdrop-filter:blur(8px);
    }}
    .tip-card b {{ color:{TM}; font-weight:600; }}

    /* ── QUIZ CARDS ─────────────────────────────────────────────────────── */
    .quiz-box {{
        background:{QBG};
        color:{TM};
        padding:20px 24px;
        border-radius:14px;
        margin-bottom:10px;
        border:1px solid {CBR};
        border-left:4px solid {QB};
        backdrop-filter:blur(8px);
        transition:border-color 0.15s, box-shadow 0.15s;
        animation:fadeUp 0.35s cubic-bezier(0.16,1,0.3,1) both;
    }}
    .quiz-box:hover {{
        border-left-color:{AC2};
        box-shadow:0 4px 16px rgba(124,58,237,0.1);
    }}

    /* ── PROFILE CARD (login) ───────────────────────────────────────────── */
    .profile-card {{
        background:{PROFBG};
        border:1px solid {PROFBR};
        border-radius:18px;
        padding:22px 14px;
        text-align:center;
        cursor:pointer;
        transition:all 0.2s cubic-bezier(0.16,1,0.3,1);
        backdrop-filter:blur(12px);
    }}
    .profile-card:hover {{
        transform:translateY(-4px);
        box-shadow:0 16px 40px rgba(124,58,237,0.2);
        border-color:rgba(139,92,246,0.5);
    }}

    /* ── FLASHCARDS ─────────────────────────────────────────────────────── */
    .flashcard {{
        background:{FBG};
        color:{FTX};
        padding:36px 28px;
        border-radius:20px;
        text-align:center;
        min-height:170px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        cursor:pointer;
        border:1px solid rgba(139,92,246,0.2);
        transition:all 0.2s cubic-bezier(0.16,1,0.3,1);
        backdrop-filter:blur(8px);
    }}
    .flashcard:hover {{
        transform:scale(1.025) translateY(-2px);
        box-shadow:0 12px 32px rgba(124,58,237,0.2);
        border-color:rgba(139,92,246,0.4);
    }}

    /* ── HISTORY ITEMS ──────────────────────────────────────────────────── */
    .history-item {{
        background:{HBG};
        border:1px solid {CBR};
        color:{TM};
        padding:13px 18px;
        border-radius:11px;
        margin-bottom:6px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        font-size:14px;
        backdrop-filter:blur(8px);
        transition:all 0.15s ease;
    }}
    .history-item:hover {{
        border-color:rgba(139,92,246,0.25);
        transform:translateX(3px);
        background:rgba(139,92,246,0.05);
    }}

    /* ── BADGES ─────────────────────────────────────────────────────────── */
    .badge {{
        display:inline-flex;
        align-items:center;
        gap:4px;
        padding:4px 12px;
        border-radius:999px;
        font-size:12px;
        font-weight:600;
        letter-spacing:0.01em;
        margin:3px;
    }}
    .badge-gold   {{ background:linear-gradient(135deg,#f59e0b,#d97706);
                     color:white; box-shadow:0 2px 8px rgba(245,158,11,0.35); }}
    .badge-silver {{ background:linear-gradient(135deg,#94a3b8,#64748b); color:white; }}
    .badge-blue   {{ background:linear-gradient(135deg,#7c3aed,#4f46e5);
                     color:white; box-shadow:0 2px 8px rgba(124,58,237,0.35); }}
    .badge-green  {{ background:linear-gradient(135deg,#22c55e,#16a34a); color:white; }}

    /* ── XP BAR ─────────────────────────────────────────────────────────── */
    .xp-bar-outer {{
        background:rgba(139,92,246,0.12);
        border-radius:999px;
        height:5px;
        overflow:hidden;
        margin:8px 0 4px;
        border:none;
    }}

    /* ── METRIC TILES ───────────────────────────────────────────────────── */
    .metric-tile {{
        background:{MBG};
        border:1px solid rgba(139,92,246,0.15);
        border-radius:14px;
        padding:18px 20px;
        text-align:center;
        backdrop-filter:blur(8px);
        transition:all 0.2s ease;
    }}
    .metric-tile:hover {{
        border-color:rgba(139,92,246,0.3);
        box-shadow:0 4px 16px rgba(124,58,237,0.1);
    }}
    .metric-value {{
        font-family:'Syne',sans-serif;
        font-size:34px;
        font-weight:800;
        color:{AC};
        line-height:1.1;
        letter-spacing:-0.03em;
    }}
    .metric-label {{
        font-size:11px;
        color:{TS};
        text-transform:uppercase;
        letter-spacing:0.07em;
        margin-top:4px;
        font-weight:600;
    }}

    /* ── BATTLE ─────────────────────────────────────────────────────────── */
    .battle-p1 {{
        background:{BP1};
        border-radius:18px;
        padding:20px;
        text-align:center;
        border:1px solid rgba(59,130,246,0.2);
        backdrop-filter:blur(8px);
    }}
    .battle-p2 {{
        background:{BP2};
        border-radius:18px;
        padding:20px;
        text-align:center;
        border:1px solid rgba(239,68,68,0.2);
        backdrop-filter:blur(8px);
    }}
    .battle-score {{
        font-family:'Syne',sans-serif;
        font-size:52px;
        font-weight:900;
        letter-spacing:-0.03em;
        color:{TM};
    }}

    /* ── LEVEL BOX ──────────────────────────────────────────────────────── */
    .level-box {{
        background:{LG};
        color:white;
        padding:18px 24px;
        border-radius:16px;
        font-family:'Syne',sans-serif;
        font-size:20px;
        font-weight:800;
        text-align:center;
        box-shadow:0 8px 24px rgba(5,150,105,0.25);
        letter-spacing:-0.02em;
    }}

    /* ── CERTIFICATE ────────────────────────────────────────────────────── */
    .certificate {{
        background:{CERTBG};
        color:{CERTC};
        padding:40px;
        border-radius:24px;
        border:2px solid {CERTBR};
        text-align:center;
        font-family:'Syne',sans-serif;
        box-shadow:0 16px 48px rgba(217,119,6,0.2);
        animation:fadeUp 0.5s ease both;
    }}

    /* ── COUNTDOWN ──────────────────────────────────────────────────────── */
    .countdown-box {{
        background:{CDBG};
        color:white;
        padding:32px;
        border-radius:20px;
        text-align:center;
        border:1px solid rgba(139,92,246,0.15);
        box-shadow:0 8px 32px rgba(0,0,0,0.3);
    }}
    .countdown-number {{
        font-family:'Syne',sans-serif;
        font-size:80px;
        font-weight:900;
        color:{AC};
        line-height:1;
        letter-spacing:-0.04em;
        text-shadow:0 0 40px rgba(139,92,246,0.5);
    }}

    /* ── WEAK TOPIC ─────────────────────────────────────────────────────── */
    .weak-topic {{
        background:{WBG};
        border:1px solid rgba(239,68,68,0.15);
        border-radius:12px;
        padding:13px 16px;
        margin-bottom:8px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        backdrop-filter:blur(8px);
    }}

    /* ── STREAMLIT COMPONENTS ───────────────────────────────────────────── */
    /* Buttons */
    .stButton>button {{
        font-family:'Inter',sans-serif!important;
        font-weight:600!important;
        font-size:13px!important;
        letter-spacing:-0.01em!important;
        border-radius:10px!important;
        padding:9px 18px!important;
        transition:all 0.15s cubic-bezier(0.16,1,0.3,1)!important;
        border:none!important;
    }}
    .stButton>button:hover {{
        transform:translateY(-1px)!important;
        filter:brightness(1.1)!important;
        box-shadow:0 6px 20px rgba(124,58,237,0.3)!important;
    }}
    .stButton>button:active {{
        transform:translateY(0)!important;
        filter:brightness(0.95)!important;
    }}

    /* Inputs */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {{
        background:{CB}!important;
        color:{TM}!important;
        border:1px solid {CBR}!important;
        border-radius:10px!important;
        font-size:14px!important;
        font-family:'Inter',sans-serif!important;
        letter-spacing:-0.01em!important;
        backdrop-filter:blur(8px)!important;
        transition:border-color 0.15s!important;
    }}
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {{
        border-color:rgba(139,92,246,0.5)!important;
        box-shadow:0 0 0 3px rgba(139,92,246,0.12)!important;
    }}

    /* Radio */
    div[data-testid="stRadio"] label {{
        color:{TM}!important;
        font-size:14px!important;
        letter-spacing:-0.01em!important;
    }}

    /* Date input */
    .stDateInput>div>div>input {{
        background:{CB}!important;
        color:{TM}!important;
        border:1px solid {CBR}!important;
        border-radius:10px!important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        font-size:14px!important;
        font-weight:500!important;
        color:{TM}!important;
        background:{CB}!important;
        border-radius:10px!important;
        letter-spacing:-0.01em!important;
    }}

    /* Alerts */
    .stSuccess,.stInfo,.stWarning,.stError {{
        border-radius:10px!important;
        font-size:13px!important;
        font-family:'Inter',sans-serif!important;
    }}

    /* Spinner */
    .stSpinner>div {{ border-top-color:{AC}!important; }}

    /* Download button */
    .stDownloadButton>button {{
        font-family:'Inter',sans-serif!important;
        border-radius:10px!important;
        border:1px solid {CBR}!important;
        background:{CB}!important;
        font-size:13px!important;
        font-weight:600!important;
    }}
    .stDownloadButton>button:hover {{
        border-color:rgba(139,92,246,0.35)!important;
        color:{AC}!important;
    }}

    /* Divider */
    hr {{ border:none; border-top:1px solid {CBR}; margin:16px 0; }}
    [data-testid="stDivider"] {{ border-color:{CBR}; }}

    /* Caption */
    .stCaption {{ font-size:12px!important; color:{TS}!important; }}

    /* Mobile */
    @media(max-width:768px) {{
        .block-container {{ padding:12px 12px 40px!important; }}
        .main-title {{ font-size:32px!important; }}
        .nova-face  {{ font-size:52px!important; }}
    }}
    </style>
    """, unsafe_allow_html=True)
    return TI, TL

# Llamar estilos aquí — session_state ya existe
toggle_icon, toggle_label = inject_styles(st.session_state.dark_mode)

# =========================================
# 4. PERFILES — Supabase (online) + JSON fallback
# =========================================
PROFILES_FILE = "nova_profiles.json"

@st.cache_resource
def _supabase():
    try:
        from supabase import create_client
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

def _default_profile(name):
    return {"name":name,"xp":0,"level":1,"total_quizzes":0,"badges":[],
            "quiz_history":[],"weak_topics":{},"exam_date":None,
            "exam_subject":"","battle_wins":0,"streak_days":0,"last_study_date":None}

def load_profiles():
    db = _supabase()
    if db:
        try:
            rows = db.table("profiles").select("*").execute().data
            return {r["name"]: r["data"] for r in rows}
        except Exception:
            pass
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE) as f:
            return json.load(f)
    return {}

def save_user_profile(name, data):
    db = _supabase()
    if db:
        try:
            db.table("profiles").upsert({"name":name,"data":data},on_conflict="name").execute()
            return
        except Exception:
            pass
    profiles = load_profiles()
    profiles[name] = data
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

def activate_profile(name):
    profiles = load_profiles()
    p = profiles.get(name, _default_profile(name))
    st.session_state.active_user = name
    for k in ["xp","level","total_quizzes","badges","quiz_history",
               "weak_topics","exam_date","exam_subject","battle_wins",
               "streak_days","last_study_date"]:
        st.session_state[k] = p.get(k, _default_profile(name).get(k))

def sync_profile():
    name = st.session_state.get("active_user")
    if not name:
        return
    profiles = load_profiles()
    p = profiles.get(name, _default_profile(name))
    for k in ["xp","level","total_quizzes","badges","quiz_history",
               "weak_topics","exam_date","exam_subject","battle_wins",
               "streak_days","last_study_date"]:
        p[k] = st.session_state.get(k, p.get(k))
    save_user_profile(name, p)

def get_avatar(name):
    return AVATARS[sum(ord(c) for c in name) % len(AVATARS)]

# =========================================
# 5. SONIDOS — components.html() con height mínimo
#    El audio SÍ sale del iframe — es solo audio, no DOM
# =========================================
_SOUND_FREQS = {
    "correct":  ([523,659,784],       "sine",     0.12, 0.25),
    "wrong":    (None,                "sawtooth", 0,    0.20),
    "levelup":  ([392,523,659,784,1047],"sine",   0.13, 0.25),
    "perfect":  ([523,659,784,1047,1319],"triangle",0.15,0.28),
}

def play_sound(sound_type: str):
    if sound_type == "wrong":
        js = """
        var c=new(window.AudioContext||window.webkitAudioContext)();
        var o=c.createOscillator(),g=c.createGain();
        o.connect(g);g.connect(c.destination);
        o.type='sawtooth';
        o.frequency.setValueAtTime(280,c.currentTime);
        o.frequency.exponentialRampToValueAtTime(100,c.currentTime+0.38);
        g.gain.setValueAtTime(0.20,c.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.38);
        o.start(c.currentTime);o.stop(c.currentTime+0.42);
        """
    else:
        cfg = _SOUND_FREQS.get(sound_type)
        if not cfg:
            return
        freqs, wave, gap, vol = cfg
        notes = ";".join([
            f"(function(){{var o=c.createOscillator(),g=c.createGain();"
            f"o.connect(g);g.connect(c.destination);"
            f"o.type='{wave}';o.frequency.value={f};"
            f"g.gain.setValueAtTime({vol},c.currentTime+{i*gap});"
            f"g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+{i*gap+0.35});"
            f"o.start(c.currentTime+{i*gap});o.stop(c.currentTime+{i*gap+0.4});}})()"
            for i,f in enumerate(freqs)
        ])
        js = f"var c=new(window.AudioContext||window.webkitAudioContext)();{notes};"

    # height=0 — el iframe existe pero no ocupa espacio visual
    components.html(f"<script>{js}</script>", height=0)

# =========================================
# 6. ANIMACIONES — components.html()
#    El confetti corre DENTRO del iframe (tamaño mínimo visible)
#    Para verlo en pantalla completa usamos position:fixed + z-index alto
#    desde el iframe. Nota: algunos navegadores limitan esto.
# =========================================
def trigger_confetti():
    components.html("""
    <style>
    *{margin:0;padding:0;}
    @keyframes fall{
        0%  {transform:translateY(-10px) rotate(0deg);   opacity:1;}
        100%{transform:translateY(300px) rotate(720deg); opacity:0;}
    }
    .piece{position:absolute;border-radius:3px;animation:fall linear forwards;}
    </style>
    <div id="box" style="position:relative;width:100%;height:300px;overflow:hidden;pointer-events:none;">
    </div>
    <script>
    var box=document.getElementById('box');
    var colors=['#38bdf8','#818cf8','#34d399','#f59e0b','#f472b6','#ffffff','#a78bfa'];
    for(var i=0;i<80;i++){
        (function(i){
            setTimeout(function(){
                var el=document.createElement('div');
                el.className='piece';
                var size=(Math.random()*10+5)+'px';
                el.style.cssText=[
                    'width:'+size,'height:'+size,
                    'left:'+(Math.random()*100)+'%',
                    'top:-10px',
                    'background:'+colors[Math.floor(Math.random()*colors.length)],
                    'border-radius:'+(Math.random()>.5?'50%':'3px'),
                    'animation-duration:'+(Math.random()*2+1.5)+'s',
                    'animation-delay:'+(Math.random()*0.5)+'s'
                ].join(';');
                box.appendChild(el);
            }, i*20);
        })(i);
    }
    </script>
    """, height=300)   # height=300 para que el confetti sea visible

def trigger_level_up_banner(level_name: str):
    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    @keyframes pop{{
        0%  {{transform:scale(0);  opacity:0;}}
        60% {{transform:scale(1.1);opacity:1;}}
        100%{{transform:scale(1);  opacity:1;}}
    }}
    @keyframes go{{
        0%  {{opacity:1;}}
        100%{{opacity:0;transform:scale(0.8);}}
    }}
    #banner{{
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        height:220px;
        background:linear-gradient(135deg,#1a56db,#0ea5e9);
        color:white;border-radius:24px;
        box-shadow:0 12px 48px rgba(26,86,219,0.5);
        font-family:sans-serif;
        animation:pop 0.5s cubic-bezier(0.175,0.885,0.32,1.275) forwards;
    }}
    .icon{{font-size:56px;margin-bottom:8px;}}
    .title{{font-size:28px;font-weight:900;letter-spacing:2px;}}
    .sub{{font-size:18px;opacity:0.9;margin-top:6px;}}
    </style>
    <div id="banner">
        <div class="icon">⚡</div>
        <div class="title">LEVEL UP!</div>
        <div class="sub">{level_name}</div>
    </div>
    <script>
    setTimeout(function(){{
        var b=document.getElementById('banner');
        b.style.animation='go 0.4s ease forwards';
    }},2400);
    </script>
    """, height=240)

# =========================================
# 7. TIPS DEL DÍA
# =========================================
_TIPS = [
    "🧠 Study in short 25-min sessions with 5-min breaks. Your brain retains more!",
    "✍️ Writing notes by hand improves memory more than typing.",
    "🔄 Review material within 24 hours to boost retention by up to 80%.",
    "🎯 Test yourself before studying — it primes your brain to absorb more.",
    "😴 Sleep consolidates memories. Don't sacrifice it before an exam.",
    "🗣️ Explain concepts out loud as if teaching someone else.",
    "📅 20 minutes of daily study beats last-minute cramming every time.",
    "🌊 Switching between topics strengthens both faster than single-subject blocks.",
    "💧 Staying hydrated improves focus and working memory.",
    "🎵 Instrumental music (no lyrics) can help maintain focus.",
    "📊 Mind maps are great for connecting concepts visually.",
    "🤔 Ask 'why' and 'how', not just 'what'. Deep questions = deep learning.",
]
def daily_tip():
    return _TIPS[datetime.now().timetuple().tm_yday % len(_TIPS)]

# =========================================
# 8. BADGES
# =========================================
BADGE_RULES = [
    {"id":"first_quiz",   "label":"First Quiz",      "icon":"🎯","cls":"badge-blue",
     "cond": lambda: st.session_state.get("total_quizzes",0) >= 1},
    {"id":"perfect",      "label":"Perfect Score",   "icon":"⭐","cls":"badge-gold",
     "cond": lambda: st.session_state.get("last_score") == 5},
    {"id":"five_quizzes", "label":"Quiz Veteran",    "icon":"🏅","cls":"badge-silver",
     "cond": lambda: st.session_state.get("total_quizzes",0) >= 5},
    {"id":"level3",       "label":"Level 3",         "icon":"🔥","cls":"badge-green",
     "cond": lambda: st.session_state.get("level",1) >= 3},
    {"id":"battle_win",   "label":"Battle Winner",   "icon":"⚔️","cls":"badge-gold",
     "cond": lambda: st.session_state.get("battle_wins",0) >= 1},
    {"id":"master",       "label":"Master Mind",     "icon":"💎","cls":"badge-gold",
     "cond": lambda: st.session_state.get("level",1) >= 6},
]

def update_streak():
    """Racha de estudio diaria — solo cuenta una vez por día."""
    today = datetime.now().strftime("%Y-%m-%d")
    last  = st.session_state.get("last_study_date")
    if last == today:
        return
    if last:
        yesterday = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
        st.session_state.streak_days = (
            st.session_state.get("streak_days",0) + 1 if last == yesterday else 1
        )
    else:
        st.session_state.streak_days = 1
    st.session_state.last_study_date = today

def update_level_and_badges():
    update_streak()
    xp = st.session_state.xp
    prev = st.session_state.level
    for lvl in sorted(XP_THRESHOLDS.keys(), reverse=True):
        if xp >= XP_THRESHOLDS[lvl]:
            st.session_state.level = lvl
            break
    if st.session_state.level > prev:
        play_sound("levelup")
        trigger_level_up_banner(LEVEL_NAMES[st.session_state.level])
    for badge in BADGE_RULES:
        if badge["id"] not in st.session_state.badges and badge["cond"]():
            st.session_state.badges.append(badge["id"])
    sync_profile()

def xp_progress():
    cur = st.session_state.level
    if cur >= 6:
        return st.session_state.xp, 200, 200
    nt = XP_THRESHOLDS[cur+1]; ct = XP_THRESHOLDS[cur]
    return st.session_state.xp - ct, nt - ct, nt

def nova_mood(score=None):
    if score is None: return "🤖","Hi! I'm Nova, your AI study partner. Let's learn something!"
    if score == 5:    return "😎","Perfect score! You absolutely crushed it! 🎉"
    if score >= 3:    return "🙂","Good job! Review the ones you missed and try again."
    return "🤔","Mistakes help your brain grow. Let's review and come back stronger!"

# =========================================
# =========================================
# 9. AI — Groq API (Llama 3.1, free, online)
# =========================================
def _chat(system, user, max_tokens=900):
    from groq import Groq
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        max_tokens=max_tokens, temperature=0.7,
    )
    return r.choices[0].message.content

def ask_ai(question):
    return _chat(
        "You are Nova, an expert academic tutor. Structure each answer:\n"
        "1. One-sentence definition.\n"
        "2. Real-world analogy (start: 'Think of it like...').\n"
        "3. Concrete example with numbers or facts.\n"
        "4. Memory tip (start: 'To remember: ...').\n"
        "Keep sections 2-3 sentences. Natural paragraphs only.",
        question
    )

def generate_quiz(topic):
    try:
        text = _chat(
            'Create a quiz. Return ONLY valid JSON, nothing else:\n'
            '{"questions":[{"question":"...","options":["A","B","C","D"],'
            '"answer_index":0,"explanation":"...","difficulty":"easy"}]}\n'
            "Rules: 5 questions. 2 easy, 2 medium, 1 hard. 4 options. answer_index 0-3.",
            f"Topic: {topic}", max_tokens=1200
        )
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group())
        qs = []
        for q in data["questions"]:
            opts = q["options"]; ai = int(q["answer_index"])
            if len(opts) != 4 or not (0 <= ai <= 3): continue
            correct = opts[ai]; random.shuffle(opts)
            qs.append({"question":q["question"],"options":opts,"answer":correct,
                       "explanation":q.get("explanation",""),"difficulty":q.get("difficulty","medium")})
        return qs if qs else _quiz_fallback(topic)
    except:
        return _quiz_fallback(topic)

def _quiz_fallback(topic):
    return [{"question":f"Best way to study {topic}?",
             "options":["Practice examples","Ignore it","Read once","Never review"],
             "answer":"Practice examples","explanation":"Active practice reinforces memory.",
             "difficulty":"easy"}]

def generate_flashcards(topic):
    try:
        text = _chat(
            'Create 6 flashcards. Return ONLY valid JSON:\n'
            '{"cards":[{"term":"...","definition":"..."}]}\n'
            "6 cards. term: 1-4 words. definition: 1-2 sentences.",
            f"Topic: {topic}"
        )
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(m.group())["cards"]
    except:
        return [{"term":f"{topic} {i+1}","definition":"Review this concept."} for i in range(6)]

def generate_study_plan(topic):
    try:
        text = _chat(
            'Create a 5-day study plan. Return ONLY valid JSON:\n'
            '{"days":[{"day":"Day 1","title":"...","task":"...","resource":"..."}]}\n'
            "5 days. Practical tasks. Free online resources.",
            f"Topic: {topic}"
        )
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(m.group())["days"]
    except:
        return [{"day":f"Day {i+1}","title":f"Session {i+1}",
                 "task":f"Study {topic}.","resource":"Khan Academy"} for i in range(5)]
# 10. UTILIDADES
# =========================================
def diff_badge(d):
    c = {"easy":"#22c55e","medium":"#f59e0b","hard":"#ef4444"}.get(d,"#94a3b8")
    l = {"easy":"Easy","medium":"Medium","hard":"Hard"}.get(d,d.capitalize())
    return f"<span style='background:{c};color:white;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;'>{l}</span>"

def rec(score, topic):
    if score==5: return f"🌟 Excellent! You've mastered **{topic}**."
    if score>=3: return f"📈 Good progress on **{topic}**. Review wrong answers and try again."
    return f"📚 Review **{topic}** with Nova Tutor first, then retake."

def create_ics(days):
    today = datetime.now()
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//NexusLearn//EN\n"
    for i,d in enumerate(days):
        s = (today+timedelta(days=i)).replace(hour=17,minute=0,second=0)
        e = s.replace(hour=17,minute=45)
        ics += (f"BEGIN:VEVENT\nSUMMARY:NexusLearn — {d.get('title','Study')}\n"
                f"DESCRIPTION:{d.get('task','')}\\nResource: {d.get('resource','')}\n"
                f"DTSTART:{s.strftime('%Y%m%dT%H%M%S')}\n"
                f"DTEND:{e.strftime('%Y%m%dT%H%M%S')}\nEND:VEVENT\n")
    return ics + "END:VCALENDAR"

def update_weak_topics(topic, score, total):
    pct = round(score/total*100)
    st.session_state.weak_topics.setdefault(topic,[]).append(pct)
    st.session_state.weak_topics[topic] = st.session_state.weak_topics[topic][-10:]

def get_weak_topics():
    return sorted(
        [{"topic":t,"avg":round(sum(s)/len(s)),"attempts":len(s)}
         for t,s in st.session_state.weak_topics.items()],
        key=lambda x: x["avg"])

# =========================================
# 11. PANTALLA DE LOGIN
#     Sin st.stop() — estructura if/else pura
# =========================================
if not st.session_state.active_user:

    st.markdown("<div class='main-title'>🚀 Nova</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Who's studying today?</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    profiles = load_profiles()

    if profiles:
        st.markdown("### 👤 Select your profile")
        # Usamos columnas de Streamlit — más confiable que CSS grid en el login
        num_cols = min(len(profiles), 4)
        cols = st.columns(num_cols)
        for i, (name, data) in enumerate(profiles.items()):
            with cols[i % num_cols]:
                av  = get_avatar(name)
                lvl = data.get("level", 1)
                xp  = data.get("xp", 0)
                # Mostrar card visual
                st.markdown(
                    f"<div class='profile-card'>"
                    f"<div style='font-size:52px;'>{av}</div>"
                    f"<div style='font-family:Syne,sans-serif;font-weight:800;"
                    f"font-size:18px;margin-top:10px;'>{name}</div>"
                    f"<div style='font-size:13px;opacity:0.65;margin-top:4px;'>"
                    f"{LEVEL_ICONS.get(lvl,'')} Lv{lvl} · {xp} XP</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                # Botón Streamlit nativo (100% funcional)
                if st.button(f"▶ Play as {name}", key=f"login_{name}",
                             use_container_width=True):
                    activate_profile(name)
                    st.rerun()

        st.markdown("---")

    st.markdown("### ✨ Create new profile")
    col_inp, col_btn = st.columns([3, 1])
    with col_inp:
        new_name = st.text_input(
            "name_input", label_visibility="collapsed",
            placeholder="Enter your name, e.g. Valeria, Mateo..."
        )
    with col_btn:
        if st.button("Create ➜", type="primary", use_container_width=True):
            nm = new_name.strip()
            if nm:
                activate_profile(nm)
                st.rerun()
            else:
                st.warning("Please enter a name.")

# =========================================
# 12. APP PRINCIPAL
# =========================================
else:
    user_name   = st.session_state.active_user
    user_avatar = get_avatar(user_name)

    # Header
    st.markdown("<div class='main-title'>🚀 Nova</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Your AI-powered study partner</div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([4,1,4])
    with c2:
        if st.button(f"{toggle_icon} {toggle_label}"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    # Tip del día
    st.markdown(
        f"<div class='tip-card'>💡 <b>Nova's Tip of the Day:</b> {daily_tip()}</div>",
        unsafe_allow_html=True
    )

    # Nova mascot + XP bar
    emoji, msg = nova_mood(st.session_state.get("last_score"))
    xp_now, xp_range, _ = xp_progress()
    pct = int(min(xp_now / max(xp_range, 1), 1.0) * 100)
    lvl_icon = LEVEL_ICONS.get(st.session_state.level, "🌱")
    lvl_name = LEVEL_NAMES.get(st.session_state.level, "Student")

    cm, cs = st.columns([1, 3])
    with cm:
        st.markdown(
            f"<div class='nova-card'><div class='nova-face'>{emoji}</div>"
            f"<div class='nova-text'>Nova AI</div></div>",
            unsafe_allow_html=True
        )
    with cs:
        st.markdown(f"""
        <div class='nova-card'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                <h2 style='color:white;margin:0;'>Nova says:</h2>
                <span style='font-size:20px;'>{user_avatar}
                    <b style='color:white;'>{user_name}</b></span>
            </div>
            <p style='font-size:17px;font-weight:500;color:rgba(255,255,255,0.95);'>{msg}</p>
            <div style='margin-top:12px;'>
                <span style='font-size:13px;opacity:0.85;'>{lvl_icon} Level {st.session_state.level}
                — {lvl_name} &nbsp;·&nbsp; {st.session_state.xp} XP</span>
                <div class='xp-bar-outer'>
                    <div style='height:100%;width:{pct}%;
                    background:linear-gradient(90deg,#a5f3fc,#818cf8);
                    border-radius:999px;'></div>
                </div>
                <span style='font-size:12px;opacity:0.7;'>{xp_now}/{xp_range} XP to next level</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown(f"## {user_avatar} {user_name}")
    st.sidebar.markdown(
        f"{lvl_icon} **{lvl_name}**  \n"
        f"XP: **{st.session_state.xp}** · Quizzes: **{st.session_state.total_quizzes}**"
    )
    if st.sidebar.button("🚪 Switch Profile"):
        st.session_state.active_user = None
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ⚡ Navigation")
    page = st.sidebar.radio("", [
        "🏠 Home", "🤖 Nova Tutor", "🎯 Quiz Arena",
        "⚔️ Battle Mode", "🃏 Flashcards", "📅 Study Plan",
        "📉 Weak Topics", "⏰ Exam Countdown",
        "🏆 Progress", "🥇 Leaderboard", "📝 About"
    ])

    # ── HOME ────────────────────────────────────────────
    if page == "🏠 Home":
        st.markdown(f"""
        <div class='card'>
            <h2>Welcome back, {user_name}! 👋</h2>
            <p>Practice quizzes, review flashcards, challenge a friend in Battle Mode,
            track weak topics, and set an exam countdown.</p>
        </div>""", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        for col,(icon,title,desc) in zip([c1,c2,c3,c4],[
            ("🤖","Nova Tutor","AI explanations on any topic."),
            ("🎯","Quiz Arena","Practice and earn XP."),
            ("⚔️","Battle Mode","Quiz duel with a friend!"),
            ("📉","Weak Topics","See where to improve.")]):
            with col:
                st.markdown(
                    f"<div class='card' style='text-align:center;'>"
                    f"<div style='font-size:36px;'>{icon}</div>"
                    f"<h3 style='margin:8px 0 4px;'>{title}</h3>"
                    f"<p style='font-size:13px;'>{desc}</p></div>",
                    unsafe_allow_html=True)

        if st.session_state.quiz_history:
            st.markdown("### 📋 Recent Activity")
            for e in reversed(st.session_state.quiz_history[-3:]):
                ps = int(e["score"]/e["total"]*100)
                bc = "#22c55e" if ps>=80 else "#f59e0b" if ps>=60 else "#ef4444"
                st.markdown(
                    f"<div class='history-item'>"
                    f"<span>📚 <b>{e['topic']}</b></span>"
                    f"<span>{e['score']}/{e['total']}</span>"
                    f"<span style='color:{bc};font-weight:700;'>{ps}%</span>"
                    f"<span style='color:#818cf8;'>+{e['xp']} XP</span>"
                    f"<span style='opacity:0.6;font-size:13px;'>{e['date']}</span>"
                    f"</div>", unsafe_allow_html=True)

        if st.session_state.exam_date:
            try:
                exam = datetime.strptime(st.session_state.exam_date, "%Y-%m-%d")
                dl = (exam - datetime.now()).days
                if dl >= 0:
                    st.markdown(
                        f"<div class='card' style='text-align:center;'>"
                        f"<h3>⏰ {st.session_state.exam_subject or 'Upcoming Exam'}</h3>"
                        f"<div style='font-size:48px;font-family:Syne,sans-serif;"
                        f"font-weight:900;color:#38bdf8;'>{dl}</div>"
                        f"<p>days remaining</p></div>", unsafe_allow_html=True)
            except: pass

    # ── NOVA TUTOR ──────────────────────────────────────
    elif page == "🤖 Nova Tutor":
        st.header("🤖 Ask Nova Tutor")
        q = st.text_area("Your question:", placeholder="e.g. Explain photosynthesis simply.", height=100)
        cb1, cb2 = st.columns([1,3])
        with cb1: go = st.button("✨ Explain", type="primary")
        with cb2: st.caption("💡 Try: 'Newton's laws', 'What causes earthquakes?'")
        if go:
            if not q.strip(): st.warning("Please write a question.")
            else:
                with st.spinner("Nova is thinking..."):
                    answer = ask_ai(q)
                st.markdown(
                    f"<div class='card'><h3>Nova's Explanation</h3>"
                    f"<p style='line-height:1.9;'>{answer.replace(chr(10),'<br>')}</p></div>",
                    unsafe_allow_html=True)
                st.success("💡 Want to practice? Go to **Quiz Arena**!")

    # ── QUIZ ARENA ──────────────────────────────────────
    elif page == "🎯 Quiz Arena":
        st.header("🎯 Quiz Arena")
        topic = st.text_input("Topic:", placeholder="e.g. photosynthesis, fractions, WWII...")
        if st.button("🎲 Generate Quiz", type="primary"):
            if not topic.strip(): st.warning("Please enter a topic.")
            else:
                with st.spinner("Generating..."):
                    st.session_state.quiz = generate_quiz(topic)
                    st.session_state.last_topic = topic
                    st.session_state.last_score = None

        if st.session_state.quiz:
            answers = {}
            for i, q in enumerate(st.session_state.quiz):
                st.markdown(
                    f"<div class='quiz-box'>"
                    f"<div style='display:flex;justify-content:space-between;"
                    f"align-items:center;margin-bottom:10px;'>"
                    f"<span style='font-family:Syne,sans-serif;font-weight:800;font-size:17px;'>"
                    f"Question {i+1}</span>{diff_badge(q.get('difficulty','medium'))}</div>"
                    f"<p style='font-size:17px;font-weight:500;'>{q['question']}</p></div>",
                    unsafe_allow_html=True)
                answers[i] = st.radio("", q["options"], key=f"q_{i}", label_visibility="collapsed")

            if st.button("✅ Submit Answers", type="primary"):
                score = sum(1 for i,q in enumerate(st.session_state.quiz) if answers[i]==q["answer"])
                st.session_state.last_score = score
                st.session_state.total_quizzes += 1
                gained = score*10 + (20 if score==5 else 0)
                st.session_state.xp += gained
                st.session_state.quiz_history.append({
                    "topic": st.session_state.last_topic, "score": score,
                    "total": len(st.session_state.quiz), "xp": gained,
                    "date": datetime.now().strftime("%b %d, %H:%M")
                })
                update_weak_topics(st.session_state.last_topic, score, len(st.session_state.quiz))
                update_level_and_badges()   # sincroniza perfil

                # Sonido + animación
                if score == len(st.session_state.quiz):
                    play_sound("perfect")
                    trigger_confetti()
                elif score >= 3:
                    play_sound("correct")
                else:
                    play_sound("wrong")

                st.markdown(
                    f"<div class='card' style='text-align:center;'>"
                    f"<h2>Score: {score} / {len(st.session_state.quiz)}</h2>"
                    f"<p style='font-size:18px;'>You earned <b>+{gained} XP</b>"
                    f"{'  🎉 (+20 bonus!)' if score==5 else ''}</p></div>",
                    unsafe_allow_html=True)
                st.info(rec(score, st.session_state.last_topic))

                st.subheader("📋 Detailed Results")
                for i, q in enumerate(st.session_state.quiz):
                    ok = answers[i] == q["answer"]
                    with st.expander(f"{'✅' if ok else '❌'} Q{i+1}: {q['question'][:55]}..."):
                        if ok: st.success(f"Correct! {answers[i]}")
                        else:
                            st.error(f"Your answer: {answers[i]}")
                            st.success(f"Correct: {q['answer']}")
                        if q.get("explanation"): st.info(f"💡 {q['explanation']}")

                if score == len(st.session_state.quiz):
                    st.markdown(
                        f"<div class='certificate'>"
                        f"<div style='font-size:64px;'>🏆</div><h1>Certificate of Achievement</h1>"
                        f"<p style='font-size:18px;'>Perfect score on <b>{st.session_state.last_topic}</b></p>"
                        f"<p>Earned by: <b>{user_name}</b></p>"
                        f"<p style='font-size:14px;opacity:0.7;'>"
                        f"{datetime.now().strftime('%B %d, %Y')}</p></div>",
                        unsafe_allow_html=True)

    # ── BATTLE MODE ─────────────────────────────────────
    elif page == "⚔️ Battle Mode":
        st.header("⚔️ Quiz Battle Mode")
        st.markdown(
            "<div class='card'><p>Two players answer the same quiz. "
            "Most correct answers wins! 🏆</p></div>", unsafe_allow_html=True)

        if not st.session_state.battle_state:
            c1, c2 = st.columns(2)
            with c1: p1 = st.text_input("Player 1:", value=user_name, key="bp1")
            with c2: p2 = st.text_input("Player 2:", placeholder="Enter name...", key="bp2")
            bt = st.text_input("Topic:", placeholder="e.g. biology, history...")
            if st.button("⚔️ Start Battle!", type="primary"):
                if not p2.strip() or not bt.strip():
                    st.warning("Enter Player 2 name and topic.")
                else:
                    with st.spinner("Generating battle quiz..."):
                        bq = generate_quiz(bt)
                    st.session_state.battle_state = {
                        "players":[p1,p2], "topic":bt, "quiz":bq,
                        "phase":1, "scores":{1:0, 2:0}
                    }
                    st.rerun()
        else:
            bs = st.session_state.battle_state
            players = bs["players"]; phase = bs["phase"]; quiz = bs["quiz"]

            # Scoreboard
            c1, cv, c2 = st.columns([2,1,2])
            with c1:
                st.markdown(f"<div class='battle-p1'>"
                            f"<div style='font-size:18px;font-weight:800;'>🔵 {players[0]}</div>"
                            f"<div class='battle-score'>{bs['scores'][1]}</div></div>",
                            unsafe_allow_html=True)
            with cv:
                st.markdown("<div style='text-align:center;padding-top:24px;"
                            "font-family:Syne,sans-serif;font-size:28px;font-weight:900;'>VS</div>",
                            unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='battle-p2'>"
                            f"<div style='font-size:18px;font-weight:800;'>🔴 {players[1]}</div>"
                            f"<div class='battle-score'>{bs['scores'][2]}</div></div>",
                            unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            if phase in [1, 2]:
                cur = players[phase-1]
                col_icon = "🔵" if phase==1 else "🔴"
                st.markdown(f"### {col_icon} {cur}'s Turn")
                st.info(f"Only **{cur}** should look now. Other player, look away! 👀")
                pa = {}
                for i, q in enumerate(quiz):
                    st.markdown(
                        f"<div class='quiz-box'>"
                        f"<div style='display:flex;justify-content:space-between;margin-bottom:8px;'>"
                        f"<span style='font-family:Syne,sans-serif;font-weight:800;'>Q{i+1}</span>"
                        f"{diff_badge(q.get('difficulty','medium'))}</div>"
                        f"<p style='font-size:16px;font-weight:500;'>{q['question']}</p></div>",
                        unsafe_allow_html=True)
                    pa[i] = st.radio("", q["options"], key=f"bt_{phase}_{i}",
                                     label_visibility="collapsed")
                if st.button(f"✅ Submit {cur}'s Answers", type="primary"):
                    sc = sum(1 for i,q in enumerate(quiz) if pa[i]==q["answer"])
                    bs["scores"][phase] = sc
                    bs["phase"] = phase + 1
                    play_sound("correct" if sc >= 3 else "wrong")
                    st.rerun()

            elif phase == 3:
                s1=bs["scores"][1]; s2=bs["scores"][2]; total=len(quiz)
                st.markdown("## 🏆 Battle Results!")
                if s1 > s2:
                    winner = players[0]; st.session_state.battle_wins += 1
                    play_sound("perfect"); trigger_confetti()
                elif s2 > s1:
                    winner = players[1]
                    play_sound("perfect"); trigger_confetti()
                else:
                    winner = None; play_sound("correct")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"<div class='battle-p1' style='padding:28px;'>"
                                f"<div style='font-size:20px;font-weight:800;'>🔵 {players[0]}</div>"
                                f"<div class='battle-score'>{s1}/{total}</div>"
                                f"<div>{int(s1/total*100)}%</div></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='battle-p2' style='padding:28px;'>"
                                f"<div style='font-size:20px;font-weight:800;'>🔴 {players[1]}</div>"
                                f"<div class='battle-score'>{s2}/{total}</div>"
                                f"<div>{int(s2/total*100)}%</div></div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                if winner:
                    st.markdown(
                        f"<div class='certificate'>"
                        f"<div style='font-size:56px;'>⚔️</div><h1>Battle Winner</h1>"
                        f"<h2>{winner}</h2>"
                        f"<p>Won with {max(s1,s2)}/{total} correct answers!</p></div>",
                        unsafe_allow_html=True)
                    update_level_and_badges()
                else:
                    st.markdown("<div class='card' style='text-align:center;'>"
                                "<div style='font-size:48px;'>🤝</div><h2>It's a Tie!</h2></div>",
                                unsafe_allow_html=True)

                with st.expander("📋 Correct answers"):
                    for i, q in enumerate(quiz):
                        st.write(f"**Q{i+1}:** {q['question']}")
                        st.success(f"✅ {q['answer']}")
                        if q.get("explanation"): st.info(f"💡 {q['explanation']}")

                if st.button("🔄 New Battle", type="primary"):
                    st.session_state.battle_state = None; st.rerun()

    # ── FLASHCARDS ──────────────────────────────────────
    elif page == "🃏 Flashcards":
        st.header("🃏 Flashcards")
        topic = st.text_input("Topic:", placeholder="e.g. mitosis, French Revolution...")
        if st.button("🃏 Generate", type="primary"):
            if not topic.strip(): st.warning("Please enter a topic.")
            else:
                with st.spinner("Creating flashcards..."):
                    st.session_state.flashcards = generate_flashcards(topic)
                    st.session_state.flash_revealed = {}
        if st.session_state.flashcards:
            if st.button("🔄 Reset All"):
                st.session_state.flash_revealed = {}; st.rerun()
            cols = st.columns(2)
            for idx, card in enumerate(st.session_state.flashcards):
                with cols[idx % 2]:
                    rev = st.session_state.flash_revealed.get(idx, False)
                    if rev:
                        st.markdown(
                            f"<div class='flashcard' style='background:linear-gradient(135deg,#065f46,#10b981);color:white;'>"
                            f"<div style='font-size:13px;letter-spacing:1px;text-transform:uppercase;"
                            f"opacity:0.8;margin-bottom:8px;'>DEFINITION</div>"
                            f"<div style='font-size:18px;font-weight:600;line-height:1.5;'>"
                            f"{card['definition']}</div></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f"<div class='flashcard'>"
                            f"<div style='font-size:13px;letter-spacing:1px;text-transform:uppercase;"
                            f"opacity:0.6;margin-bottom:8px;'>TERM</div>"
                            f"<div style='font-size:24px;font-weight:800;font-family:Syne,sans-serif;'>"
                            f"{card['term']}</div>"
                            f"<div style='font-size:13px;opacity:0.6;margin-top:10px;'>Tap to reveal ↓</div>"
                            f"</div>", unsafe_allow_html=True)
                    if st.button("🙈 Hide" if rev else "👁 Reveal", key=f"fl_{idx}"):
                        st.session_state.flash_revealed[idx] = not rev; st.rerun()

    # ── STUDY PLAN ──────────────────────────────────────
    elif page == "📅 Study Plan":
        st.header("📅 AI Study Plan")
        topic = st.text_input("Topic:", placeholder="e.g. algebra, photosynthesis...")
        if st.button("📅 Generate Plan", type="primary"):
            if not topic.strip(): st.warning("Please enter a topic.")
            else:
                with st.spinner("Creating plan..."):
                    st.session_state.study_plan_days = generate_study_plan(topic)
        if st.session_state.study_plan_days:
            icons = ["🌱","📖","✏️","🔍","🏆"]
            for i, d in enumerate(st.session_state.study_plan_days):
                res = d.get("resource","")
                st.markdown(
                    f"<div class='card'>"
                    f"<div style='display:flex;align-items:center;gap:12px;margin-bottom:8px;'>"
                    f"<span style='font-size:32px;'>{icons[i] if i<5 else '📌'}</span>"
                    f"<div><h3 style='margin:0;'>{d.get('day','Day')}: {d.get('title','')}</h3>"
                    f"{'<span style=\"font-size:13px;opacity:0.7;\">📌 '+res+'</span>' if res else ''}"
                    f"</div></div><p>{d.get('task','')}</p></div>",
                    unsafe_allow_html=True)
            st.download_button(
                "📥 Download Calendar (.ics)",
                data=create_ics(st.session_state.study_plan_days),
                file_name="nova_plan.ics", mime="text/calendar")

    # ── WEAK TOPICS ─────────────────────────────────────
    elif page == "📉 Weak Topics":
        st.header("📉 Weak Topic Analysis")
        st.markdown(
            "<div class='card'><p>Nova tracks your quiz scores per topic. "
            "Anything below 70% shows here so you know exactly where to focus.</p></div>",
            unsafe_allow_html=True)
        weak = get_weak_topics()
        if not weak:
            st.info("Complete at least one quiz to see your analysis! 🎯")
        else:
            needs = [t for t in weak if t["avg"] < 70]
            good  = [t for t in weak if t["avg"] >= 70]
            if needs:
                st.markdown("### ⚠️ Topics that need more practice")
                for t in needs:
                    c = "#ef4444" if t["avg"]<50 else "#f59e0b"
                    st.markdown(
                        f"<div class='weak-topic'>"
                        f"<div><b>{t['topic']}</b>"
                        f"<div style='font-size:12px;opacity:0.7;'>{t['attempts']} attempt(s)</div></div>"
                        f"<div style='flex:1;margin:0 20px;'>"
                        f"<div style='background:rgba(239,68,68,0.15);border-radius:999px;height:10px;'>"
                        f"<div style='width:{t['avg']}%;height:100%;background:{c};border-radius:999px;'>"
                        f"</div></div></div>"
                        f"<span style='color:{c};font-weight:800;font-size:18px;'>{t['avg']}%</span>"
                        f"</div>", unsafe_allow_html=True)
                    if st.button(f"🎯 Practice {t['topic']}", key=f"pr_{t['topic']}"):
                        st.info(f"Go to **Quiz Arena** and type **{t['topic']}**!")
            if good:
                st.markdown("### ✅ Topics you're mastering")
                for t in good:
                    st.markdown(
                        f"<div class='history-item'>"
                        f"<span>📚 <b>{t['topic']}</b></span>"
                        f"<span style='opacity:0.7;'>{t['attempts']} attempt(s)</span>"
                        f"<span style='color:#22c55e;font-weight:800;font-size:18px;'>"
                        f"{t['avg']}% ✅</span></div>", unsafe_allow_html=True)
            if needs:
                w0 = needs[0]
                st.markdown(
                    f"<div class='tip-card'>🤖 <b>Nova recommends:</b> "
                    f"Your weakest topic is <b>{w0['topic']}</b> ({w0['avg']}% avg). "
                    f"Ask Nova Tutor, make flashcards, then retake the quiz!</div>",
                    unsafe_allow_html=True)

    # ── EXAM COUNTDOWN ──────────────────────────────────
    elif page == "⏰ Exam Countdown":
        st.header("⏰ Exam Countdown")
        c1, c2 = st.columns(2)
        with c1:
            subj = st.text_input("Exam subject:",
                                  value=st.session_state.exam_subject or "",
                                  placeholder="e.g. Biology Final, Math Midterm...")
        with c2:
            dval = None
            if st.session_state.exam_date:
                try: dval = datetime.strptime(st.session_state.exam_date, "%Y-%m-%d").date()
                except: pass
            dinp = st.date_input("Exam date:", value=dval, min_value=datetime.now().date())
        if st.button("💾 Save", type="primary"):
            st.session_state.exam_date    = dinp.strftime("%Y-%m-%d")
            st.session_state.exam_subject = subj
            sync_profile(); st.success("Saved! ✅")
        if st.session_state.exam_date:
            try:
                exam = datetime.strptime(st.session_state.exam_date, "%Y-%m-%d")
                dl   = (exam - datetime.now()).days
                subj_d = st.session_state.exam_subject or "Your Exam"
                if dl < 0:
                    st.markdown(
                        "<div class='countdown-box'>"
                        "<div style='font-size:48px;'>🎉</div>"
                        "<h2 style='color:white;'>Exam completed!</h2></div>",
                        unsafe_allow_html=True)
                else:
                    urg = "🔴" if dl<=3 else "🟡" if dl<=7 else "🟢"
                    tip = ("Final review only — focus on weak topics!" if dl<=3
                           else "Do practice quizzes every day." if dl<=7
                           else "You have time — build a study plan and stick to it.")
                    st.markdown(
                        f"<div class='countdown-box'>"
                        f"<div style='font-size:18px;opacity:0.8;margin-bottom:8px;'>"
                        f"{urg} {subj_d}</div>"
                        f"<div class='countdown-number'>{dl}</div>"
                        f"<div style='font-size:20px;color:rgba(255,255,255,0.7);margin:8px 0;'>"
                        f"day{'s' if dl!=1 else ''} remaining</div>"
                        f"<div style='font-size:14px;color:rgba(255,255,255,0.6);margin-top:16px;'>"
                        f"📅 {exam.strftime('%A, %B %d, %Y')}</div></div>",
                        unsafe_allow_html=True)
                    st.markdown(
                        f"<div class='tip-card'>💡 <b>Nova says:</b> {tip}</div>",
                        unsafe_allow_html=True)
            except: st.error("Invalid date.")
            if st.button("🗑️ Clear"):
                st.session_state.exam_date = None
                st.session_state.exam_subject = ""
                sync_profile(); st.rerun()

    # ── PROGRESS ────────────────────────────────────────
    elif page == "🏆 Progress":
        st.header("🏆 Student Progress")
        lvl = st.session_state.level
        st.markdown(
            f"<div class='level-box'>{LEVEL_ICONS.get(lvl,'🌱')} "
            f"Level {lvl} — {LEVEL_NAMES.get(lvl,'')}</div>",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        xp_now, xp_range, _ = xp_progress()
        pct = int(min(xp_now/max(xp_range,1), 1.0)*100)
        c1,c2,c3,c4 = st.columns(4)
        for col,(icon,val,label) in zip([c1,c2,c3,c4],[
            ("🔢", st.session_state.xp, "Total XP"),
            ("🎯", st.session_state.total_quizzes, "Quizzes Done"),
            ("⭐", st.session_state.last_score if st.session_state.get("last_score") is not None else "—", "Last Score"),
            ("🏅", len(st.session_state.badges), "Badges")]):
            with col:
                st.markdown(
                    f"<div class='metric-tile'><div style='font-size:28px;'>{icon}</div>"
                    f"<div class='metric-value'>{val}</div>"
                    f"<div class='metric-label'>{label}</div></div>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:14px;margin-bottom:4px;'>XP to next level: <b>{xp_now}/{xp_range}</b></div>"
            f"<div class='xp-bar-outer' style='height:20px;'>"
            f"<div style='height:100%;width:{pct}%;background:linear-gradient(90deg,#38bdf8,#818cf8);border-radius:999px;'>"
            f"</div></div>", unsafe_allow_html=True)
        st.markdown("### 🏅 Badges")
        if st.session_state.badges:
            html = ""
            for bid in st.session_state.badges:
                rule = next((b for b in BADGE_RULES if b["id"]==bid), None)
                if rule:
                    cls = rule["cls"]; ico = rule["icon"]; lbl = rule["label"]
                    html += f"<span class='badge {cls}'>{ico} {lbl}</span> "
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("Complete quizzes to earn badges! 🎯")
        st.markdown("### 📋 Quiz History")
        if st.session_state.quiz_history:
            for e in reversed(st.session_state.quiz_history):
                ps = int(e["score"]/e["total"]*100)
                c = "#22c55e" if ps>=80 else "#f59e0b" if ps>=60 else "#ef4444"
                st.markdown(
                    f"<div class='history-item'>"
                    f"<span>📚 <b>{e['topic']}</b></span>"
                    f"<span style='opacity:0.7;'>{e['date']}</span>"
                    f"<span>{e['score']}/{e['total']}</span>"
                    f"<span style='color:{c};font-weight:700;'>{ps}%</span>"
                    f"<span style='color:#818cf8;'>+{e['xp']} XP</span></div>",
                    unsafe_allow_html=True)
        else:
            st.info("No quiz history yet! 🎯")

    # ── LEADERBOARD ─────────────────────────────────────
    elif page == "🥇 Leaderboard":
        st.header("🥇 Leaderboard")
        board = st.session_state.leaderboard.copy()
        for name, data in load_profiles().items():
            ex = next((p for p in board if p["name"]==name), None)
            if ex: ex["xp"]=data.get("xp",0); ex["level"]=data.get("level",1)
            else: board.append({"name":name,"xp":data.get("xp",0),"level":data.get("level",1)})
        board.sort(key=lambda x: x["xp"], reverse=True)
        rank_icons = {1:"🥇",2:"🥈",3:"🥉"}
        for rank, player in enumerate(board, 1):
            is_you = player["name"] == user_name
            border = "3px solid #38bdf8" if is_you else "1px solid rgba(99,179,237,0.18)"
            fw    = "800" if is_you else "600"
            you   = "← You" if is_you else ""
            rank_icon = rank_icons.get(rank, f"{rank}.")
            plvl  = LEVEL_ICONS.get(player["level"],"") + " " + LEVEL_NAMES.get(player["level"],"")
            st.markdown(
                f"<div class='history-item' style='border:{border};padding:18px 22px;'>"
                f"<span style='font-size:24px;min-width:36px;'>{rank_icon}</span>"
                f"<span style='font-weight:{fw};font-size:16px;flex:1;'>"
                f"{player['name']} {you}</span>"
                f"<span style='opacity:0.7;'>{plvl}</span>"
                f"<span style='color:#818cf8;font-weight:700;'>{player['xp']} XP</span></div>",
                unsafe_allow_html=True)
        st.caption("Real profiles from nexuslearn_profiles.json appear here automatically.")

    # ── ABOUT ───────────────────────────────────────────
    elif page == "📝 About":
        st.header("📝 About Nova")
        for label, value in [
            ("Project Name", "Nova 🚀"),
            ("Academic Problem", "Students often lack immediate support outside the classroom."),
            ("Features", "AI explanations · Quizzes with sounds & animations · "
                         "Flashcards · Battle Mode · Study Plans · Weak Topic Analysis · "
                         "Exam Countdown · Multi-user Profiles · Leaderboard."),
            ("Tools Used", "Python, Streamlit, Ollama (Llama 3.1), "
                           "Web Audio API, streamlit.components.v1, iCal export."),
        ]:
            st.markdown(
                f"<div class='card' style='padding:16px 24px;'>"
                f"<span style='font-weight:700;font-size:14px;text-transform:uppercase;"
                f"letter-spacing:0.8px;opacity:0.6;'>{label}</span>"
                f"<p style='margin:4px 0 0;font-size:16px;'>{value}</p></div>",
                unsafe_allow_html=True)

    # Footer
    st.divider()
    st.caption("Nova 🚀 — Streamlit Cloud · Groq · Supabase · 100% free")
