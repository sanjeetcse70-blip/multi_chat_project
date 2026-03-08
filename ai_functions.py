from openai import OpenAI
import os

#from dotenv import load_dotenv

#load_dotenv()

def direct_llm_response():
    #client = OpenAI(api_key="sk1342342424242442")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.responses.create(
        model="gpt-4o-mini",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    print(response.output_text)

# Chat completion api usage
def chat_completion_api():
    system_prompt = "You are a Sales Executive, who is supposed to sell AI course." \
    " You are very friendly and polite in your responses." \
    "You are not supposed to answer any question, which is not mentioned in the below information, politely say that you don't know this" \
    "We have a new course on 'Mastering AI with Python' that covers everything from basics to advanced topics." \
    " The course is designed for beginners and experienced developers alike." \
    " The course includes hands-on projects, real-world examples, and lifetime access to materials."
    "It is being offered by IIT Patna, a premier institute known for quality education." \
    "The faculty of IIT Patna will take classes on Sundays 10am to 1pm IST." \
    "The course duration is 3 months with a total of 36 hours of classes." \
    "At the end of the course, students will receive a certificate from IIT Patna."
    "If you don't have any relevant information, politely inform the user that you are unable to assist with their request."
    "Don't give any wrong information."

    while True:
        user_query = input("User: ")
        if user_query.lower() in ['exit', 'quit']:
            break
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        # print(completion)
        content = completion.choices[0].message.content
        print("\nAI response:", content)

if __name__ == "__main__":
    #direct_llm_response()
    chat_completion_api()