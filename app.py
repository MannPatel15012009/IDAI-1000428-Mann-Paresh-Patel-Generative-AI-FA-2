
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from google import genai
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="🌾 AgroNova Enterprise",
    page_icon="🌱",
    layout="wide"
)

# =====================================================
# CLEAN ENTERPRISE UI
# =====================================================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#071e14,#0c2f20); color:#e8f5ec;}
.block-container {max-width:1100px;padding-top:2rem;}
.header {background:#145c3a;padding:2rem;border-radius:18px;margin-bottom:1.5rem;}
.card {background:#0f3d28;padding:1.2rem;border-radius:12px;margin-bottom:1rem;}
.recommendation {background:#0c3323;padding:1.2rem;border-radius:10px;border-left:4px solid #22c55e;margin-bottom:0.8rem;}
.safe {color:#22c55e;font-weight:bold;}
.warn {color:#facc15;font-weight:bold;}
.danger {color:#ef4444;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
<h1>🌾 AgroNova Enterprise AI</h1>
<p>Elite Smart Farming Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# API INITIALIZATION
# =====================================================
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Add GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_NAME = "gemini-3-flash-preview"

# =====================================================
# WEATHER MODULE
# =====================================================
def fetch_weather(location, api_key):
    if not api_key or not location:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        data = requests.get(url).json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall_last_hour": data.get("rain", {}).get("1h", 0)
        }
    except:
        return None

# =====================================================
# SAFETY CLASSIFIER
# =====================================================
def classify_safety(text):
    risk_keywords = ["high dosage", "toxic", "hazard", "danger"]
    for word in risk_keywords:
        if word in text.lower():
            return "RED"
    if "chemical" in text.lower():
        return "YELLOW"
    return "GREEN"

# =====================================================
# AI ORCHESTRATOR
# =====================================================
def run_ai_orchestrator(context_prompt, temperature):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=context_prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": 1000
        }
    )
    if hasattr(response, "text") and response.text:
        return response.text
    return None

# =====================================================
# SIDEBAR CONFIG
# =====================================================
with st.sidebar:
    st.header("Farm Configuration")

    country = st.selectbox("Country", ["India","Ghana","Canada","USA","Brazil","Australia"])
    state = st.text_input("State / Province")
    stage = st.selectbox("Crop Stage", ["Planning","Sowing","Growing","Harvesting","Storage"])
    goals = st.multiselect("Goals",
        ["High Yield","Low Cost","Organic","Water Saving","Pest Control","Soil Health"])
    creativity = st.slider("AI Creativity",0.2,0.8,0.4)
    weather_key = st.text_input("Weather API Key (Optional)")

# =====================================================
# WEATHER INJECTION
# =====================================================
weather_data = fetch_weather(state, weather_key)
if weather_data:
    st.info(f"🌦 Temp: {weather_data['temperature']}°C | Humidity: {weather_data['humidity']}% | Rain: {weather_data['rainfall_last_hour']}mm")

# =====================================================
# IMAGE UPLOAD
# =====================================================
uploaded_image = st.file_uploader("Upload Crop Image (Optional)", type=["jpg","jpeg","png"])

# =====================================================
# FARM QUESTION
# =====================================================
question = st.text_area("Describe your farm issue")

# =====================================================
# ENTERPRISE GENERATION
# =====================================================
if st.button("Generate Enterprise Farm Plan"):

    if not state or not question:
        st.warning("Please complete required fields.")
    else:
        base_prompt = f"""
You are AgroNova Enterprise AI.

Return output STRICTLY in JSON format:

{{
  "recommendations":[
    {{"action":"", "why":"", "risk":"LOW/MEDIUM/HIGH"}}
  ],
  "confidence_score": number_between_0_and_100
}}

Context:
Country: {country}
State: {state}
Stage: {stage}
Goals: {', '.join(goals) if goals else 'General'}
Weather: {weather_data if weather_data else 'Not available'}

User Question:
{question}

Use simple language.
Avoid unsafe chemical advice.
Provide exactly 3 recommendations.
"""

        try:
            # Low temperature version
            low_output = run_ai_orchestrator(base_prompt, 0.3)
            high_output = run_ai_orchestrator(base_prompt, 0.7)

            parsed = json.loads(low_output)

            st.success("Enterprise Farm Plan Ready")

            for rec in parsed["recommendations"]:
                st.markdown(f"""
                <div class="recommendation">
                <b>Action:</b> {rec["action"]}<br>
                <b>Why:</b> {rec["why"]}<br>
                <b>Risk Level:</b> {rec["risk"]}
                </div>
                """, unsafe_allow_html=True)

            safety = classify_safety(low_output)
            if safety == "GREEN":
                st.markdown('<p class="safe">🟢 Safety Score: SAFE</p>', unsafe_allow_html=True)
            elif safety == "YELLOW":
                st.markdown('<p class="warn">🟡 Safety Score: MODERATE</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="danger">🔴 Safety Score: HIGH RISK</p>', unsafe_allow_html=True)

            st.markdown(f"### 🔍 AI Confidence Score: {parsed['confidence_score']}%")

            # Model comparison view
            with st.expander("Model Comparison (0.3 vs 0.7)"):
                st.write("### Conservative Output (0.3)")
                st.code(low_output)
                st.write("### Creative Output (0.7)")
                st.code(high_output)

            # Logging
            log_entry = {
                "timestamp": datetime.now(),
                "country": country,
                "state": state,
                "confidence": parsed["confidence_score"],
                "safety": safety
            }
            pd.DataFrame([log_entry]).to_csv("agronova_logs.csv", mode="a", header=False, index=False)

            # PDF Export
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            styles = getSampleStyleSheet()
            elements = []
            elements.append(Paragraph("AgroNova Enterprise Farm Report", styles["Heading1"]))
            elements.append(Spacer(1,0.3*inch))
            elements.append(Paragraph(low_output.replace("\n","<br/>"), styles["Normal"]))
            doc.build(elements)
            buffer.seek(0)

            st.download_button(
                "Download Enterprise PDF Report",
                buffer,
                file_name="AgroNova_Enterprise_Report.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error("AI service unavailable.")
            st.code(str(e))

# =====================================================
# FOOTER
# =====================================================
st.markdown(f"""
<hr>
<p style="text-align:center;">
AgroNova Enterprise AI Platform • {datetime.now().year}
</p>
""", unsafe_allow_html=True)
