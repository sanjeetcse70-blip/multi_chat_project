"""
Multi-LLM Chat Application
Allows users to interact with both OpenAI GPT and Google Gemini models,
compare responses, and choose which to continue conversations with.
"""

import os
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Model configurations
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-3-flash-preview"

# Conversation histories for both models
openai_history = []
gemini_history = []

# System prompt (can be customized)
SYSTEM_PROMPT = "You are a helpful AI assistant. Provide clear, accurate, and concise responses."


def get_openai_response(user_message: str) -> str:
    """Get response from OpenAI GPT model."""
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(openai_history)
        messages.append({"role": "user", "content": user_message})
        
        completion = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages
        )
        
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        return f"OpenAI Error: {str(e)}"


def get_gemini_response(user_message: str) -> str:
    """Get response from Google Gemini model."""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Build conversation history for Gemini
        chat_history = []
        for msg in gemini_history:
            if msg["role"] == "user":
                chat_history.append({"role": "user", "parts": [msg["content"]]})
            else:
                chat_history.append({"role": "model", "parts": [msg["content"]]})
        
        # Start chat with history
        chat = model.start_chat(history=chat_history)
        
        # Add system prompt context if it's the first message
        if not gemini_history:
            full_message = f"System context: {SYSTEM_PROMPT}\n\nUser: {user_message}"
        else:
            full_message = user_message
        
        response = chat.send_message(full_message)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"


def display_responses(openai_response: str, gemini_response: str):
    """Display both responses for comparison."""
    print("\n" + "=" * 60)
    print("📘 OPENAI GPT RESPONSE:")
    print("-" * 60)
    print(openai_response)
    print("\n" + "=" * 60)
    print("📗 GOOGLE GEMINI RESPONSE:")
    print("-" * 60)
    print(gemini_response)
    print("=" * 60 + "\n")


def update_history(user_message: str, openai_response: str, gemini_response: str, choice: str):
    """Update conversation histories based on user's choice."""
    global openai_history, gemini_history
    
    if choice in ['1', 'openai', 'both', '3']:
        openai_history.append({"role": "user", "content": user_message})
        openai_history.append({"role": "assistant", "content": openai_response})
    
    if choice in ['2', 'gemini', 'both', '3']:
        gemini_history.append({"role": "user", "content": user_message})
        gemini_history.append({"role": "assistant", "content": gemini_response})


def get_user_choice() -> str:
    """Get user's choice on which response to continue with."""
    print("Which response would you like to continue with?")
    print("  [1] OpenAI GPT")
    print("  [2] Google Gemini")
    print("  [3] Both (continue conversation with both models)")
    print("  [0] Neither (discard both responses)")
    
    while True:
        choice = input("\nYour choice (1/2/3/0): ").strip().lower()
        if choice in ['0', '1', '2', '3', 'openai', 'gemini', 'both', 'neither']:
            return choice
        print("Invalid choice. Please enter 1, 2, 3, or 0.")


def display_conversation_status():
    """Display current conversation status for both models."""
    openai_turns = len(openai_history) // 2
    gemini_turns = len(gemini_history) // 2
    
    status = []
    if openai_turns > 0:
        status.append(f"OpenAI: {openai_turns} turn(s)")
    if gemini_turns > 0:
        status.append(f"Gemini: {gemini_turns} turn(s)")
    
    if status:
        print(f"[Active conversations: {' | '.join(status)}]")


def main():
    """Main function to run the multi-LLM chat application."""
    print("\n" + "=" * 60)
    print("   MULTI-LLM CHAT APPLICATION")
    print("   Compare responses from OpenAI GPT and Google Gemini")
    print("=" * 60)
    print("\nCommands:")
    print("  'exit' or 'quit' - End the conversation")
    print("  'clear' - Clear conversation history for both models")
    print("  'status' - Show conversation history status")
    print("-" * 60 + "\n")
    
    while True:
        # Show conversation status
        display_conversation_status()
        
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Handle special commands
        if not user_input:
            print("Please enter a message or command.")
            continue
        
        if user_input.lower() in ['exit', 'quit']:
            print("\nThank you for using Multi-LLM Chat! Goodbye.\n")
            break
        
        if user_input.lower() == 'clear':
            openai_history.clear()
            gemini_history.clear()
            print("Conversation history cleared for both models.")
            continue
        
        if user_input.lower() == 'status':
            if not openai_history and not gemini_history:
                print("No active conversations.")
            else:
                print(f"\nOpenAI history: {len(openai_history)} messages")
                print(f"Gemini history: {len(gemini_history)} messages")
            continue
        
        # Get responses from both models
        print("\nFetching responses from both models...")
        
        openai_response = get_openai_response(user_input)
        gemini_response = get_gemini_response(user_input)
        
        # Display both responses
        display_responses(openai_response, gemini_response)
        
        # Get user's choice
        choice = get_user_choice()
        
        # Update conversation histories based on choice
        if choice in ['0', 'neither']:
            print("Responses discarded. Starting fresh for next query.")
        else:
            update_history(user_input, openai_response, gemini_response, choice)
            
            if choice in ['1', 'openai']:
                print("✓ Continuing with OpenAI GPT response.")
            elif choice in ['2', 'gemini']:
                print("✓ Continuing with Google Gemini response.")
            else:
                print("✓ Continuing with both responses.")


if __name__ == "__main__":
    main()
