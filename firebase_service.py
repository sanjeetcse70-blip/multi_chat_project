"""
Firebase Service Module
Handles Firebase Authentication (Google Sign-In) and Firestore operations
for the Multi-LLM Chat application.

Firestore Structure:
  users (collection)
    └── {user_id} (document)
          ├── email
          ├── display_name
          ├── created_at
          ├── last_login
          ├── conversations (subcollection)
          │     └── {conversation_id} (document)
          │           ├── title
          │           ├── created_at
          │           ├── updated_at
          │           └── messages (subcollection)
          │                 └── {timestamp_id} (document)
          │                       ├── role (user/assistant)
          │                       ├── content
          │                       ├── model (openai/gemini)
          │                       └── timestamp
          └── ratings (subcollection)
                └── {rating_id} (document)
                      ├── conversation_id
                      ├── message_pair_id
                      ├── preferred_model (openai/gemini)
                      ├── user_query
                      └── timestamp
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid
import json

load_dotenv()

# Firebase initialization
# In production (Railway), set FIREBASE_CREDENTIALS env var with the JSON content
# Locally, falls back to the credentials file
CREDENTIALS_PATH = 'multi-llm-chat-487415-p7-firebase-adminsdk-fbsvc-7c0f689a7a.json'

if not firebase_admin._apps:
    firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS')
    if firebase_creds_json:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ==================== Google Sign-In User Management ====================

def get_or_create_google_user(email, display_name=""):
    """
    After Google OAuth sign-in, create or update the user document in Firestore.
    Uses a sanitized email as the document ID.
    """
    user_id = email.replace('@', '_at_').replace('.', '_dot_')

    user_doc = db.collection('users').document(user_id).get()

    if user_doc.exists:
        db.collection('users').document(user_id).update({
            'last_login': datetime.utcnow()
        })
        data = user_doc.to_dict()
        return {
            'user_id': user_id,
            'email': data.get('email', email),
            'display_name': data.get('display_name', display_name)
        }
    else:
        user_data = {
            'email': email,
            'display_name': display_name if display_name else email.split('@')[0],
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow()
        }
        db.collection('users').document(user_id).set(user_data)
        return {
            'user_id': user_id,
            'email': email,
            'display_name': user_data['display_name']
        }


# ==================== Conversation Functions ====================

def create_conversation(user_id, title="New Chat"):
    """Create a new conversation and return its ID."""
    conv_ref = db.collection('users').document(user_id) \
        .collection('conversations').document()

    conv_data = {
        'title': title,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    conv_ref.set(conv_data)
    return conv_ref.id


def get_conversations(user_id):
    """Get all conversations for a user, ordered by most recent first."""
    docs = db.collection('users').document(user_id) \
        .collection('conversations') \
        .order_by('updated_at', direction=firestore.Query.DESCENDING) \
        .stream()

    conversations = []
    for doc in docs:
        conv = doc.to_dict()
        conv['id'] = doc.id
        conversations.append(conv)

    return conversations


def rename_conversation(user_id, conversation_id, new_title):
    """Rename a conversation."""
    db.collection('users').document(user_id) \
        .collection('conversations').document(conversation_id) \
        .update({'title': new_title})


def delete_conversation(user_id, conversation_id):
    """Delete a conversation and all its messages."""
    conv_ref = db.collection('users').document(user_id) \
        .collection('conversations').document(conversation_id)

    # Delete all messages in the conversation
    messages = conv_ref.collection('messages').stream()
    batch = db.batch()
    count = 0
    for msg in messages:
        batch.delete(msg.reference)
        count += 1
        if count % 450 == 0:
            batch.commit()
            batch = db.batch()
    if count % 450 != 0:
        batch.commit()

    # Delete the conversation document
    conv_ref.delete()


def auto_title_conversation(user_id, conversation_id, first_message):
    """Set conversation title based on first user message (truncated)."""
    title = first_message[:50] + ('...' if len(first_message) > 50 else '')
    db.collection('users').document(user_id) \
        .collection('conversations').document(conversation_id) \
        .update({'title': title, 'updated_at': datetime.utcnow()})


# ==================== Message Functions (within conversation) ====================

def save_chat_message(user_id, role, content, model="", conversation_id=None):
    """
    Save a chat message to a conversation's messages subcollection.
    Falls back to legacy chat_history if no conversation_id.
    """
    timestamp = datetime.utcnow()
    doc_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")

    message_data = {
        'role': role,
        'content': content,
        'model': model,
        'timestamp': timestamp
    }

    if conversation_id:
        db.collection('users').document(user_id) \
            .collection('conversations').document(conversation_id) \
            .collection('messages').document(doc_id) \
            .set(message_data)

        # Update conversation's updated_at
        db.collection('users').document(user_id) \
            .collection('conversations').document(conversation_id) \
            .update({'updated_at': timestamp})
    else:
        # Legacy fallback
        db.collection('users').document(user_id) \
            .collection('chat_history').document(doc_id) \
            .set(message_data)

    return doc_id


def get_chat_history(user_id, conversation_id=None, limit=100):
    """
    Retrieve chat history for a conversation, ordered by timestamp.
    """
    if conversation_id:
        docs = db.collection('users').document(user_id) \
            .collection('conversations').document(conversation_id) \
            .collection('messages') \
            .order_by('timestamp') \
            .limit(limit) \
            .stream()
    else:
        docs = db.collection('users').document(user_id) \
            .collection('chat_history') \
            .order_by('timestamp') \
            .limit(limit) \
            .stream()

    messages = []
    for doc in docs:
        msg = doc.to_dict()
        msg['id'] = doc.id
        messages.append(msg)

    return messages


def clear_chat_history(user_id, conversation_id=None):
    """Delete all messages in a conversation."""
    if conversation_id:
        docs = db.collection('users').document(user_id) \
            .collection('conversations').document(conversation_id) \
            .collection('messages').stream()
    else:
        docs = db.collection('users').document(user_id) \
            .collection('chat_history').stream()

    batch = db.batch()
    count = 0
    for doc in docs:
        batch.delete(doc.reference)
        count += 1
        if count % 450 == 0:
            batch.commit()
            batch = db.batch()

    if count % 450 != 0:
        batch.commit()

    return count


# ==================== Rating Functions ====================

def save_rating(user_id, conversation_id, message_pair_id, preferred_model, user_query):
    """
    Save a user's preference rating for a pair of model responses.
    
    Args:
        user_id: User document ID
        conversation_id: Which conversation the rating belongs to
        message_pair_id: Identifier linking the two responses being compared
        preferred_model: 'openai' or 'gemini'
        user_query: The original user query for context
    """
    rating_data = {
        'conversation_id': conversation_id,
        'message_pair_id': message_pair_id,
        'preferred_model': preferred_model,
        'user_query': user_query,
        'timestamp': datetime.utcnow()
    }

    db.collection('users').document(user_id) \
        .collection('ratings').document(message_pair_id) \
        .set(rating_data)


def get_rating(user_id, message_pair_id):
    """Get an existing rating for a message pair."""
    doc = db.collection('users').document(user_id) \
        .collection('ratings').document(message_pair_id).get()
    return doc.to_dict() if doc.exists else None


def get_rating_stats(user_id):
    """
    Get aggregated rating statistics for a user.
    Returns dict with counts per model and total.
    """
    docs = db.collection('users').document(user_id) \
        .collection('ratings').stream()

    stats = {'openai': 0, 'gemini': 0, 'total': 0}
    for doc in docs:
        data = doc.to_dict()
        model = data.get('preferred_model', '')
        if model in stats:
            stats[model] += 1
        stats['total'] += 1

    return stats
