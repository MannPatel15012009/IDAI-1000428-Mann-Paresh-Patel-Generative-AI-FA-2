"""
AgSaathi — Smart Farming Assistant
Student:Mann Paresh Patel | Reg: 1000442 
Assessment: FA-2 | Course: Generative AI | School: Aspee Nutan Academy
Model: gemini-3.0-flash-preview | Temperature: 0.2 | Max Tokens: 1000

SECURITY: API key loaded from st.secrets — never hardcoded.
Deploy: Add GEMINI_API_KEY to .streamlit/secrets.toml or Streamlit Cloud secrets.
"""

import streamlit as st
import google.generativeai as genai
import json
import re
import csv
import os
from datetime import datetime
from typing import Dict, Any, Optional

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgSaathi — Smart Farming Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GEMINI SETUP — KEY FROM SECRETS (never hardcode) ─────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
if not GEMINI_API_KEY:
    st.error("⚠️ Gemini API key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.info("**How to fix:**\n1. Create `.streamlit/secrets.toml`\n2. Add: `GEMINI_API_KEY = \"your_key_here\"`\n3. On Streamlit Cloud: Settings → Secrets → paste the same.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME        = "gemini-3-flash-preview"
MODEL_TEMPERATURE = 0.2
MODEL_MAX_TOKENS  = 4096

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=genai.GenerationConfig(
            temperature=MODEL_TEMPERATURE,
            max_output_tokens=MODEL_MAX_TOKENS,
        )
    )

# ── RATE LIMITING — max 20 queries per session ────────────────────────────────
MAX_QUERIES_PER_SESSION = 20

def check_rate_limit() -> bool:
    """Returns True if query is allowed, False if limit reached."""
    used = st.session_state.stats.get('queries', 0)
    return used < MAX_QUERIES_PER_SESSION

def rate_limit_warning():
    st.warning(f"⚠️ Daily limit of {MAX_QUERIES_PER_SESSION} AI queries reached for this session. Refresh to reset.")

# ── LANGUAGE CODE MAP ────────────────────────────────────────────────────────
LANG_CODES = {
    'English':    'English (en)',
    'Hindi':      'Hindi / हिन्दी (hi)',
    'Tamil':      'Tamil / தமிழ் (ta)',
    'Telugu':     'Telugu / తెలుగు (te)',
    'Bengali':    'Bengali / বাংলা (bn)',
    'Marathi':    'Marathi / मराठी (mr)',
    'Gujarati':   'Gujarati / ગુજરાતી (gu)',
    'Kannada':    'Kannada / ಕನ್ನಡ (kn)',
    'French':     'French / Français (fr)',
    'Spanish':    'Spanish / Español (es)',
    'Portuguese': 'Portuguese / Português (pt)',
    'Afrikaans':  'Afrikaans (af)',
    'Zulu':       'Zulu / isiZulu (zu)',
    'Xhosa':      'Xhosa / isiXhosa (xh)',
    'Twi':        'Twi (tw)',
    'Ga':         'Ga (gaa)',
    'Yoruba':     'Yoruba (yo)',
    'Hausa':      'Hausa (ha)',
    'Igbo':       'Igbo (ig)',
}

# ── FULL UI TRANSLATION STRINGS ───────────────────────────────────────────────
# All static UI text translated per language
UI_STRINGS = {
    'English': {
        'tagline': 'Kisan Saathi · Smart Farming Assistant',
        'hero_title': 'AgSaathi',
        'hero_body': 'AI-powered, region-specific, multilingual farming advice\nfor small and marginal farmers worldwide —\npowered by Gemini AI.',
        'begin_btn': '🌾 Begin — Select Your Location →',
        'where_farm': 'Where is your farm?',
        'where_sub': 'Select your country for region-specific farming advice.',
        'which_state': 'Which state are you in?',
        'state_sub': 'Hyper-local advice starts with your specific region.',
        'choose_lang': 'Choose your language',
        'continue_btn': '✅ Continue',
        'back_btn': '← Back',
        'next_btn': 'Next →',
        'quick_select': 'Quick Select',
        'selected_region': 'SELECTED REGION',
        'location_label': 'LOCATION · LANGUAGE',
        'change_location': '⟳  Change Location',
        'change_lang': '🌐  Change Language',
        'dashboard': 'Dashboard',
        'ai_assistant': 'AI Assistant',
        'crop_rec': 'Crop Recommendation',
        'pest': 'Pest & Disease',
        'soil': 'Soil & Fertilizer',
        'sustainable': 'Sustainable Tips',
        'weather': 'Weather Alerts',
        'calendar': 'Crop Calendar',
        'validate': 'Model Validation',
        'history': 'Query History',
        'feedback': 'Feedback',
        'good_morning': 'Good morning, Farmer',
        'good_afternoon': 'Good afternoon, Farmer',
        'good_evening': 'Good evening, Farmer',
        'ai_queries': 'AI Queries',
        'crops_advised': 'Crops Advised',
        'soil_analyses': 'Soil Analyses',
        'diagnoses': 'Diagnoses',
        'saved_queries': 'Saved Queries',
        'core_features': 'Core Features',
        'open': 'Open',
        'example_qs': 'Example Questions',
        'ask_ai': '→ Ask AI',
        'asking': 'Consulting AI...',
        'you': 'You',
        'loc_analysis': 'Location Analysis',
        'recommendations': 'Recommendations',
        'safety_note': 'Safety Note',
        'confidence': 'AI CONFIDENCE',
        'view_json': '🔬 View Raw JSON Response',
        'analyse_soil': '🔬 Analyse Soil & Get Recommendations',
        'soil_report': 'Soil Analysis Report',
        'ask_more': 'Ask AI more about this soil →',
        'no_history': 'No queries yet — start with AI Assistant',
        'ask_again': '↺ Ask Again',
        'delete': '✕ Delete',
        'submit_feedback': 'Submit Feedback →',
        'feedback_title': 'Feedback title',
        'feedback_msg': 'Your message',
        'rating': 'Rating',
        'positive': '👍 Positive',
        'suggestion': '💡 Suggestion',
        'bug_report': '🐛 Bug Report',
        'thank_you': '✓ Thank you — recorded.',
        'history_title': 'Query History',
        'validation_title': 'Model Validation — FA-2 Step 5',
        'run_test': '🧪 Run Test & Validate',
        'run_all': '🔄 Run All 3 Test Prompts',
        'test_score': 'Validation Score',
        'target': 'TARGET: 70%+',
        'type_question': 'Or type your own question...',
    },
    'Hindi': {
        'tagline': 'किसान साथी · स्मार्ट खेती सहायक',
        'hero_title': 'AgSaathi',
        'hero_body': 'AI-आधारित, क्षेत्र-विशिष्ट, बहुभाषी खेती सलाह\nछोटे और सीमांत किसानों के लिए —\nGemini AI द्वारा संचालित।',
        'begin_btn': '🌾 शुरू करें — अपना स्थान चुनें →',
        'where_farm': 'आपका खेत कहाँ है?',
        'where_sub': 'क्षेत्र-विशिष्ट खेती सलाह के लिए अपना देश चुनें।',
        'which_state': 'आप किस राज्य में हैं?',
        'state_sub': 'सटीक सलाह के लिए अपना क्षेत्र चुनें।',
        'choose_lang': 'अपनी भाषा चुनें',
        'continue_btn': '✅ जारी रखें',
        'back_btn': '← वापस',
        'next_btn': 'अगला →',
        'quick_select': 'त्वरित चयन',
        'selected_region': 'चयनित क्षेत्र',
        'location_label': 'स्थान · भाषा',
        'change_location': '⟳  स्थान बदलें',
        'change_lang': '🌐  भाषा बदलें',
        'dashboard': 'डैशबोर्ड',
        'ai_assistant': 'AI सहायक',
        'crop_rec': 'फसल सिफारिश',
        'pest': 'कीट और रोग',
        'soil': 'मिट्टी और खाद',
        'sustainable': 'टिकाऊ खेती',
        'weather': 'मौसम चेतावनी',
        'calendar': 'फसल कैलेंडर',
        'validate': 'मॉडल सत्यापन',
        'history': 'क्वेरी इतिहास',
        'feedback': 'प्रतिक्रिया',
        'good_morning': 'सुप्रभात, किसान',
        'good_afternoon': 'नमस्कार, किसान',
        'good_evening': 'शुभ संध्या, किसान',
        'ai_queries': 'AI प्रश्न',
        'crops_advised': 'फसल सलाह',
        'soil_analyses': 'मिट्टी विश्लेषण',
        'diagnoses': 'निदान',
        'saved_queries': 'सहेजे गए',
        'core_features': 'मुख्य सुविधाएं',
        'open': 'खोलें',
        'example_qs': 'उदाहरण प्रश्न',
        'ask_ai': '→ AI से पूछें',
        'asking': 'AI से सलाह ले रहे हैं...',
        'you': 'आप',
        'loc_analysis': 'स्थान विश्लेषण',
        'recommendations': 'सिफारिशें',
        'safety_note': 'सुरक्षा नोट',
        'confidence': 'AI विश्वास',
        'view_json': '🔬 JSON प्रतिक्रिया देखें',
        'analyse_soil': '🔬 मिट्टी विश्लेषण करें',
        'soil_report': 'मिट्टी विश्लेषण रिपोर्ट',
        'ask_more': 'इस मिट्टी के बारे में और पूछें →',
        'no_history': 'अभी तक कोई प्रश्न नहीं — AI सहायक से शुरू करें',
        'ask_again': '↺ फिर पूछें',
        'delete': '✕ हटाएं',
        'submit_feedback': 'प्रतिक्रिया भेजें →',
        'feedback_title': 'प्रतिक्रिया शीर्षक',
        'feedback_msg': 'आपका संदेश',
        'rating': 'रेटिंग',
        'positive': '👍 सकारात्मक',
        'suggestion': '💡 सुझाव',
        'bug_report': '🐛 बग रिपोर्ट',
        'thank_you': '✓ धन्यवाद — दर्ज किया गया।',
        'history_title': 'क्वेरी इतिहास',
        'validation_title': 'मॉडल सत्यापन — FA-2 चरण 5',
        'run_test': '🧪 परीक्षण करें',
        'run_all': '🔄 सभी 3 परीक्षण चलाएं',
        'test_score': 'सत्यापन स्कोर',
        'target': 'लक्ष्य: 70%+',
        'type_question': 'या अपना प्रश्न टाइप करें...',
    },
    'Tamil': {
        'tagline': 'கிசான் சாத்தி · புத்திசாலி விவசாய உதவியாளர்',
        'hero_title': 'AgSaathi',
        'hero_body': 'AI-இயங்கும், பிராந்திய-குறிப்பிட்ட விவசாய ஆலோசனை\nசிறு மற்றும் குறு விவசாயிகளுக்காக —\nGemini AI மூலம்.',
        'begin_btn': '🌾 தொடங்கு — உங்கள் இடத்தை தேர்ந்தெடு →',
        'where_farm': 'உங்கள் பண்ணை எங்கே உள்ளது?',
        'where_sub': 'பிராந்திய-குறிப்பிட்ட ஆலோசனைக்கு உங்கள் நாட்டை தேர்ந்தெடுக்கவும்.',
        'which_state': 'நீங்கள் எந்த மாநிலத்தில் இருக்கிறீர்கள்?',
        'state_sub': 'துல்லியமான ஆலோசனைக்கு உங்கள் பகுதியை தேர்ந்தெடுக்கவும்.',
        'choose_lang': 'உங்கள் மொழியை தேர்ந்தெடுக்கவும்',
        'continue_btn': '✅ தொடர்க',
        'back_btn': '← பின்செல்',
        'next_btn': 'அடுத்து →',
        'quick_select': 'விரைவு தேர்வு',
        'selected_region': 'தேர்ந்தெடுக்கப்பட்ட பகுதி',
        'location_label': 'இடம் · மொழி',
        'change_location': '⟳  இடத்தை மாற்று',
        'change_lang': '🌐  மொழியை மாற்று',
        'dashboard': 'டாஷ்போர்ட்',
        'ai_assistant': 'AI உதவியாளர்',
        'crop_rec': 'பயிர் பரிந்துரை',
        'pest': 'பூச்சி & நோய்',
        'soil': 'மண் & உரம்',
        'sustainable': 'நிலையான விவசாயம்',
        'weather': 'வானிலை எச்சரிக்கை',
        'calendar': 'பயிர் நாட்காட்டி',
        'validate': 'மாதிரி சரிபார்ப்பு',
        'history': 'வினவல் வரலாறு',
        'feedback': 'கருத்து',
        'good_morning': 'காலை வணக்கம், விவசாயி',
        'good_afternoon': 'மதிய வணக்கம், விவசாயி',
        'good_evening': 'மாலை வணக்கம், விவசாயி',
        'ai_queries': 'AI வினவல்கள்',
        'crops_advised': 'பயிர் ஆலோசனை',
        'soil_analyses': 'மண் பகுப்பாய்வு',
        'diagnoses': 'நோய் கண்டறிதல்',
        'saved_queries': 'சேமித்தவை',
        'core_features': 'முக்கிய அம்சங்கள்',
        'open': 'திற',
        'example_qs': 'உதாரண கேள்விகள்',
        'ask_ai': '→ AI-யிடம் கேள்',
        'asking': 'AI-யிடம் ஆலோசனை பெறுகிறோம்...',
        'you': 'நீங்கள்',
        'loc_analysis': 'இட பகுப்பாய்வு',
        'recommendations': 'பரிந்துரைகள்',
        'safety_note': 'பாதுகாப்பு குறிப்பு',
        'confidence': 'AI நம்பிக்கை',
        'view_json': '🔬 JSON பதிலை பார்',
        'analyse_soil': '🔬 மண்ணை பகுப்பாய்வு செய்',
        'soil_report': 'மண் பகுப்பாய்வு அறிக்கை',
        'ask_more': 'இந்த மண்ணைப் பற்றி மேலும் கேள் →',
        'no_history': 'இன்னும் வினவல்கள் இல்லை — AI உதவியாளரிடம் தொடங்கு',
        'ask_again': '↺ மீண்டும் கேள்',
        'delete': '✕ நீக்கு',
        'submit_feedback': 'கருத்தை சமர்பி →',
        'feedback_title': 'கருத்து தலைப்பு',
        'feedback_msg': 'உங்கள் செய்தி',
        'rating': 'மதிப்பீடு',
        'positive': '👍 நேர்மறை',
        'suggestion': '💡 பரிந்துரை',
        'bug_report': '🐛 பிழை அறிக்கை',
        'thank_you': '✓ நன்றி — பதிவு செய்யப்பட்டது.',
        'history_title': 'வினவல் வரலாறு',
        'validation_title': 'மாதிரி சரிபார்ப்பு — FA-2',
        'run_test': '🧪 சோதனை இயக்கு',
        'run_all': '🔄 அனைத்து 3 சோதனைகளும்',
        'test_score': 'சரிபார்ப்பு மதிப்பெண்',
        'target': 'இலக்கு: 70%+',
        'type_question': 'அல்லது உங்கள் கேள்வியை தட்டச்சு செய்யவும்...',
    },
}

