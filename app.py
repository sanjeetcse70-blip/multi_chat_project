"""
Multi-LLM Chat Application
Streamlit app with Google Sign-In (Firebase), Firestore chat history,
multi-conversation support, and response rating.

Run with: streamlit run app.py
"""

import streamlit as st
from streamlit_google_auth import Authenticate
from firebase_service import (
    get_or_create_google_user,
    save_chat_message, get_chat_history, clear_chat_history,
    create_conversation, get_conversations,
    rename_conversation, delete_conversation, auto_title_conversation,
    save_rating, get_rating, get_rating_stats
)
from llm_functions import  get_response_from_openai
# from llm_functions import get_gemini_response, get_response_from_openai
import os
from dotenv import load_dotenv
import threading
from datetime import datetime

load_dotenv()

# ==================== Page Config ====================
st.set_page_config(
    page_title="Multi-LLM Chat",
    page_icon="🤖",
    layout="wide"
)

# ==================== Session State Initialization ====================
defaults = {
    'connected': False,
    'user_id': None,
    'user_email': None,
    'display_name': None,
    'openai_chat_history': [],
    'gemini_chat_history': [],
    'model_choice': 'Both',
    'chat_loaded': False,
    'current_conversation_id': None,
    'conversation_message_count': 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================== Google Authentication ====================

# In production, set GOOGLE_OAUTH_CREDENTIALS env var with JSON content
# and REDIRECT_URI to your Railway app URL
google_creds_json = os.getenv('GOOGLE_OAUTH_CREDENTIALS')
redirect_uri = os.getenv('REDIRECT_URI', 'http://localhost:8501')

if google_creds_json:
    # Production: write credentials to a temp file (library requires a file path)
    import tempfile, json
    _creds_dict = json.loads(google_creds_json)
    _tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(_creds_dict, _tmp)
    _tmp.close()
    _google_creds_path = _tmp.name
else:
    _google_creds_path = 'D:\multi_chat_project\client_secret_374882620159-ru0jopndjeun4rmdbpnnnlkugcmophh2.apps.googleusercontent.com.json'

authenticator = Authenticate(
    secret_credentials_path=_google_creds_path,
    cookie_name='multi_llm_chat_auth',
    cookie_key='multi_llm_chat_secret_key',
    redirect_uri=redirect_uri,
)

authenticator.check_authentification()


# ==================== Helper Functions ====================

def switch_conversation(conv_id):
    """Switch to a different conversation."""
    st.session_state.current_conversation_id = conv_id
    st.session_state.chat_loaded = False
    st.session_state.openai_chat_history = []
    st.session_state.gemini_chat_history = []
    st.session_state.conversation_message_count = 0


def load_chat_history():
    """Load chat history from Firestore into session state."""
    if not st.session_state.chat_loaded and st.session_state.user_id and st.session_state.current_conversation_id:
        history = get_chat_history(
            st.session_state.user_id,
            conversation_id=st.session_state.current_conversation_id
        )
        st.session_state.openai_chat_history = []
        st.session_state.gemini_chat_history = []

        for msg in history:
            if msg['role'] == 'user':
                st.session_state.openai_chat_history.append({
                    "role": "user", "content": msg['content']
                })
                st.session_state.gemini_chat_history.append({
                    "role": "user", "content": msg['content']
                })
            elif msg['role'] == 'assistant':
                if msg.get('model') == 'openai':
                    st.session_state.openai_chat_history.append({
                        "role": "assistant", "content": msg['content']
                    })
                elif msg.get('model') == 'gemini':
                    st.session_state.gemini_chat_history.append({
                        "role": "assistant", "content": msg['content']
                    })

        st.session_state.conversation_message_count = len([m for m in history if m['role'] == 'user'])
        st.session_state.chat_loaded = True


def show_login_page():
    """Display the Google Sign-In login page."""
    st.markdown("<h1 style='text-align: center;'>🤖 Multi-LLM Chat</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Welcome! Sign in to continue</h3>", unsafe_allow_html=True)
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        authenticator.login()
        st.markdown("---")
        st.caption("Sign in with your Google account to access the Multi-LLM Chat application.")


# ==================== Chat Page ====================

def show_chat_page():
    """Display the main chat interface with conversations sidebar."""

    # Register user in Firestore on first login
    if not st.session_state.user_id:
        user_info = get_or_create_google_user(
            email=st.session_state.user_email,
            display_name=st.session_state.display_name or ''
        )
        st.session_state.user_id = user_info['user_id']

    user_id = st.session_state.user_id

    # ---- Sidebar ----
    with st.sidebar:
        if st.session_state.get('user_info', {}).get('picture'):
            st.image(st.session_state['user_info']['picture'], width=80)
        st.markdown(f"### 👤 {st.session_state.display_name or st.session_state.user_email}")
        st.caption(st.session_state.user_email)
        st.markdown("---")

        # Model selection
        st.subheader("🔧 Model Selection")
        model_choice = st.radio(
            "Choose AI Model:",
            ["OpenAI", "Gemini", "Both"],
            index=["OpenAI", "Gemini", "Both"].index(st.session_state.model_choice),
            key="model_radio"
        )
        st.session_state.model_choice = model_choice

        st.markdown("---")

        # ---- Conversations List ----
        st.subheader("💬 Conversations")

        # New conversation button
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            new_id = create_conversation(user_id, "New Chat")
            switch_conversation(new_id)
            st.rerun()

        # List existing conversations
        conversations = get_conversations(user_id)

        # Auto-create first conversation if none exist
        if not conversations and not st.session_state.current_conversation_id:
            new_id = create_conversation(user_id, "New Chat")
            switch_conversation(new_id)
            st.rerun()

        for conv in conversations:
            conv_id = conv['id']
            is_active = (conv_id == st.session_state.current_conversation_id)
            title = conv.get('title', 'Untitled')

            col_btn, col_del = st.columns([5, 1])
            with col_btn:
                btn_type = "primary" if is_active else "secondary"
                if st.button(
                    f"{'▶ ' if is_active else ''}{title}",
                    key=f"conv_{conv_id}",
                    use_container_width=True,
                    type=btn_type
                ):
                    switch_conversation(conv_id)
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{conv_id}", help="Delete conversation"):
                    delete_conversation(user_id, conv_id)
                    if is_active:
                        remaining = [c for c in conversations if c['id'] != conv_id]
                        if remaining:
                            switch_conversation(remaining[0]['id'])
                        else:
                            new_id = create_conversation(user_id, "New Chat")
                            switch_conversation(new_id)
                    st.rerun()

        # Select first conversation if none selected
        if not st.session_state.current_conversation_id and conversations:
            switch_conversation(conversations[0]['id'])
            st.rerun()

        st.markdown("---")

        # ---- Rating Stats ----
        st.subheader("📊 Model Preferences")
        stats = get_rating_stats(user_id)
        if stats['total'] > 0:
            col_o, col_g = st.columns(2)
            with col_o:
                pct_o = round(stats['openai'] / stats['total'] * 100) if stats['total'] else 0
                st.metric("OpenAI", f"{stats['openai']} ({pct_o}%)")
            with col_g:
                pct_g = round(stats['gemini'] / stats['total'] * 100) if stats['total'] else 0
                st.metric("Gemini", f"{stats['gemini']} ({pct_g}%)")
            st.caption(f"Total ratings: {stats['total']}")
        else:
            st.caption("No ratings yet. Use 'Both' mode and rate responses!")

        st.markdown("---")

        # Clear current conversation
        if st.button("🗑️ Clear Current Chat", use_container_width=True):
            if st.session_state.current_conversation_id:
                clear_chat_history(user_id, conversation_id=st.session_state.current_conversation_id)
                st.session_state.openai_chat_history = []
                st.session_state.gemini_chat_history = []
                st.session_state.chat_loaded = False
                st.session_state.conversation_message_count = 0
                st.rerun()

        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            authenticator.logout()

    # ---- Main Chat Area ----
    st.title("🤖 Multi-LLM Chat")

    conv_id = st.session_state.current_conversation_id
    if not conv_id:
        st.info("Create a new conversation to start chatting.")
        return

    # Load existing chat history from Firestore
    load_chat_history()

    # Display chat history
    history = get_chat_history(user_id, conversation_id=conv_id) if conv_id else []

    i = 0
    while i < len(history):
        msg = history[i]
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
            i += 1
        elif msg['role'] == 'assistant':
            next_msg = history[i + 1] if i + 1 < len(history) else None
            if next_msg and next_msg['role'] == 'assistant' and msg.get('model') != next_msg.get('model'):
                # Side by side display
                col1, col2 = st.columns(2)
                with col1:
                    model_label = msg.get('model', 'AI').upper()
                    with st.chat_message("assistant"):
                        st.caption(f"🤖 {model_label}")
                        st.write(msg['content'])
                with col2:
                    model_label2 = next_msg.get('model', 'AI').upper()
                    with st.chat_message("assistant"):
                        st.caption(f"🤖 {model_label2}")
                        st.write(next_msg['content'])

                # Rating buttons for this pair
                pair_id = f"{msg['id']}_{next_msg['id']}"
                existing_rating = get_rating(user_id, pair_id)

                # Find the user query above this pair
                user_query_for_rating = ""
                for j in range(i - 1, -1, -1):
                    if history[j]['role'] == 'user':
                        user_query_for_rating = history[j]['content']
                        break

                rc1, rc2, rc3 = st.columns([1, 1, 2])
                with rc1:
                    openai_label = "✅ OpenAI" if existing_rating and existing_rating.get('preferred_model') == 'openai' else "👍 Prefer OpenAI"
                    if st.button(openai_label, key=f"rate_o_{pair_id}"):
                        save_rating(user_id, conv_id, pair_id, 'openai', user_query_for_rating)
                        st.rerun()
                with rc2:
                    gemini_label = "✅ Gemini" if existing_rating and existing_rating.get('preferred_model') == 'gemini' else "👍 Prefer Gemini"
                    if st.button(gemini_label, key=f"rate_g_{pair_id}"):
                        save_rating(user_id, conv_id, pair_id, 'gemini', user_query_for_rating)
                        st.rerun()
                with rc3:
                    if existing_rating:
                        st.caption(f"Preferred: **{existing_rating['preferred_model'].upper()}**")

                i += 2
            else:
                model_label = msg.get('model', 'AI').upper()
                with st.chat_message("assistant"):
                    st.caption(f"🤖 {model_label}")
                    st.write(msg['content'])
                i += 1
        else:
            i += 1

    # ---- Chat Input ----
    if user_query := st.chat_input("Type your message..."):
        with st.chat_message("user"):
            st.write(user_query)

        # Save user message
        save_chat_message(user_id, 'user', user_query, conversation_id=conv_id)

        # Auto-title on first message
        if st.session_state.conversation_message_count == 0:
            auto_title_conversation(user_id, conv_id, user_query)

        st.session_state.conversation_message_count += 1

        openai_response = None
        gemini_response = None

        if st.session_state.model_choice == "Both":
            openai_history = list(st.session_state.openai_chat_history)
            gemini_history = list(st.session_state.gemini_chat_history)

            def fetch_openai():
                nonlocal openai_response
                openai_response = get_response_from_openai(user_query, openai_history)

            # def fetch_gemini():
            #     nonlocal gemini_response
            #     gemini_response = get_gemini_response(user_query, gemini_history)

            t1 = threading.Thread(target=fetch_openai)
            # t2 = threading.Thread(target=fetch_gemini)
            t1.start()
            # t2.start()

            with st.spinner("Fetching responses from both models..."):
                t1.join()
                # t2.join()

            # Display side by side
            col1, col2 = st.columns(2)
            with col1:
                with st.chat_message("assistant"):
                    st.caption("🤖 OPENAI")
                    st.write(openai_response)
            with col2:
                with st.chat_message("assistant"):
                    st.caption("🤖 GEMINI")
                    st.write(gemini_response)

            # Save to Firestore
            oid = save_chat_message(user_id, 'assistant', openai_response, model='openai', conversation_id=conv_id)
            gid = save_chat_message(user_id, 'assistant', gemini_response, model='gemini', conversation_id=conv_id)

            # Rating buttons for new response
            pair_id = f"{oid}_{gid}"
            rc1, rc2, rc3 = st.columns([1, 1, 2])
            with rc1:
                if st.button("👍 Prefer OpenAI", key=f"rate_o_{pair_id}"):
                    save_rating(user_id, conv_id, pair_id, 'openai', user_query)
                    st.rerun()
            with rc2:
                if st.button("👍 Prefer Gemini", key=f"rate_g_{pair_id}"):
                    save_rating(user_id, conv_id, pair_id, 'gemini', user_query)
                    st.rerun()

            # Update session histories
            st.session_state.openai_chat_history.append({"role": "user", "content": user_query})
            st.session_state.openai_chat_history.append({"role": "assistant", "content": openai_response})
            st.session_state.gemini_chat_history.append({"role": "user", "content": user_query})
            st.session_state.gemini_chat_history.append({"role": "assistant", "content": gemini_response})

        elif st.session_state.model_choice == "OpenAI":
            with st.chat_message("assistant"):
                st.caption("🤖 OPENAI")
                with st.spinner("OpenAI is thinking..."):
                    openai_response = get_response_from_openai(
                        user_query, st.session_state.openai_chat_history
                    )
                st.write(openai_response)

            st.session_state.openai_chat_history.append({"role": "user", "content": user_query})
            st.session_state.openai_chat_history.append({"role": "assistant", "content": openai_response})
            save_chat_message(user_id, 'assistant', openai_response, model='openai', conversation_id=conv_id)

        # elif st.session_state.model_choice == "Gemini":
        #     with st.chat_message("assistant"):
        #         st.caption("🤖 GEMINI")
        #         with st.spinner("Gemini is thinking..."):sssss
        #             gemini_response = get_gemini_response(
        #                 user_query, st.session_state.gemini_chat_history
        #             )
        #         st.write(gemini_response)

            st.session_state.gemini_chat_history.append({"role": "user", "content": user_query})
            st.session_state.gemini_chat_history.append({"role": "assistant", "content": gemini_response})
            save_chat_message(user_id, 'assistant', gemini_response, model='gemini', conversation_id=conv_id)


# ==================== Main App Router ====================

if st.session_state.get('connected'):
    st.session_state.user_email = st.session_state.get('user_info', {}).get('email', '')
    st.session_state.display_name = st.session_state.get('user_info', {}).get('name', '')
    show_chat_page()
else:
    show_login_page()
