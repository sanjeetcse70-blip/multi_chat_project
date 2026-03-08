# Multi-LLM Chat Application

A Streamlit-based chat application that allows you to interact with multiple AI models (OpenAI and Google Gemini) simultaneously, with Firebase authentication and cloud-based chat history storage.

## Features

- 🔐 **Google Sign-In** authentication via Firebase
- 🤖 **Multi-Model Support**: Chat with OpenAI GPT-4, Google Gemini, or both at once
- 💾 **Persistent Chat History**: All conversations stored in Firebase Firestore
- 👤 **User Profiles**: Each user has their own isolated chat history
- 🎨 **Clean UI**: Modern Streamlit interface with model selection

## Prerequisites

- Python 3.7 or higher
- Google account for Firebase
- OpenAI API key
- Google Gemini API key
- Firebase project with Firestore enabled
- Google OAuth credentials

## Setup Instructions

### 1. Clone or Download the Project

```bash
cd C:\Users\shash\PycharmProjects\multi_llm_chat
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following:

```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

**How to get API keys:**
- **OpenAI**: Visit [platform.openai.com](https://platform.openai.com/api-keys)
- **Gemini**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

### 5. Set Up Firebase

#### A. Firebase Admin SDK Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (`multi-llm-chat-487415`)
3. Go to **Project Settings** (gear icon) → **Service Accounts**
4. Click **"Generate New Private Key"**
5. Save the downloaded JSON file as:
   ```
   multi-llm-chat-487415-firebase-adminsdk-fbsvc-7ee1f7cdc6.json
   ```
   in the project root directory

#### B. Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **Credentials**
4. Click **"Create Credentials"** → **"OAuth 2.0 Client ID"**
5. Application type: **Web application**
6. Add **Authorized redirect URIs**:
   ```
   http://localhost:8501
   ```
7. Click **Create** and download the JSON file
8. Save it in the project root (should already be there):
   ```
   client_secret_773603901652-nq0ekpsh39cqvtm5ss19c11ilrvdr2cd.apps.googleusercontent.com.json
   ```

#### C. Enable Firebase Services

1. In Firebase Console, enable:
   - **Firestore Database** (already done)
   - **Authentication** → **Google Sign-In** (already enabled)

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Usage

### First Time Login

1. Click **"Sign in with Google"** button
2. Choose your Google account
3. Grant permissions
4. You'll be redirected to the chat interface

### Chatting

1. Select your preferred AI model from the sidebar:
   - **OpenAI**: Chat with GPT-4
   - **Gemini**: Chat with Google Gemini
   - **Both**: Get responses from both models simultaneously
2. Type your message in the chat input
3. View AI responses labeled by model
4. All messages are automatically saved to Firestore

### Managing Chat History

- **Clear History**: Click the "🗑️ Clear Chat History" button in the sidebar
- **Logout**: Click the "🚪 Logout" button to sign out

## Project Structure

```
multi_llm_chat/
├── app.py                          # Main Streamlit application
├── firebase_service.py             # Firebase authentication & Firestore operations
├── llm_functions.py                # OpenAI and Gemini API integrations
├── main_agent.py                   # Original CLI chat interface
├── ai_functions.py                 # Additional AI utilities
├── requirements.txt                # Python dependencies
├── .env                            # API keys (not in git)
├── multi-llm-chat-***.json        # Firebase Admin SDK credentials (not in git)
├── client_secret_***.json         # Google OAuth credentials (not in git)
├── test_firebase.py               # Firebase connection test script
├── write_test_doc.py              # Firebase write test script
└── README.md                       # This file
```

## Firestore Database Structure

```
users (collection)
└── {user_id} (document)
    ├── email: string
    ├── display_name: string
    ├── created_at: timestamp
    ├── last_login: timestamp
    └── chat_history (subcollection)
        └── {timestamp_id} (document)
            ├── role: "user" | "assistant"
            ├── content: string
            ├── model: "openai" | "gemini"
            └── timestamp: timestamp
```

## Troubleshooting

### Virtual Environment Issues

If activation fails, try:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Firebase Connection Errors

- Verify the Firebase credentials JSON file is in the correct location
- Check that Firestore is enabled in Firebase Console
- Ensure your IP is not blocked by Firebase security rules

### Google Sign-In Not Working

- Verify `http://localhost:8501` is in the authorized redirect URIs
- Check that the OAuth credentials file name matches in `app.py`
- Clear browser cookies and try again

### API Key Errors

- Verify API keys in `.env` file are correct
- Check for extra spaces or quotes around keys
- Ensure you have billing enabled for OpenAI

### Module Not Found Errors

Make sure virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

## Security Notes

⚠️ **Never commit these files to version control:**
- `.env` (contains API keys)
- `*firebase-adminsdk*.json` (Firebase credentials)
- `client_secret_*.json` (Google OAuth credentials)

These files are already in `.gitignore`.

## Dependencies

- `streamlit` - Web UI framework
- `firebase-admin` - Firebase Admin SDK
- `streamlit-google-auth` - Google authentication
- `openai` - OpenAI API client
- `google-generativeai` - Google Gemini API client
- `python-dotenv` - Environment variable management
- `requests` - HTTP library

## License

This project is for educational purposes.

## Support

For issues or questions, refer to:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google AI Documentation](https://ai.google.dev/)

---

**Version:** 1.0  
**Last Updated:** February 22, 2026