def T(key: str) -> str:
    """Get UI string in selected language, fallback to English."""
    lang = st.session_state.get('language', 'English')
    return UI_STRINGS.get(lang, UI_STRINGS['English']).get(key, UI_STRINGS['English'].get(key, key))

# ── GEO DATA ─────────────────────────────────────────────────────────────────
GEO = {
    'India 🇮🇳': {
        'languages': ['English', 'Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi', 'Gujarati', 'Kannada'],
        'states': ['Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat',
                   'Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh',
                   'Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab',
                   'Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh',
                   'Uttarakhand','West Bengal'],
    },
    'Canada 🇨🇦': {
        'languages': ['English', 'French'],
        'states': ['Alberta','British Columbia','Manitoba','New Brunswick','Newfoundland and Labrador',
                   'Northwest Territories','Nova Scotia','Nunavut','Ontario','Prince Edward Island',
                   'Quebec','Saskatchewan','Yukon'],
    },
    'Ghana 🇬🇭': {
        'languages': ['English', 'Twi', 'Ga'],
        'states': ['Ahafo','Ashanti','Bono','Bono East','Central','Eastern','Greater Accra',
                   'North East','Northern','Oti','Savannah','Upper East','Upper West','Volta',
                   'Western','Western North'],
    },
    'United States 🇺🇸': {
        'languages': ['English', 'Spanish'],
        'states': ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',
                   'Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa',
                   'Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan',
                   'Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire',
                   'New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio',
                   'Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota',
                   'Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia',
                   'Wisconsin','Wyoming'],
    },
    'Brazil 🇧🇷': {
        'languages': ['Portuguese', 'English'],
        'states': ['Acre','Alagoas','Amapá','Amazonas','Bahia','Ceará','Distrito Federal',
                   'Espírito Santo','Goiás','Maranhão','Mato Grosso','Mato Grosso do Sul',
                   'Minas Gerais','Pará','Paraíba','Paraná','Pernambuco','Piauí',
                   'Rio de Janeiro','Rio Grande do Norte','Rio Grande do Sul','Rondônia',
                   'Roraima','Santa Catarina','São Paulo','Sergipe','Tocantins'],
    },
    'Nigeria 🇳🇬': {
        'languages': ['English', 'Yoruba', 'Hausa', 'Igbo'],
        'states': ['Abia','Adamawa','Akwa Ibom','Anambra','Bauchi','Bayelsa','Benue','Borno',
                   'Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','Gombe','Imo','Jigawa',
                   'Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger',
                   'Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe',
                   'Zamfara','FCT Abuja'],
    },
    'Australia 🇦🇺': {
        'languages': ['English'],
        'states': ['Australian Capital Territory','New South Wales','Northern Territory',
                   'Queensland','South Australia','Tasmania','Victoria','Western Australia'],
    },
    'South Africa 🇿🇦': {
        'languages': ['English', 'Afrikaans', 'Zulu', 'Xhosa'],
        'states': ['Eastern Cape','Free State','Gauteng','KwaZulu-Natal','Limpopo',
                   'Mpumalanga','Northern Cape','North West','Western Cape'],
    },
    'Mexico 🇲🇽': {
        'languages': ['Spanish', 'English'],
        'states': ['Aguascalientes','Baja California','Baja California Sur','Campeche','Chiapas',
                   'Chihuahua','Coahuila','Colima','Durango','Guanajuato','Guerrero','Hidalgo',
                   'Jalisco','Mexico City','México','Michoacán','Morelos','Nayarit','Nuevo León',
                   'Oaxaca','Puebla','Querétaro','Quintana Roo','San Luis Potosí','Sinaloa',
                   'Sonora','Tabasco','Tamaulipas','Tlaxcala','Veracruz','Yucatán','Zacatecas'],
    },
    'France 🇫🇷': {
        'languages': ['French', 'English'],
        'states': ["Auvergne-Rhône-Alpes","Bourgogne-Franche-Comté","Bretagne",
                   "Centre-Val de Loire","Corse","Grand Est","Hauts-de-France",
                   "Île-de-France","Normandie","Nouvelle-Aquitaine","Occitanie",
                   "Pays de la Loire","Provence-Alpes-Côte d'Azur"],
    },
}

SEASONAL = {
    'Spring 🌸': {'temp':'15–25°C','crops':[
        {'name':'Tomatoes','plant':'Early Spring','harvest':'60–80 days','temp':'18–24°C','tip':'Plant after last frost. Full sun. Water regularly.'},
        {'name':'Lettuce','plant':'Early Spring','harvest':'30–45 days','temp':'15–20°C','tip':'Succession planting gives continuous harvest.'},
        {'name':'Carrots','plant':'Mid Spring','harvest':'70–80 days','temp':'16–21°C','tip':'Loose, well-drained soil. Thin to 3 inches apart.'},
    ]},
    'Summer ☀️': {'temp':'25–40°C','crops':[
        {'name':'Corn (Maize)','plant':'Late Spring','harvest':'60–100 days','temp':'25–30°C','tip':'Full sun. Plant in blocks for pollination.'},
        {'name':'Watermelon','plant':'Early Summer','harvest':'80–90 days','temp':'25–35°C','tip':'Sandy loam soil. Needs lots of space.'},
        {'name':'Peppers','plant':'Late Spring','harvest':'60–90 days','temp':'21–29°C','tip':'Mulch to retain moisture. Loves heat.'},
    ]},
    'Autumn 🍂': {'temp':'10–20°C','crops':[
        {'name':'Broccoli','plant':'Late Summer','harvest':'70–100 days','temp':'15–20°C','tip':'Harvest before flowers open. Cool season.'},
        {'name':'Cauliflower','plant':'Late Summer','harvest':'75–85 days','temp':'15–20°C','tip':'Consistent moisture throughout growth.'},
        {'name':'Cabbage','plant':'Late Summer','harvest':'70–120 days','temp':'15–20°C','tip':'Cold hardy. Harvest when heads are firm.'},
    ]},
    'Winter ❄️': {'temp':'0–15°C','crops':[
        {'name':'Garlic','plant':'Late Autumn','harvest':'240–270 days','temp':'0–15°C','tip':'Plant cloves pointy end up.'},
        {'name':'Onions','plant':'Late Autumn','harvest':'180–240 days','temp':'5–15°C','tip':'Plant sets in fall for spring harvest.'},
        {'name':'Winter Wheat','plant':'Early Winter','harvest':'210–240 days','temp':'0–15°C','tip':'Sow before ground freezes.'},
    ]},
}

