import google.generativeai as genai
import os

gemini_api_key = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=gemini_api_key)

def translate(speech):
    model = genai.GenerativeModel(
        model_name= "gemini-1.5-flash",
        system_instruction="You are a poet that translates everyday speech into romantic speech")

    response = model.generate_content(
        "Translate the following:" + speech,
        generation_config = genai.GenerationConfig(
            max_output_tokens=50,
            temperature=0.9,
            candidate_count=1,
            stop_sequences=['.']
        )
    )

    print(response.text)

translate('How are you')


