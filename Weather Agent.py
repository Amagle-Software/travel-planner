import google.generativeai as genai
import requests
from flask import Flask, request, jsonify

# Configure Gemini
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Weather API Key
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_KEY"

app = Flask(__name__)

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    # Ask Gemini to extract city name
    prompt = f"""
    Extract the city name from this message:
    "{user_message}"
    Only return the city name.
    """

    city_response = model.generate_content(prompt)
    city = city_response.text.strip()

    weather_data = get_weather(city)

    if "main" in weather_data:
        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]

        final_prompt = f"""
        User asked: {user_message}
        Weather in {city}:
        Temperature: {temp}°C
        Description: {description}

        Generate a friendly weather response.
        """

        final_response = model.generate_content(final_prompt)

        return jsonify({"response": final_response.text})

    else:
        return jsonify({"response": "Sorry, I couldn't find that city."})

if __name__ == "__main__":
    app.run(debug=True)
