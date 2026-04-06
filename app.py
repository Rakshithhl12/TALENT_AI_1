# ==========================================================
# app.py — TalentAI v6.0  |  Reliable Sidebar + MySQL
# ==========================================================
import streamlit as st

st.set_page_config(
    page_title="TalentAI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.database import create_database_if_not_exists

@st.cache_resource
def init_db():
    try:
        create_database_if_not_exists()
        return True
    except Exception as e:
        return str(e)

db_ok = init_db()

from modules import (
    dashboard, analytics, resume_upload, resume_ranking,
    bulk_processing, job_matching, interview_scheduler,
    report_generation, chatbot,
)

# ──────────────────────────────────────────────────────────
# CSS — Simple, reliable, sidebar always visible
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@700;800&display=swap');

/* === BASE === */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background: #0B0F1C !important;
    color: #CBD5E1 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Background glow */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 800px 500px at 10% 5%,  rgba(59,130,246,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 600px 400px at 90% 95%, rgba(16,185,129,0.06) 0%, transparent 60%);
}

/* === HIDE ONLY WHAT WE MUST — keep header so toggle works === */
#MainMenu, footer, .stDeployButton { display: none !important; }

/* Zero-height header but overflow visible keeps the toggle button */
header[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    background: transparent !important;
    overflow: visible !important;
    position: relative !important;
    z-index: 1000 !important;
}

/* === SIDEBAR TOGGLE BUTTON === */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 999999 !important;
    width: 36px !important; height: 36px !important;
    align-items: center !important;
    justify-content: center !important;
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: background 0.2s, border-color 0.2s !important;
}
[data-testid="collapsedControl"]:hover {
    background: #1D4ED8 !important;
    border-color: #3B82F6 !important;
}
[data-testid="collapsedControl"] svg {
    color: #94A3B8 !important;
    fill: #94A3B8 !important;
    width: 16px !important; height: 16px !important;
}
[data-testid="collapsedControl"]:hover svg {
    color: #fff !important; fill: #fff !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: #0F172A !important;
    border-right: 1px solid #1E293B !important;
    width: 256px !important;
    min-width: 256px !important;
    max-width: 256px !important;
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
    padding: 0 !important;
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
section[data-testid="stSidebar"] {
    background: #0F172A !important;
}

/* Sidebar scrollable area */
[data-testid="stSidebarContent"] {
    background: #0F172A !important;
    padding: 0 !important;
    overflow-y: auto !important;
    height: 100% !important;
}

/* === SIDEBAR — RADIO NAV === */
/* Hide the radio widget label text */
[data-testid="stSidebar"] .stRadio > label { display: none !important; }

/* Radio container — vertical list */
[data-testid="stSidebar"] .stRadio > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    padding: 0 !important;
}

/* Each nav option label */
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 11px 20px !important;
    margin: 0 !important;
    border-radius: 0 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    cursor: pointer !important;
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    transition: all 0.15s !important;
    white-space: nowrap !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #E2E8F0 !important;
    background: rgba(255,255,255,0.04) !important;
    border-left-color: #475569 !important;
}
/* Active selected item */
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    color: #60A5FA !important;
    background: rgba(59,130,246,0.1) !important;
    border-left-color: #3B82F6 !important;
    font-weight: 600 !important;
}

/* Hide radio circle dots */
[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: rgba(255,255,255,0.04) !important;
    color: #94A3B8 !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    padding: 8px 16px !important;
    text-align: left !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.1) !important;
    color: #60A5FA !important;
    border-color: rgba(59,130,246,0.3) !important;
}

