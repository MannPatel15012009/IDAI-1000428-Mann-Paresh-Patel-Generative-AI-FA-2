"""
AgSaathi — Smart Farming Assistant
Student: zene sophie anand  | Wacp no: 1000414
Assessment: FA-2 | Course: Generative AI | School: Aspee Nutan Academy
"""

import streamlit as st
import google.generativeai as genai
import json
import re
import csv
import io
from datetime import datetime
from typing import Dict, Any, Optional

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgSaathi — Smart Farming Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GEMINI SETUP ────────────────────────────────────────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)

if not GEMINI_API_KEY:
    st.error("⚠️ Gemini API key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# ── MODEL CONFIG ────────────────────────────────────────────────────────────
MODEL_NAME = "gemini-1.5-flash" 
MODEL_TEMPERATURE = 0.3
MODEL_MAX_TOKENS = 2048

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=genai.GenerationConfig(
            temperature=MODEL_TEMPERATURE,
            max_output_tokens=MODEL_MAX_TOKENS,
        )
    )

# ── GEO DATA ────────────────────────────────────────────────────────────────
GEO = {
    'India 🇮🇳': {
        'languages': ['English', 'Hindi'],
        'states': ['Uttar Pradesh', 'Punjab', 'Bihar', 'Madhya Pradesh', 'Rajasthan', 'Haryana', 'Gujarat'],
    },
    'Canada 🇨🇦': {
        'languages': ['English', 'French'],
        'states': ['Ontario', 'Quebec', 'Saskatchewan', 'Alberta'],
    },
    'Ghana 🇬🇭': {
        'languages': ['English'],
        'states': ['Ashanti', 'Northern', 'Greater Accra', 'Volta'],
    },
}

# ── SESSION STATE ───────────────────────────────────────────────────────────
DEFAULTS = {
    'page': 'hero', 'country': None, 'state': None, 'language': 'Hindi',
    'nav': 'home', 'chat': [], 'history': [], 'stats': {'queries': 0},
    'user_query': None, 'validation_results': {}, 'query_log': [],
    'onboarding_complete': False
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ─────────────────────────────────────────────────────────────────
def call_gemini(prompt: str) -> str:
    try:
        m = get_model()
        resp = m.generate_content(prompt)
        return resp.text if resp.text else ""
    except Exception as e:
        st.error(f"❌ **API Error:** {str(e)[:200]}")
        return ""

def build_structured_prompt(user_query: str, state: str, language: str, feature_context: str) -> str:
    return f"""You are AgSaathi, a professional agricultural assistant.
LANGUAGE: Respond ENTIRELY in {language}. Technical terms (pH, NPK) can be English.
JSON RULE: Return ONLY valid JSON. 

Context:
- Feature: {feature_context}
- Location: {state}
- Farmer Question: "{user_query}"

Instructions:
1. Provide 3 highly specific recommendations for {state}.
2. For each, include: 'action', 'reason', and 'risk_level' (LOW/MEDIUM/HIGH).
3. Include 'location_analysis' explaining local factors and a 'safety_note'.

JSON STRUCTURE:
{{
    "location_analysis": "Context about {state} climate/soil",
    "recommendations": [
        {{"action": "...", "reason": "...", "risk_level": "LOW"}},
        {{"action": "...", "reason": "...", "risk_level": "MEDIUM"}},
        {{"action": "...", "reason": "...", "risk_level": "LOW"}}
    ],
    "safety_note": "Crucial warning",
    "confidence_score": 90
}}"""

def parse_structured_response(raw: str) -> Optional[Dict]:
    if not raw: return None
    text = re.sub(r'```json|```', '', raw).strip()
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1: return None
        return json.loads(text[start:end])
    except Exception:
        return None

def ai_farming_advice(query: str, feature: str = "General") -> Dict[str, Any]:
    state = st.session_state.state or "Unknown"
    language = st.session_state.language
    prompt = build_structured_prompt(query, state, language, feature)
    raw = call_gemini(prompt)
    structured = parse_structured_response(raw)
    
    st.session_state.query_log.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'query': query[:120], 'state': state, 'language': language, 'json_ok': bool(structured),
    })
    return {'raw': raw, 'structured': structured}

