import streamlit as st
import os
from Crypto.Random import get_random_bytes
from datetime import datetime

def generate_key():
    return get_random_bytes(32)

def save_quantum_key(key, key_id):
    filename = f"quantum_keys/quantum_key_{key_id}.key"
    with open(filename, 'wb') as f:
        f.write(key)
    st.session_state.quantum_keys[key_id] = {
        'key': key,
        'filename': filename,
        'created_at': datetime.now()
    }

def load_quantum_keys():
    quantum_keys_dir = "quantum_keys"
    if not os.path.exists(quantum_keys_dir):
        os.makedirs(quantum_keys_dir)
        return {}
    
    keys = {}
    for filename in os.listdir(quantum_keys_dir):
        if filename.endswith('.key'):
            key_id = filename.replace('quantum_key_', '').replace('.key', '')
            with open(os.path.join(quantum_keys_dir, filename), 'rb') as f:
                keys[key_id] = {
                    'key': f.read(),
                    'filename': filename,
                    'created_at': datetime.fromtimestamp(os.path.getctime(os.path.join(quantum_keys_dir, filename)))
                }
    return keys

def initialize_directories():
    os.makedirs("stego_images", exist_ok=True)
    os.makedirs("quantum_keys", exist_ok=True)
    os.makedirs("analytics", exist_ok=True)

def initialize_session_state():
    if 'analytics_data' not in st.session_state:
        st.session_state.analytics_data = {
            'embed_operations': [],
            'extract_operations': [],
            'message_lengths': [],
            'image_sizes': [],
            'operation_times': [],
            'qkd_sessions': []
        }
    
    if 'stego_images' not in st.session_state:
        st.session_state.stego_images = []
    
    if 'quantum_keys' not in st.session_state:
        st.session_state.quantum_keys = load_quantum_keys()