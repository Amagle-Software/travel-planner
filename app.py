import streamlit as st
import requests
from groq import Groq

# API Keys (UNCHANGED)
WEATHER_API_KEY = "6940d255ab274054b54200838252502"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)


# 🌤 Weather Tool
def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    response = requests.get(url)
    data = response.json()

    if "current" in data:
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        return temp, condition
    return None, None


# Extract Personal Info
def extract_profile_info(text):
    prompt = f"""
    Extract any user information if present.
    Name, city, or workplace.
    If not present, return 'none'.

    Text: {text}
    """

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return chat.choices[0].message.content.lower()



#  AI Response with Memory
def ai_chat_response(user_input, chat_history, user_profile):
    system_prompt = f"""
    You are a friendly weather chatbot.
    Remember user details and speak naturally.

    Known user info:
    Name: {user_profile.get('name')}
    City: {user_profile.get('city')}
    Workplace: {user_profile.get('workplace')}

    Use this information if relevant.
    """

    messages = [{"role": "system", "content": system_prompt}]

    # Add chat history
    for msg in chat_history:
        messages.append(msg)

    messages.append({"role": "user", "content": user_input})

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    return chat.choices[0].message.content


# -------------------------------
# 🎨 Streamlit UI
# -------------------------------
st.set_page_config(page_title="Smart Weather Chatbot")
st.title("🌤 Smart Weather Chatbot (with Memory)")

# Initialize memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": None,
        "city": None,
        "workplace": None
    }

# Welcome message
if len(st.session_state.chat_history) == 0:
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": "Hello 👋 I can remember our conversation. Tell me about your city or work!"
    })

# Display messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
user_input = st.chat_input("Talk to me...")

if user_input:
    # Store user message
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    # Extract profile info
    extracted = extract_profile_info(user_input)

    if "pune" in extracted:
        st.session_state.user_profile["city"] = "Pune"
    if "indore" in extracted:
        st.session_state.user_profile["city"] = "Indore"
    if "working" in extracted:
        st.session_state.user_profile["workplace"] = extracted

    # If city known, fetch weather
    city = st.session_state.user_profile.get("city")
    if city:
        temp, condition = get_weather(city)
        weather_context = f"The current weather in {city} is {temp}°C with {condition}."
    else:
        weather_context = ""

    # AI reply
    reply = ai_chat_response(
        user_input + "\n" + weather_context,
        st.session_state.chat_history,
        st.session_state.user_profile
    )

    st.session_state.chat_history.append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.write(reply)
