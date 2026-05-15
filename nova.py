"""
Nova 🚀 — AI-powered study companion
Stack: Streamlit Cloud (free) + Groq API (free) + Supabase (free)
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import re
import random
import os
from datetime import datetime, timedelta

# ── Cloud clients (lazy-loaded) ──────────────────────────────────────────────
@st.cache_resource
def get_groq():
    from groq import Groq
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

@st.cache_resource
def get_supabase():
    from supabase import create_client
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================================
# 1. PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Nova 🚀", page_icon="🚀",
    layout="wide", initial_sidebar_state="expanded"
)

# =========================================
# 2. SESSION STATE
# =========================================
LEVEL_NAMES = {1:"Spark",2:"Seeker",3:"Builder",
               4:"Champion",5:"Luminary",6:"Sage"}
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
# 3. SUPABASE — perfiles online
# =========================================
def _db():
    return get_supabase()

def load_profiles() -> dict:
    """Carga todos los perfiles desde Supabase."""
    try:
        rows = _db().table("profiles").select("*").execute().data
        return {r["name"]: r["data"] for r in rows}
    except Exception:
        return {}

def save_user_profile(name: str, data: dict):
    """Upsert (crea o actualiza) el perfil en Supabase."""
    try:
        _db().table("profiles").upsert(
            {"name": name, "data": data},
            on_conflict="name"
        ).execute()
    except Exception:
        pass   # silencioso — no rompe la app si hay error de red

def activate_profile(name: str):
    profiles = load_profiles()
    p = profiles.get(name, _default_profile(name))
    st.session_state.active_user = name
    for k in ["xp","level","total_quizzes","badges","quiz_history",
               "weak_topics","exam_date","exam_subject","battle_wins"]:
        st.session_state[k] = p.get(k, _default_profile(name)[k])

def sync_profile():
    name = st.session_state.get("active_user")
    if not name:
        return
    profiles = load_profiles()
    p = profiles.get(name, _default_profile(name))
    for k in ["xp","level","total_quizzes","badges","quiz_history",
               "weak_topics","exam_date","exam_subject","battle_wins"]:
        p[k] = st.session_state.get(k, p.get(k))
    save_user_profile(name, p)

def _default_profile(name: str) -> dict:
    return {"name":name,"xp":0,"level":1,"total_quizzes":0,"badges":[],
            "quiz_history":[],"weak_topics":{},"exam_date":None,
            "exam_subject":"","battle_wins":0}

def get_avatar(name: str) -> str:
    return AVATARS[sum(ord(c) for c in name) % len(AVATARS)]

# =========================================
# 4. GROQ — reemplaza Ollama
# =========================================
MODEL = "llama-3.1-8b-instant"   # gratis, mismo modelo que usabas

def chat(system: str, user: str, max_tokens: int = 900) -> str:
    r = get_groq().chat.completions.create(
        model=MODEL,
        messages=[{"role":"system","content":system},
                  {"role":"user","content":user}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return r.choices[0].message.content

def ask_ai(question: str) -> str:
    return chat(
        "You are Nova, a warm and expert academic tutor. Structure every answer:\n"
        "1. One-sentence definition in simple language.\n"
        "2. Real-world analogy (start: 'Think of it like...').\n"
        "3. Concrete example with numbers or facts.\n"
        "4. Memory tip (start: 'To remember: ...').\n"
        "Keep each section 2-3 sentences. Natural paragraphs only. Be encouraging.",
        question
    )

def generate_quiz(topic: str) -> list:
    text = chat(
        'Create a quiz. Return ONLY valid JSON, nothing else:\n'
        '{"questions":[{"question":"...","options":["A","B","C","D"],'
        '"answer_index":0,"explanation":"...","difficulty":"easy"}]}\n'
        "Rules: 5 questions. 2 easy, 2 medium, 1 hard. 4 options. answer_index 0-3.",
        f"Topic: {topic}",
        max_tokens=1200
    )
    try:
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

def _quiz_fallback(topic: str) -> list:
    return [{"question":f"Best way to study {topic}?",
             "options":["Practice examples","Read once","Ignore it","Never review"],
             "answer":"Practice examples","explanation":"Active practice reinforces memory.",
             "difficulty":"easy"}]

def generate_flashcards(topic: str) -> list:
    text = chat(
        'Create 6 flashcards. Return ONLY valid JSON:\n'
        '{"cards":[{"term":"...","definition":"..."}]}\n'
        "6 cards. term: 1-4 words. definition: 1-2 sentences.",
        f"Topic: {topic}"
    )
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(m.group())["cards"]
    except:
        return [{"term":f"{topic} {i+1}","definition":"Review this concept."} for i in range(6)]

def generate_study_plan(topic: str) -> list:
    text = chat(
        'Create a 5-day study plan. Return ONLY valid JSON:\n'
        '{"days":[{"day":"Day 1","title":"...","task":"...","resource":"..."}]}\n'
        "5 days. Practical tasks. Free online resources only.",
        f"Topic: {topic}"
    )
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(m.group())["days"]
    except:
        return [{"day":f"Day {i+1}","title":f"Session {i+1}",
                 "task":f"Study {topic}.","resource":"Khan Academy"} for i in range(5)]

# =========================================
# 5. SONIDOS (components.html)
# =========================================
def play_sound(sound_type: str):
    scripts = {
        "correct": "var c=new(window.AudioContext||window.webkitAudioContext)();[523,659,784].forEach(function(f,i){var o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);o.type='sine';o.frequency.value=f;g.gain.setValueAtTime(0.25,c.currentTime+i*0.12);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+i*0.12+0.3);o.start(c.currentTime+i*0.12);o.stop(c.currentTime+i*0.12+0.35);});",
        "wrong":   "var c=new(window.AudioContext||window.webkitAudioContext)();var o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);o.type='sawtooth';o.frequency.setValueAtTime(280,c.currentTime);o.frequency.exponentialRampToValueAtTime(100,c.currentTime+0.35);g.gain.setValueAtTime(0.2,c.currentTime);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.35);o.start(c.currentTime);o.stop(c.currentTime+0.4);",
        "levelup": "var c=new(window.AudioContext||window.webkitAudioContext)();[392,523,659,784,1047].forEach(function(f,i){var o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);o.type='sine';o.frequency.value=f;g.gain.setValueAtTime(0.25,c.currentTime+i*0.13);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+i*0.13+0.3);o.start(c.currentTime+i*0.13);o.stop(c.currentTime+i*0.13+0.35);});",
        "perfect": "var c=new(window.AudioContext||window.webkitAudioContext)();[523,659,784,1047,1319].forEach(function(f,i){var o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);o.type='triangle';o.frequency.value=f;g.gain.setValueAtTime(0.28,c.currentTime+i*0.15);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+i*0.15+0.45);o.start(c.currentTime+i*0.15);o.stop(c.currentTime+i*0.15+0.5);});",
    }
    js = scripts.get(sound_type, "")
    if js:
        components.html(f"<script>{js}</script>", height=0)

# =========================================
# 6. ANIMACIONES (components.html)
# =========================================
def trigger_confetti():
    components.html("""
    <style>@keyframes fall{to{top:110vh;opacity:0;transform:rotate(720deg);}}</style>
    <script>
    var colors=['#a78bfa','#34d399','#f59e0b','#f472b6','#38bdf8','#fff'];
    for(var i=0;i<100;i++){(function(i){setTimeout(function(){
        var el=document.createElement('div'),s=Math.random()*10+5;
        el.style.cssText='position:fixed;top:-20px;left:'+(Math.random()*100)+'vw;width:'+s+'px;height:'+s+'px;background:'+colors[Math.floor(Math.random()*colors.length)]+';border-radius:'+(Math.random()>.5?'50%':'3px')+';z-index:99999;pointer-events:none;animation:fall '+(Math.random()*2+1.5)+'s ease-in forwards;';
        document.body.appendChild(el);setTimeout(function(){el.remove();},4000);
    },i*18);})(i);}
    </script>""", height=0)

def trigger_level_up_banner(level_name: str):
    components.html(f"""
    <style>
    @keyframes pop{{0%{{transform:translate(-50%,-50%) scale(0);opacity:0}}70%{{transform:translate(-50%,-50%) scale(1.08)}}100%{{transform:translate(-50%,-50%) scale(1);opacity:1}}}}
    @keyframes fadeOut{{to{{opacity:0}}}}
    </style>
    <script>
    var b=document.createElement('div');
    b.style.cssText='position:fixed;top:50%;left:50%;background:linear-gradient(135deg,#7c3aed,#a78bfa);color:white;padding:40px 60px;border-radius:28px;text-align:center;z-index:99999;box-shadow:0 20px 60px rgba(124,58,237,0.6);font-family:sans-serif;animation:pop 0.5s cubic-bezier(0.175,0.885,0.32,1.275) forwards;';
    b.innerHTML='<div style="font-size:60px;margin-bottom:10px">✨</div><div style="font-size:32px;font-weight:900;letter-spacing:2px">LEVEL UP!</div><div style="font-size:20px;opacity:0.9;margin-top:8px">{level_name}</div>';
    document.body.appendChild(b);
    setTimeout(function(){{b.style.animation='fadeOut 0.4s ease forwards';setTimeout(function(){{b.remove();}},400);}},2500);
    </script>""", height=0)

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
def daily_tip() -> str:
    return _TIPS[datetime.now().timetuple().tm_yday % len(_TIPS)]

# =========================================
# 8. BADGES
# =========================================
BADGE_RULES = [
    {"id":"first_quiz",   "label":"First Quiz",    "icon":"🎯","cls":"badge-blue",
     "cond": lambda: st.session_state.get("total_quizzes",0) >= 1},
    {"id":"perfect",      "label":"Perfect Score", "icon":"⭐","cls":"badge-gold",
     "cond": lambda: st.session_state.get("last_score") == 5},
    {"id":"five_quizzes", "label":"Quiz Veteran",  "icon":"🏅","cls":"badge-silver",
     "cond": lambda: st.session_state.get("total_quizzes",0) >= 5},
    {"id":"level3",       "label":"Level 3",       "icon":"🔥","cls":"badge-green",
     "cond": lambda: st.session_state.get("level",1) >= 3},
    {"id":"battle_win",   "label":"Battle Winner", "icon":"⚔️","cls":"badge-gold",
     "cond": lambda: st.session_state.get("battle_wins",0) >= 1},
    {"id":"master",       "label":"Sage",          "icon":"💎","cls":"badge-gold",
     "cond": lambda: st.session_state.get("level",1) >= 6},
]

def update_level_and_badges():
    xp = st.session_state.xp
    prev = st.session_state.level
    for lvl in sorted(XP_THRESHOLDS.keys(), reverse=True):
        if xp >= XP_THRESHOLDS[lvl]:
            st.session_state.level = lvl; break
    if st.session_state.level > prev:
        play_sound("levelup")
        trigger_level_up_banner(LEVEL_NAMES[st.session_state.level])
    for badge in BADGE_RULES:
        if badge["id"] not in st.session_state.badges and badge["cond"]():
            st.session_state.badges.append(badge["id"])
    sync_profile()

def xp_progress():
    cur = st.session_state.level
    if cur >= 6: return st.session_state.xp, 200, 200
    nt = XP_THRESHOLDS[cur+1]; ct = XP_THRESHOLDS[cur]
    return st.session_state.xp - ct, nt - ct, nt

def nova_mood(score=None):
    if score is None: return "✨","Hi! I'm Nova, your AI study companion. Let's learn something today!"
    if score == 5:    return "🌟","Perfect score! You are absolutely on fire right now! 🎉"
    if score >= 3:    return "😊","Good work! Review the ones you missed and try again."
    return "💡","Every mistake is a step forward. Let's review and come back stronger!"

# =========================================
# 9. UTILS
# =========================================
def diff_badge(d: str) -> str:
    c = {"easy":"#22c55e","medium":"#f59e0b","hard":"#ef4444"}.get(d,"#94a3b8")
    l = {"easy":"Easy","medium":"Medium","hard":"Hard"}.get(d,d.capitalize())
    return f"<span style='background:{c};color:white;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;'>{l}</span>"

def rec(score: int, topic: str) -> str:
    if score==5: return f"🌟 Excellent! You've mastered **{topic}**."
    if score>=3: return f"📈 Good progress on **{topic}**. Review wrong answers and try again."
    return f"📚 Ask Nova to explain **{topic}**, make flashcards, then retake."

def create_ics(days: list) -> str:
    today = datetime.now()
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Nova//EN\n"
    for i,d in enumerate(days):
        s = (today+timedelta(days=i)).replace(hour=17,minute=0,second=0)
        e = s.replace(hour=17,minute=45)
        ics += (f"BEGIN:VEVENT\nSUMMARY:Nova — {d.get('title','Study')}\n"
                f"DESCRIPTION:{d.get('task','')}\\nResource: {d.get('resource','')}\n"
                f"DTSTART:{s.strftime('%Y%m%dT%H%M%S')}\n"
                f"DTEND:{e.strftime('%Y%m%dT%H%M%S')}\nEND:VEVENT\n")
    return ics + "END:VCALENDAR"

def update_weak_topics(topic: str, score: int, total: int):
    pct = round(score/total*100)
    st.session_state.weak_topics.setdefault(topic,[]).append(pct)
    st.session_state.weak_topics[topic] = st.session_state.weak_topics[topic][-10:]

def get_weak_topics() -> list:
    return sorted(
        [{"topic":t,"avg":round(sum(s)/len(s)),"attempts":len(s)}
         for t,s in st.session_state.weak_topics.items()],
        key=lambda x: x["avg"])

# =========================================
# 10. ESTILOS
# =========================================
def inject_styles(dark: bool):
    if dark:
        BG="linear-gradient(135deg,#0d0a1e 0%,#130f2a 50%,#0d0a1e 100%)"
        SB="linear-gradient(180deg,#0a0718 0%,#130f2a 100%)"
        TM="#e8e4f8"; TS="#9e97c8"; CB="rgba(20,15,45,0.85)"; CBR="rgba(167,139,250,0.2)"
        NG="linear-gradient(135deg,#5b21b6,#7c3aed)"; QB="#7c3aed"; QBG="rgba(20,15,45,0.9)"
        LG="linear-gradient(135deg,#065f46,#10b981)"
        CERTBG="linear-gradient(135deg,#1c1400,#2d1f00)"; CERTBR="#d97706"; CERTC="#fbbf24"
        FBG="linear-gradient(135deg,#1e1b4b,#312e81)"; FTX="#c7d2fe"
        HBG="rgba(20,15,45,0.7)"; AC="#a78bfa"
        TI="☀️"; TL="Light mode"; MBG="rgba(167,139,250,0.1)"
        TIPBG="linear-gradient(135deg,#1a1040,#2d1b69)"; TIPC="#c4b5fd"
        BP1="linear-gradient(135deg,#1e3a5f,#1a56db)"; BP2="linear-gradient(135deg,#5f1e1e,#db1a1a)"
        WBG="rgba(239,68,68,0.1)"; CDBG="linear-gradient(135deg,#0f0a1e,#1a1040)"
        PROFBG="rgba(20,15,45,0.85)"; PROFBR="rgba(167,139,250,0.35)"
    else:
        BG="linear-gradient(135deg,#f5f3ff 0%,#ede9fe 50%,#faf5ff 100%)"
        SB="linear-gradient(180deg,#1e1b4b 0%,#312e81 100%)"
        TM="#1e1b4b"; TS="#6d6ba0"; CB="#ffffff"; CBR="#ddd6fe"
        NG="linear-gradient(135deg,#5b21b6,#7c3aed)"; QB="#7c3aed"; QBG="#ffffff"
        LG="linear-gradient(135deg,#16a34a,#22c55e)"
        CERTBG="linear-gradient(135deg,#fef3c7,#fde68a)"; CERTBR="#f59e0b"; CERTC="#78350f"
        FBG="linear-gradient(135deg,#ede9fe,#ddd6fe)"; FTX="#4c1d95"
        HBG="#f5f3ff"; AC="#7c3aed"
        TI="🌙"; TL="Dark mode"; MBG="rgba(124,58,237,0.07)"
        TIPBG="linear-gradient(135deg,#f5f3ff,#ede9fe)"; TIPC="#5b21b6"
        BP1="linear-gradient(135deg,#dbeafe,#bfdbfe)"; BP2="linear-gradient(135deg,#fee2e2,#fecaca)"
        WBG="rgba(239,68,68,0.07)"; CDBG="linear-gradient(135deg,#1e1b4b,#312e81)"
        PROFBG="#ffffff"; PROFBR="#c4b5fd"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');
    html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;}}
    .stApp{{background:{BG};color:{TM};}}
    [data-testid="stSidebar"]{{background:{SB};}}
    [data-testid="stSidebar"] *{{color:white!important;}}
    .main-title{{font-family:'Syne',sans-serif;font-size:clamp(36px,6vw,68px);font-weight:900;
        text-align:center;background:linear-gradient(90deg,{AC},#f0abfc,{AC});
        background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;animation:shine 4s linear infinite;letter-spacing:-2px;}}
    @keyframes shine{{to{{background-position:200% center;}}}}
    .subtitle{{font-size:18px;text-align:center;color:{TS};margin-bottom:32px;font-weight:300;}}
    .card{{background:{CB};color:{TM};padding:26px 30px;border-radius:20px;
        box-shadow:0 4px 32px rgba(0,0,0,0.12);margin-bottom:20px;border:1.5px solid {CBR};
        backdrop-filter:blur(8px);transition:transform 0.2s,box-shadow 0.2s;}}
    .card:hover{{transform:translateY(-2px);box-shadow:0 8px 40px rgba(0,0,0,0.18);}}
    .nova-card{{background:{NG};color:white;padding:24px;border-radius:24px;
        box-shadow:0 8px 32px rgba(124,58,237,0.35);margin-bottom:20px;
        position:relative;overflow:hidden;}}
    .nova-card::before{{content:'';position:absolute;top:-40px;right:-40px;
        width:120px;height:120px;background:rgba(255,255,255,0.08);border-radius:50%;}}
    .nova-face{{font-size:72px;text-align:center;animation:float 3s ease-in-out infinite;}}
    @keyframes float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-8px);}}}}
    .nova-text{{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;text-align:center;}}
    .tip-card{{background:{TIPBG};color:{TIPC};padding:20px 24px;border-radius:18px;
        margin-bottom:20px;border-left:5px solid {AC};font-size:16px;line-height:1.6;font-weight:500;}}
    .quiz-box{{background:{QBG};color:{TM};padding:24px 28px;border-radius:18px;
        margin-bottom:18px;border-left:6px solid {QB};box-shadow:0 4px 20px rgba(0,0,0,0.1);}}
    .quiz-box:hover{{border-left-color:#f0abfc;}}
    .level-box{{background:{LG};color:white;padding:22px;border-radius:20px;
        font-family:'Syne',sans-serif;font-size:22px;font-weight:800;text-align:center;}}
    .certificate{{background:{CERTBG};color:{CERTC};padding:40px;border-radius:28px;
        border:3px solid {CERTBR};text-align:center;font-family:'Syne',sans-serif;}}
    .flashcard{{background:{FBG};color:{FTX};padding:40px 32px;border-radius:24px;
        text-align:center;min-height:180px;display:flex;flex-direction:column;
        justify-content:center;transition:transform 0.2s;
        border:1.5px solid rgba(196,181,253,0.3);}}
    .flashcard:hover{{transform:scale(1.02);}}
    .history-item{{background:{HBG};border:1px solid {CBR};color:{TM};padding:16px 20px;
        border-radius:14px;margin-bottom:10px;display:flex;justify-content:space-between;
        align-items:center;font-size:15px;transition:transform 0.15s;}}
    .history-item:hover{{transform:translateX(4px);}}
    .badge{{display:inline-block;padding:4px 14px;border-radius:20px;font-size:13px;font-weight:600;margin:3px;}}
    .badge-gold{{background:linear-gradient(135deg,#f59e0b,#d97706);color:white;}}
    .badge-silver{{background:linear-gradient(135deg,#94a3b8,#64748b);color:white;}}
    .badge-blue{{background:linear-gradient(135deg,#7c3aed,#5b21b6);color:white;}}
    .badge-green{{background:linear-gradient(135deg,#22c55e,#16a34a);color:white;}}
    .xp-bar-outer{{background:rgba(167,139,250,0.15);border-radius:999px;height:14px;overflow:hidden;margin:8px 0 4px;}}
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
    .profile-card{{background:{PROFBG};border:2px solid {PROFBR};border-radius:20px;padding:20px;
        text-align:center;transition:all 0.2s ease;}}
    .profile-card:hover{{transform:translateY(-4px);box-shadow:0 12px 32px rgba(124,58,237,0.2);}}
    h1,h2,h3{{font-family:'Syne',sans-serif!important;color:{TM}!important;}}
    .stButton>button{{font-family:'DM Sans',sans-serif!important;font-weight:600!important;
        border-radius:12px!important;transition:all 0.2s!important;}}
    .stButton>button:hover{{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(124,58,237,0.25)!important;}}
    div[data-testid="stRadio"] label{{color:{TM}!important;}}
    .stTextInput>div>div>input,.stTextArea>div>div>textarea{{
        background:{CB}!important;color:{TM}!important;
        border-radius:12px!important;border:1.5px solid {CBR}!important;}}
    p,li,span{{color:{TS};}}
    .card p,.card h2,.card h3,.card span,.card li{{color:{TM}!important;}}
    </style>
    """, unsafe_allow_html=True)
    return TI, TL