CHECKLIST = [
    "Is the advice specific to the input region and state?",
    "Does the output provide valid and logical reasoning?",
    "Is the language simple enough for a non-technical farmer?",
    "Are outputs appropriately detailed (not too generic)?",
    "Does the model avoid misleading or unsafe chemical dosages?",
    "Are actionable next steps clearly listed?",
    "Is the response concise for mobile field use?",
]

FEATURE_PROMPTS = {
    "crop_rec": [
        "Recommend 3 high-value horticultural crops for 1 acre in {state} with 5x profit over wheat.",
        "What should I grow in July in {state} given monsoon rainfall?",
        "Suggest crops for sandy, low-water soil in {state}.",
    ],
    "pest": [
        "My banana plants in {state} show yellowing lower leaves. Diagnostic checklist?",
        "Organic treatment for aphids on mustard in {state}.",
        "Identify Red Rot in sugarcane and provide prevention steps for {state}.",
    ],
    "weather": [
        "Heavy rain forecast for {state}. Should I harvest sugarcane today?",
        "45°C heatwave expected in {state}. Irrigation schedule for young bananas?",
        "Emergency plan for waterlogging in rice fields in {state}.",
    ],
    "soil": [
        "How much gypsum for 1 acre of alkaline soil (pH 10.5) in {state}?",
        "Steps to neutralize slightly acidic soil in {state}.",
        "Reduce urea for wheat using Vermicompost in {state}.",
    ],
    "sustainable": [
        "Explain drip irrigation benefits for banana farmers in {state}.",
        "Alternatives to stubble burning that improve soil health in {state}.",
        "How to use a digital chatbot for long-term soil monitoring in {state}?",
    ],
}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
DEFAULTS = {
    'page': 'hero', 'country': None, 'state': None, 'language': 'English',
    'nav': 'home', 'chat': [], 'history': [], 'activity': [],
    'stats': {'queries':0,'crops':0,'calendar':0,'soil_checks':0,'disease_checks':0},
    'user_query': None, 'feedback_type': None,
    'soil_result': None, 'validation_results': {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ───────────────────────────────────────────────────────────────────
def loc():
    c = (st.session_state.country or '')
    for flag in ['🇮🇳','🇨🇦','🇬🇭','🇺🇸','🇧🇷','🇳🇬','🇦🇺','🇿🇦','🇲🇽','🇫🇷']:
        c = c.replace(flag,'')
    c = c.strip()
    s = st.session_state.state or ''
    return f"{s}, {c}" if s and c else c or "Unknown location"

def country_name():
    c = st.session_state.country or ''
    for flag in ['🇮🇳','🇨🇦','🇬🇭','🇺🇸','🇧🇷','🇳🇬','🇦🇺','🇿🇦','🇲🇽','🇫🇷']:
        c = c.replace(flag,'')
    return c.strip()

def get_lang_full():
    return LANG_CODES.get(st.session_state.language, st.session_state.language)

def call_gemini(prompt: str) -> str:
    """
    Call Gemini API. Surfaces real errors in the UI instead of silently failing.
    Returns empty string on error so callers can detect failure.
    """
    try:
        m = get_model()
        resp = m.generate_content(prompt)
        return resp.text if resp.text else ""
    except Exception as e:
        err = str(e)
        if "404" in err or "not found" in err.lower() or "does not exist" in err.lower():
            st.error(
                f"❌ **Model not found:** `{MODEL_NAME}` is not available. "
                "Check your API key has access to this model, or update MODEL_NAME."
            )
        elif "403" in err or "permission" in err.lower():
            st.error("❌ **Permission denied.** Check your GEMINI_API_KEY in Streamlit secrets.")
        elif "INVALID_ARGUMENT" in err and "api_key" in err.lower():
            st.error("❌ **Invalid API key.** Check GEMINI_API_KEY in .streamlit/secrets.toml")
        elif "429" in err or "quota" in err.lower() or "RESOURCE_EXHAUSTED" in err:
            st.warning("⚠️ **API quota exceeded.** Wait a moment and try again.")
        else:
            st.error(f"❌ **Gemini API error:** {err[:300]}")
        return ""


def build_structured_prompt(user_query: str, country: str, state: str,
                             soil_type: str = "Unknown",
                             weather_data: str = "Normal seasonal conditions") -> str:
    lang_full = get_lang_full()
    lang_name = st.session_state.language
    return f"""You are AgSaathi, a responsible AI agricultural assistant.

LANGUAGE RULE:
- Use {lang_full} as the primary language for all text values.
- Technical terms (pH, NPK, drip irrigation, compost, kg, etc.) may remain in English if needed.
- JSON keys (action, reason, risk_level, etc.) must always stay in English.

Context:
- Country: {country}
- State/Region: {state}
- Soil Type: {soil_type}
- Weather: {weather_data}
- Output Language: {lang_full}

Farmer Question: "{user_query}"

Instructions:
1. Analyze how location, soil, and weather affect the situation specifically for {state}, {country}.
2. Give exactly 3 practical, location-specific recommendations.
3. Each must have: action (what to do), reason (why it works), risk_level (LOW/MEDIUM/HIGH).
4. Avoid unsafe chemical dosages. Prefer organic options where possible.
5. Use simple language a farmer with no technical background can understand.
6. confidence_score must be an integer between 0 and 100 — no quotes, no decimals.
7. Return ONLY valid JSON — no markdown, no code fences, no text outside the JSON object.

Return ONLY this JSON (text values in {lang_name}, technical terms may be English):
{{
  "location_analysis": "Brief explanation of how {state}, {country} climate/soil affects this question",
  "recommendations": [
    {{
      "action": "Specific step 1 the farmer must do",
      "reason": "Why this step helps the crop/soil",
      "risk_level": "LOW"
    }},
    {{
      "action": "Specific step 2",
      "reason": "Why this helps",
      "risk_level": "MEDIUM"
    }},
    {{
      "action": "Specific step 3",
      "reason": "Why this helps",
      "risk_level": "LOW"
    }}
  ],
  "safety_note": "One critical safety warning for the farmer",
  "confidence_score": 80
}}"""


def parse_structured_response(raw: str) -> Optional[Dict]:
    """
    Robust JSON extractor using find/rfind (safer than regex for nested braces).
    Falls back to regex auto-repair if initial parse fails.
    """
    if not raw:
        return None
    # Strip markdown code fences
    text = re.sub(r'```(?:json)?', '', raw).strip().rstrip('`').strip()
    # Use find/rfind — safer than greedy regex for nested JSON
    start = text.find('{')
    end   = text.rfind('}') + 1
    if start == -1 or end == 0:
        return None
    json_str = text[start:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Auto-repair: trailing commas
        fixed = re.sub(r',\s*([}\]])', r'\1', json_str)
        try:
            return json.loads(fixed)
        except Exception:
            return None


def _safe_confidence(raw_score) -> int:
    """FIX 8 — Enforce confidence_score is int 0–100, reject floats/strings."""
    if isinstance(raw_score, bool):
        return 0
    if isinstance(raw_score, float):
        raw_score = int(raw_score)
    if not isinstance(raw_score, int):
        try:
            raw_score = int(str(raw_score).strip())
        except Exception:
            return 0
    return max(0, min(100, raw_score))


def ai_farming_advice(query: str, soil_type: str = "Unknown",
                      weather_data: str = "Normal seasonal conditions",
                      retry: bool = True) -> Dict[str, Any]:
    """
    Main AI call. Auto-retries once with a simplified prompt if JSON parse fails.
    Logs query to session CSV log.
    """
    c     = country_name()
    state = st.session_state.state or 'Unknown Region'
    lang  = st.session_state.language

    prompt = build_structured_prompt(query, c, state, soil_type, weather_data)
    raw    = call_gemini(prompt)
    structured = parse_structured_response(raw)

    # ── AUTO-RETRY if JSON failed ─────────────────────────────────────────────
    if not structured and retry:
        retry_prompt = f"""Previous response was not valid JSON. Try again.
Return ONLY a JSON object, no other text.
Question: "{query}" for {state}, {c}. Language: {lang}.
Format:
{{"location_analysis":"...","recommendations":[{{"action":"...","reason":"...","risk_level":"LOW"}},{{"action":"...","reason":"...","risk_level":"MEDIUM"}},{{"action":"...","reason":"...","risk_level":"LOW"}}],"safety_note":"...","confidence_score":75}}"""
        raw2 = call_gemini(retry_prompt)
        structured = parse_structured_response(raw2)
        if structured:
            raw = raw2  # use the successful raw

    # ── LOG TO CSV ────────────────────────────────────────────────────────────
    _log_query(query, state, c, lang, bool(structured))

    result: Dict[str, Any] = {
        'raw': raw, 'structured': structured,
        'crops': [], 'steps': [], 'why': '',
        'safety': '', 'next': '', 'confidence_score': 0,
    }

    if structured and 'recommendations' in structured:
        result['why']              = structured.get('location_analysis', '')
        result['safety']           = structured.get('safety_note', '')
        result['confidence_score'] = _safe_confidence(structured.get('confidence_score', 0))
        recs = structured.get('recommendations', [])
        for i, rec in enumerate(recs):
            result['crops'].append({
                'name'  : f"Recommendation {i+1}",
                'reason': rec.get('action', ''),
                'risk'  : rec.get('risk_level', 'LOW'),
            })
            result['steps'].append(rec.get('reason', ''))
        if recs:
            low_recs = [r for r in recs if r.get('risk_level') == 'LOW']
            first    = low_recs[0] if low_recs else recs[0]
            result['next'] = first.get('action', '')
    else:
        result['crops']  = [{'name':'Contact Local Extension Officer',
                              'reason': f'Agri extension office in {state} can give precise local guidance.',
                              'risk': 'LOW'}]
        result['steps']  = ['Assess current crop condition',
                             'Contact local extension officer',
                             'Test soil if possible', 'Monitor for 7 days']
        result['safety'] = 'Always wear gloves and mask when applying any chemical.'
        result['next']   = 'Consult your nearest agricultural extension officer.'
        # Show raw response if available — helps debug
        result['why']    = raw if raw and len(raw) > 10 else 'No response received. Check your API key and model name.'

    return result


def _log_query(query: str, state: str, country: str, lang: str, success: bool):
    """Append query log to session_state list (downloadable as CSV from Validation page)."""
    if 'query_log' not in st.session_state:
        st.session_state.query_log = []
    st.session_state.query_log.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'query'    : query[:120],
        'state'    : state,
        'country'  : country,
        'language' : lang,
        'json_ok'  : success,
    })


def soil_analysis_prompt(ph, n, p, k, om, stype) -> str:
    lang_full = get_lang_full()
    lang_name = st.session_state.language
    location = loc()
    return call_gemini(f"""You are AgSaathi soil expert for {location}.
CRITICAL: Respond ENTIRELY in {lang_full}. Every word must be in {lang_name}.

Soil: pH={ph}, N={n}, P={p}, K={k}, OM={om}%, Type={stype}

Provide in {lang_name}:
SOIL HEALTH SCORE: [0-100]/100
STATUS: [Poor/Fair/Good/Excellent]
TOP 3 CROPS: (for this soil)
AMENDMENTS: (products, quantities per acre)
3-STEP PLAN: (practical, numbered)
REASON: (1-2 sentences)

Be specific to {location}.""")


def validate_response(query: str, response: str) -> Dict[str, bool]:
    """
    FA-2 Step 5 validator — forces numbered YES/NO output, parses by splitting on ':'.
    More robust than checking for 'YES' in free-text line.
    """
    prompt = f"""You are a quality checker for an agricultural AI assistant.
Evaluate the AI response. Answer ONLY with the numbered format shown — no explanations.

Question: "{query}"
Response: "{response[:700]}"

Answer EXACTLY in this format (number colon space YES or NO):
1: YES
2: NO
3: YES
4: YES
5: NO

Questions:
1: Is the advice specific to a region (not generic advice that works anywhere)?
2: Does it provide logical reasoning for each recommendation?
3: Is the language simple enough for a non-technical farmer?
4: Does it avoid dangerous or misleading chemical dosages?
5: Does it include at least one actionable next step?"""

    raw = call_gemini(prompt)
    labels = [
        "Region-specific advice (not generic)?",
        "Logical reasoning for recommendations?",
        "Simple language for non-technical farmers?",
        "Avoids dangerous chemical dosages?",
        "Includes actionable next step?",
    ]
    checks: Dict[str, bool] = {lbl: False for lbl in labels}
    for line in raw.strip().split('\n'):
        line = line.strip()
        if ':' not in line:
            continue
        parts = line.split(':', 1)
        try:
            idx    = int(parts[0].strip()) - 1
            answer = parts[1].strip().upper()
            if 0 <= idx < len(labels):
                checks[labels[idx]] = answer.startswith('Y')
        except (ValueError, IndexError):
            continue
    return checks

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@400;500&family=Nunito+Sans:wght@400;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{
  --soil:#1A0F07;--bark:#3D2010;--clay:#A0522D;--straw:#D4A853;
  --wheat:#E8C97A;--sage:#7A9E7E;--meadow:#4A7C59;--sky:#B8D4C8;
  --cream:#F5EDD8;--danger:#C0392B;--success:#27AE60;
}
html,body{background:var(--soil)!important;}
[data-testid="stAppViewContainer"]{
  background:radial-gradient(ellipse at 12% 8%,rgba(74,124,89,.14) 0%,transparent 42%),
             radial-gradient(ellipse at 88% 88%,rgba(92,61,46,.22) 0%,transparent 42%),
             linear-gradient(158deg,#140D07 0%,#261408 45%,#161C10 100%)!important;
  min-height:100vh;
}
[data-testid="stHeader"]{background:transparent!important;}
.main .block-container{padding:2rem 2.5rem 4rem!important;max-width:1240px;}

/* SIDEBAR */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#110900 0%,#1E1008 60%,#110900 100%)!important;
  border-right:1px solid rgba(212,168,83,.18)!important;
}
[data-testid="stSidebar"] *{color:var(--cream)!important;}
[data-testid="stSidebar"] hr{border-color:rgba(212,168,83,.15)!important;}
[data-testid="stSidebar"] .stButton>button{
  background:transparent!important;border:1px solid rgba(212,168,83,.16)!important;
  border-radius:8px!important;color:rgba(245,237,216,.78)!important;
  font-family:'Nunito Sans',sans-serif!important;font-weight:600!important;
  font-size:.85em!important;padding:9px 12px!important;margin:1px 0!important;
  transition:all .2s ease!important;text-align:left!important;width:100%!important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(212,168,83,.1)!important;border-color:var(--straw)!important;
  color:var(--wheat)!important;transform:translateX(3px)!important;
}
/* TYPOGRAPHY */
h1,h2,h3{font-family:'Playfair Display',Georgia,serif!important;color:var(--cream)!important;}
h1{font-size:2.4rem!important;font-weight:900!important;}
h2{font-size:1.6rem!important;font-weight:700!important;}
h3{font-size:1.1rem!important;font-weight:700!important;}
p,span,label,div{font-family:'Nunito Sans',sans-serif!important;color:rgba(245,237,216,.9)!important;}

/* DROPDOWNS */
[data-baseweb="popover"],[data-baseweb="menu"],[data-baseweb="select"] [role="listbox"],
ul[role="listbox"],div[role="listbox"]{
  background-color:#2C1810!important;border:1px solid rgba(212,168,83,.35)!important;border-radius:10px!important;
}
[data-baseweb="menu"] li,[data-baseweb="option"],[role="option"]{
  background-color:#2C1810!important;color:var(--cream)!important;font-family:'Nunito Sans',sans-serif!important;
}
[data-baseweb="menu"] li:hover,[role="option"]:hover{background-color:rgba(212,168,83,.18)!important;color:var(--wheat)!important;}
[aria-selected="true"]{background-color:rgba(74,124,89,.3)!important;color:var(--sky)!important;}
[data-testid="stSelectbox"]>div>div{
  background:rgba(44,24,16,.92)!important;border:1px solid rgba(212,168,83,.32)!important;
  border-radius:10px!important;color:var(--cream)!important;
}

/* CARDS */
.card{background:rgba(245,237,216,.042);border:1px solid rgba(212,168,83,.19);
  border-radius:16px;padding:24px 26px;margin-bottom:16px;transition:all .3s ease;}
.card:hover{background:rgba(245,237,216,.07);border-color:rgba(212,168,83,.4);
  transform:translateY(-3px);box-shadow:0 14px 36px rgba(0,0,0,.28);}

/* HERO */
.hero{background:rgba(245,237,216,.033);border:1px solid rgba(212,168,83,.26);
  border-radius:24px;padding:52px 46px;text-align:center;position:relative;overflow:hidden;}
.hero::after{content:'';position:absolute;top:-80px;right:-80px;width:300px;height:300px;
  border-radius:50%;background:radial-gradient(circle,rgba(212,168,83,.06) 0%,transparent 70%);}
.hero-title{font-family:'Playfair Display',serif!important;font-size:4rem!important;
  font-weight:900!important;color:var(--wheat)!important;line-height:1.07!important;letter-spacing:-2px;}
.hero-sub{font-family:'DM Mono',monospace!important;font-size:.71rem!important;
  color:var(--straw)!important;letter-spacing:4px!important;text-transform:uppercase!important;opacity:.8;}
.hero-body{font-family:'Nunito Sans',sans-serif!important;font-size:1.05rem!important;
  color:rgba(245,237,216,.65)!important;line-height:1.8!important;max-width:480px;margin:0 auto!important;}

/* STEP BAR */
.steps{display:flex;align-items:center;margin-bottom:32px;}
.sdot{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-family:'DM Mono',monospace;font-size:.72rem;}
.sdot.done{background:var(--meadow);color:#fff;border:2px solid var(--sage);}
.sdot.active{background:var(--straw);color:var(--soil);border:2px solid var(--straw);}
.sdot.idle{background:transparent;color:rgba(245,237,216,.3);border:2px solid rgba(212,168,83,.2);}
.slbl{font-family:'Nunito Sans',sans-serif;font-size:.78rem;font-weight:600;margin-left:6px;}
.slbl.done{color:var(--sage);}.slbl.active{color:var(--wheat);}.slbl.idle{color:rgba(245,237,216,.28);}
.sline{flex:1;height:1px;background:rgba(212,168,83,.18);margin:0 10px;min-width:30px;}
.sline.done{background:var(--sage);}

/* STATS */
.srow{display:flex;gap:12px;margin:20px 0;}
.sbox{flex:1;background:rgba(245,237,216,.038);border:1px solid rgba(212,168,83,.16);
  border-radius:12px;padding:20px 14px;text-align:center;position:relative;overflow:hidden;transition:all .25s ease;}
.sbox::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--sage),var(--straw));}
.sbox:hover{background:rgba(212,168,83,.07);border-color:rgba(212,168,83,.36);transform:translateY(-3px);}
.snum{font-family:'Playfair Display',serif;font-size:2.1rem;font-weight:900;color:var(--wheat)!important;line-height:1;margin-bottom:5px;}
.slb{font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:2px;text-transform:uppercase;color:rgba(212,168,83,.6)!important;}

