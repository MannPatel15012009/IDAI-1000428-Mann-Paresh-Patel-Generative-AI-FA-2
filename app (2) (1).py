import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="🌾 FarmaBuddy",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- FONT AWESOME + ULTRA CLEAN CSS ----------
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<style>
    /* ----- GLOBAL: BLACK TEXT, NO FUNNY STYLES ----- */
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        box-sizing: border-box;
    }
    .stApp {
        background-color: #F9FFF9;
    }
    p, li, div:not(.header-container):not(.sidebar-header):not(.title-text):not(.subtitle-text):not(.badge):not(.stButton > button):not(.stTabs [data-baseweb="tab"]):not(.footer) {
        color: #000000 !important;
    }

    /* ----- VIBRANT SOLID COLOR PALETTE ----- */
    :root {
        --green: #2E7D32;
        --orange: #FF8C42;
        --blue: #3A86FF;
        --yellow: #FFBE0B;
        --red: #FF595E;
        --purple: #9B5DE5;
        --light-bg: #F8FFF8;
        --white: #FFFFFF;
        --black: #000000;
    }

    /* ----- HEADER – BOLD, CLEAN ----- */
    .header-container {
        background-color: var(--green);
        padding: 2rem 2.5rem;
        border-radius: 30px 30px 30px 0;
        margin-bottom: 2rem;
        border: 6px solid var(--yellow);
        box-shadow: 12px 12px 0 rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .header-text { flex: 2; }
    .header-icon {
        flex: 1;
        text-align: center;
        font-size: 5rem;
        color: var(--yellow);
        text-shadow: 6px 6px 0 rgba(0,0,0,0.1);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .title-text {
        font-size: 3.8rem !important;
        font-weight: 900 !important;
        color: white !important;
        margin-bottom: 0.2rem !important;
        text-shadow: 6px 6px 0 rgba(0,0,0,0.1);
        line-height: 1.2;
    }
    .subtitle-text {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--yellow) !important;
        text-shadow: 3px 3px 0 rgba(0,0,0,0.1);
    }

    /* ----- SIDEBAR – CRYSTAL CLEAR DROPDOWNS ----- */
    .sidebar .sidebar-content {
        background-color: var(--green);
        border-right: 8px solid var(--yellow);
        padding-top: 1.5rem;
    }
    .sidebar-header {
        background-color: var(--yellow);
        padding: 1.2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        border: 4px solid white;
        text-align: center;
    }
    .sidebar-header * { color: black !important; }

    /* ----- INPUT LABELS – ICON + TEXT, ABOVE THE WIDGET ----- */
    .input-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        color: white !important;
        margin-bottom: 6px;
        padding-left: 4px;
    }
    .input-label i {
        font-size: 1.2rem;
        width: 24px;
        text-align: center;
        color: white !important;
    }

    /* ----- BIG, VISIBLE WIDGETS ----- */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="multiselect"] > div {
        background-color: white !important;
        border: 4px solid var(--orange) !important;
        border-radius: 20px !important;
        color: black !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        margin-bottom: 16px !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="input"] > div:hover,
    div[data-baseweb="multiselect"] > div:hover {
        border-color: var(--red) !important;
    }
    /* Dropdown menu itself */
    div[data-baseweb="select"] div[data-baseweb="popover"] {
        background-color: white !important;
        border: 3px solid var(--orange) !important;
        border-radius: 15px !important;
    }

    /* ----- TABS – ICONS VIA CSS PSEUDO-ELEMENTS (NO RAW HTML) ----- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: var(--yellow);
        padding: 12px;
        border-radius: 60px;
        border: 4px solid white;
        box-shadow: 8px 8px 0 rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        display: flex;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: 70px;
        background-color: white !important;
        border-radius: 50px !important;
        color: black !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        border: 4px solid var(--green) !important;
        padding: 0 2rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px;
        white-space: nowrap;
    }
    /* Add icons via pseudo-elements */
    .stTabs [data-baseweb="tab"]:nth-child(1)::before {
        font-family: "Font Awesome 6 Free";
        content: "\\f0ae";  /* list-check */
        font-weight: 900;
        font-size: 1.4rem;
        margin-right: 6px;
        color: var(--green);
    }
    .stTabs [data-baseweb="tab"]:nth-child(2)::before {
        font-family: "Font Awesome 6 Free";
        content: "\\f544";  /* robot */
        font-weight: 900;
        font-size: 1.4rem;
        margin-right: 6px;
        color: var(--green);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--green) !important;
        color: white !important;
        border-color: var(--yellow) !important;
    }
    .stTabs [aria-selected="true"]::before {
        color: white !important;
    }

    /* ----- CARDS – CLEAN SHADOW, GOOD SPACING ----- */
    .recommendation-card {
        background-color: white;
        border-radius: 30px 30px 30px 0;
        padding: 1.8rem 2rem;
        margin: 1.5rem 0;
        border-left: 12px solid var(--green);
        box-shadow: 12px 12px 0 rgba(46,125,50,0.12);
        transition: all 0.2s;
    }
    .recommendation-card:hover {
        transform: translateY(-5px);
        box-shadow: 16px 16px 0 rgba(46,125,50,0.18);
    }
    .recommendation-card h4 {
        color: var(--green) !important;
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        border-bottom: 4px dashed var(--yellow);
        padding-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* ----- CHAT BUBBLES – ICON & TEXT VERTICAL ALIGNED ----- */
    .user-message, .ai-message {
        padding: 1.2rem 1.8rem;
        border-radius: 40px 40px 40px 0;
        margin: 1rem 0;
        border: 4px solid white;
        box-shadow: 8px 8px 0 rgba(0,0,0,0.08);
        max-width: 85%;
        font-size: 1.05rem;
        display: flex;
        align-items: flex-start;
        gap: 14px;
    }
    .user-message i, .ai-message i {
        font-size: 1.8rem;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .user-message p, .ai-message p {
        color: black !important;
        font-weight: 500;
        margin: 0;
        flex: 1;
        line-height: 1.5;
    }
    .user-message {
        background-color: #D4EDF7;
        border-left: 12px solid var(--blue);
        margin-left: auto;
    }
    .ai-message {
        background-color: #E2F3E2;
        border-left: 12px solid var(--green);
    }

    /* ----- BADGES – ICON + TEXT INLINE, CENTERED ----- */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0.25rem;
        border: 3px solid white;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.1);
        background-color: var(--orange);
        color: white !important;
    }
    .badge i { font-size: 1.1rem; }

    /* ----- FARM TILES – CLEAN, CENTERED ----- */
    .farm-tile {
        background-color: white;
        border-radius: 20px;
        padding: 1.4rem 0.5rem;
        border-bottom: 10px solid var(--yellow);
        box-shadow: 8px 8px 0 rgba(0,0,0,0.06);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        height: 100%;
    }
    .farm-tile i { font-size: 2.8rem; color: var(--green); }
    .farm-tile h3 { color: var(--green); font-weight: 800; margin: 0; font-size: 1.4rem; }
    .farm-tile p { margin: 0; font-size: 0.9rem; }

    /* ----- BUTTONS – JUMBO, ICON LEFT, TEXT CENTERED ----- */
    .stButton > button {
        background-color: var(--orange) !important;
        color: white !important;
        border: 4px solid white !important;
        border-radius: 50px !important;
        padding: 0.9rem 1.8rem !important;
        font-weight: 800 !important;
        font-size: 1.3rem !important;
        box-shadow: 8px 8px 0 rgba(0,0,0,0.1) !important;
        transition: all 0.1s ease !important;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }
    .stButton > button i { font-size: 1.4rem; }
    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 12px 12px 0 rgba(0,0,0,0.15) !important;
        background-color: var(--red) !important;
    }

    /* ----- FOOTER – CLEAN & BRIGHT ----- */
    .footer {
        background-color: var(--green);
        padding: 2rem;
        border-radius: 40px 40px 0 0;
        border-top: 8px solid var(--yellow);
        color: white;
        text-align: center;
        margin-top: 3rem;
    }
    .footer * { color: white !important; }
    .footer i { margin: 0 10px; font-size: 1.5rem; }

    /* ----- CUSTOM PROMPT EDITOR ----- */
    .prompt-editor {
        background-color: #FFF9E6;
        border-left: 8px solid var(--yellow);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 2px solid var(--yellow);
    }
    textarea {
        border: 3px solid var(--green) !important;
        border-radius: 15px !important;
        font-size: 0.95rem !important;
    }

    /* ----- FEEDBACK EMOJIS – BIG & CENTERED ----- */
    .stButton button[key*="fb"] {
        font-size: 2.2rem !important;
        padding: 0.3rem !important;
        background-color: var(--yellow) !important;
        color: black !important;
        border: 3px solid white !important;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.1) !important;
    }
    .stButton button[key*="fb"]:hover {
        transform: scale(1.1);
        background-color: #FFD966 !important;
    }

    /* ----- STREAMLIT HIDDEN LABELS ----- */
    .stSelectbox label, .stTextInput label, .stMultiSelect label, .stSlider label {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- API KEY ----------------
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("🔐 API Key Missing - Please add GOOGLE_API_KEY to Streamlit Secrets")
    st.stop()
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# ---------------- HEADER ----------------
st.markdown("""
<div class="header-container">
    <div class="header-text">
        <h1 class="title-text"><i class="fas fa-leaf" style="margin-right:12px;"></i>FarmaBuddy</h1>
        <h4 class="subtitle-text"><i class="fas fa-robot"></i> AI Farmer Friend</h4>
        <p style="color: white; font-size: 1.3rem; margin-top: 0.5rem;">
            <i class="fas fa-seedling"></i> Smart advice, big harvests  <i class="fas fa-tractor"></i>
        </p>
    </div>
    <div class="header-icon">
        <i class="fas fa-sprout"></i>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR (CRYSTAL CLEAR DROPDOWNS) ----------------
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h3 style="margin:0;">🧑‍🌾 Your Farm Setup</h3></div>', unsafe_allow_html=True)

    # ---- REGION – FULLY VISIBLE, ICON INSIDE LABEL ----
    st.markdown('<label class="input-label"><i class="fas fa-globe-americas"></i> Where is your farm?</label>', unsafe_allow_html=True)
    region = st.selectbox(
        "region",
        ["India", "Ghana", "Canada", "USA", "Australia", "Brazil", "Kenya", "France"],
        label_visibility="collapsed",
        key="region_select"
    )

    # ---- LOCATION ----
    st.markdown('<label class="input-label"><i class="fas fa-map-marker-alt"></i> State / Province</label>', unsafe_allow_html=True)
    location = st.text_input(
        "location",
        placeholder="e.g. Punjab, Ontario...",
        label_visibility="collapsed",
        key="location_input"
    )

    # ---- CROP STAGE ----
    st.markdown('<label class="input-label"><i class="fas fa-seedling"></i> Crop stage?</label>', unsafe_allow_html=True)
    crop_stage_options = {
        "Planning": "📋 Planning",
        "Sowing": "🌱 Sowing",
        "Growing": "🌿 Growing",
        "Harvesting": "🌾 Harvesting",
        "Post-Harvest": "🏭 Storage"
    }
    crop_stage = st.selectbox(
        "crop",
        list(crop_stage_options.keys()),
        format_func=lambda x: crop_stage_options[x],
        label_visibility="collapsed",
        key="crop_select"
    )

    # ---- PRIORITIES ----
    st.markdown('<label class="input-label"><i class="fas fa-bullseye"></i> Your goals</label>', unsafe_allow_html=True)
    priority = st.multiselect(
        "priority",
        ["💧 Save Water", "📈 High Yield", "🌿 Organic", "💰 Low Cost", 
         "🛡️ Pest Control", "🌱 Soil Health", "🚜 Automation", "♻️ Sustainability"],
        default=["📈 High Yield"],
        label_visibility="collapsed",
        key="priority_multiselect"
    )

    # ---- AI CREATIVITY ----
    st.markdown('<label class="input-label"><i class="fas fa-brain"></i> AI Creativity</label>', unsafe_allow_html=True)
    temperature = st.slider(
        "creativity",
        0.2, 0.9, 0.5,
        label_visibility="collapsed",
        key="temp_slider",
        help="More creative = surprising ideas, Consistent = safe advice"
    )
    creativity_percent = int((temperature - 0.2) / 0.7 * 100)
    st.markdown(f"""
    <div style="background: #FFBE0B; padding: 0.8rem; border-radius: 30px; text-align: center; border:4px solid white; margin-top: 0.5rem;">
        <span style="font-weight:800; font-size:1.4rem; color:black;">✨ {creativity_percent}% creative</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Your summary")
    cols = st.columns(2)
    with cols[0]:
        if location:
            st.markdown(f'<span class="badge"><i class="fas fa-map-marker-alt"></i> {location[:10]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge"><i class="fas fa-seedling"></i> {crop_stage_options[crop_stage][:2]}</span>', unsafe_allow_html=True)
    with cols[1]:
        for p in priority[:2]:
            st.markdown(f'<span class="badge">{p[:10]}</span>', unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'full_output' not in st.session_state:
    st.session_state.full_output = None
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False
if 'custom_rec_prompt' not in st.session_state:
    st.session_state.custom_rec_prompt = ""
if 'custom_chat_prompt' not in st.session_state:
    st.session_state.custom_chat_prompt = ""

# ---------------- TABS (NO RAW HTML, ICONS VIA CSS) ----------------
tab1, tab2 = st.tabs(["GET ADVICE", "ASK FARM BOT"])

# ========== TAB 1: RECOMMENDATIONS ==========
with tab1:
    st.markdown("## 🚜 Your Farm Dashboard")
    col_tile1, col_tile2, col_tile3, col_tile4 = st.columns(4)
    with col_tile1:
        st.markdown(f"""
        <div class="farm-tile">
            <i class="fas fa-globe-asia"></i>
            <h3>{region}</h3>
            <p style="color:black;">Region</p>
        </div>
        """, unsafe_allow_html=True)
    with col_tile2:
        st.markdown(f"""
        <div class="farm-tile">
            <i class="fas fa-calendar-alt"></i>
            <h3>{crop_stage}</h3>
            <p style="color:black;">Stage</p>
        </div>
        """, unsafe_allow_html=True)
    with col_tile3:
        st.markdown(f"""
        <div class="farm-tile">
            <i class="fas fa-bullseye"></i>
            <h3>{len(priority)}</h3>
            <p style="color:black;">Goals</p>
        </div>
        """, unsafe_allow_html=True)
    with col_tile4:
        creativity_icon = "🎨" if temperature > 0.6 else "⚖️" if temperature > 0.4 else "🎯"
        st.markdown(f"""
        <div class="farm-tile">
            <i class="fas fa-brain"></i>
            <h3>{creativity_icon}</h3>
            <p style="color:black;">{creativity_percent}%</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ---- Custom Prompt Expander ----
    with st.expander("🛠️ Advanced: Customize recommendation prompt"):
        st.markdown('<div class="prompt-editor">', unsafe_allow_html=True)
        st.info("Edit the prompt below. {placeholders} will be filled automatically.")
        default_rec_prompt = f"""You are an expert agricultural advisor. 
Farmer location: {{region}}, {{location}}.
Current crop stage: {{crop_stage}}.
Farmer priorities: {{priority}}.

Give EXACTLY 3 farming recommendations in this format:

Recommendation 1:
• Action: (clear, one sentence)
• Why: (one sentence)

Recommendation 2:
• Action:
• Why:

Recommendation 3:
• Action:
• Why:

Use simple words, region-specific advice, and avoid unsafe chemicals."""
        st.session_state.custom_rec_prompt = st.text_area(
            "Edit prompt",
            value=st.session_state.custom_rec_prompt or default_rec_prompt,
            height=280,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Generate Button ----
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🚜 GENERATE FARM PLAN", use_container_width=True, key="gen_btn"):
            if not location:
                st.warning("📍 Please enter your location first")
            else:
                try:
                    with st.spinner("🌿 AI is analyzing your farm..."):
                        prompt = st.session_state.custom_rec_prompt or default_rec_prompt
                        prompt = prompt.format(
                            region=region,
                            location=location,
                            crop_stage=crop_stage,
                            priority=', '.join(priority) if priority else 'General'
                        )
                        response = client.models.generate_content(
                            model="gemini-3-flash-preview",
                            contents=prompt,
                            config={"temperature": temperature, "max_output_tokens": 1024}
                        )
                        if hasattr(response, "text") and response.text:
                            full_output = response.text
                        else:
                            full_output = "⚠️ Could not get advice. Try again."
                        st.session_state.full_output = full_output
                        st.session_state.show_recommendations = True
                except Exception as e:
                    st.error("⚠️ AI service busy. Try again.")
    with col2:
        st.markdown("""
        <div style="background-color: #FFBE0B; border-radius: 30px; padding: 1rem; text-align: center; border:4px solid white;">
            <i class="fas fa-lightbulb" style="font-size:2rem; color:black;"></i>
            <p style="color:black; font-weight:700; margin:0;">Tap to get advice</p>
        </div>
        """, unsafe_allow_html=True)

    # ---- Display Recommendations ----
    if st.session_state.show_recommendations and st.session_state.full_output:
        st.success("✅ Your personalized farm plan is ready!")
        st.markdown("## 📋 3 STEPS TO A BETTER HARVEST")
        recs = st.session_state.full_output.split('\n\n')
        icons = ["1️⃣", "2️⃣", "3️⃣"]
        for i, rec in enumerate(recs[:3], 1):
            if rec.strip():
                cleaned = rec.replace('•', '➤').replace('Recommendation', '').strip()
                st.markdown(f"""
                <div class="recommendation-card">
                    <h4>{icons[i-1]} Recommendation {i}</h4>
                    <div style="font-size:1.2rem; line-height:1.8;">
                        {cleaned}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ========== TAB 2: CHAT ==========
with tab2:
    st.markdown("## 💬 Chat with FarmaBuddy")
    st.markdown('<p style="font-size:1.2rem; color:black;"><i class="fas fa-comment-dots"></i> Ask anything – pests, fertilizers, weather...</p>', unsafe_allow_html=True)

    # ---- Custom Chat Prompt ----
    with st.expander("🛠️ Advanced: Customize chat AI prompt"):
        st.markdown('<div class="prompt-editor">', unsafe_allow_html=True)
        st.info("This system prompt guides how the AI responds. {placeholders} are replaced with your farm data.")
        default_chat_prompt = f"""You are FarmaBuddy, a helpful farming assistant.
Current farmer context:
- Region: {{region}}
- Location: {{location}}
- Crop stage: {{crop_stage}}
- Priorities: {{priority}}

Answer the user's question with:
- Very simple, practical language
- Short sentences
- No unsafe chemicals
- Focus on actionable advice
If the question is not about farming, politely redirect."""
        st.session_state.custom_chat_prompt = st.text_area(
            "Edit system prompt",
            value=st.session_state.custom_chat_prompt or default_chat_prompt,
            height=220,
            label_visibility="collapsed",
            key="chat_prompt_edit"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Chat Container ----
    chat_container = st.container()
    with chat_container:
        st.markdown('<div style="background: #F0F7F0; border-radius: 40px; padding: 1.5rem;">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'''
                <div class="user-message">
                    <i class="fas fa-user"></i>
                    <p><strong>You:</strong> {msg["content"]}</p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="ai-message">
                    <i class="fas fa-robot"></i>
                    <p><strong>FarmaBuddy:</strong> {msg["content"]}</p>
                </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Input & Send ----
    col_in1, col_in2 = st.columns([5, 1])
    with col_in1:
        user_q = st.text_input("", placeholder="💭 Type your farming question...", label_visibility="collapsed", key="chat_input")
    with col_in2:
        send_click = st.button("📤 SEND", use_container_width=True, key="send_btn")

    if send_click and user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        try:
            with st.spinner("🌱 AI is answering..."):
                system_prompt = st.session_state.custom_chat_prompt or default_chat_prompt
                system_prompt = system_prompt.format(
                    region=region,
                    location=location if location else 'unknown',
                    crop_stage=crop_stage,
                    priority=', '.join(priority) if priority else 'General'
                )
                full_prompt = f"{system_prompt}\n\nUser question: {user_q}"
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=full_prompt,
                    config={"temperature": temperature, "max_output_tokens": 1024}
                )
                if hasattr(response, "text") and response.text:
                    ai_reply = response.text
                else:
                    ai_reply = "😕 I didn't get that. Please rephrase."
                st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
                st.rerun()
        except Exception as e:
            st.session_state.chat_history.append({"role": "assistant", "content": "⚠️ AI service is busy. Try again."})
            st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat", use_container_width=True, key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

# ---------------- FEEDBACK (EMOJI ONLY) ----------------
st.markdown("---")
st.markdown("## 👍 How was your experience?")
cols = st.columns(5)
emojis = ["😞", "🙁", "😐", "🙂", "😍"]
for i, emoji in enumerate(emojis, 1):
    with cols[i-1]:
        if st.button(emoji, key=f"fb{i}"):
            st.balloons() if i >= 3 else st.toast("Thank you!")

# ---------------- SESSION LOG ----------------
st.markdown("---")
st.markdown("## 📊 Today's activity")
log_data = {
    "Time": datetime.now().strftime("%H:%M"),
    "Region": region,
    "Location": location or "—",
    "Stage": crop_stage,
    "Goals": len(priority),
    "Chats": len(st.session_state.chat_history)
}
st.dataframe(pd.DataFrame([log_data]), use_container_width=True, hide_index=True)

# ---------------- FOOTER ----------------
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: center; gap: 30px; align-items: center;">
        <i class="fas fa-leaf"></i>
        <span style="font-size:1.8rem; font-weight:800;">FarmaBuddy</span>
        <i class="fas fa-tractor"></i>
    </div>
    <p style="font-size:1.2rem; margin-top:1rem;">❤️ Made for farmers – simple, colorful, smart</p>
    <p style="font-size:0.9rem;">{datetime.now().strftime("%B %Y")}</p>
</div>
""", unsafe_allow_html=True)
