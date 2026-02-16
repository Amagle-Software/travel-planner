import streamlit as st
import requests
import google.generativeai as genai
import json
import re

# =============================
# 🔑 API KEYS
# =============================
OPENWEATHER_API_KEY = "7419159b8393b2558edec36f2d99a3a7"
GEMINI_API_KEY = "AIzaSyCYC0BeZyXqRxob5mU8irxyKUWj8Odp6yE"

# =============================
# CONFIGURE GEMINI
# =============================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# =============================
# STREAMLIT PAGE CONFIG
# =============================
st.set_page_config(
    page_title="AI Weather Assistant",
    page_icon="☁️",
    layout="centered"
)

# =============================
# CUSTOM CSS
# =============================
st.markdown("""
<style>
.suggestion-box {
    background: linear-gradient(135deg, #0b2d4a, #143a5c);
    padding: 18px;
    border-radius: 12px;
    margin-top: 20px;
    color: #dbefff;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 🔍 EXTRACT CITY USING GEMINI
# =============================
def extract_city(user_text):
    prompt = f"""
Extract ONLY the city name from the sentence below.
Do NOT include district, state, or country.

Sentence: "{user_text}"

Return ONLY valid JSON:
{{ "city": "CityName" }}
"""
    try:
        response = model.generate_content(prompt)
        raw = re.sub(r"```json|```", "", response.text).strip()
        city = json.loads(raw).get("city", "")
        city = re.sub(r"[^a-zA-Z\s]", "", city).strip().title()
        return city
    except:
        return None

# =============================
# 🔁 FALLBACK CITY EXTRACTION
# =============================
def fallback_city_extraction(text):
    match = re.search(r"in\s+([a-zA-Z\s]+)", text.lower())
    if match:
        return match.group(1).title().strip()
    return None

# =============================
# 🌦 GET WEATHER DATA
# =============================
def get_weather(city):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    res = requests.get(url)

    if res.status_code != 200:
        return None

    data = res.json()
    return {
        "city": data["name"],
        "temp": round(data["main"]["temp"], 2),
        "humidity": data["main"]["humidity"],
        "wind": round(data["wind"]["speed"], 2),
        "condition": data["weather"][0]["description"].title()
    }

# =============================
# ☁ WEATHER ICON
# =============================
def get_icon(condition):
    c = condition.lower()
    if "cloud" in c:
        return "☁️"
    elif "rain" in c:
        return "🌧️"
    elif "clear" in c:
        return "☀️"
    elif "storm" in c or "thunder" in c:
        return "⛈️"
    else:
        return "🌤️"

# =============================
# 🤖 AI WEATHER SUGGESTION
# =============================
def generate_weather_suggestion(weather):
    prompt = f"""
Create a short, friendly, professional weather suggestion.

Weather details:
Temperature: {weather['temp']} °C
Humidity: {weather['humidity']} %
Wind Speed: {weather['wind']} m/s
Condition: {weather['condition']}

Do NOT mention numbers explicitly.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# =============================
# 🖥 UI HEADER
# =============================
st.markdown("""
<h1 style="text-align:center;">☁️ AI Weather Assistant</h1>
<p style="text-align:center; color:gray;">
Ask naturally like: <i>"What's the weather in Bengaluru today?"</i>
</p>
""", unsafe_allow_html=True)

# =============================
# 🔤 INPUT
# =============================
query = st.text_input("Enter your question")

if st.button("Get Weather"):

    if not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Fetching weather..."):

        # 1️⃣ Extract city using AI
        city = extract_city(query)

        # 2️⃣ Fallback if AI fails
        if not city:
            city = fallback_city_extraction(query)

        if not city:
            st.error(
                "❌ Could not detect city.\n\n"
                "Try:\n"
                "- Weather in Bengaluru\n"
                "- Temperature in Tiptur"
            )
            st.stop()

        # 3️⃣ Fetch weather
        weather = get_weather(city)

        if not weather:
            st.error(
                f"❌ Weather data not found for **{city}**.\n\n"
                "Try another city name."
            )
            st.stop()

        # 4️⃣ Display result
        icon = get_icon(weather["condition"])
        suggestion = generate_weather_suggestion(weather)

        st.markdown("---")
        st.markdown(f"## 📍 {weather['city']}")
        st.markdown(f"### {icon}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("🌡 Temperature", f"{weather['temp']} °C")
            st.metric("🌬 Wind Speed", f"{weather['wind']} m/s")

        with col2:
            st.metric("💧 Humidity", f"{weather['humidity']} %")
            st.markdown(f"**☁ Condition:** {weather['condition']}")

        st.markdown(
            f"""
            <div class="suggestion-box">
            🤖 {suggestion}
            </div>
            """,
            unsafe_allow_html=True
        )