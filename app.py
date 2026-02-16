import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# ================= LOAD ENV =================
load_dotenv()
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ================= WEATHER FUNCTION =================
def get_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_KEY}&units=metric"
    )
    data = requests.get(url).json()

    if data.get("cod") != 200:
        return None

    return {
        "city": data["name"],
        "temp": data["main"]["temp"],
        "feels": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "condition": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"]
    }

# ================= GEMINI NLP =================
def extract_city_and_intent(text):
    prompt = f"""
    Extract city and intent from user message.
    Respond ONLY in JSON.

    Message: "{text}"

    Example:
    {{
      "city": "Bengaluru",
      "intent": "weather"
    }}
    """

    response = model.generate_content(prompt)
    return json.loads(response.text)

# ================= UI CONFIG =================
st.set_page_config(page_title="Weather Chatbot", page_icon="🌦️", layout="centered")

st.markdown("<h1 style='text-align:center'>🌦️ Weather Chatbot Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Ask anything about weather in natural language</p>", unsafe_allow_html=True)

# ================= CHAT INPUT =================
user_input = st.chat_input("Ask like: Will it rain in Mysuru today?")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    try:
        result = extract_city_and_intent(user_input)
        city = result.get("city")

        weather = get_weather(city)

        with st.chat_message("assistant"):
            if weather:
                st.markdown(
                    f"""
                    <div style="background:#f0f8ff;padding:20px;border-radius:15px;text-align:center">
                        <h2>📍 {weather['city']}</h2>
                        <img src="https://openweathermap.org/img/wn/{weather['icon']}@2x.png">
                        <h1>{weather['temp']}°C</h1>
                        <p>{weather['condition']}</p>
                        <p>🌡️ Feels Like: {weather['feels']}°C</p>
                        <p>💧 Humidity: {weather['humidity']}%</p>
                        <p>💨 Wind: {weather['wind']} m/s</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error("❌ City not found. Please check spelling.")

    except Exception as e:
        st.error("⚠️ Error understanding your request.")
