import google.generativeai as genai # pip install google-generativeai
import speech_recognition as sr # pip install SpeechRecognition
import os

gemini_api_key = os.getenv('GEMINI_API_KEY')

# Configure the Gemini API key
genai.configure(api_key=gemini_api_key)

conversation_history = [] # comeback

def romantic_translation_with_gemini(text):
    try:
        # Combine the conversation history and the new input text
        prompt = "\n".join([entry["text"] for entry in conversation_history] + [f"User: {text}"])

        # Create a model instance with the specified configuration
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="Translate the input into romantic speech, keeping the same length and using the context of previous translations."
        )


