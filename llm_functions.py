from dotenv import load_dotenv
from openai import OpenAI
import os
import google.generativeai as genai

load_dotenv()

# Define the models to be used
OPEN_AI_MODEL = "gpt-4o-mini"
# GEMINI_MODEL = "gemini-3-flash-preview"

# Initialize the Gemini client
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the openai client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = "You are a Sales Executive, who is supposed to sell AI course." \
    " You are very friendly and polite in your responses." \
    "You are not supposed to answer any question, which is not mentioned in the below information, politely say that you don't know this" \
    "We have a new course on 'Mastering AI with Python' that covers everything from basics to advanced topics." \
    " The course is designed for beginners and experienced developers alike." \
    " The course includes hands-on projects, real-world examples, and lifetime access to materials." \
    "It is being offered by IIT Patna, a premier institute known for quality education." \
    "The faculty of IIT Patna will take classes on Sundays 10am to 1pm IST." \
    "The course duration is 3 months with a total of 36 hours of classes." \
    "At the end of the course, students will receive a certificate from IIT Patna." \
    "If you don't have any relevant information, politely inform the user that you are unable to assist with their request." \
    "Don't give any wrong information."

def get_response_from_openai(user_query, open_ai_chat_history):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        messages.extend(open_ai_chat_history)
        messages.append({"role": "user", "content": user_query})

        completion = openai_client.chat.completions.create(
            model=OPEN_AI_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error getting response from OpenAI: {e}")
        return "Sorry, I'm having trouble processing your request right now."
    
# def get_gemini_response(user_query, gemini_chat_history):
#     try:
#         model = genai.GenerativeModel(GEMINI_MODEL)
#         # Build message history for Gemini
#         chat_history = []
#         for msg in gemini_chat_history:
#             if msg['role'] == 'user':
#                 chat_history.append({"role": "user", "parts": [msg["content"]]})
#             else:
#                 chat_history.append({"role": "model", "parts": [msg["content"]]})

        # start chat with history
        chat = model.start_chat(history=chat_history)

        # Add system prompt context if it's first message
        if not gemini_chat_history:
            full_msg = f"System context: {SYSTEM_PROMPT}\n\nuser: {user_query}"
        else:
            full_msg = user_query
        
        response = chat.send_message(full_msg)
        return response.text
    except Exception as e:
        print(f"Error getting response from OpenAI: {e}")
        return "Sorry, I'm having trouble processing your request right now."



