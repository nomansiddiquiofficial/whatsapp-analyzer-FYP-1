from datetime import datetime
import re
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase init (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("whatsapp-analyzer-29d80-057eec373036.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Parse WhatsApp chat data
def parse_whatsapp_chat(uploaded_file):
    chat_data = uploaded_file.getvalue().decode("utf-8")
    lines = chat_data.split('\n')
    parsed_data = []
    current_message = {'timestamp': None, 'sender': None, 'message': []}

    for line in lines:
        if re.match(r'\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}\s[APap][Mm]\s-', line):
            if current_message['sender']:
                parsed_data.append({
                    'timestamp': current_message['timestamp'],
                    'sender': current_message['sender'],
                    'message': ' '.join(current_message['message']).strip()
                })
            timestamp = line.split(" - ")[0]
            content = line.split(" - ", 1)[1]
            if ": " in content:
                sender, message = content.split(": ", 1)
            else:
                sender, message = content, ''
            current_message = {
                'timestamp': timestamp,
                'sender': sender,
                'message': [message]
            }
        else:
            current_message['message'].append(line)

    if current_message['sender']:
        parsed_data.append({
            'timestamp': current_message['timestamp'],
            'sender': current_message['sender'],
            'message': ' '.join(current_message['message']).strip()
        })

    df = pd.DataFrame(parsed_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y, %I:%M %p', errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    return df

# Accept file and parse it
def load_data(uploaded_file):
    if uploaded_file is not None:
        return parse_whatsapp_chat(uploaded_file)
    return None

# Save to Firestore
def save_chat_to_firestore(df, user_id,uploaded_file):
    # Create a unique name per upload (e.g. timestamp-based)
    chat_id = uploaded_file.name.replace('.txt', '')

    
    chat_ref = db.collection("whatsapp_chats").document(user_id).collection("chats").document(chat_id).collection("messages")
    
    for _, row in df.iterrows():
        chat_ref.add({
            "timestamp": row['timestamp'],
            "sender": row['sender'],
            "message": row['message']
        })
def fetch_available_chats(user_id):
    try:
        chats_ref = db.collection("whatsapp_chats").document(user_id).collection("chats")
        chat_docs = chats_ref.get()
        
        if not chat_docs:
            print(f"No chats found for user {user_id}")
            return []
            
        return [doc.id for doc in chat_docs]
        
    except Exception as e:
        print(f"Error fetching chats: {str(e)}")
        return []
    
