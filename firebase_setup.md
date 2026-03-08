# Firebase Setup Guide for Multi LLM Chat Project

## Prerequisites
- Google account
- Python 3.7+ installed
- Active internet connection

---

## Part 1: Google Cloud Console & Firebase Setup

### Step 1: Access Google Cloud Console
1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account

### Step 2: Create a New Project
1. Click on the project dropdown at the top of the page (next to "Google Cloud")
2. Click "NEW PROJECT" button
3. Enter project details:
   - **Project name**: `multi-llm-chat` (or your preferred name)
   - **Organization**: Leave as default or select your organization
   - **Location**: Leave as default or select preferred location
4. Click "CREATE"
5. Wait for project creation (takes 10-30 seconds)
6. Select your newly created project from the dropdown

### Step 3: Enable Firebase for Your Project
1. Navigate to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select your existing Google Cloud project
3. If selecting existing project:
   - Find your `multi-llm-chat` project
   - Click on it
   - Confirm Firebase setup by clicking "Continue"
4. Configure Google Analytics (optional but recommended):
   - Toggle "Enable Google Analytics for this project" (ON/OFF based on preference)
   - If enabled, select or create an Analytics account
   - Click "Add Firebase"
5. Wait for Firebase initialization (takes 30-60 seconds)

### Step 4: Enable Required Firebase Services
1. In Firebase Console, from the left sidebar, configure services:

   **a) Firestore Database:**
   - Click "Firestore Database" → "Create database"
   - Choose mode:
     - **Production mode**: Secure by default (recommended)
     - **Test mode**: Open access (only for development)
   - Select Firestore location (choose closest to your users)
   - Click "Enable"

   **b) Firebase Authentication (if needed):**
   - Click "Authentication" → "Get started"
   - Enable sign-in methods you need (Email/Password, Google, etc.)

   **c) Firebase Storage (if needed for file uploads):**
   - Click "Storage" → "Get started"
   - Accept security rules
   - Choose storage location
   - Click "Done"

   **d) Firebase Realtime Database (alternative to Firestore):**
   - Click "Realtime Database" → "Create Database"
   - Choose location and security rules
   - Click "Enable"

---

## Part 2: Generate Firebase Credentials

### Step 5: Create Service Account Key
1. In Firebase Console, click the gear icon (⚙️) next to "Project Overview"
2. Select "Project settings"
3. Navigate to "Service accounts" tab
4. Click "Generate new private key"
5. Click "Generate key" in the confirmation dialog
6. A JSON file will download - **SAVE THIS FILE SECURELY**
7. Rename the file to `firebase-credentials.json`
8. Move it to your project directory: `c:\Users\shash\PycharmProjects\multi_llm_chat\`

### Step 6: Get Firebase Configuration (for Web/Client SDK)
1. In Firebase Console "Project settings"
2. Scroll down to "Your apps" section
3. Click the web icon (`</>`) to add a web app
4. Register your app:
   - **App nickname**: `multi-llm-chat-web`
   - Check "Also set up Firebase Hosting" (optional)
   - Click "Register app"
5. Copy the `firebaseConfig` object (you'll need these values)

---

## Part 3: Integrate Firebase with Your Python Application

### Step 7: Install Firebase Admin SDK
Open your terminal in the project directory and run:
```bash
pip install firebase-admin
```

For additional Firebase features:
```bash
pip install firebase-admin google-cloud-firestore google-cloud-storage
```

### Step 8: Update requirements.txt
Add to your `requirements.txt`:
```
firebase-admin>=6.0.0
google-cloud-firestore>=2.11.0
google-cloud-storage>=2.10.0
```

### Step 9: Create Firebase Initialization Module
Create a new file `firebase_config.py`:

```python
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os

# Path to your service account key
CREDENTIALS_PATH = 'firebase-credentials.json'

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'your-project-id.appspot.com'  # Replace with your project ID
        })
    return True

def get_firestore_client():
    """Get Firestore database client"""
    initialize_firebase()
    return firestore.client()

def get_auth_client():
    """Get Firebase Auth client"""
    initialize_firebase()
    return auth

def get_storage_bucket():
    """Get Firebase Storage bucket"""
    initialize_firebase()
    return storage.bucket()

# Initialize on import
initialize_firebase()
```

### Step 10: Create Database Helper Functions
Create a new file `firebase_db.py`:

```python
from firebase_config import get_firestore_client
from datetime import datetime

db = get_firestore_client()