/* === MAIN CONTENT === */
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Page header bar */
.page-topbar {
    padding: 24px 36px 16px 36px;
    border-bottom: 1px solid #1E293B;
    margin-bottom: 24px;
    background: rgba(15,23,42,0.5);
    backdrop-filter: blur(10px);
    position: relative; z-index: 1;
}
.page-crumb {
    font-size: 0.68rem; color: #475569;
    letter-spacing: 0.08em; text-transform: uppercase;
    font-weight: 600; margin-bottom: 6px;
}
.page-topbar h1 {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(1.4rem, 2.2vw, 1.9rem);
    font-weight: 800; color: #F1F5F9;
    letter-spacing: -0.03em; line-height: 1.1;
}
.page-topbar p {
    font-size: 0.82rem; color: #475569;
    margin-top: 4px;
}
.accent { color: #3B82F6; }

/* Content padding */
.content-wrap {
    padding: 0 36px 40px;
    position: relative; z-index: 1;
}

/* === METRIC CARDS === */
[data-testid="stMetric"] {
    background: #131929 !important;
    border: 1px solid #1E293B !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    transition: all 0.2s !important;
}
[data-testid="stMetric"]:hover {
    border-color: #2563EB !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
}
[data-testid="stMetric"] label {
    font-size: 0.68rem !important; font-weight: 700 !important;
    letter-spacing: 0.09em !important; text-transform: uppercase !important;
    color: #475569 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.8rem !important; font-weight: 800 !important;
    color: #F1F5F9 !important;
}

/* === BUTTONS === */
.stButton > button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.84rem !important;
    border-radius: 9px !important; padding: 0.5rem 1.2rem !important;
    transition: all 0.18s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1D4ED8, #3B82F6) !important;
    color: #fff !important; border: none !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 22px rgba(37,99,235,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: #131929 !important; color: #94A3B8 !important;
    border: 1px solid #1E293B !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #1E293B !important; color: #E2E8F0 !important;
}
.stButton > button:not([kind]) {
    background: #131929 !important; color: #94A3B8 !important;
    border: 1px solid #1E293B !important;
}
.stButton > button:not([kind]):hover {
    background: #1E293B !important; color: #E2E8F0 !important;
}

