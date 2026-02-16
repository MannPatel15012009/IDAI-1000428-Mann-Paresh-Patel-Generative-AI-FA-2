# 🌾 AgroNova Enterprise AI  
### Generative AI Powered Smart Farming Assistant  

> Developed for **IDAI-1000428 – Generative AI FA-2**  
> By **Mann Paresh Patel**

---

## 📌 Project Overview

AgroNova Enterprise AI is an intelligent agricultural decision-support system built using **Streamlit** and **Google Generative AI (Gemini)**.

The application leverages large language models to generate structured, explainable, and practical farm recommendations based on user inputs such as:

- 🌍 Country and State  
- 🌱 Crop Growth Stage  
- 🎯 Farming Goals  
- 🌦️ Weather Conditions  
- ❓ Custom Farmer Queries  

The goal of this project is to demonstrate how **Generative AI can be responsibly integrated into real-world agricultural workflows** to enhance productivity, planning, and risk assessment.

---

## 🎯 Objectives

- Apply Generative AI in a domain-specific real-world use case.
- Generate structured JSON outputs for reliability.
- Integrate weather context into AI responses.
- Provide risk classification and confidence scoring.
- Export results into professional PDF reports.
- Maintain a clean and interactive UI using Streamlit.

---

## 🧠 Core Features

### 1️⃣ AI-Based Smart Farm Planning
- Uses Google Gemini model to generate:
  - Actionable farming steps
  - Justifications ("Why this action?")
  - Risk levels (LOW / MEDIUM / HIGH)
  - Confidence score
- Output is structured in JSON format for clarity and scalability.

---

### 2️⃣ Multi-Level AI Creativity
Users can select different creativity levels:
- Conservative (Low temperature)
- Balanced
- Creative (High temperature)

This demonstrates controlled generative AI output tuning.

---

### 3️⃣ Weather Integration 🌦️
- Real-time weather data fetching via API.
- Weather context is injected into AI prompts.
- Allows better contextual farm recommendations.

---

### 4️⃣ Image Upload Capability 🖼️
- Users can upload crop images.
- Designed for future AI vision integration.
- Demonstrates multimodal AI readiness.

---

### 5️⃣ Safety Classification & Risk Analysis ⚠️
- Each recommendation is labeled with a risk category.
- Encourages responsible AI usage in agriculture.
- Helps farmers evaluate decision safety.

---

### 6️⃣ PDF Report Generation 📄
- Generates a formatted farm advisory report.
- Includes:
  - Recommendations
  - Risk levels
  - Confidence score
- Built using ReportLab.
- Downloadable directly from the app.

---

### 7️⃣ Confidence Score Display 📊
- AI generates a confidence percentage.
- Helps users understand reliability of output.

---

## 🏗️ Technology Stack

| Component | Technology |
|------------|------------|
| Frontend | Streamlit |
| Backend Logic | Python |
| AI Model | Google Gemini |
| Weather API | OpenWeather (or compatible API) |
| PDF Generation | ReportLab |
| Data Handling | Pandas |
| API Calls | Requests |

---

## 📂 Project Structure


IDAI-1000428-Mann-Paresh-Patel-Generative-AI-FA-2/
│
├── app.py
├── requirements.txt
├── README.md
└── assets/ (if applicable)


---

## ⚙️ Installation Guide

### Step 1: Clone Repository

```bash
git clone https://github.com/MannPatel15012009/IDAI-1000428-Mann-Paresh-Patel-Generative-AI-FA-2.git
cd IDAI-1000428-Mann-Paresh-Patel-Generative-AI-FA-2
```
Step 2: Install Dependencies
`pip install -r requirements.txt`

If needed:
`
pip install streamlit google-genai requests pandas reportlab
`
Step 3: Configure API Keys

Create a .streamlit/secrets.toml file:

```
GOOGLE_API_KEY="your_google_api_key_here"
WEATHER_API_KEY="your_weather_api_key_here"
```
Step 4: Run the Application
`streamlit run app.py`
🔄 Application Workflow

User selects:

Country

State

Crop stage

Farming goal

Creativity level

(Optional) Weather API fetches live weather.

Prompt is constructed dynamically.

Gemini generates structured JSON response.

Output is parsed and displayed cleanly.

User can download PDF report.

🧪 Sample Output Format
```
{
  "recommendations": [
    {
      "action": "Apply nitrogen fertilizer in split doses.",
      "why": "Supports vegetative growth during early stage.",
      "risk": "LOW"
    }
  ],
  "confidence_score": 85
}
```
🔐 Responsible AI Considerations

No automated irreversible decisions.

Risk labeling included.

Human oversight required.

Designed as advisory support tool only.

📈 Future Improvements

Multimodal AI integration (image-based crop diagnosis).

Soil health database integration.

Market price forecasting.

Pest detection module.

Multilingual support.

AI-powered district-level recommendation system.

🎓 Academic Context

This project was developed as part of:

IDAI-1000428 – Generative AI Final Assessment (FA-2)

It demonstrates:

Prompt engineering

Structured AI output design

API integration

AI temperature control

Responsible AI practices

End-to-end deployment using Streamlit

🤝 Contribution

Pull requests and improvements are welcome.

To contribute:

Fork the repository

Create a feature branch

Commit changes

Open a pull request

📜 License

This project is licensed under the MIT License.

👨‍💻 Author

Mann Paresh Patel
Generative AI Enthusiast | Python Developer | Applied AI Explorer

⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!


---