class FirebaseDB:
    """Helper class for Firebase Firestore operations"""
    
    @staticmethod
    def create_document(collection, document_id, data):
        """Create a new document"""
        doc_ref = db.collection(collection).document(document_id)
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        doc_ref.set(data)
        return document_id
    
    @staticmethod
    def read_document(collection, document_id):
        """Read a document"""
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    @staticmethod
    def update_document(collection, document_id, data):
        """Update a document"""
        doc_ref = db.collection(collection).document(document_id)
        data['updated_at'] = datetime.utcnow()
        doc_ref.update(data)
        return True
    
    @staticmethod
    def delete_document(collection, document_id):
        """Delete a document"""
        db.collection(collection).document(document_id).delete()
        return True
    
    @staticmethod
    def query_collection(collection, field=None, operator=None, value=None):
        """Query documents in a collection"""
        if field and operator and value:
            docs = db.collection(collection).where(field, operator, value).stream()
        else:
            docs = db.collection(collection).stream()
        return [doc.to_dict() for doc in docs]
    
    @staticmethod
    def add_document(collection, data):
        """Add document with auto-generated ID"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        doc_ref = db.collection(collection).add(data)
        return doc_ref[1].id  # Returns the auto-generated ID
```

### Step 11: Secure Your Credentials

**IMPORTANT SECURITY STEPS:**

1. **Create `.gitignore` file** (if not exists):
```
firebase-credentials.json
*.json
__pycache__/
*.pyc
.env
```

2. **Add environment variable** (optional, more secure):
   - Create `.env` file:
     ```
     FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
     FIREBASE_PROJECT_ID=your-project-id
     ```
   - Install python-dotenv:
     ```bash
     pip install python-dotenv
     ```
   - Update `firebase_config.py` to use environment variables

3. **Never commit credentials to version control**

---

## Part 4: Testing the Integration

### Step 12: Test Firebase Connection
Create `test_firebase.py`:

```python
from firebase_db import FirebaseDB
import uuid

def test_firebase_connection():
    """Test Firebase database operations"""
    try:
        # Test Create
        test_id = str(uuid.uuid4())
        test_data = {
            'test_field': 'Hello Firebase',
            'timestamp': 'test'
        }
        
        print("Testing CREATE...")
        FirebaseDB.create_document('test_collection', test_id, test_data)
        print("✓ Document created successfully")
        
        # Test Read
        print("\nTesting READ...")
        doc = FirebaseDB.read_document('test_collection', test_id)
        print(f"✓ Document read: {doc}")
        
        # Test Update
        print("\nTesting UPDATE...")
        FirebaseDB.update_document('test_collection', test_id, {'test_field': 'Updated!'})
        print("✓ Document updated successfully")
        
        # Test Query
        print("\nTesting QUERY...")
        docs = FirebaseDB.query_collection('test_collection')
        print(f"✓ Found {len(docs)} documents")
        
        # Test Delete
        print("\nTesting DELETE...")
        FirebaseDB.delete_document('test_collection', test_id)
        print("✓ Document deleted successfully")
        
        print("\n🎉 All Firebase operations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_firebase_connection()
```

Run the test:
```bash
python test_firebase.py
```

---

## Part 5: Integration with Your Multi LLM Chat Project

### Step 13: Database Schema Design

For your multi-LLM chat project, consider these collections:

**1. `conversations` collection:**
```python
{
    'conversation_id': 'uuid',
    'title': 'Conversation title',
    'created_at': timestamp,
    'updated_at': timestamp,
    'user_id': 'user_identifier',
    'metadata': {}
}
```

**2. `messages` collection:**
```python
{
    'message_id': 'uuid',
    'conversation_id': 'uuid',
    'role': 'user' | 'assistant' | 'system',
    'content': 'message content',
    'model': 'gpt-4' | 'claude' | 'gemini',
    'timestamp': timestamp,
    'tokens_used': int,
    'metadata': {}
}
```

**3. `user_preferences` collection:**
```python
{
    'user_id': 'uuid',
    'preferred_models': [],
    'settings': {},
    'created_at': timestamp
}
```

### Step 14: Example Integration
Update your existing files to use Firebase:

```python
# Example: Saving chat messages to Firebase
from firebase_db import FirebaseDB
import uuid

def save_chat_message(conversation_id, role, content, model):
    """Save a chat message to Firebase"""
    message_data = {
        'conversation_id': conversation_id,
        'role': role,
        'content': content,
        'model': model,
        'tokens_used': len(content.split())  # Simple approximation
    }
    message_id = str(uuid.uuid4())
    FirebaseDB.create_document('messages', message_id, message_data)
    return message_id

def get_conversation_history(conversation_id):
    """Retrieve all messages for a conversation"""
    messages = FirebaseDB.query_collection(
        'messages',
        'conversation_id',
        '==',
        conversation_id
    )
    return sorted(messages, key=lambda x: x['created_at'])
```

---

## Troubleshooting

### Common Issues:

1. **"DefaultCredentialsError"**
   - Ensure `firebase-credentials.json` is in the correct location
   - Check file permissions

2. **"Permission Denied" errors**
   - Review Firestore security rules in Firebase Console
   - Update rules for development/production

3. **"Project not found"**
   - Verify project ID in credentials file
   - Ensure Firebase is enabled for the project

4. **Import errors**
   - Reinstall: `pip install --upgrade firebase-admin`
   - Check Python version compatibility

---

## Security Best Practices

1. ✅ Keep credentials file secure and private
2. ✅ Add credentials to `.gitignore`
3. ✅ Use environment variables for production
4. ✅ Set up proper Firestore security rules
5. ✅ Enable Firebase App Check for production
6. ✅ Regularly rotate service account keys
7. ✅ Use least-privilege IAM roles
8. ✅ Enable audit logging in Google Cloud Console

---

## Next Steps

1. [ ] Complete Firebase setup in Google Cloud Console
2. [ ] Download and secure credentials file
3. [ ] Install Firebase Admin SDK
4. [ ] Create `firebase_config.py` and `firebase_db.py`
5. [ ] Test connection with `test_firebase.py`
6. [ ] Design your database schema
7. [ ] Integrate with existing application files
8. [ ] Set up proper security rules
9. [ ] Test thoroughly before production deployment

---

## Useful Resources

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Firebase Console](https://console.firebase.google.com/)

---

**Project:** Multi LLM Chat
**Setup Date:** February 14, 2026
**Status:** Ready for implementation