/* BADGES */
.lbadge{display:inline-flex;align-items:center;gap:6px;background:rgba(74,124,89,.16);
  border:1px solid rgba(122,158,126,.32);border-radius:50px;padding:6px 14px;
  font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:1.5px;color:var(--sky)!important;margin-bottom:18px;}
.sec{font-family:'DM Mono',monospace!important;font-size:.6rem!important;letter-spacing:3px!important;
  text-transform:uppercase!important;color:var(--straw)!important;opacity:.6;
  margin-bottom:12px!important;margin-top:28px!important;}

/* FEATURE CARDS */
.fc{background:rgba(245,237,216,.038);border:1px solid rgba(212,168,83,.17);
  border-radius:12px;padding:24px 20px;height:100%;transition:all .28s ease;}
.fc:hover{background:rgba(245,237,216,.07);border-color:rgba(212,168,83,.37);
  transform:translateY(-4px);box-shadow:0 12px 30px rgba(0,0,0,.25);}
.fi{font-size:1.9rem;margin-bottom:12px;display:block;}
.fc h3{font-size:1.05rem!important;color:var(--wheat)!important;margin-bottom:7px!important;}
.fc p{font-size:.84rem!important;color:rgba(245,237,216,.55)!important;line-height:1.58!important;}

/* AI RESPONSE */
.rec-card{background:rgba(74,124,89,.12);border:1px solid rgba(122,158,126,.26);
  border-radius:10px;padding:16px 18px;margin-bottom:10px;}
