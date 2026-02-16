import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import google.generativeai as genai

# =============================
# 🔑 API KEYS (PASTE YOUR KEYS)
# =============================
OPENWEATHER_API_KEY = "7419159b8393b2558edec36f2d99a3a7"
GEMINI_API_KEY = "AIzaSyCYC0BeZyXqRxob5mU8irxyKUWj8Odp6yE"

# =============================
# Configure Gemini
# =============================
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash"
)

# =============================
# Fetch Weather Data
# =============================
def get_weather(city):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return None

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"]
    }

# =============================
# Chatbot Logic
# =============================
def get_bot_response(city):
    weather = get_weather(city)

    if not weather:
        return "❌ Unable to fetch weather. Please check the city name."

    prompt = f"""
    You are a friendly weather chatbot.

    City: {weather['city']}
    Temperature: {weather['temperature']}°C
    Humidity: {weather['humidity']}%
    Weather condition: {weather['condition']}

    Respond politely with simple advice.
    """

    response = model.generate_content(prompt)
    return response.text

# =============================
# Button Click Function
# =============================
def send_message():
    city = city_entry.get().strip()

    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name")
        return

    chat_area.insert(tk.END, f"You: {city}\n")
    city_entry.delete(0, tk.END)

    try:
        reply = get_bot_response(city)
        chat_area.insert(tk.END, f"Bot: {reply}\n\n")
        chat_area.yview(tk.END)
    except Exception as e:
        chat_area.insert(tk.END, "Bot: ❌ Error generating response\n\n")

# =============================
# Tkinter UI Setup
# =============================
root = tk.Tk()
root.title("🌦️ Weather Chatbot Agent")
root.geometry("600x500")

# Heading
heading = tk.Label(
    root,
    text="🌦️ Weather Chatbot",
    font=("Arial", 18, "bold")
)
heading.pack(pady=10)

# Chat display area
chat_area = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    width=70,
    height=20,
    font=("Arial", 10)
)
chat_area.pack(padx=10, pady=10)
chat_area.insert(tk.END, "Bot: Hello! Enter a city name to get weather info 🌍\n\n")
chat_area.config(state="normal")

# Input frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

city_entry = tk.Entry(
    input_frame,
    width=40,
    font=("Arial", 12)
)
city_entry.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(
    input_frame,
    text="Get Weather",
    font=("Arial", 12),
    bg="#4CAF50",
    fg="white",
    command=send_message
)
send_button.pack(side=tk.LEFT)

# Start UI
root.mainloop()