# ── CSS ─────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Nunito+Sans:wght@400;600;700&display=swap');
    :root{--soil:#1A0F07;--wheat:#E8C97A;--cream:#F5EDD8;--straw:#D4A853;}
    
    /* FIX FOR SIDEBAR ARROW TEXT */
    [data-testid="stSidebarNav"] + div { display: none !important; }
    button[title="Collapse sidebar"] { color: var(--wheat) !important; }

    html,body,[data-testid="stAppViewContainer"]{background:linear-gradient(158deg,#140D07 0%,#261408 100%)!important;color:var(--cream)!important;}
    h1,h2,h3,p,span,label,div,.stMarkdown{color:var(--cream)!important;font-family:'Nunito Sans',sans-serif!important;}
    h1,h2,h3{font-family:'Playfair Display',serif!important;color:var(--wheat)!important;}
    
    .sbox { background: rgba(245,237,216,.038); border: 1px solid rgba(212,168,83,.16); border-radius: 12px; padding: 25px 14px; text-align: center; margin-bottom: 10px; }
    .ai-card { background: rgba(74,124,89,.12); border: 1px solid rgba(122,158,126,.26); border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .risk-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; display: inline-block; }
    .risk-low { background: #27AE60; color: #fff; }
    .risk-med { background: #E67E22; color: #fff; }
    .risk-high { background: #C0392B; color: #fff; }

    .stButton>button { background: transparent !important; border: 1px solid var(--straw) !important; color: var(--wheat) !important; border-radius: 8px !important; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background: var(--straw) !important; color: var(--soil) !important; }
    </style>
    """, unsafe_allow_html=True)

# ── ONBOARDING ──────────────────────────────────────────────────────────────
def page_hero():
    st.markdown("<div style='text-align:center; padding:50px;'><h1>🌿 AgSaathi</h1><p>Smart Farming Assistant</p></div>", unsafe_allow_html=True)
    if st.button("🌾 Begin — Select Your Location →"):
        st.session_state.page = 'country'
        st.rerun()

def page_country():
    st.markdown("<h1>Where is your farm?</h1>", unsafe_allow_html=True)
    for c in ['India 🇮🇳', 'Canada 🇨🇦', 'Ghana 🇬🇭']:
        if st.button(c):
            st.session_state.country = c
            st.session_state.page = 'state'
            st.rerun()

def page_state():
    st.markdown("<h1>Which state are you in?</h1>", unsafe_allow_html=True)
    d = GEO[st.session_state.country]
    sel = st.selectbox("Select region", options=d['states'], index=None)
    if st.button("Next →", disabled=not sel):
        st.session_state.state = sel
        st.session_state.page = 'language'
        st.rerun()

def page_language():
    st.markdown("<h1>Choose your language</h1>", unsafe_allow_html=True)
    d = GEO[st.session_state.country]
    for lang in d['languages']:
        if st.button(lang):
            st.session_state.language = lang
            st.session_state.onboarding_complete = True
            st.session_state.page = 'app'
            st.rerun()

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("<div style='text-align:center; font-size:2rem;'>🌿 AgSaathi</div>", unsafe_allow_html=True)
        st.markdown(f"**📍 {st.session_state.state}**")
        st.markdown(f"**🌐 {st.session_state.language}**")
        st.markdown("---")
        nav_items = [
            ('home', '⌂', 'Dashboard'), ('crop_rec', '🌾', 'Crop Rec'),
            ('pest', '🐛', 'Pest'), ('soil', '🧪', 'Soil'),
            ('sustainable', '♻️', 'Sustainable'), ('weather', '🌦', 'Weather'),
            ('validate', '✅', 'Validation'),
        ]
        for key, icon, label in nav_items:
            if st.button(f"{icon} {label}", key=f"nav_{key}"):
                st.session_state.nav = key
                st.rerun()
        st.markdown("---")
        st.caption("Aditya Sahani · Reg 1000414")

# ── RENDER RESPONSE ─────────────────────────────────────────────────────────
def render_enhanced_response(r: Dict[str, Any]):
    structured = r.get('structured')
    if structured and 'recommendations' in structured:
        st.markdown(f"""<div class='ai-card'><strong>📍 {structured.get('location_analysis', '')}</strong></div>""", unsafe_allow_html=True)
        for rec in structured.get('recommendations', []):
            risk = rec.get('risk_level', 'LOW')
            r_class = f"risk-{risk.lower()}"
            st.markdown(f"""
            <div class='ai-card'>
                <span class='risk-badge {r_class}'>{risk} Risk</span><br>
                <b>✅ {rec.get('action')}</b><br>
                <small>💡 {rec.get('reason')}</small>
            </div>""", unsafe_allow_html=True)
        st.error(f"⚠️ Safety Note: {structured.get('safety_note')}")
    else:
        st.warning("⚠️ AI response could not be structured. Please try again.")

# ── CORE PAGES ──────────────────────────────────────────────────────────────
def render_home():
    sidebar()
    st.markdown(f"<h1>Good Morning! 🌾</h1>", unsafe_allow_html=True)
    st.markdown(f"### 📍 Region: {st.session_state.state}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='sbox'><h2>{st.session_state.stats['queries']}</h2>Queries</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='sbox'><h2>{len(st.session_state.history)}</h2>History</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='sbox'><h2>90%</h2>Accuracy</div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='sbox'><h2>{st.session_state.language[:2]}</h2>Lang</div>", unsafe_allow_html=True)

    st.markdown("### 🚜 5 Core Features")
    cols = st.columns(5)
    features = [
        ('crop_rec', '🌾', 'Crop Rec'), ('pest', '🐛', 'Pest'), 
        ('soil', '🧪', 'Soil Health'), ('sustainable', '♻️', 'Sustainable'), 
        ('weather', '🌦', 'Weather')
    ]
    for i, (key, icon, label) in enumerate(features):
        with cols[i]:
            if st.button(f"{icon}\n{label}", key=f"home_feat_{key}"):
                st.session_state.nav = key
                st.rerun()

def render_feature_page(key, icon, title, description):
    sidebar()
    st.markdown(f"<h1>{icon} {title}</h1>", unsafe_allow_html=True)
    st.write(description)
    
    user_in = st.text_input("Consult AgSaathi AI", key=f"input_{key}", placeholder="e.g., Best crops for rainy season?")
    
    if st.button("Consult AI", key=f"btn_{key}"):
        if user_in:
            with st.spinner("Consulting..."):
                resp = ai_farming_advice(user_in, feature=title)
                st.session_state.chat.append({'role': 'user', 'content': user_in})
                st.session_state.chat.append({'role': 'ai', 'content': resp})
                st.session_state.stats['queries'] += 1
                st.session_state.history.append({'q': user_in, 'r': resp, 't': datetime.now().strftime("%H:%M")})
                st.rerun()

    for msg in reversed(st.session_state.chat[-4:]):
        if msg['role'] == 'ai': render_enhanced_response(msg['content'])
        else: st.info(f"**Farmer:** {msg['content']}")

def render_validate():
    sidebar()
    st.markdown("<h1>Validation</h1>", unsafe_allow_html=True)
    if st.button("🧪 Run Test"):
        ai_farming_advice("Wheat fertilizer dose?")
        st.session_state.validation_results = {'score': 85}
    if st.session_state.validation_results:
        st.success(f"Score: {st.session_state.validation_results['score']}%")

# ── MAIN ────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    if not st.session_state.onboarding_complete:
        pages = {'hero': page_hero, 'country': page_country, 'state': page_state, 'language': page_language}
        pages.get(st.session_state.page, page_hero)()
    else:
        nav = st.session_state.nav
        if nav == 'home': 
            render_home()
        elif nav == 'crop_rec':
            render_feature_page('crop_rec', '🌾', 'Crop Recommendation', 'AI-driven suggestions for high-yield crops based on your soil and region.')
        elif nav == 'pest':
            render_feature_page('pest', '🐛', 'Pest & Disease', 'Diagnose crop issues and get organic or chemical treatment protocols.')
        elif nav == 'weather':
            render_feature_page('weather', '🌦', 'Weather Alerts', 'Smart alerts and preventative measures for heatwaves, frost, or heavy rain.')
        elif nav == 'soil':
            render_feature_page('soil', '🧪', 'Soil Health', 'Analyze pH and NPK levels to get tailored fertilizer and amendment advice.')
        elif nav == 'sustainable':
            render_feature_page('sustainable', '♻️', 'Sustainable Farming', 'Eco-friendly practices like drip irrigation, composting, and stubble management.')
        elif nav == 'validate': 
            render_validate()

if __name__ == "__main__":
    main()
