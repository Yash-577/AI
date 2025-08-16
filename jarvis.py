import os
import requests
import json
import pyttsx3
import speech_recognition as sr
from googletrans import Translator
import webbrowser

# Setup voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Translator setup
translator = Translator()

# API Keys (put your own here)
DEEPSEEK_API_KEY = "Your_Api_Key_Here"
url = "https://api.deepseek.com/v1/chat/completions"

OPENWEATHER_API_KEY = "your_openweather_api_key"

# Speak function
import re

def clean_text_for_speech(text):
    # Remove unwanted special characters except basic punctuation
    text = re.sub(r"[#@*^_=~`$%{}\[\]\\<>|\/]", "", text)
    # Replace multiple spaces with one
    text = re.sub(r"\s+", " ", text).strip()
    return text

def speak(text, lang='en'):
    print("Jarvis:", text)
    translated = translator.translate(text, dest=lang)
    cleaned = clean_text_for_speech(translated.text)
    engine.say(cleaned)
    engine.runAndWait()
 
# Listen function
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command
    except:
        speak("Sorry, I didn't catch that.")
        return ""

# Get weather info
def get_weather(city="London"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather_desc = data["weather"][0]["description"]
        result = f"The temperature in {city} is {main['temp']}°C with {weather_desc}."
        return result
    else:
        return "City not found."

# Call DeepSeek R1 API
def ask_deepseek(prompt, language='en'):
    url = "https://openrouter.ai/api/v1/chat/completions"  # OpenRouter endpoint
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",       # Your OpenRouter key
        "HTTP-Referer": "http://localhost",                  # Required by OpenRouter
        "X-Title": "Jarvis Assistant"                        # Optional: name your app
    }
    body = {
        "model": "deepseek/deepseek-r1:free",  # Free-tier model on OpenRouter
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    try:
        data = response.json()
        print("DEBUG OpenRouter:", data)  # See the raw reply

        if response.status_code == 200 and "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            err = data.get("error") or data
            return f"API error: {err}"
    except Exception as e:
        return f"Failed to parse response: {str(e)}"
  
    

    
    

# Command-based functions
def execute_command(command):
    command = command.lower()

    # Control PC
    if "open notepad" in command:
        os.system("notepad")
        speak("Opening Notepad.")
    elif "open browser" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening browser.")
    elif "weather" in command:
        city = command.split("in")[-1].strip() if "in" in command else "London"
        weather = get_weather(city)
        speak(weather)
    elif any(phrase in command for phrase in ["chatgpt", "chat gpt", "chat g p t", "chat jee pee tee"]):
        webbrowser.open("https://chat.openai.com")
        speak("Opening ChatGPT")


    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
    


    # New commands start here
    elif "shutdown" in command:
        speak("Shutting down the computer. Goodbye!")
        # For Windows
        os.system("shutdown /s /t 5")
        # For Linux, uncomment the line below and comment the above line
        # os.system("sudo shutdown now")
    elif "restart" in command or "reboot" in command:
        speak("Restarting the computer.")
        # For Windows
        os.system("shutdown /r /t 5")
        # For Linux, uncomment the line below and comment the above line
        # os.system("sudo reboot")
    elif "search" in command:
        # Extract search query
        query = command.split("search",1)[1].strip()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Here are the search results for {query}.")
        else:
            speak("Please tell me what you want to search for.")
    elif "exit" in command or "quit" in command:
        speak("Goodbye!")
        exit()
    else:
        # Ask DeepSeek
        reply = ask_deepseek(command)
        speak(reply)


# MAIN LOOP
if __name__ == "__main__":
    speak("Hello! I am your assistant. How can I help you?")
    
while True:
    try:
        text = listen()
        if text:
            if "jarvis" in text.lower():
                speak("Yes, I'm listening.")
                command = listen()  # Listen again for the actual command
                if command:
                    execute_command(command)
                    break
            else:
                print("Waiting for wake word...")
    except KeyboardInterrupt:
        speak("Goodbye!")
        break


