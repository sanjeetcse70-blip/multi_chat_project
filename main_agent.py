from llm_functions import get_gemini_response, get_response_from_openai

open_ai_chat_history = []
gemini_chat_history = []

def display_responses(open_ai_response, gemini_ai_response, user_choice):
    if user_choice == 1 or user_choice == 3:
        print("\n\nOpenAI: ", open_ai_response)
    if user_choice == 2 or user_choice == 3:
        print("\n\nGemini: ", gemini_ai_response)

def update_history(user_query, open_ai_respone, gemini_response, user_choice):
    if user_choice == 1 or user_choice == 3:
        open_ai_chat_history.append({"role": "user", "content": user_query})
        open_ai_chat_history.append({"role": "assistant", "content": open_ai_respone})
    if user_choice == 2 or user_choice == 3:
        gemini_chat_history.append({"role": "user", "content": user_query})
        gemini_chat_history.append({"role": "assistant", "content": gemini_response})

def main():
    print("\n\nWelcome to the Mult-LLM chat application\n\n")
    user_choice = 3
    while True:

        # Get user input
        user_query = input("\nYou: ")

        print("\n Fetching responses from AI\n\n")

        if user_choice == 1 or user_choice == 3:
            open_ai_response = get_response_from_openai(user_query, open_ai_chat_history)
        if user_choice == 2 or user_choice == 3:
            gemini_ai_response = get_gemini_response(user_query, gemini_chat_history)

        display_responses(open_ai_response, gemini_ai_response, user_choice)

        update_history(user_query=user_query, open_ai_respone=open_ai_response, gemini_response=gemini_ai_response,
                       user_choice=user_choice)
        
        if user_choice == 3:
            print("\n\nSelect which response you prefer: ")
            print("1. OpenAI")
            print("2. Gemini")
            print("3. Both")
            print("4. Exit")

            user_choice = int(input("Select: "))
        else:
            user_selection = input("Enter 4 to exit, or just enter to continue")
            if user_selection == "4":
                break
        if user_choice == 4:
            break

if __name__ == "__main__":
    main()