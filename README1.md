# AgroNova Enterprise AI

### Generative AI Powered Smart Farming Assistant

> Developed for *IDAI-1000428, Generative AI FA-2*  
> By *Mann Paresh Patel*

---

## Project Overview

AgroNova Enterprise AI is an intelligent agricultural decision-support system created with *Streamlit* and *Google Generative AI (Gemini). The application uses large language models to provide structured, clear, and practical farm recommendations based on user inputs like:

- Country and State  
- Crop Growth Stage  
- Farming Goals  
- Weather Conditions  
- Custom Farmer Queries  

This project aims to show how **Generative AI can be responsibly included in real-world agricultural practices* to improve productivity, planning, and risk assessment.

---

## Objectives

- Apply Generative AI in a specific real-world case.  
- Generate structured JSON outputs for reliability.  
- Incorporate weather context into AI responses.  
- Provide risk classification and confidence scoring.  
- Export results into professional PDF reports.  
- Keep a clean and interactive UI with Streamlit.  

---

## Core Features

### 1. AI-Based Smart Farm Planning

- Utilizes the Google Gemini model to produce:  
  - Actionable farming steps  
  - Reasons ("Why this action?")  
  - Risk levels (LOW / MEDIUM / HIGH)  
  - Confidence score  
- Outputs are structured in JSON format for clarity and scalability.  

---

### 2. Multi-Level AI Creativity

Users can choose different creativity levels:

- Conservative (Low temperature)  
- Balanced  
- Creative (High temperature)  

This feature shows how to control generative AI output tuning.

---

### 3. Weather Integration

- Fetches real-time weather data via API.  
- Integrates weather context into AI prompts.  
- Provides better contextual farm recommendations.  

---

### 4. Image Upload Capability

- Users can upload crop images.  
- This feature is designed for future AI vision integration.  
- Shows readiness for multimodal AI.  

---

### 5. Safety Classification & Risk Analysis

- Each recommendation includes a risk category.  
- Promotes responsible AI use in farming.  
- Assists farmers in evaluating decision safety.  

---

### 6. PDF Report Generation

- Generates a formatted farm advisory report.  
- Contains:  
  - Recommendations  
  - Risk levels  
  - Confidence score  
- Built with ReportLab.  
- Users can download it directly from the app.  

---

### 7. Confidence Score Display

- AI produces a confidence percentage.  
- This helps users assess the reliability of the output.  

---

## Technology Stack

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

## Project Structure


IDAI-1000428-Mann-Paresh-Patel-Generative-AI-FA-2/
│
├── app.py
├── requirements.txt
├── README.md
└── assets/ (if applicable)


---

## Installation Guide

### Step 1: Clone Repository

```bash
git clone https://github.com/MannPatel15012009/IDAI-1000428-Mann-Paresh-Patel-Generative-AI-FA-2.git
cd IDAI-1000428-Mann-Paresh-Patel-Generative-AI-FA-2
```
Step 2: Install Dependencies
`pip install -r requirements.txt`

If needed:

`pip install streamlit google-genai requests pandas reportlab`
Step 3: Configure API Keys

Create a .streamlit/secrets.toml file:
```
GOOGLE_API_KEY="your_google_api_key_here"
WEATHER_API_KEY="your_weather_api_key_here"
```
Step 4: Run the Application
`streamlit run app.py`
Application Workflow

User selects:

Country

State

Crop stage

Farming goal

Creativity level (Optional)

Weather API fetches live weather.
The prompt is constructed dynamically.
Gemini generates a structured JSON response.
Output is parsed and displayed neatly.
Users can download the PDF report.

Sample Output Format
```{
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
Responsible AI Considerations

No automated irreversible decisions.

Risk labeling is included.

Human oversight is required.

Designed as an advisory support tool only.

Future Improvements

Multimodal AI integration (image-based crop diagnosis).

Soil health database integration.

Market price forecasting.

Pest detection module.

Multilingual support.

AI-powered district-level recommendation system.

Academic Context

This project was developed as part of:

IDAI-1000428, Generative AI Final Assessment (FA-2)

It showcases:

Prompt engineering

Structured AI output design

API integration

AI temperature control

Responsible AI practices

End-to-end deployment using Streamlit

Contribution

Pull requests and improvements are welcome.

To contribute:

Fork the repository

Create a feature branch

Commit changes

Open a pull request

License

This project is licensed under the MIT License.

Author

Mann Paresh Patel
Generative AI Enthusiast | Python Developer | Applied AI Explorer

Support

If you find this project useful, consider giving it a star on GitHub!