toggle_icon, toggle_label = inject_styles(st.session_state.dark_mode)

# =========================================
# 11. LOGIN
# =========================================
if not st.session_state.active_user:
    st.markdown("<div class='main-title'>🚀 Nova</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Your AI-powered study companion. Who's learning today?</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("Loading profiles..."):
        profiles = load_profiles()

    if profiles:
        st.markdown("### 👤 Select your profile")
        num_cols = min(len(profiles), 4)
        cols = st.columns(num_cols)
        for i,(name,data) in enumerate(profiles.items()):
            with cols[i % num_cols]:
                av  = get_avatar(name)
                lvl = data.get("level",1)
                xp  = data.get("xp",0)
                st.markdown(
                    f"<div class='profile-card'>"
                    f"<div style='font-size:52px;'>{av}</div>"
                    f"<div style='font-family:Syne,sans-serif;font-weight:800;font-size:18px;margin-top:10px;'>{name}</div>"
                    f"<div style='font-size:13px;opacity:0.65;margin-top:4px;'>"
                    f"{LEVEL_ICONS.get(lvl,'')} {LEVEL_NAMES.get(lvl,'')} · {xp} XP</div>"
                    f"</div>", unsafe_allow_html=True)
                if st.button(f"▶ Play as {name}", key=f"login_{name}", use_container_width=True):
                    activate_profile(name)
                    st.rerun()
        st.markdown("---")

    st.markdown("### ✨ Create new profile")
    c1,c2 = st.columns([3,1])
    with c1:
        new_name = st.text_input("name_input", label_visibility="collapsed",
                                  placeholder="Enter your name...")
    with c2:
        if st.button("Create ➜", type="primary", use_container_width=True):
            nm = new_name.strip()
            if nm:
                activate_profile(nm)
                save_user_profile(nm, _default_profile(nm))
                st.rerun()
            else:
                st.warning("Please enter a name.")

else:
    # =========================================
    # 12. APP PRINCIPAL
    # =========================================
    user_name   = st.session_state.active_user
    user_avatar = get_avatar(user_name)

    st.markdown("<div class='main-title'>🚀 Nova</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Your AI-powered study companion</div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([4,1,4])
    with c2:
        if st.button(f"{toggle_icon} {toggle_label}"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"<div class='tip-card'>💡 <b>Nova's Tip of the Day:</b> {daily_tip()}</div>",
                unsafe_allow_html=True)

    emoji, msg = nova_mood(st.session_state.get("last_score"))
    xp_now, xp_range, _ = xp_progress()
    pct = int(min(xp_now/max(xp_range,1),1.0)*100)
    lvl_icon = LEVEL_ICONS.get(st.session_state.level,"🌱")
    lvl_name = LEVEL_NAMES.get(st.session_state.level,"Spark")

    cm,cs = st.columns([1,3])
    with cm:
        st.markdown(f"<div class='nova-card'><div class='nova-face'>{emoji}</div>"
                    f"<div class='nova-text'>Nova AI</div></div>", unsafe_allow_html=True)
    with cs:
        st.markdown(f"""<div class='nova-card'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                <h2 style='color:white;margin:0;'>Nova says:</h2>
                <span style='font-size:20px;'>{user_avatar} <b style='color:white;'>{user_name}</b></span>
            </div>
            <p style='font-size:17px;font-weight:500;color:rgba(255,255,255,0.95);'>{msg}</p>
            <div style='margin-top:12px;'>
                <span style='font-size:13px;opacity:0.85;'>{lvl_icon} {lvl_name} · Level {st.session_state.level}
                &nbsp;·&nbsp; {st.session_state.xp} XP</span>
                <div class='xp-bar-outer'>
                    <div style='height:100%;width:{pct}%;background:linear-gradient(90deg,#c4b5fd,#f0abfc);border-radius:999px;'></div>
                </div>
                <span style='font-size:12px;opacity:0.7;'>{xp_now}/{xp_range} XP to next level</span>
            </div></div>""", unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown(f"## {user_avatar} {user_name}")
    st.sidebar.markdown(f"{lvl_icon} **{lvl_name}**  \nXP: **{st.session_state.xp}** · Quizzes: **{st.session_state.total_quizzes}**")
    if st.sidebar.button("🚪 Switch Profile"):
        st.session_state.active_user = None; st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio("", [
        "🏠 Home","🤖 Nova Tutor","🎯 Quiz Arena",
        "⚔️ Battle Mode","🃏 Flashcards","📅 Study Plan",
        "📉 Weak Topics","⏰ Exam Countdown",
        "🏆 Progress","🥇 Leaderboard","📝 About"
    ])

    # ── HOME ──────────────────────────────────────────
    if page == "🏠 Home":
        st.markdown(f"""<div class='card'>
            <h2>Welcome back, {user_name}! 👋</h2>
            <p>Practice quizzes, review flashcards, challenge a friend in Battle Mode,
            track weak topics, and count down to your next exam.</p></div>""",
            unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        for col,(icon,title,desc) in zip([c1,c2,c3,c4],[
            ("🤖","Nova Tutor","AI explanations on any topic."),
            ("🎯","Quiz Arena","Practice and earn XP."),
            ("⚔️","Battle Mode","Quiz duel with a friend!"),
            ("📉","Weak Topics","See where to improve.")]):
            with col:
                st.markdown(f"<div class='card' style='text-align:center;'>"
                            f"<div style='font-size:36px;'>{icon}</div>"
                            f"<h3 style='margin:8px 0 4px;'>{title}</h3>"
                            f"<p style='font-size:13px;'>{desc}</p></div>", unsafe_allow_html=True)
        if st.session_state.quiz_history:
            st.markdown("### 📋 Recent Activity")
            for e in reversed(st.session_state.quiz_history[-3:]):
                ps=int(e["score"]/e["total"]*100)
                bc="#22c55e" if ps>=80 else "#f59e0b" if ps>=60 else "#ef4444"
                st.markdown(f"<div class='history-item'><span>📚 <b>{e['topic']}</b></span>"
                            f"<span>{e['score']}/{e['total']}</span>"
                            f"<span style='color:{bc};font-weight:700;'>{ps}%</span>"
                            f"<span style='color:#a78bfa;'>+{e['xp']} XP</span>"
                            f"<span style='opacity:0.6;font-size:13px;'>{e['date']}</span></div>",
                            unsafe_allow_html=True)
        if st.session_state.exam_date:
            try:
                exam=datetime.strptime(st.session_state.exam_date,"%Y-%m-%d")
                dl=(exam-datetime.now()).days
                if dl>=0:
                    st.markdown(f"<div class='card' style='text-align:center;'>"
                                f"<h3>⏰ {st.session_state.exam_subject or 'Upcoming Exam'}</h3>"
                                f"<div style='font-size:48px;font-family:Syne,sans-serif;font-weight:900;color:#a78bfa;'>{dl}</div>"
                                f"<p>days remaining</p></div>", unsafe_allow_html=True)
            except: pass

    # ── LUMIO TUTOR ───────────────────────────────────
    elif page == "🤖 Nova Tutor":
        st.header("🤖 Ask Nova")
        q = st.text_area("Your question:", placeholder="e.g. Explain photosynthesis simply.", height=100)
        cb1,cb2 = st.columns([1,3])
        with cb1: go = st.button("✨ Explain", type="primary")
        with cb2: st.caption("Try: 'Newton's laws', 'What causes earthquakes?', 'How does compound interest work?'")
        if go:
            if not q.strip(): st.warning("Please write a question.")
            else:
                with st.spinner("Nova is thinking..."):
                    answer = ask_ai(q)
                st.markdown(f"<div class='card'><h3>Nova's Explanation</h3>"
                            f"<p style='line-height:1.9;'>{answer.replace(chr(10),'<br>')}</p></div>",
                            unsafe_allow_html=True)
                st.success("💡 Want to practice? Head to **Quiz Arena**!")

    # ── QUIZ ARENA ────────────────────────────────────
    elif page == "🎯 Quiz Arena":
        st.header("🎯 Quiz Arena")
        topic = st.text_input("Topic:", placeholder="e.g. photosynthesis, fractions, WWII...")
        if st.button("🎲 Generate Quiz", type="primary"):
            if not topic.strip(): st.warning("Please enter a topic.")
            else:
                with st.spinner("Generating your quiz..."):
                    st.session_state.quiz = generate_quiz(topic)
                    st.session_state.last_topic = topic
                    st.session_state.last_score = None

        if st.session_state.quiz:
            answers = {}
            for i,q in enumerate(st.session_state.quiz):
                st.markdown(f"<div class='quiz-box'>"
                            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
                            f"<span style='font-family:Syne,sans-serif;font-weight:800;font-size:17px;'>Question {i+1}</span>"
                            f"{diff_badge(q.get('difficulty','medium'))}</div>"
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
                    "topic":st.session_state.last_topic,"score":score,
                    "total":len(st.session_state.quiz),"xp":gained,
                    "date":datetime.now().strftime("%b %d, %H:%M")
                })
                update_weak_topics(st.session_state.last_topic, score, len(st.session_state.quiz))
                update_level_and_badges()

                if score == len(st.session_state.quiz):
                    play_sound("perfect"); trigger_confetti()
                elif score >= 3: play_sound("correct")
                else: play_sound("wrong")

                st.markdown(f"<div class='card' style='text-align:center;'>"
                            f"<h2>Score: {score} / {len(st.session_state.quiz)}</h2>"
                            f"<p style='font-size:18px;'>You earned <b>+{gained} XP</b>"
                            f"{'  🎉 (+20 bonus!)' if score==5 else ''}</p></div>",
                            unsafe_allow_html=True)
                st.info(rec(score, st.session_state.last_topic))

                st.subheader("📋 Detailed Results")
                for i,q in enumerate(st.session_state.quiz):
                    ok = answers[i]==q["answer"]
                    with st.expander(f"{'✅' if ok else '❌'} Q{i+1}: {q['question'][:55]}..."):
                        if ok: st.success(f"Correct! {answers[i]}")
                        else: st.error(f"Your answer: {answers[i]}"); st.success(f"Correct: {q['answer']}")
                        if q.get("explanation"): st.info(f"💡 {q['explanation']}")

                if score == len(st.session_state.quiz):
                    st.markdown(f"<div class='certificate'>"
                                f"<div style='font-size:64px;'>🏆</div><h1>Certificate of Achievement</h1>"
                                f"<p style='font-size:18px;'>Perfect score on <b>{st.session_state.last_topic}</b></p>"
                                f"<p>Earned by: <b>{user_name}</b></p>"
                                f"<p style='font-size:14px;opacity:0.7;'>{datetime.now().strftime('%B %d, %Y')}</p></div>",
                                unsafe_allow_html=True)

    # ── BATTLE MODE ───────────────────────────────────
    elif page == "⚔️ Battle Mode":
        st.header("⚔️ Quiz Battle Mode")
        st.markdown("<div class='card'><p>Two players answer the same quiz on the same screen. Most correct answers wins! 🏆</p></div>", unsafe_allow_html=True)
        if not st.session_state.battle_state:
            c1,c2 = st.columns(2)
            with c1: p1=st.text_input("Player 1:",value=user_name,key="bp1")
            with c2: p2=st.text_input("Player 2:",placeholder="Enter name...",key="bp2")
            bt=st.text_input("Topic:",placeholder="e.g. biology, history...")
            if st.button("⚔️ Start Battle!",type="primary"):
                if not p2.strip() or not bt.strip(): st.warning("Enter Player 2 name and topic.")
                else:
                    with st.spinner("Generating battle quiz..."):
                        bq=generate_quiz(bt)
                    st.session_state.battle_state={"players":[p1,p2],"topic":bt,"quiz":bq,"phase":1,"scores":{1:0,2:0}}
                    st.rerun()
        else:
            bs=st.session_state.battle_state; players=bs["players"]; phase=bs["phase"]; quiz=bs["quiz"]
            c1,cv,c2=st.columns([2,1,2])
            with c1: st.markdown(f"<div class='battle-p1'><div style='font-size:18px;font-weight:800;'>🔵 {players[0]}</div><div class='battle-score'>{bs['scores'][1]}</div></div>",unsafe_allow_html=True)
            with cv: st.markdown("<div style='text-align:center;padding-top:24px;font-family:Syne,sans-serif;font-size:28px;font-weight:900;'>VS</div>",unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='battle-p2'><div style='font-size:18px;font-weight:800;'>🔴 {players[1]}</div><div class='battle-score'>{bs['scores'][2]}</div></div>",unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            if phase in [1,2]:
                cur=players[phase-1]; col_icon="🔵" if phase==1 else "🔴"
                st.markdown(f"### {col_icon} {cur}'s Turn")
                st.info(f"Only **{cur}** should look now. Other player, look away! 👀")
                pa={}
                for i,q in enumerate(quiz):
                    st.markdown(f"<div class='quiz-box'><div style='display:flex;justify-content:space-between;margin-bottom:8px;'><span style='font-family:Syne,sans-serif;font-weight:800;'>Q{i+1}</span>{diff_badge(q.get('difficulty','medium'))}</div><p style='font-size:16px;font-weight:500;'>{q['question']}</p></div>",unsafe_allow_html=True)
                    pa[i]=st.radio("",q["options"],key=f"bt_{phase}_{i}",label_visibility="collapsed")
                if st.button(f"✅ Submit {cur}'s Answers",type="primary"):
                    sc=sum(1 for i,q in enumerate(quiz) if pa[i]==q["answer"])
                    bs["scores"][phase]=sc; bs["phase"]=phase+1
                    play_sound("correct" if sc>=3 else "wrong"); st.rerun()
            elif phase==3:
                s1=bs["scores"][1]; s2=bs["scores"][2]; total=len(quiz)
                st.markdown("## 🏆 Battle Results!")
                if s1>s2: winner=players[0]; st.session_state.battle_wins+=1; play_sound("perfect"); trigger_confetti()
                elif s2>s1: winner=players[1]; play_sound("perfect"); trigger_confetti()
                else: winner=None; play_sound("correct")
                c1,c2=st.columns(2)
                with c1: st.markdown(f"<div class='battle-p1' style='padding:28px;'><div style='font-size:20px;font-weight:800;'>🔵 {players[0]}</div><div class='battle-score'>{s1}/{total}</div><div>{int(s1/total*100)}%</div></div>",unsafe_allow_html=True)
                with c2: st.markdown(f"<div class='battle-p2' style='padding:28px;'><div style='font-size:20px;font-weight:800;'>🔴 {players[1]}</div><div class='battle-score'>{s2}/{total}</div><div>{int(s2/total*100)}%</div></div>",unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                if winner:
                    st.markdown(f"<div class='certificate'><div style='font-size:56px;'>⚔️</div><h1>Battle Winner</h1><h2>{winner}</h2><p>Won with {max(s1,s2)}/{total} correct answers!</p></div>",unsafe_allow_html=True)
                    update_level_and_badges()
                else:
                    st.markdown("<div class='card' style='text-align:center;'><div style='font-size:48px;'>🤝</div><h2>It's a Tie!</h2></div>",unsafe_allow_html=True)
                with st.expander("📋 Correct answers"):
                    for i,q in enumerate(quiz):
                        st.write(f"**Q{i+1}:** {q['question']}"); st.success(f"✅ {q['answer']}")
                        if q.get("explanation"): st.info(f"💡 {q['explanation']}")
                if st.button("🔄 New Battle",type="primary"): st.session_state.battle_state=None; st.rerun()

    # ── FLASHCARDS ────────────────────────────────────
    elif page == "🃏 Flashcards":
        st.header("🃏 Flashcards")
        topic=st.text_input("Topic:",placeholder="e.g. mitosis, French Revolution...")
        if st.button("🃏 Generate",type="primary"):
            if not topic.strip(): st.warning("Please enter a topic.")
            else:
                with st.spinner("Creating flashcards..."): st.session_state.flashcards=generate_flashcards(topic); st.session_state.flash_revealed={}
        if st.session_state.flashcards:
            if st.button("🔄 Reset All"): st.session_state.flash_revealed={}; st.rerun()
            cols=st.columns(2)
            for idx,card in enumerate(st.session_state.flashcards):
                with cols[idx%2]:
                    rev=st.session_state.flash_revealed.get(idx,False)
                    if rev:
                        st.markdown(f"<div class='flashcard' style='background:linear-gradient(135deg,#065f46,#10b981);color:white;'><div style='font-size:13px;letter-spacing:1px;text-transform:uppercase;opacity:0.8;margin-bottom:8px;'>DEFINITION</div><div style='font-size:18px;font-weight:600;line-height:1.5;'>{card['definition']}</div></div>",unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='flashcard'><div style='font-size:13px;letter-spacing:1px;text-transform:uppercase;opacity:0.6;margin-bottom:8px;'>TERM</div><div style='font-size:24px;font-weight:800;font-family:Syne,sans-serif;'>{card['term']}</div><div style='font-size:13px;opacity:0.6;margin-top:10px;'>Tap to reveal ↓</div></div>",unsafe_allow_html=True)
                    if st.button("🙈 Hide" if rev else "👁 Reveal",key=f"fl_{idx}"):
                        st.session_state.flash_revealed[idx]=not rev; st.rerun()

    # ── STUDY PLAN ────────────────────────────────────
    elif page == "📅 Study Plan":
        st.header("📅 AI Study Plan")
        topic=st.text_input("Topic:",placeholder="e.g. algebra, photosynthesis...")
        if st.button("📅 Generate Plan",type="primary"):
            if not topic.strip(): st.warning("Please enter a topic.")
            else:
                with st.spinner("Creating plan..."): st.session_state.study_plan_days=generate_study_plan(topic)
        if st.session_state.study_plan_days:
            icons=["🌱","📖","✏️","🔍","🏆"]
            for i,d in enumerate(st.session_state.study_plan_days):
                res=d.get("resource","")
                st.markdown(f"<div class='card'><div style='display:flex;align-items:center;gap:12px;margin-bottom:8px;'><span style='font-size:32px;'>{icons[i] if i<5 else '📌'}</span><div><h3 style='margin:0;'>{d.get('day','Day')}: {d.get('title','')}</h3>{'<span style=\"font-size:13px;opacity:0.7;\">📌 '+res+'</span>' if res else ''}</div></div><p>{d.get('task','')}</p></div>",unsafe_allow_html=True)
            st.download_button("📥 Download Calendar (.ics)",data=create_ics(st.session_state.study_plan_days),file_name="nova_plan.ics",mime="text/calendar")

    # ── WEAK TOPICS ───────────────────────────────────
    elif page == "📉 Weak Topics":
        st.header("📉 Weak Topic Analysis")
        st.markdown("<div class='card'><p>Nova tracks your quiz scores per topic. Anything below 70% shows here so you know where to focus.</p></div>",unsafe_allow_html=True)
        weak=get_weak_topics()
        if not weak: st.info("Complete at least one quiz to see your analysis! 🎯")
        else:
            needs=[t for t in weak if t["avg"]<70]; good=[t for t in weak if t["avg"]>=70]
            if needs:
                st.markdown("### ⚠️ Needs more practice")
                for t in needs:
                    c="#ef4444" if t["avg"]<50 else "#f59e0b"
                    st.markdown(f"<div class='weak-topic'><div><b>{t['topic']}</b><div style='font-size:12px;opacity:0.7;'>{t['attempts']} attempt(s)</div></div><div style='flex:1;margin:0 20px;'><div style='background:rgba(239,68,68,0.15);border-radius:999px;height:10px;'><div style='width:{t['avg']}%;height:100%;background:{c};border-radius:999px;'></div></div></div><span style='color:{c};font-weight:800;font-size:18px;'>{t['avg']}%</span></div>",unsafe_allow_html=True)
                    if st.button(f"🎯 Practice {t['topic']}",key=f"pr_{t['topic']}"): st.info(f"Go to **Quiz Arena** and type **{t['topic']}**!")
            if good:
                st.markdown("### ✅ Mastering")
                for t in good:
                    st.markdown(f"<div class='history-item'><span>📚 <b>{t['topic']}</b></span><span style='opacity:0.7;'>{t['attempts']} attempt(s)</span><span style='color:#22c55e;font-weight:800;font-size:18px;'>{t['avg']}% ✅</span></div>",unsafe_allow_html=True)
            if needs:
                w0=needs[0]
                st.markdown(f"<div class='tip-card'>✨ <b>Nova recommends:</b> Your weakest topic is <b>{w0['topic']}</b> ({w0['avg']}% avg). Ask Nova Tutor, make flashcards, then retake!</div>",unsafe_allow_html=True)

    # ── EXAM COUNTDOWN ────────────────────────────────
    elif page == "⏰ Exam Countdown":
        st.header("⏰ Exam Countdown")
        c1,c2=st.columns(2)
        with c1: subj=st.text_input("Exam subject:",value=st.session_state.exam_subject or "",placeholder="e.g. Biology Final...")
        with c2:
            dval=None
            if st.session_state.exam_date:
                try: dval=datetime.strptime(st.session_state.exam_date,"%Y-%m-%d").date()
                except: pass
            dinp=st.date_input("Exam date:",value=dval,min_value=datetime.now().date())
        if st.button("💾 Save",type="primary"):
            st.session_state.exam_date=dinp.strftime("%Y-%m-%d"); st.session_state.exam_subject=subj
            sync_profile(); st.success("Saved! ✅")
        if st.session_state.exam_date:
            try:
                exam=datetime.strptime(st.session_state.exam_date,"%Y-%m-%d"); dl=(exam-datetime.now()).days
                subj_d=st.session_state.exam_subject or "Your Exam"
                if dl<0: st.markdown("<div class='countdown-box'><div style='font-size:48px;'>🎉</div><h2 style='color:white;'>Exam completed!</h2></div>",unsafe_allow_html=True)
                else:
                    urg="🔴" if dl<=3 else "🟡" if dl<=7 else "🟢"
                    tip=("Final review only — focus on weak topics!" if dl<=3 else "Do practice quizzes every day." if dl<=7 else "You have time — build a study plan and stick to it.")
                    st.markdown(f"<div class='countdown-box'><div style='font-size:18px;opacity:0.8;margin-bottom:8px;'>{urg} {subj_d}</div><div class='countdown-number'>{dl}</div><div style='font-size:20px;color:rgba(255,255,255,0.7);margin:8px 0;'>day{'s' if dl!=1 else ''} remaining</div><div style='font-size:14px;color:rgba(255,255,255,0.6);margin-top:16px;'>📅 {exam.strftime('%A, %B %d, %Y')}</div></div>",unsafe_allow_html=True)
                    st.markdown(f"<div class='tip-card'>💡 <b>Nova says:</b> {tip}</div>",unsafe_allow_html=True)
            except: st.error("Invalid date.")
            if st.button("🗑️ Clear"): st.session_state.exam_date=None; st.session_state.exam_subject=""; sync_profile(); st.rerun()

    # ── PROGRESS ──────────────────────────────────────
    elif page == "🏆 Progress":
        st.header("🏆 Your Progress")
        lvl=st.session_state.level
        st.markdown(f"<div class='level-box'>{LEVEL_ICONS.get(lvl,'🌱')} {LEVEL_NAMES.get(lvl,'')} — Level {lvl}</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        xp_now,xp_range,_=xp_progress(); pct=int(min(xp_now/max(xp_range,1),1.0)*100)
        c1,c2,c3,c4=st.columns(4)
        for col,(icon,val,label) in zip([c1,c2,c3,c4],[
            ("🔢",st.session_state.xp,"Total XP"),("🎯",st.session_state.total_quizzes,"Quizzes Done"),
            ("⭐",st.session_state.last_score if st.session_state.get("last_score") is not None else "—","Last Score"),
            ("🏅",len(st.session_state.badges),"Badges")]):
            with col: st.markdown(f"<div class='metric-tile'><div style='font-size:28px;'>{icon}</div><div class='metric-value'>{val}</div><div class='metric-label'>{label}</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:14px;margin-bottom:4px;'>XP to next level: <b>{xp_now}/{xp_range}</b></div><div class='xp-bar-outer' style='height:20px;'><div style='height:100%;width:{pct}%;background:linear-gradient(90deg,#c4b5fd,#f0abfc);border-radius:999px;'></div></div>",unsafe_allow_html=True)
        st.markdown("### 🏅 Badges")
        if st.session_state.badges:
            html=""
            for bid in st.session_state.badges:
                rule=next((b for b in BADGE_RULES if b["id"]==bid),None)
                if rule:
                    cls=rule["cls"]; ico=rule["icon"]; lbl=rule["label"]
                    html+=f"<span class='badge {cls}'>{ico} {lbl}</span> "
            st.markdown(html,unsafe_allow_html=True)
        else: st.info("Complete quizzes to earn badges! 🎯")
        st.markdown("### 📋 Quiz History")
        if st.session_state.quiz_history:
            for e in reversed(st.session_state.quiz_history):
                ps=int(e["score"]/e["total"]*100)
                c="#22c55e" if ps>=80 else "#f59e0b" if ps>=60 else "#ef4444"
                st.markdown(f"<div class='history-item'><span>📚 <b>{e['topic']}</b></span><span style='opacity:0.7;'>{e['date']}</span><span>{e['score']}/{e['total']}</span><span style='color:{c};font-weight:700;'>{ps}%</span><span style='color:#a78bfa;'>+{e['xp']} XP</span></div>",unsafe_allow_html=True)
        else: st.info("No quiz history yet! 🎯")

    # ── LEADERBOARD ───────────────────────────────────
    elif page == "🥇 Leaderboard":
        st.header("🥇 Leaderboard")
        with st.spinner("Loading..."):
            board=st.session_state.leaderboard.copy()
            for name,data in load_profiles().items():
                ex=next((p for p in board if p["name"]==name),None)
                if ex: ex["xp"]=data.get("xp",0); ex["level"]=data.get("level",1)
                else: board.append({"name":name,"xp":data.get("xp",0),"level":data.get("level",1)})
        board.sort(key=lambda x:x["xp"],reverse=True)
        rank_icons={1:"🥇",2:"🥈",3:"🥉"}
        for rank,player in enumerate(board,1):
            is_you=player["name"]==user_name
            border="3px solid #a78bfa" if is_you else "1px solid rgba(167,139,250,0.2)"
            fw="800" if is_you else "600"; you="← You" if is_you else ""
            ri=rank_icons.get(rank,f"{rank}.")
            plvl=LEVEL_ICONS.get(player["level"],"")+" "+LEVEL_NAMES.get(player["level"],"")
            st.markdown(f"<div class='history-item' style='border:{border};padding:18px 22px;'><span style='font-size:24px;min-width:36px;'>{ri}</span><span style='font-weight:{fw};font-size:16px;flex:1;'>{player['name']} {you}</span><span style='opacity:0.7;'>{plvl}</span><span style='color:#a78bfa;font-weight:700;'>{player['xp']} XP</span></div>",unsafe_allow_html=True)
        st.caption("All Nova users with saved profiles appear here automatically.")

    # ── ABOUT ─────────────────────────────────────────
    elif page == "📝 About":
        st.header("📝 About Nova")
        for label,value in [
            ("Name","Nova 🚀 — from 'lumen', light of knowledge"),
            ("Mission","Make quality AI-powered studying accessible to every student, anywhere."),
            ("Features","AI explanations · Quizzes with sounds & animations · Flashcards · Battle Mode · Study Plans · Weak Topic Analysis · Exam Countdown · Multi-user Profiles · Leaderboard."),
            ("Stack","Streamlit Cloud · Groq API (Llama 3.1) · Supabase · Python · 100% free to run."),
        ]:
            st.markdown(f"<div class='card' style='padding:16px 24px;'><span style='font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:0.8px;opacity:0.6;'>{label}</span><p style='margin:4px 0 0;font-size:16px;'>{value}</p></div>",unsafe_allow_html=True)

    st.divider()
    st.caption("Nova 🚀 — Streamlit Cloud · Groq (Llama 3.1) · Supabase · 100% free")