/* === INPUTS === */
.stTextInput > div > div > input,
.stTextArea textarea, .stNumberInput input,
.stDateInput input, .stTimeInput input {
    background: #131929 !important;
    border: 1px solid #1E293B !important;
    border-radius: 9px !important; color: #E2E8F0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.87rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label, .stDateInput label, .stTimeInput label,
.stMultiselect label, .stSlider label, .stFileUploader label,
[data-testid="stWidgetLabel"] {
    color: #64748B !important; font-size: 0.75rem !important;
    font-weight: 600 !important; letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: #131929 !important;
    border-color: #1E293B !important;
    border-radius: 9px !important; color: #E2E8F0 !important;
}
[data-baseweb="menu"] {
    background: #0F172A !important;
    border: 1px solid #1E293B !important;
    border-radius: 9px !important;
}
[data-baseweb="option"] { background: transparent !important; color: #CBD5E1 !important; }
[data-baseweb="option"]:hover { background: rgba(59,130,246,0.12) !important; }

/* === TABS === */
.stTabs [data-baseweb="tab-list"] {
    background: #131929 !important;
    border-radius: 10px !important; padding: 4px !important;
    border: 1px solid #1E293B !important; gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #64748B !important;
    border-radius: 7px !important; font-size: 0.82rem !important;
    font-weight: 600 !important; border: none !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(59,130,246,0.15) !important; color: #60A5FA !important;
}

/* === DATAFRAME === */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid #1E293B !important; overflow: hidden !important;
}

/* === EXPANDERS === */
details {
    background: #131929 !important; border: 1px solid #1E293B !important;
    border-radius: 10px !important; margin-bottom: 6px !important; overflow: hidden !important;
}
details:hover { border-color: #2563EB !important; }
details summary {
    padding: 12px 16px !important; color: #CBD5E1 !important;
    font-size: 0.87rem !important; font-weight: 600 !important; cursor: pointer !important;
}
details > div { padding: 0 16px 16px !important; }

/* === ALERTS === */
[data-testid="stAlert"] { border-radius: 10px !important; }
.stSuccess > div { background:rgba(16,185,129,0.08)!important; border-color:rgba(16,185,129,0.25)!important; color:#6EE7B7!important; border-radius:10px!important; }
.stInfo    > div { background:rgba(59,130,246,0.08)!important; border-color:rgba(59,130,246,0.25)!important; color:#93C5FD!important; border-radius:10px!important; }
.stWarning > div { background:rgba(245,158,11,0.08)!important; border-color:rgba(245,158,11,0.25)!important; color:#FCD34D!important; border-radius:10px!important; }
.stError   > div { background:rgba(239,68,68,0.08)!important; border-color:rgba(239,68,68,0.25)!important; color:#FCA5A5!important; border-radius:10px!important; }

/* === FILE UPLOADER === */
[data-testid="stFileUploaderDropzone"] {
    background: #131929 !important;
    border: 2px dashed #1E293B !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #3B82F6 !important; background: rgba(59,130,246,0.04) !important;
}

/* === PROGRESS === */
[data-testid="stProgressBar"] > div {
    background: #1E293B !important; border-radius: 999px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg,#2563EB,#10B981) !important;
    border-radius: 999px !important;
}

/* === CHAT === */
[data-testid="stChatMessage"] {
    background: #131929 !important; border: 1px solid #1E293B !important;
    border-radius: 12px !important; margin-bottom: 8px !important;
}

/* === DOWNLOAD BUTTON === */
[data-testid="stDownloadButton"] > button {
    background: rgba(16,185,129,0.08) !important; color: #34D399 !important;
    border: 1px solid rgba(16,185,129,0.25) !important;
    border-radius: 9px !important; font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(16,185,129,0.15) !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.2) !important;
}

/* === MISC === */
hr { border-color: #1E293B !important; margin: 18px 0 !important; }
[data-baseweb="tag"] {
    background: rgba(59,130,246,0.12) !important;
    border-color: rgba(59,130,246,0.2) !important;
    color: #93C5FD !important; border-radius: 6px !important;
}
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0B0F1C; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* === RESPONSIVE === */
@media (max-width: 768px) {
    .content-wrap  { padding: 0 16px 24px !important; }
    .page-topbar   { padding: 16px 16px 12px !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────
with st.sidebar:
    # ── Logo & DB badge ──
    badge_cls   = "live" if db_ok is True else "err"
    badge_label = "MySQL Live" if db_ok is True else "DB Error"
    badge_color = "#10B981" if db_ok is True else "#EF4444"
    badge_bg    = "rgba(16,185,129,0.1)" if db_ok is True else "rgba(239,68,68,0.1)"
    badge_border= "rgba(16,185,129,0.25)" if db_ok is True else "rgba(239,68,68,0.25)"

    st.markdown(f"""
    <div style="padding:24px 20px 16px; border-bottom:1px solid #1E293B;
                background:linear-gradient(135deg,rgba(59,130,246,0.06),rgba(139,92,246,0.04));">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#3B82F6,#8B5CF6);
                        border-radius:9px;display:flex;align-items:center;justify-content:center;
                        font-size:18px;box-shadow:0 4px 12px rgba(59,130,246,0.4);flex-shrink:0;">⚡</div>
            <span style="font-family:'Outfit',sans-serif;font-size:1.2rem;font-weight:800;
                         color:#F1F5F9;letter-spacing:-0.02em;">TalentAI</span>
        </div>
        <div style="font-size:0.62rem;color:#475569;letter-spacing:0.07em;
                    text-transform:uppercase;margin-left:44px;">Enterprise Recruitment</div>
        <div style="display:inline-flex;align-items:center;gap:5px;margin-top:10px;
                    padding:4px 10px;border-radius:999px;font-size:0.67rem;font-weight:700;
                    letter-spacing:0.05em;text-transform:uppercase;
                    background:{badge_bg};color:{badge_color};border:1px solid {badge_border};">
            <span style="width:6px;height:6px;border-radius:50%;background:{badge_color};
                         display:inline-block;animation:blink 2s infinite;"></span>
            {badge_label}
        </div>
    </div>
    <style>@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.2}}}}</style>
    """, unsafe_allow_html=True)

    # ── Section label ──
    st.markdown("""
    <div style="padding:16px 20px 6px;font-size:0.6rem;font-weight:700;
                letter-spacing:0.12em;text-transform:uppercase;color:#334155;">
        Navigation
    </div>""", unsafe_allow_html=True)

    # ── Nav radio ──
    NAV_LABELS = [
        "📊  Dashboard",
        "📂  Resume Upload",
        "🤖  AI Ranking",
        "⚡  Bulk Processing",
        "🎯  Job Matching",
        "📅  Interviews",
        "📈  Analytics",
        "📄  Reports",
        "💬  Chatbot",
    ]
    NAV_MAP = {
        "📊  Dashboard":       "Dashboard",
        "📂  Resume Upload":   "Resume Upload",
        "🤖  AI Ranking":      "AI Ranking",
        "⚡  Bulk Processing": "Bulk Processing",
        "🎯  Job Matching":    "Job Matching",
        "📅  Interviews":      "Interviews",
        "📈  Analytics":       "Analytics",
        "📄  Reports":         "Reports",
        "💬  Chatbot":         "Chatbot",
    }

    choice = st.radio("nav", NAV_LABELS, label_visibility="collapsed")
    active = NAV_MAP[choice]

    # ── Actions ──
    st.markdown("""
    <div style="padding:14px 20px 6px;font-size:0.6rem;font-weight:700;
                letter-spacing:0.12em;text-transform:uppercase;color:#334155;
                border-top:1px solid #1E293B;margin-top:8px;">
        Actions
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    with col2:
        if st.button("❓ Help", use_container_width=True):
            st.session_state["show_help"] = True

    # ── Footer ──
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;width:256px;
                padding:12px 20px;border-top:1px solid #1E293B;
                background:#0F172A;text-align:center;">
        <span style="font-size:0.62rem;color:#334155;">TalentAI v6.0 · MySQL · AI</span>
    </div>
    <div style="height:48px;"></div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# PAGE HEADER
# ──────────────────────────────────────────────────────────
PAGE_META = {
    "Dashboard":       ("📊", "Dashboard",       "Live recruitment metrics from MySQL"),
    "Resume Upload":   ("📂", "Resume Upload",    "Parse · Score · Store resumes in MySQL"),
    "AI Ranking":      ("🤖", "AI Ranking",       "AI-powered candidate ranking & status updates"),
    "Bulk Processing": ("⚡", "Bulk Processing",  "Mass re-score, bulk update, or delete records"),
    "Job Matching":    ("🎯", "Job Matching",     "Match all candidates against any job role"),
    "Interviews":      ("📅", "Interviews",       "Schedule and manage interview pipeline"),
    "Analytics":       ("📈", "Analytics",        "Live visual hiring insights from MySQL"),
    "Reports":         ("📄", "Reports",          "Export CSV and multi-sheet Excel reports"),
    "Chatbot":         ("💬", "HR Chatbot",       "Ask anything — powered by your MySQL data"),
}
icon, title, subtitle = PAGE_META[active]

st.markdown(f"""
<div class="page-topbar">
    <div class="page-crumb">TalentAI &rsaquo; {title}</div>
    <h1>{icon}&nbsp;<span class="accent">{title}</span></h1>
    <p>{subtitle}</p>
</div>
<div class="content-wrap">
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# ROUTING
# ──────────────────────────────────────────────────────────
if   active == "Dashboard":       dashboard.run()
elif active == "Resume Upload":   resume_upload.run()
elif active == "AI Ranking":      resume_ranking.run()
elif active == "Bulk Processing": bulk_processing.run()
elif active == "Job Matching":    job_matching.run()
elif active == "Interviews":      interview_scheduler.run()
elif active == "Analytics":       analytics.run()
elif active == "Reports":         report_generation.run()
elif active == "Chatbot":         chatbot.run()

st.markdown("</div>", unsafe_allow_html=True)