.rec-label{font-size:.65rem;font-family:'DM Mono',monospace;letter-spacing:1.5px;
  padding:3px 10px;border-radius:4px;color:#fff;display:inline-block;margin-bottom:8px;text-transform:uppercase;}
.rec-action{font-size:.95rem;color:rgba(245,237,216,.95)!important;font-weight:600;line-height:1.5;margin-bottom:6px;}
.rec-reason{font-size:.84rem;color:rgba(245,237,216,.65)!important;line-height:1.55;}
.why-box{background:rgba(45,90,61,.14);border:1px solid rgba(74,124,89,.28);border-radius:9px;
  padding:13px 16px;margin:10px 0;font-size:.87rem;color:rgba(245,237,216,.78)!important;line-height:1.6;}
.safe-box{background:rgba(160,82,45,.1);border:1px solid rgba(160,82,45,.3);border-radius:9px;
  padding:12px 16px;margin-top:10px;font-size:.86rem;color:rgba(245,237,216,.74)!important;}
.conf-row{display:flex;align-items:center;gap:12px;background:rgba(245,237,216,.06);
  border:1px solid rgba(212,168,83,.16);border-radius:8px;padding:11px 15px;margin-top:10px;}
.conf-bar-bg{flex:1;background:rgba(245,237,216,.08);border-radius:4px;height:7px;}
.conf-fill{height:7px;border-radius:4px;}
.conf-lbl{font-family:'DM Mono',monospace;font-size:.58rem;color:rgba(212,168,83,.58);white-space:nowrap;}
.conf-val{font-family:'DM Mono',monospace;font-size:.72rem;font-weight:700;white-space:nowrap;}
.json-pre{background:rgba(20,10,4,.8);border:1px solid rgba(212,168,83,.2);border-radius:9px;
  padding:14px;font-family:'DM Mono',monospace;font-size:.72rem;color:rgba(245,237,216,.68)!important;
  line-height:1.65;overflow-x:auto;white-space:pre-wrap;word-break:break-word;}

/* CHAT */
.bubble-u{background:rgba(74,124,89,.15);border:1px solid rgba(122,158,126,.24);
  border-radius:12px 12px 3px 12px;padding:14px 18px;margin:10px 0;}
.bubble-a{background:rgba(245,237,216,.036);border:1px solid rgba(212,168,83,.15);
  border-radius:12px 12px 12px 3px;padding:16px 20px;margin:10px 0;}
.bubble-lbl{font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:6px;opacity:.5;}
.bubble-u .bubble-lbl{color:var(--sky)!important;}.bubble-a .bubble-lbl{color:var(--straw)!important;}
.bubble-text{font-size:.9rem;color:var(--cream)!important;line-height:1.55;}

/* HISTORY — fixed overlap */
.hist-item{background:rgba(245,237,216,.036);border:1px solid rgba(212,168,83,.15);
  border-radius:12px;padding:18px 20px;margin-bottom:14px;overflow:hidden;}
.hist-q{font-size:.9rem;color:var(--wheat)!important;font-weight:600;
  line-height:1.45;word-break:break-word;margin-bottom:8px;}
.hist-meta{font-family:'DM Mono',monospace;font-size:.6rem;color:rgba(212,168,83,.5)!important;
  letter-spacing:1px;margin-bottom:12px;}
.hist-body{font-size:.84rem;color:rgba(245,237,216,.72)!important;line-height:1.6;
  word-break:break-word;overflow-wrap:break-word;}

/* ALERTS */
.alert-card{border-radius:11px;padding:18px 20px;margin-bottom:13px;
  border-left:4px solid;display:flex;align-items:flex-start;gap:12px;}
.alert-card.warn{background:rgba(212,168,83,.08);border-left-color:var(--straw);}
.alert-card.danger{background:rgba(160,82,45,.11);border-left-color:var(--clay);}
.alert-card.info{background:rgba(122,158,126,.09);border-left-color:var(--sage);}
.alert-title{font-family:'Playfair Display',serif!important;font-size:.96rem!important;
  color:var(--wheat)!important;margin-bottom:3px!important;}
.alert-body{font-size:.82rem!important;color:rgba(245,237,216,.6)!important;line-height:1.52!important;}

/* SOIL RESULT */
.soil-result{background:rgba(44,24,16,.72);border:1px solid rgba(212,168,83,.2);border-radius:11px;
  padding:18px 20px;margin-top:12px;font-size:.88rem;color:rgba(245,237,216,.82)!important;
  line-height:1.7;white-space:pre-wrap;word-break:break-word;}

/* CALENDAR */
.crop-card{background:rgba(245,237,216,.036);border:1px solid rgba(212,168,83,.13);
  border-radius:11px;padding:18px;margin-bottom:12px;transition:all .22s ease;}
.crop-card:hover{background:rgba(212,168,83,.06);border-color:rgba(212,168,83,.28);transform:translateX(3px);}
.crop-name{font-family:'Playfair Display',serif;font-size:1.02rem;color:var(--wheat)!important;margin-bottom:8px;}
.crop-tag{font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:1px;
  background:rgba(212,168,83,.1);border:1px solid rgba(212,168,83,.18);border-radius:4px;
  padding:2px 7px;color:var(--straw)!important;margin-right:5px;}
.crop-tip{font-size:.8rem;color:rgba(245,237,216,.5)!important;font-style:italic;margin-top:7px;}

/* COUNTRY PANEL */
.country-box{background:rgba(74,124,89,.09);border:1px solid rgba(122,158,126,.26);
  border-radius:14px;padding:24px 20px;text-align:center;}

/* INPUTS */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{
  background:rgba(44,24,16,.85)!important;border:1px solid rgba(212,168,83,.26)!important;
  border-radius:9px!important;color:var(--cream)!important;font-family:'Nunito Sans',sans-serif!important;}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{
  color:rgba(245,237,216,.3)!important;}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{
  border-color:var(--straw)!important;box-shadow:0 0 0 3px rgba(212,168,83,.08)!important;}

/* BUTTONS */
.stButton>button{background:transparent!important;border:1px solid rgba(212,168,83,.34)!important;
  border-radius:8px!important;color:var(--wheat)!important;font-family:'Nunito Sans',sans-serif!important;
  font-weight:700!important;font-size:.86rem!important;padding:10px 16px!important;
  transition:all .2s ease!important;}
.stButton>button:hover{background:rgba(212,168,83,.11)!important;border-color:var(--straw)!important;
  color:var(--straw)!important;transform:translateY(-2px)!important;
  box-shadow:0 6px 18px rgba(0,0,0,.2)!important;}

hr{border:none!important;border-top:1px solid rgba(212,168,83,.13)!important;margin:20px 0!important;}
[data-testid="stAlert"]{background:rgba(245,237,216,.036)!important;
  border:1px solid rgba(212,168,83,.18)!important;border-radius:9px!important;}
[data-testid="stExpander"]{background:rgba(245,237,216,.026)!important;
  border:1px solid rgba(212,168,83,.15)!important;border-radius:11px!important;}
details summary{font-family:'Nunito Sans',sans-serif!important;color:var(--cream)!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:rgba(245,237,216,.03)!important;
  border-radius:8px!important;padding:3px!important;border:1px solid rgba(212,168,83,.13)!important;}
[data-testid="stTabs"] [data-baseweb="tab"]{font-family:'Nunito Sans',sans-serif!important;
  color:rgba(245,237,216,.5)!important;font-weight:600!important;border-radius:6px!important;}
[data-testid="stTabs"] [aria-selected="true"]{background:rgba(212,168,83,.15)!important;color:var(--wheat)!important;}
::-webkit-scrollbar{width:6px;}
::-webkit-scrollbar-track{background:rgba(26,18,11,.8);}
::-webkit-scrollbar-thumb{background:rgba(212,168,83,.26);border-radius:3px;}
</style>""", unsafe_allow_html=True)


# ── STEP BAR ──────────────────────────────────────────────────────────────────
def step_bar(cur):
    labels = [T('where_farm').split()[0], T('which_state').split()[0], T('choose_lang').split()[0]]
    labels = ['Country', 'State', 'Language']
    parts = []
    for i, lbl in enumerate(labels):
        n = i + 1
        cls = 'done' if n < cur else ('active' if n == cur else 'idle')
        dot = '✓' if n < cur else str(n)
        parts.append(f'<div style="display:flex;align-items:center;gap:6px"><div class="sdot {cls}">{dot}</div><span class="slbl {cls}">{lbl}</span></div>')
        if i < 2:
            lc = 'done' if n < cur else ''
            parts.append(f'<div class="sline {lc}"></div>')
    st.markdown(f'<div class="steps">{"".join(parts)}</div>', unsafe_allow_html=True)


# ── ONBOARDING ────────────────────────────────────────────────────────────────
def page_hero():
    col1, col2, col3 = st.columns([1, 2.1, 1])
    with col2:
        st.markdown(f"""
        <div class="hero">
            <div class="hero-sub" style="margin-bottom:14px;">{T('tagline')}</div>
            <div class="hero-title" style="margin-bottom:14px;">{T('hero_title')}</div>
            <p class="hero-body" style="margin-bottom:32px;">{T('hero_body').replace(chr(10),'<br>')}</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(T('begin_btn'), use_container_width=True):
            st.session_state.page = 'country'; st.rerun()
        st.markdown("""
        <div style="text-align:center;margin-top:14px;font-family:'DM Mono',monospace;
             font-size:.62rem;letter-spacing:3px;color:rgba(212,168,83,.36);">
            CROP ADVICE · PEST DIAGNOSIS · SOIL HEALTH · MARKET INSIGHTS
        </div>""", unsafe_allow_html=True)


def page_country():
    step_bar(1)
    st.markdown(f'<h1>{T("where_farm")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(245,237,216,.48);margin-bottom:26px;">{T("where_sub")}</p>', unsafe_allow_html=True)
    countries = list(GEO.keys())
    for row_start in range(0, len(countries), 5):
        row = countries[row_start:row_start + 5]
        cols = st.columns(len(row))
        for i, c in enumerate(row):
            with cols[i]:
                flag = c.split()[-1]
                cname = c.replace(flag, '').strip()
                if st.button(f"{flag}\n\n{cname}", key=f"c_{c}", use_container_width=True):
                    st.session_state.country = c
                    st.session_state.state = None
                    st.session_state.page = 'state'; st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🌍 10 countries supported. Focus: India (UP), Canada, Ghana — FA-2 pilot regions.")


def page_state():
    if not st.session_state.country:
        st.session_state.page = 'country'; st.rerun()
    c = st.session_state.country
    d = GEO[c]
    step_bar(2)
    left, right = st.columns([1.35, 0.85])
    with left:
        st.markdown(f'<h1>{T("which_state")}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:rgba(245,237,216,.48);margin-bottom:22px;">{T("state_sub")}</p>', unsafe_allow_html=True)
        sel = st.selectbox("State", options=d['states'], index=None,
                           placeholder=f"Search {len(d['states'])} regions...", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        cb, cn = st.columns(2)
        with cb:
            if st.button(T('back_btn'), use_container_width=True):
                st.session_state.page = 'country'; st.rerun()
        with cn:
            if st.button(T('next_btn'), use_container_width=True, disabled=not sel):
                st.session_state.state = sel
                st.session_state.page = 'language'; st.rerun()
        if sel:
            st.markdown(f"""
            <div class="card" style="margin-top:20px;background:rgba(74,124,89,.09);border-color:rgba(122,158,126,.3);">
                <div style="font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:2px;color:rgba(212,168,83,.5);margin-bottom:6px;">{T('selected_region')}</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.35rem;color:var(--wheat);">📍 {sel}</div>
                <div style="font-size:.78rem;color:rgba(245,237,216,.45);margin-top:3px;">{c.split()[0]}</div>
            </div>""", unsafe_allow_html=True)
    with right:
        flag = c.split()[-1]
        cname = c.replace(flag, '').strip()
        st.markdown(f"""
        <div class="country-box">
            <div style="font-size:3.5rem;margin-bottom:8px;">{flag}</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.4rem;color:var(--wheat);font-weight:700;">{cname}</div>
            <div style="font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:1.5px;color:rgba(212,168,83,.5);margin-top:5px;">{len(d['states'])} REGIONS · {len(d['languages'])} LANGUAGES</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="sec">{T("quick_select")}</div>', unsafe_allow_html=True)
        for s in d['states'][:8]:
            if st.button(s, key=f"qs_{s}", use_container_width=True):
                st.session_state.state = s
                st.session_state.page = 'language'; st.rerun()


def page_language():
    if not st.session_state.country or not st.session_state.state:
        st.session_state.page = 'country'; st.rerun()
    c = st.session_state.country
    d = GEO[c]
    step_bar(3)
    st.markdown(f'<h1>{T("choose_lang")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="lbadge">📍 {st.session_state.state}, {c.split()[0]}</div>', unsafe_allow_html=True)
    icons = {'English':'🇬🇧','Hindi':'🇮🇳','Tamil':'🔤','Telugu':'🔡','Bengali':'🔡',
             'French':'🇫🇷','Spanish':'🇪🇸','Portuguese':'🇵🇹','Afrikaans':'🇿🇦',
             'Marathi':'🔡','Gujarati':'🔡','Kannada':'🔡','Twi':'🔡','Ga':'🔡',
             'Yoruba':'🔡','Hausa':'🔡','Igbo':'🔡','Xhosa':'🔡','Zulu':'🔡'}
    cols = st.columns(min(4, len(d['languages'])))
    for i, lang in enumerate(d['languages']):
        with cols[i % 4]:
            active = st.session_state.language == lang
            label = f"{'✅ ' if active else ''}{icons.get(lang,'🗣️')}  {lang}"
            if st.button(label, key=f"l_{lang}", use_container_width=True):
                st.session_state.language = lang; st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    cb, cn = st.columns(2)
    with cb:
        if st.button(T('back_btn')):
            st.session_state.page = 'state'; st.rerun()
    with cn:
        if st.button(f"{T('continue_btn')} ({st.session_state.language})", use_container_width=True):
            st.session_state.page = 'app'; st.session_state.nav = 'home'; st.rerun()


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def sidebar():
    s = st.session_state.state or ''
    c = st.session_state.country or ''
    lang = st.session_state.language
    flag = c.split()[-1] if c else ''
    cname = country_name()

    st.sidebar.markdown(f"""
    <div style="padding:6px 0 14px;text-align:center;">
        <div style="font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:900;color:var(--wheat);">AgSaathi</div>
        <div style="font-family:'DM Mono',monospace;font-size:.53rem;letter-spacing:3px;color:rgba(212,168,83,.4);margin-top:2px;">KISAN SAATHI · FA-2</div>
    </div>""", unsafe_allow_html=True)

    if s and c:
        st.sidebar.markdown(f"""
        <div style="background:rgba(74,124,89,.1);border:1px solid rgba(122,158,126,.24);
             border-radius:9px;padding:11px 12px;margin-bottom:11px;">
            <div style="font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:1.5px;
                 color:rgba(212,168,83,.46);margin-bottom:3px;">{T('location_label')}</div>
            <div style="font-size:.84rem;font-weight:700;color:var(--sky);">{flag} {s}</div>
            <div style="font-size:.72rem;color:rgba(245,237,216,.42);">{cname} · <span style="color:var(--straw);">{lang}</span></div>
        </div>""", unsafe_allow_html=True)

    # Nav items — single definition, no duplicates
    nav_items = [
        ('home',      '⌂',  T('dashboard')),
        ('ai',        '◈',  T('ai_assistant')),
        ('crop_rec',  '🌾', T('crop_rec')),
        ('pest',      '🐛', T('pest')),
        ('soil',      '◉',  T('soil')),
        ('sustainable','♻️', T('sustainable')),
        ('weather',   '🌦', T('weather')),
        ('calendar',  '▣',  T('calendar')),
        ('validate',  '✅', T('validate')),
        ('history',   '◷',  T('history')),
        ('feedback',  '◎',  T('feedback')),
    ]
    for key, icon, label in nav_items:
        if st.sidebar.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.nav = key; st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button(T('change_location'), use_container_width=True, key="sb_loc"):
        st.session_state.page = 'country'; st.session_state.country = None; st.session_state.state = None; st.rerun()
    if st.sidebar.button(f"{T('change_lang')} ({lang})", use_container_width=True, key="sb_lang"):
        st.session_state.page = 'language'; st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.markdown("""<div style="font-family:'DM Mono',monospace;font-size:.55rem;letter-spacing:1.5px;
        color:rgba(212,168,83,.38);text-align:center;">ADITYA SAHANI · REG 1000414<br>GENERATIVE AI · FA-2</div>""", unsafe_allow_html=True)


# ── RENDER AI RESPONSE ────────────────────────────────────────────────────────
def render_ai_response(r: Dict[str, Any], show_json: bool = False):
    """Renders structured JSON response cleanly."""
    lang = st.session_state.language
    structured = r.get('structured')

    if structured and 'recommendations' in structured:
        # Location analysis
        loc_text = structured.get('location_analysis', '')
        if loc_text:
            st.markdown(f'<div class="why-box">📍 <strong>{T("loc_analysis")}:</strong> {loc_text}</div>', unsafe_allow_html=True)

        # 3 recommendations
        recs = structured.get('recommendations', [])
        if recs:
            st.markdown(f'<div class="sec">{T("recommendations")}</div>', unsafe_allow_html=True)
            for i, rec in enumerate(recs):
                risk = rec.get('risk_level', 'LOW')
                risk_color = '#C0392B' if risk=='HIGH' else '#E67E22' if risk=='MEDIUM' else '#27AE60'
                st.markdown(f"""
                <div class="rec-card">
                    <span class="rec-label" style="background:{risk_color};">{risk} · #{i+1}</span>
                    <div class="rec-action">{rec.get('action','')}</div>
                    <div class="rec-reason">💡 {rec.get('reason','')}</div>
                </div>""", unsafe_allow_html=True)

        # Safety note
        safety = structured.get('safety_note', '')
        if safety:
            st.markdown(f'<div class="safe-box">⚠️ <strong>{T("safety_note")}:</strong> {safety}</div>', unsafe_allow_html=True)

        # Confidence bar
        score = int(structured.get('confidence_score', 0))
        score = max(0, min(100, score))
        score_color = '#27AE60' if score >= 70 else '#E67E22' if score >= 50 else '#C0392B'
        st.markdown(f"""
        <div class="conf-row">
            <span class="conf-lbl">{T('confidence')}</span>
            <div class="conf-bar-bg">
                <div class="conf-fill" style="width:{score}%;background:{score_color};"></div>
            </div>
            <span class="conf-val" style="color:{score_color};">{score}/100</span>
        </div>""", unsafe_allow_html=True)

        if show_json:
            with st.expander(T('view_json')):
                st.markdown(f'<div class="json-pre">{json.dumps(structured, indent=2, ensure_ascii=False)}</div>', unsafe_allow_html=True)
    else:
        # Fallback for failed JSON — show raw response so user can see what happened
        raw = r.get('raw', '')
        why = r.get('why', '')
        display_text = why if (why and len(why) > 10) else (raw if raw else None)
        if display_text and len(display_text) > 5:
            if display_text.startswith('No response') or display_text.startswith('Could not'):
                st.warning(f"⚠️ {display_text}")
            else:
                st.markdown(f'<div class="why-box">{display_text[:800]}</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ No response from AI. Check your API key and try again.")
        safety = r.get('safety', '')
        if safety:
            st.markdown(f'<div class="safe-box">⚠️ {safety}</div>', unsafe_allow_html=True)


# ── APP ROUTER ────────────────────────────────────────────────────────────────
def page_app():
    sidebar()
    pages = {
        'home': render_home, 'ai': render_ai,
        'crop_rec': render_crop_rec, 'pest': render_pest,
        'soil': render_soil, 'sustainable': render_sustainable,
        'weather': render_weather_alerts, 'calendar': render_calendar,
        'validate': render_validate, 'history': render_history,
        'feedback': render_feedback,
    }
    pages.get(st.session_state.nav, render_home)()


# ── HOME ──────────────────────────────────────────────────────────────────────
def render_home():
    c = st.session_state.country or ''; s = st.session_state.state or ''
    flag = c.split()[-1] if c else '🌍'; lang = st.session_state.language
    hr = datetime.now().hour
    greet = T('good_morning') if hr < 12 else (T('good_afternoon') if hr < 18 else T('good_evening'))
    st.markdown(f'<div class="lbadge">📍 {s}, {country_name() or "—"} {flag} · {lang}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1>{greet}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(245,237,216,.44);font-size:.86rem;margin-bottom:4px;">{datetime.now().strftime("%A, %d %B %Y")}</p>', unsafe_allow_html=True)
    stats = st.session_state.stats
    st.markdown(f"""
    <div class="srow">
        <div class="sbox"><div class="snum">{stats['queries']}</div><div class="slb">{T('ai_queries')}</div></div>
        <div class="sbox"><div class="snum">{stats['crops']}</div><div class="slb">{T('crops_advised')}</div></div>
        <div class="sbox"><div class="snum">{stats['soil_checks']}</div><div class="slb">{T('soil_analyses')}</div></div>
        <div class="sbox"><div class="snum">{stats['disease_checks']}</div><div class="slb">{T('diagnoses')}</div></div>
        <div class="sbox"><div class="snum">{len(st.session_state.history)}</div><div class="slb">{T('saved_queries')}</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="sec">{T("core_features")}</div>', unsafe_allow_html=True)
    tools = [
        ('crop_rec','🌾',T('crop_rec'),'Data-driven crop suggestions with risk levels and confidence scores.'),
        ('pest','🐛',T('pest'),'Diagnose symptoms. Risk-rated treatment protocols.'),
        ('weather','🌦',T('weather'),'Emergency advice for heatwaves, floods, and frost.'),
        ('soil','◉',T('soil'),'Soil pH, NPK analysis, and amendment advice.'),
        ('sustainable','♻️',T('sustainable'),'Eco-friendly practices and drip irrigation.'),
        ('validate','✅',T('validate'),'FA-2 Step 5 — Validate AI outputs with JSON viewer.'),
    ]
    for row_start in range(0, len(tools), 3):
        row = tools[row_start:row_start + 3]
        cols = st.columns(3)
        for col, (key, icon, title, desc) in zip(cols, row):
            with col:
                st.markdown(f'<div class="fc"><span class="fi">{icon}</span><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
                if st.button(f"{T('open')} {title}", key=f"h_{key}", use_container_width=True):
                    st.session_state.nav = key; st.rerun()


# ── GENERIC FEATURE PAGE ──────────────────────────────────────────────────────
def render_feature_page(feature_key: str, icon: str, title: str, description: str, prompts: list):
    s = st.session_state.state or ''; lang = st.session_state.language
    st.markdown(f'<div class="lbadge">📍 {s}, {country_name() or "—"} · 🌐 {lang}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1>{icon} {title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(245,237,216,.48);margin-bottom:20px;">{description}</p>', unsafe_allow_html=True)

    if lang != 'English':
        st.info(f"🌐 {T('asking').replace('...','').strip()} — AI will respond in **{lang}**")

    st.markdown(f'<div class="sec">{T("example_qs")}</div>', unsafe_allow_html=True)
    cols = st.columns(min(3, len(prompts)))
    for i, ex in enumerate(prompts):
        with cols[i % 3]:
            label = ex.replace('{state}', s or 'your region')
            if st.button(label, key=f"ex_{feature_key}_{i}", use_container_width=True):
                st.session_state.user_query = label

    st.markdown("<br>", unsafe_allow_html=True)
    user_in = st.text_input("", placeholder=T('type_question'), key=f"in_{feature_key}", label_visibility="collapsed")
    if st.button(T('ask_ai'), key=f"send_{feature_key}", use_container_width=True):
        if user_in.strip():
            st.session_state.user_query = user_in

    # Process pending query
    if st.session_state.user_query:
        q = st.session_state.user_query; st.session_state.user_query = None
        # Rate limit guard
        if not check_rate_limit():
            rate_limit_warning()
        else:
            with st.spinner(f"{T('asking')} — {lang}"):
                resp = ai_farming_advice(q)
            st.session_state.chat.append({'role': 'user', 'content': q, 'feature': title})
            st.session_state.chat.append({'role': 'ai', 'content': resp})
            st.session_state.stats['queries'] += 1
            st.session_state.stats['crops'] += len(resp.get('crops', []))
            st.session_state.history.append({
                'q': q, 'r': resp,
                'loc': f"{s}, {country_name() or '—'}",
                't': datetime.now().strftime("%b %d, %H:%M"),
                'feature': title, 'lang': lang,
            })
            st.rerun()

    # Chat history display
    if st.session_state.chat:
        st.markdown("---")
        for msg in st.session_state.chat[-8:]:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="bubble-u">
                    <div class="bubble-lbl">{T('you')} · {msg.get('feature','')}</div>
                    <div class="bubble-text">{msg['content']}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bubble-a"><div class="bubble-lbl">AgSaathi AI · gemini-2.5-flash</div>', unsafe_allow_html=True)
                render_ai_response(msg['content'], show_json=True)
                st.markdown('</div>', unsafe_allow_html=True)


# ── FEATURE PAGES ─────────────────────────────────────────────────────────────
def render_ai():
    s = st.session_state.state or 'your region'
    render_feature_page('ai', '◈', T('ai_assistant'),
        'Ask any farming question — crops, pests, soil, weather.',
        FEATURE_PROMPTS['crop_rec'][:2] + FEATURE_PROMPTS['pest'][:1])

def render_crop_rec():
    s = st.session_state.state or 'your region'
    render_feature_page('crop_rec', '🌾', T('crop_rec'),
        'Get region-specific crop suggestions with risk ratings and confidence scores.',
        [p.replace('{state}', s) for p in FEATURE_PROMPTS['crop_rec']])

def render_pest():
    s = st.session_state.state or 'your region'
    render_feature_page('pest', '🐛', T('pest'),
        'Diagnose crop symptoms and get risk-rated treatment protocols.',
        [p.replace('{state}', s) for p in FEATURE_PROMPTS['pest']])

def render_sustainable():
    s = st.session_state.state or 'your region'
    render_feature_page('sustainable', '♻️', T('sustainable'),
        'Eco-friendly practices: drip irrigation, stubble alternatives, composting.',
        [p.replace('{state}', s) for p in FEATURE_PROMPTS['sustainable']])


def render_soil():
    s = st.session_state.state or ''; lang = st.session_state.language
    st.markdown(f'<div class="lbadge">📍 {s}, {country_name() or "—"} · 🌐 {lang}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1>◉ {T("soil")}</h1>', unsafe_allow_html=True)
    if lang != 'English':
        st.info(f"🌐 Soil report will be in **{lang}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        ph = st.slider("Soil pH", 3.5, 10.5, 6.5, 0.1)
        om = st.slider("Organic Matter %", 0.0, 10.0, 2.5, 0.1)
    with col2:
        nitrogen   = st.select_slider("Nitrogen",   ["Low","Medium","High"], value="Medium")
        phosphorus = st.select_slider("Phosphorus", ["Low","Medium","High"], value="Medium")
    with col3:
        potassium = st.select_slider("Potassium", ["Low","Medium","High"], value="Medium")
        stype = st.selectbox("Soil Type", ["Clay","Sandy","Loamy","Silty","Usar (Alkaline)","Acidic","Saline"], index=2)
    if st.button(T('analyse_soil'), use_container_width=True):
        st.session_state.stats['soil_checks'] += 1
        with st.spinner(f"{T('asking')}"):
            result = soil_analysis_prompt(ph, nitrogen, phosphorus, potassium, om, stype)
        st.session_state.soil_result = result
    if st.session_state.soil_result:
        st.markdown(f'<div class="sec">{T("soil_report")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="soil-result">{st.session_state.soil_result}</div>', unsafe_allow_html=True)
        if st.button(T('ask_more')):
            st.session_state.user_query = f"My soil pH is {ph}, {nitrogen} nitrogen, {stype} type in {s}. What crops and amendments are best?"
            st.session_state.nav = 'ai'; st.rerun()


def render_weather_alerts():
    s = st.session_state.state or ''; lang = st.session_state.language
    st.markdown(f'<div class="lbadge">📍 {s}, {country_name() or "—"} · 🌐 {lang}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1>🌦 {T("weather")}</h1>', unsafe_allow_html=True)
    alerts = [
        ("warn","⚠","Heavy Rainfall Warning","Ensure field drainage and protect young crops. Avoid fertilizer application."),
        ("danger","🌪","Pest Alert — Fall Armyworm","Monitor maize crops closely. Apply recommended controls early."),
        ("warn","🌡","Heatwave Advisory","Irrigate early morning/late evening. Apply mulching. Shade sensitive seedlings."),
        ("info","❄","Frost Risk (Highlands)","Cover sensitive crops overnight. Delay planting if below 4°C."),
        ("danger","💧","Waterlogging Risk","Clear drains immediately. Harvest early if crop is mature."),
    ]
    for kind, icon, title, body in alerts:
        st.markdown(f"""
        <div class="alert-card {kind}">
            <div style="font-size:1.5rem;flex-shrink:0;">{icon}</div>
            <div><div class="alert-title">{title}</div><div class="alert-body">{body}</div></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"{T('ask_ai')}: {title}", key=f"al_{title[:10]}", use_container_width=False):
            st.session_state.user_query = f"What should I do about '{title}' as a farmer in {s}?"
            st.session_state.nav = 'ai'; st.rerun()
        st.markdown("<br style='margin:2px'>", unsafe_allow_html=True)


def render_calendar():
    s = st.session_state.state or ''
    st.markdown(f'<div class="lbadge">📍 {s}, {country_name() or "—"}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1>▣ {T("calendar")}</h1>', unsafe_allow_html=True)
    st.session_state.stats['calendar'] += 1
    tabs = st.tabs(list(SEASONAL.keys()))
    for tab, (season, data) in zip(tabs, SEASONAL.items()):
        with tab:
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;letter-spacing:2px;color:rgba(212,168,83,.52);margin:16px 0 12px;">IDEAL TEMP · {data["temp"]}</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            for i, crop in enumerate(data['crops']):
                with (col1 if i % 2 == 0 else col2):
                    st.markdown(f"""
                    <div class="crop-card">
                        <div class="crop-name">{crop['name']}</div>
                        <div><span class="crop-tag">🌡 {crop['temp']}</span><span class="crop-tag">📅 {crop['plant']}</span><span class="crop-tag">⏱ {crop['harvest']}</span></div>
                        <div class="crop-tip">{crop['tip']}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"{T('ask_ai')} — {crop['name']}", key=f"cal_{season}_{i}", use_container_width=True):
                        st.session_state.user_query = f"How do I grow {crop['name']} in {s}? Full planting, care, and harvest guide."
                        st.session_state.nav = 'ai'; st.rerun()


def render_validate():
    s = st.session_state.state or ''; lang = st.session_state.language
    st.markdown(f'<h1>✅ {T("validation_title")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(245,237,216,.48);margin-bottom:20px;">Language: <strong style="color:var(--straw);">{lang}</strong> · Model: {MODEL_NAME} · Temperature: {MODEL_TEMPERATURE} · Max Tokens: {MODEL_MAX_TOKENS}</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div style="font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:2px;color:rgba(212,168,83,.52);margin-bottom:11px;">FA-2 CHECKLIST CRITERIA</div>
        <div style="font-size:.86rem;color:rgba(245,237,216,.74);line-height:1.9;">
        ✅ Region-specific advice (not generic)?<br>
        ✅ Logical reasoning provided?<br>
        ✅ Simple language for farmers?<br>
        ✅ Avoids dangerous chemical dosages?<br>
        ✅ Actionable next steps included?<br>
        ✅ Structured JSON output?<br>
        ✅ Language matches selected language?
        </div>
    </div>""", unsafe_allow_html=True)

    test_prompts = [
        f"Recommend 3 crops for 1 acre in {s or 'Barabanki, UP'} with 5x profit over wheat.",
        "Organic treatment for aphids on mustard in Punjab, India.",
        "Emergency plan for waterlogging in Eastern UP rice fields.",
        "Best crops for cocoa-growing region in Ashanti, Ghana.",
        "Frost-resistant crops for Saskatchewan, Canada.",
        "Gypsum dosage for Usar soil (pH 10) in Uttar Pradesh?",
    ]
    sel = st.selectbox("Select test prompt", options=test_prompts)
    custom = st.text_input("Or custom test prompt", placeholder=T('type_question'))
    final_q = custom.strip() if custom.strip() else sel

    col1, col2 = st.columns(2)
    with col1:
        if st.button(T('run_test'), use_container_width=True):
            with st.spinner(f"Generating structured JSON in {lang}..."):
                resp = ai_farming_advice(final_q)
                checks = validate_response(final_q, resp['raw'])
            st.session_state.validation_results = {'q': final_q, 'r': resp, 'c': checks}
            st.session_state.stats['queries'] += 1
    with col2:
        if st.button(T('run_all'), use_container_width=True):
            results = []
            for tp in test_prompts[:3]:
                with st.spinner(f"Testing: {tp[:40]}..."):
                    r = ai_farming_advice(tp)
                    ch = validate_response(tp, r['raw'])
                    results.append({'q': tp, 'r': r, 'c': ch})
            st.session_state.validation_results = {'batch': results}

    vr = st.session_state.validation_results
    if vr:
        if 'batch' in vr:
            for i, item in enumerate(vr['batch']):
                with st.expander(f"Test {i+1}: {item['q'][:55]}..."):
                    render_ai_response(item['r'], show_json=True)
                    passed = sum(1 for v in item['c'].values() if v)
                    st.markdown(f'<div class="card"><b>{T("test_score")}: {passed}/{len(item["c"])}</b></div>', unsafe_allow_html=True)
        elif 'q' in vr:
            st.markdown(f'<div class="card"><b>Prompt:</b> {vr["q"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="bubble-a"><div class="bubble-lbl">AgSaathi AI Response</div>', unsafe_allow_html=True)
            render_ai_response(vr['r'], show_json=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if vr.get('c'):
                st.markdown(f'<div class="sec">{T("test_score")}</div>', unsafe_allow_html=True)
                passed = 0
                for label, ok in vr['c'].items():
                    color = '#27AE60' if ok else '#C0392B'
                    icon = '✅' if ok else '❌'
                    st.markdown(f'<div style="color:{color};padding:5px 0;font-size:.87rem;font-weight:700;">{icon} {label}</div>', unsafe_allow_html=True)
                    if ok: passed += 1
                total = len(vr['c'])
                score = int((passed / total) * 100) if total else 0
                sc = '#27AE60' if score >= 70 else '#E67E22' if score >= 50 else '#C0392B'
                st.markdown(f'<div class="card" style="text-align:center;margin-top:14px;"><div style="font-size:1.7rem;font-weight:900;color:{sc};">{score}%</div><div style="font-family:\'DM Mono\',monospace;font-size:.62rem;letter-spacing:2px;color:rgba(212,168,83,.58);">{T("test_score")} · {T("target")}</div></div>', unsafe_allow_html=True)

    # ── CSV DOWNLOAD — Query log for evaluation ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sec">Query Log — Download for Evaluation</div>', unsafe_allow_html=True)
    log = st.session_state.get('query_log', [])
    if log:
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=['timestamp','query','state','country','language','json_ok'])
        writer.writeheader()
        writer.writerows(log)
        st.download_button(
            label=f"📥 Download Query Log ({len(log)} entries)",
            data=buf.getvalue(),
            file_name=f"agsaathi_log_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
        st.markdown(f'<p style="font-size:.8rem;color:rgba(245,237,216,.4);">{len(log)} queries logged this session · JSON success rate: {sum(1 for r in log if r["json_ok"])}/{len(log)}</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:.8rem;color:rgba(245,237,216,.3);">No queries logged yet. Run a test above.</p>', unsafe_allow_html=True)


def render_history():
    st.markdown(f'<h1>◷ {T("history_title")}</h1>', unsafe_allow_html=True)
    count = len(st.session_state.history)
    st.markdown(f'<p style="font-family:\'DM Mono\',monospace;font-size:.65rem;letter-spacing:1.5px;color:rgba(212,168,83,.46);">{count} {T("saved_queries").upper()}</p>', unsafe_allow_html=True)

    if not count:
        st.markdown(f"""
        <div style="text-align:center;padding:50px 22px;color:rgba(245,237,216,.2);">
            <div style="font-size:2rem;margin-bottom:10px;">◷</div>
            <div style="font-family:'DM Mono',monospace;font-size:.66rem;letter-spacing:2px;">{T('no_history')}</div>
        </div>""", unsafe_allow_html=True)
        return

    for i, item in enumerate(reversed(st.session_state.history)):
        idx = count - 1 - i
        # History item — no overlap: question, meta, then expander for full response
        q_preview = item['q'][:80] + ('...' if len(item['q']) > 80 else '')
        st.markdown(f"""
        <div class="hist-item">
            <div class="hist-q">Q{idx+1}. {q_preview}</div>
            <div class="hist-meta">📍 {item.get('loc','—')} · ⏱ {item.get('t','—')} · 🌐 {item.get('lang','English')} · {item.get('feature','General')}</div>
        </div>""", unsafe_allow_html=True)

        # Buttons on same row
        b1, b2, b3 = st.columns([2, 1, 1])
        with b2:
            if st.button(T('ask_again'), key=f"re_{i}", use_container_width=True):
                st.session_state.user_query = item['q']
                st.session_state.nav = 'ai'; st.rerun()
        with b3:
            if st.button(T('delete'), key=f"del_{i}", use_container_width=True):
                st.session_state.history.pop(idx); st.rerun()

        # Full response in clean expander — no text overlap
        with st.expander(f"View full AI response #{idx+1}"):
            r = item['r']
            render_ai_response(r, show_json=False)


def render_feedback():
    lang = st.session_state.language
    st.markdown(f'<h1>◎ {T("feedback")}</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(245,237,216,.46);margin-bottom:24px;">Help improve AgSaathi. Your feedback improves the AI advisory system.</p>', unsafe_allow_html=True)
    rating = st.select_slider(T('rating'), options=[1,2,3,4,5], value=4,
                              format_func=lambda x: "⭐"*x, label_visibility="collapsed")
    labels = {1:"Poor",2:"Needs work",3:"Neutral",4:"Good",5:"Excellent"}
    st.markdown(f'<p style="color:var(--straw);font-family:\'DM Mono\',monospace;font-size:.74rem;">{rating}/5 — {labels[rating]}</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(T('positive'), key="fp", use_container_width=True): st.session_state.feedback_type = "Positive"
    with col2:
        if st.button(T('suggestion'), key="fs", use_container_width=True): st.session_state.feedback_type = "Suggestion"
    with col3:
        if st.button(T('bug_report'), key="fb", use_container_width=True): st.session_state.feedback_type = "Bug Report"
    if st.session_state.feedback_type:
        st.success(f"Category: {st.session_state.feedback_type}")
    with st.form("fb_form"):
        title = st.text_input(T('feedback_title'), placeholder="Brief summary...")
        msg = st.text_area(T('feedback_msg'), placeholder="Describe in detail... (min 20 characters)", height=130)
        if st.form_submit_button(T('submit_feedback'), use_container_width=True):
            if not title: st.error("Please enter a title.")
            elif len(msg) < 20: st.error("Message must be at least 20 characters.")
            else:
                st.success(T('thank_you')); st.balloons()
                st.session_state.feedback_type = None


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    p = st.session_state.page
    if   p == 'hero':     page_hero()
    elif p == 'country':  page_country()
    elif p == 'state':    page_state()
    elif p == 'language': page_language()
    elif p == 'app':      page_app()

if __name__ == "__main__":
    main()

