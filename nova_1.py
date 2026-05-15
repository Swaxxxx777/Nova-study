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
    "mascot_mood": "idle", "motivational_msg": "",
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
    if dark:
        BG  = "linear-gradient(135deg,#0a0f1e 0%,#0d1b2a 50%,#0a1628 100%)"
        SB  = "linear-gradient(180deg,#050a14 0%,#0d1b2a 100%)"
        TM="#e2e8f0"; TS="#94a3b8"; CB="rgba(15,25,50,0.85)"; CBR="rgba(99,179,237,0.18)"
        NG="linear-gradient(135deg,#1a56db,#0ea5e9)"; QB="#3b82f6"; QBG="rgba(15,25,50,0.9)"
        LG="linear-gradient(135deg,#065f46,#10b981)"
        CERTBG="linear-gradient(135deg,#1c1400,#2d1f00)"; CERTBR="#d97706"; CERTC="#fbbf24"
        FBG="linear-gradient(135deg,#1e1b4b,#312e81)"; FTX="#c7d2fe"
        HBG="rgba(15,25,50,0.7)"; AC="#38bdf8"
        TI="☀️"; TL="Modo claro"; MBG="rgba(56,189,248,0.1)"
        TIPBG="linear-gradient(135deg,#1a1040,#2d1b69)"; TIPC="#c4b5fd"
        BP1="linear-gradient(135deg,#1e3a5f,#1a56db)"; BP2="linear-gradient(135deg,#5f1e1e,#db1a1a)"
        WBG="rgba(239,68,68,0.1)"; CDBG="linear-gradient(135deg,#0f2027,#203a43,#2c5364)"
        PROFBG="rgba(15,25,50,0.85)"; PROFBR="rgba(99,179,237,0.35)"
    else:
        BG  = "linear-gradient(135deg,#f0f9ff 0%,#e0f2fe 50%,#fef9c3 100%)"
        SB  = "linear-gradient(180deg,#1e293b 0%,#334155 100%)"
        TM="#0f172a"; TS="#475569"; CB="#ffffff"; CBR="#bfdbfe"
        NG="linear-gradient(135deg,#2563eb,#0ea5e9)"; QB="#2563eb"; QBG="#ffffff"
        LG="linear-gradient(135deg,#16a34a,#22c55e)"
        CERTBG="linear-gradient(135deg,#fef3c7,#fde68a)"; CERTBR="#f59e0b"; CERTC="#78350f"
        FBG="linear-gradient(135deg,#ede9fe,#ddd6fe)"; FTX="#4c1d95"
        HBG="#f8fafc"; AC="#2563eb"
        TI="🌙"; TL="Modo oscuro"; MBG="rgba(37,99,235,0.08)"
        TIPBG="linear-gradient(135deg,#f5f3ff,#ede9fe)"; TIPC="#5b21b6"
        BP1="linear-gradient(135deg,#dbeafe,#bfdbfe)"; BP2="linear-gradient(135deg,#fee2e2,#fecaca)"
        WBG="rgba(239,68,68,0.07)"; CDBG="linear-gradient(135deg,#0f172a,#1e293b)"
        PROFBG="#ffffff"; PROFBR="#bfdbfe"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');
    html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;}}
    .stApp{{background:{BG};color:{TM};}}
    [data-testid="stSidebar"]{{background:{SB};}}
    [data-testid="stSidebar"] *{{color:white!important;}}
    .main-title{{font-family:'Syne',sans-serif;font-size:clamp(36px,6vw,64px);font-weight:900;
        text-align:center;background:linear-gradient(90deg,{AC},#818cf8,{AC});
        background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;animation:shine 4s linear infinite;letter-spacing:-1px;}}
    @keyframes shine{{to{{background-position:200% center;}}}}
    .subtitle{{font-size:18px;text-align:center;color:{TS};margin-bottom:32px;font-weight:300;}}
    /* ---- Pantalla de perfil ---- */
    .profile-grid{{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:24px;}}
    .profile-card{{background:{PROFBG};border:2px solid {PROFBR};border-radius:20px;
        padding:24px 16px;text-align:center;transition:all 0.2s ease;min-width:140px;}}
    .profile-card:hover{{transform:translateY(-4px);
        box-shadow:0 12px 32px rgba(0,0,0,0.22);border-color:{AC};}}
    /* ---- Cards generales ---- */
    .card{{background:{CB};color:{TM};padding:26px 30px;border-radius:20px;
        box-shadow:0 4px 32px rgba(0,0,0,0.15);margin-bottom:20px;border:1.5px solid {CBR};
        backdrop-filter:blur(8px);transition:transform 0.2s,box-shadow 0.2s;}}
    .card:hover{{transform:translateY(-2px);box-shadow:0 8px 40px rgba(0,0,0,0.22);}}
    .nova-card{{background:{NG};color:white;padding:24px;border-radius:24px;
        box-shadow:0 8px 32px rgba(37,99,235,0.3);margin-bottom:20px;position:relative;overflow:hidden;}}
    .nova-card::before{{content:'';position:absolute;top:-40px;right:-40px;
        width:120px;height:120px;background:rgba(255,255,255,0.08);border-radius:50%;}}
    .nova-face{{font-size:72px;text-align:center;animation:float 3s ease-in-out infinite;}}
    @keyframes float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-8px);}}}}
    .nova-text{{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;text-align:center;}}
    .tip-card{{background:{TIPBG};color:{TIPC};padding:20px 24px;border-radius:18px;
        margin-bottom:20px;border-left:5px solid {AC};font-size:16px;line-height:1.6;font-weight:500;}}
    .quiz-box{{background:{QBG};color:{TM};padding:24px 28px;border-radius:18px;
        margin-bottom:18px;border-left:6px solid {QB};box-shadow:0 4px 20px rgba(0,0,0,0.12);
        transition:border-color 0.2s;}}
    .quiz-box:hover{{border-left-color:#818cf8;}}
    .level-box{{background:{LG};color:white;padding:22px;border-radius:20px;
        font-family:'Syne',sans-serif;font-size:22px;font-weight:800;text-align:center;}}
    .certificate{{background:{CERTBG};color:{CERTC};padding:40px;border-radius:28px;
        border:3px solid {CERTBR};text-align:center;font-family:'Syne',sans-serif;}}
    .flashcard{{background:{FBG};color:{FTX};padding:40px 32px;border-radius:24px;
        text-align:center;min-height:180px;display:flex;flex-direction:column;
        justify-content:center;transition:transform 0.2s;border:1.5px solid rgba(165,180,252,0.3);}}
    .flashcard:hover{{transform:scale(1.02);}}
    .history-item{{background:{HBG};border:1px solid {CBR};color:{TM};padding:16px 20px;
        border-radius:14px;margin-bottom:10px;display:flex;justify-content:space-between;
        align-items:center;font-size:15px;transition:transform 0.15s;}}
    .history-item:hover{{transform:translateX(4px);}}
    .badge{{display:inline-block;padding:4px 14px;border-radius:20px;font-size:13px;font-weight:600;margin:3px;}}
    .badge-gold{{background:linear-gradient(135deg,#f59e0b,#d97706);color:white;}}
    .badge-silver{{background:linear-gradient(135deg,#94a3b8,#64748b);color:white;}}
    .badge-blue{{background:linear-gradient(135deg,#3b82f6,#2563eb);color:white;}}
    .badge-green{{background:linear-gradient(135deg,#22c55e,#16a34a);color:white;}}
    .xp-bar-outer{{background:rgba(99,102,241,0.15);border-radius:999px;height:14px;overflow:hidden;margin:8px 0 4px;}}
    .metric-tile{{background:{MBG};border:1px solid {CBR};border-radius:16px;padding:18px 22px;text-align:center;}}
    .metric-value{{font-family:'Syne',sans-serif;font-size:36px;font-weight:900;color:{AC};}}
    .metric-label{{font-size:13px;color:{TS};text-transform:uppercase;letter-spacing:0.8px;margin-top:4px;}}
    .battle-p1{{background:{BP1};border-radius:20px;padding:20px;text-align:center;border:2px solid #3b82f6;}}
    .battle-p2{{background:{BP2};border-radius:20px;padding:20px;text-align:center;border:2px solid #ef4444;}}
    .battle-score{{font-family:'Syne',sans-serif;font-size:48px;font-weight:900;}}
    .countdown-box{{background:{CDBG};color:white;padding:32px;border-radius:24px;text-align:center;}}
    .countdown-number{{font-family:'Syne',sans-serif;font-size:72px;font-weight:900;color:{AC};line-height:1;}}
    .weak-topic{{background:{WBG};border:1px solid rgba(239,68,68,0.3);border-radius:14px;
        padding:14px 18px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;}}
    h1,h2,h3{{font-family:'Syne',sans-serif!important;color:{TM}!important;}}
    .stButton>button{{font-family:'DM Sans',sans-serif!important;font-weight:600!important;
        border-radius:12px!important;transition:all 0.2s!important;}}
    .stButton>button:hover{{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(0,0,0,0.2)!important;}}
    div[data-testid="stRadio"] label{{color:{TM}!important;}}
    .stTextInput>div>div>input,.stTextArea>div>div>textarea{{
        background:{CB}!important;color:{TM}!important;
        border-radius:12px!important;border:1.5px solid {CBR}!important;}}
    p,li,span{{color:{TS};}}
    .card p,.card h2,.card h3,.card span,.card li{{color:{TM}!important;}}
    </style>
    """, unsafe_allow_html=True)
    return TI, TL

# Llamar estilos aquí — session_state ya existe
toggle_icon, toggle_label = inject_styles(st.session_state.dark_mode)

# =========================================
# 4. PERFILES — JSON local
# =========================================
PROFILES_FILE = "nova_profiles.json"

@st.cache_resource
def _supabase():
    try:
        from supabase import create_client
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

def _default_profile(name: str) -> dict:
    return {"name":name,"xp":0,"level":1,"total_quizzes":0,"badges":[],
            "quiz_history":[],"weak_topics":{},"exam_date":None,
            "exam_subject":"","battle_wins":0,"streak_days":0,"last_study_date":None}

def load_profiles() -> dict:
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

def activate_profile(name):
    """Carga perfil del disco → session_state."""
    profiles = load_profiles()
    p = profiles.get(name, _default_profile(name))
    st.session_state.active_user = name
    for k in ["xp","level","total_quizzes","badges","quiz_history",
               "weak_topics","exam_date","exam_subject","battle_wins",
               "streak_days","last_study_date"]:
        st.session_state[k] = p.get(k, _default_profile(name)[k])

def save_user_profile(name: str, data: dict):
    """Guarda perfil en Supabase (online) o JSON local (fallback)."""
    db = _supabase()
    if db:
        try:
            db.table("profiles").upsert(
                {"name": name, "data": data}, on_conflict="name"
            ).execute()
            return
        except Exception:
            pass
    # Fallback JSON local
    profiles = load_profiles()
    profiles[name] = data
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

def sync_profile():
    """Guarda session_state → Supabase/disco."""
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

def update_level_and_badges():
    update_streak()  # racha de estudio
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

# ── MASCOTA: estados de ánimo según progreso ────────────────────────────────
MASCOT_STATES = {
    "idle":    ("🤖", "✨"),
    "happy":   ("😊", "🌟"),
    "excited": ("🤩", "🎉"),
    "perfect": ("🥳", "🏆"),
    "thinking":("🤔", "💭"),
    "sad":     ("😢", "💪"),
    "sleepy":  ("😴", "☕"),
    "streak":  ("🔥", "⚡"),
}

MOTIVATIONAL_MSGS = {
    "perfect":  ["You're unstoppable! Perfect score! 🎉",
                 "Absolutely crushed it! You're on fire! 🔥",
                 "100%! Nothing can stop you now! 🏆"],
    "good":     ["Good job! Review the ones you missed 💪",
                 "Solid work! Keep pushing forward! 📈",
                 "You're improving every day! 🌱"],
    "low":      ["Every mistake makes you stronger! 💡",
                 "Don't give up — review and try again! 🔄",
                 "Struggle is how the brain grows. You got this! 🧠"],
    "idle":     ["Ready to learn something new today? 🚀",
                 "Your brain is waiting for a challenge! ⚡",
                 "Let's make today count! 🎯"],
    "streak_1": ["Day 1 streak! Every journey starts here 🌱"],
    "streak_3": ["3 days in a row! You're building a habit! 🔥"],
    "streak_7": ["One full week! You're unstoppable! 🏆"],
}

def get_motivational_msg(mood_key: str) -> str:
    msgs = MOTIVATIONAL_MSGS.get(mood_key, MOTIVATIONAL_MSGS["idle"])
    return random.choice(msgs)

def update_streak():
    """Actualiza la racha de días consecutivos estudiando."""
    today = datetime.now().strftime("%Y-%m-%d")
    last = st.session_state.get("last_study_date")
    if last == today:
        return  # ya estudió hoy
    if last:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if last == yesterday:
            st.session_state.streak_days += 1
        else:
            st.session_state.streak_days = 1  # racha rota
    else:
        st.session_state.streak_days = 1
    st.session_state.last_study_date = today
    sync_profile()

def nova_mood(score=None):
    streak = st.session_state.get("streak_days", 0)
    if score is None:
        if streak >= 7:
            return MASCOT_STATES["streak"], get_motivational_msg("streak_7")
        if streak >= 3:
            return MASCOT_STATES["streak"], get_motivational_msg("streak_3")
        return MASCOT_STATES["idle"], get_motivational_msg("idle")
    if score == 5:    return MASCOT_STATES["perfect"], get_motivational_msg("perfect")
    if score >= 3:    return MASCOT_STATES["happy"],   get_motivational_msg("good")
    return MASCOT_STATES["sad"], get_motivational_msg("low")

# =========================================
# 9. AI — Groq (online) / Ollama (local)
# =========================================
def _chat(system: str, user: str, max_tokens: int = 900) -> str:
    """Llama a Groq si hay API key, sino a Ollama local."""
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":system},
                      {"role":"user","content":user}],
            max_tokens=max_tokens, temperature=0.7,
        )
        return r.choices[0].message.content
    except Exception:
        # Fallback a Ollama local
        import ollama
        r = ollama.chat(model="llama3.1:8b",
            messages=[{"role":"system","content":system},
                      {"role":"user","content":user}])
        return r["message"]["content"]

def ask_ai(question: str) -> str:
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
    r = ollama.chat(model="llama3.1:8b", messages=[
        {"role":"system","content":(
            'Create a quiz. Return ONLY valid JSON, nothing else:\n'
            '{"questions":[{"question":"...","options":["A","B","C","D"],'
            '"answer_index":0,"explanation":"...","difficulty":"easy"}]}\n'
            "Rules: 5 questions. 2 easy, 2 medium, 1 hard. 4 options. answer_index 0-3.")},
        {"role":"user","content":f"Topic: {topic}"}])
    try:
        m = re.search(r"\{.*\}", r["message"]["content"], re.DOTALL)
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

def generate_flashcards(topic: str) -> list:
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


def generate_study_plan(topic: str) -> list:
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

# =========================================
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
    st.markdown("<div class='subtitle'>Your AI-powered study companion</div>", unsafe_allow_html=True)

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
    mood_state, msg = nova_mood(st.session_state.get("last_score"))
    emoji, anim = mood_state
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

        # ── STREAK CARD ──────────────────────────────────────────────────
        streak = st.session_state.get('streak_days', 0)
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            fire = '🔥' * min(streak, 7)
            color = '#f59e0b' if streak >= 3 else '#38bdf8'
            st.markdown(
                f"<div class='card' style='text-align:center;'>"
                f"<div style='font-size:13px;opacity:0.6;text-transform:uppercase;"
                f"letter-spacing:1px;'>Study Streak</div>"
                f"<div style='font-size:56px;font-family:Syne,sans-serif;"
                f"font-weight:900;color:{color};'>{streak}</div>"
                f"<div style='font-size:20px;'>{fire if fire else '🌱'}</div>"
                f"<div style='font-size:13px;opacity:0.7;margin-top:4px;'>"
                f"{'days in a row!' if streak else 'Start today!'}</div>"
                f"</div>", unsafe_allow_html=True)
        with c_s2:
            lvl_now = st.session_state.level
            xn, xr, _ = xp_progress()
            pct_now = int(min(xn/max(xr,1),1.0)*100)
            next_lvl = LEVEL_NAMES.get(min(lvl_now+1,6),'Max')
            st.markdown(
                f"<div class='card' style='text-align:center;'>"
                f"<div style='font-size:13px;opacity:0.6;text-transform:uppercase;"
                f"letter-spacing:1px;'>Next Level</div>"
                f"<div style='font-size:22px;font-family:Syne,sans-serif;"
                f"font-weight:800;margin:8px 0;'>{LEVEL_ICONS.get(min(lvl_now+1,6),'💎')} {next_lvl}</div>"
                f"<div style='background:rgba(99,102,241,0.15);border-radius:999px;"
                f"height:12px;overflow:hidden;'>"
                f"<div style='height:100%;width:{pct_now}%;background:linear-gradient(90deg,#a5f3fc,#818cf8);"
                f"border-radius:999px;'></div></div>"
                f"<div style='font-size:12px;opacity:0.6;margin-top:6px;'>{xn}/{xr} XP</div>"
                f"</div>", unsafe_allow_html=True)

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
        st.header("📝 About NexusLearn AI")
        for label, value in [
            ("Project Name", "Nova 🚀 v2.0"),
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
    st.caption("Nova 🚀 v2.0 — Streamlit Cloud · Groq · Supabase · 100% free")
