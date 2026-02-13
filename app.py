import streamlit as st
import requests
from datetime import datetime
from google import genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="🌾 AgroNova",
    page_icon="🌱",
    layout="wide"
)

# -------------------------------------------------
# UI STYLE
# -------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0c2f20, #071e14);
    color: #e8f5ec;
}
.header {
    background: #145c3a;
    padding: 1.8rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
}
.card {
    background: #0f3d28;
    padding: 1.2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}
.stButton>button {
    background: #22c55e;
    border-radius: 8px;
    border: none;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
<h1>🌾 AgroNova</h1>
<p>Weather-Aware • Multimodal • AI Smart Farming System</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# GOOGLE API
# -------------------------------------------------
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Add GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_NAME = "gemini-3-flash-preview"

# -------------------------------------------------
# LOCATION API FUNCTIONS
# -------------------------------------------------
@st.cache_data
def get_states(country):
    url = "https://countriesnow.space/api/v0.1/countries/states"
    response = requests.post(url, json={"country": country})
    data = response.json()
    if data["error"] == False:
        return [state["name"] for state in data["data"]["states"]]
    return []

@st.cache_data
def get_districts(country, state):
    url = "https://countriesnow.space/api/v0.1/countries/state/cities"
    response = requests.post(url, json={
        "country": country,
        "state": state
    })
    data = response.json()
    if data["error"] == False:
        return data["data"]
    return []

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.header("Farm Configuration")

    country = st.selectbox(
        "Country",
        ["India", "Ghana", "Canada", "USA", "Brazil", "Australia"]
    )

    states = get_states(country)
    state = st.selectbox("State / Province", states) if states else None

    districts = get_districts(country, state) if state else []
    district = st.selectbox("District", districts) if districts else None

    crop_stage = st.selectbox(
        "Crop Stage",
        ["Planning", "Sowing", "Growing", "Harvesting", "Storage"]
    )

    goals = st.multiselect(
        "Goals",
        ["High Yield", "Low Cost", "Organic",
         "Water Saving", "Pest Control", "Soil Health"]
    )

    temperature = st.slider("AI Creativity", 0.2, 0.8, 0.4)

    st.markdown("---")
    weather_key = st.text_input("Weather API Key (Optional)")

# -------------------------------------------------
# WEATHER FUNCTION
# -------------------------------------------------
def get_weather(location, key):
    if not key or not location:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={key}&units=metric"
        data = requests.get(url).json()
        return {
            "Temp": data["main"]["temp"],
            "Humidity": data["main"]["humidity"],
            "Rain": data.get("rain", {}).get("1h", 0)
        }
    except:
        return None

location_query = f"{district},{state},{country}" if district else None
weather_data = get_weather(location_query, weather_key)

if weather_data:
    st.info(
        f"🌦 Temp: {weather_data['Temp']}°C | "
        f"Humidity: {weather_data['Humidity']}% | "
        f"Rain (1h): {weather_data['Rain']} mm"
    )

# -------------------------------------------------
# IMAGE UPLOAD
# -------------------------------------------------
uploaded_image = st.file_uploader(
    "Upload crop image (optional)",
    type=["jpg", "jpeg", "png"]
)

# -------------------------------------------------
# FARM QUESTION
# -------------------------------------------------
question = st.text_area("Describe your farm issue")

# -------------------------------------------------
# GENERATE ADVICE
# -------------------------------------------------
if st.button("Generate Farm Advice"):

    if not state or not district:
        st.warning("Select country, state and district.")
    elif not question:
        st.warning("Enter farm issue.")
    else:
        try:
            base_prompt = f"""
You are an expert agricultural advisor.

Country: {country}
State: {state}
District: {district}
Crop Stage: {crop_stage}
Goals: {', '.join(goals) if goals else 'General productivity'}
Weather: {weather_data if weather_data else 'Not provided'}

Question:
{question}

Provide EXACTLY 3 recommendations.

Format:

Recommendation 1:
• Action:
• Why:

Recommendation 2:
• Action:
• Why:

Recommendation 3:
• Action:
• Why:

Use simple language.
Avoid unsafe chemicals.
"""

            contents = base_prompt

            if uploaded_image:
                contents = [
                    {"text": base_prompt},
                    {
                        "inline_data": {
                            "mime_type": uploaded_image.type,
                            "data": uploaded_image.getvalue()
                        }
                    }
                ]

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config={
                    "temperature": temperature,
                    "max_output_tokens": 900
                }
            )

            if hasattr(response, "text") and response.text:
                result = response.text
                st.success("Farm Plan Ready")
                st.markdown(
                    f'<div class="card">{result}</div>',
                    unsafe_allow_html=True
                )

                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer)
                styles = getSampleStyleSheet()
                elements = []

                elements.append(
                    Paragraph("AgroNova Farm Report", styles["Heading1"])
                )
                elements.append(Spacer(1, 0.3 * inch))
                elements.append(
                    Paragraph(result.replace("\n", "<br/>"),
                              styles["Normal"])
                )

                doc.build(elements)
                buffer.seek(0)

                st.download_button(
                    "Download PDF Report",
                    buffer,
                    file_name="AgroNova_Farm_Report.pdf",
                    mime="application/pdf"
                )

            else:
                st.error("No response received.")

        except Exception as e:
            st.error("AI service unavailable.")
            st.code(str(e))

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(f"""
<hr>
<p style="text-align:center;">
AgroNova • AI Smart Farming Assistant • {datetime.now().year}
</p>
""", unsafe_allow_html=True)
