import streamlit as st
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import numpy as np
from PIL import Image
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import time
import random
import hashlib
from enum import Enum
import secrets

# Quantum simulation components
class Basis(Enum):
    RECTILINEAR = 0  # + basis
    DIAGONAL = 1     # x basis

class QuantumState:
    def __init__(self, bit, basis):
        self.bit = bit
        self.basis = basis

class QuantumChannel:
    def __init__(self, error_rate=0.05):
        self.error_rate = error_rate
        self.eavesdropper_present = False
    
    def transmit(self, states):
        """Simulate quantum transmission with potential eavesdropping"""
        received_states = []
        
        for state in states:
            if self.eavesdropper_present and random.random() < 0.5:
                # Eve measures randomly
                eve_basis = random.choice([Basis.RECTILINEAR, Basis.DIAGONAL])
                if eve_basis == state.basis:
                    eve_bit = state.bit
                else:
                    eve_bit = random.randint(0, 1)
                
                # Eve resends
                resent_basis = random.choice([Basis.RECTILINEAR, Basis.DIAGONAL])
                received_states.append(QuantumState(eve_bit, resent_basis))
            else:
                # Normal transmission with quantum error
                if random.random() < self.error_rate:
                    received_states.append(QuantumState(1 - state.bit, state.basis))
                else:
                    received_states.append(QuantumState(state.bit, state.basis))
        
        return received_states

class QKDSystem:
    def __init__(self, key_length=256, error_rate=0.05):
        self.key_length = key_length
        self.quantum_channel = QuantumChannel(error_rate)
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bases = []
        self.bob_measurements = []
        self.sifted_key = []
        self.final_key = []
    
    def alice_prepare_states(self):
        """Alice prepares random bits in random bases"""
        self.alice_bits = [random.randint(0, 1) for _ in range(self.key_length * 2)]
        self.alice_bases = [random.choice([Basis.RECTILINEAR, Basis.DIAGONAL]) 
                           for _ in range(self.key_length * 2)]
        
        states = []
        for bit, basis in zip(self.alice_bits, self.alice_bases):
            states.append(QuantumState(bit, basis))
        
        return states
    
    def bob_measure_states(self, states):
        """Bob measures states with random bases"""
        self.bob_bases = [random.choice([Basis.RECTILINEAR, Basis.DIAGONAL]) 
                         for _ in range(len(states))]
        self.bob_measurements = []
        
        for state, bob_basis in zip(states, self.bob_bases):
            if state.basis == bob_basis:
                # Same basis - measurement is correct
                self.bob_measurements.append(state.bit)
            else:
                # Different basis - random result
                self.bob_measurements.append(random.randint(0, 1))
        
        return self.bob_measurements
    
    def sift_key(self):
        """Keep only bits where bases match"""
        self.sifted_key = []
        matching_indices = []
        
        for i, (alice_basis, bob_basis) in enumerate(zip(self.alice_bases, self.bob_bases)):
            if alice_basis == bob_basis and len(self.sifted_key) < self.key_length:
                self.sifted_key.append(self.alice_bits[i])
                matching_indices.append(i)
        
        return matching_indices
    
    def estimate_error_rate(self, test_fraction=0.5):
        """Estimate quantum bit error rate (QBER)"""
        test_size = int(len(self.sifted_key) * test_fraction)
        if test_size == 0:
            return 0
        
        test_indices = random.sample(range(len(self.sifted_key)), test_size)
        
        error_count = 0
        for idx in test_indices:
            original_idx = self._get_original_index(idx)
            if self.alice_bits[original_idx] != self.sifted_key[idx]:
                error_count += 1
        
        qber = error_count / test_size
        return qber
    
    def _get_original_index(self, sifted_idx):
        """Map sifted key index back to original transmission index"""
        matching_count = 0
        for i, (alice_basis, bob_basis) in enumerate(zip(self.alice_bases, self.bob_bases)):
            if alice_basis == bob_basis:
                if matching_count == sifted_idx:
                    return i
                matching_count += 1
        return -1
    
    def privacy_amplification(self, initial_key, target_length, qber):
        """Apply privacy amplification to generate final secure key"""
        if qber > 0.11:  # Security threshold
            return None
        
        # Use cryptographic hash for privacy amplification
        key_str = ''.join(str(bit) for bit in initial_key)
        hashed = hashlib.sha256(key_str.encode()).digest()
        
        # Convert to bit array of target length
        final_key_bits = []
        for byte in hashed:
            for i in range(8):
                if len(final_key_bits) < target_length:
                    final_key_bits.append((byte >> i) & 1)
        
        self.final_key = final_key_bits
        return self.final_key
    
    def bits_to_bytes(self, bits):
        """Convert bit array to bytes"""
        byte_array = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= (bits[i + j] << j)
            byte_array.append(byte)
        return bytes(byte_array)
    
    def run_protocol(self):
        """Execute complete BB84 QKD protocol"""
        st.info(" Starting BB84 Quantum Key Distribution Protocol...")
        
        # Step 1: Alice prepares quantum states
        with st.spinner("Alice preparing quantum states..."):
            states = self.alice_prepare_states()
            time.sleep(1)
        
        # Step 2: Quantum transmission
        with st.spinner("Transmitting quantum states through quantum channel..."):
            received_states = self.quantum_channel.transmit(states)
            time.sleep(1)
        
        # Step 3: Bob measures states
        with st.spinner("Bob measuring quantum states..."):
            bob_results = self.bob_measure_states(received_states)
            time.sleep(1)
        
        # Step 4: Basis reconciliation
        with st.spinner("Performing basis reconciliation (sifting)..."):
            matching_indices = self.sift_key()
            time.sleep(1)
        
        # Step 5: Error estimation
        with st.spinner("Estimating Quantum Bit Error Rate (QBER)..."):
            qber = self.estimate_error_rate()
            time.sleep(1)
        
        # Step 6: Privacy amplification
        with st.spinner("Applying privacy amplification..."):
            final_key = self.privacy_amplification(self.sifted_key, 256, qber)
            time.sleep(1)
        
        return final_key, qber, matching_indices

# Set page configuration
st.set_page_config(
    page_title="Quantum Secure Steganography",
    page_icon="",
    layout="wide"
)

# Initialize session state
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
    st.session_state.quantum_keys = {}

# Create directories
os.makedirs("stego_images", exist_ok=True)
os.makedirs("quantum_keys", exist_ok=True)
os.makedirs("analytics", exist_ok=True)

# Existing AES and LSB functions (from previous implementation)
def encrypt_message(message, key):
    try:
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        message_bytes = message.encode('utf-8')
        padded_message = pad(message_bytes, AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return iv + encrypted_message
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt_message(encrypted_message, key):
    try:
        if len(encrypted_message) < AES.block_size:
            raise ValueError("Encrypted message is too short")
        iv = encrypted_message[:AES.block_size]
        encrypted_message = encrypted_message[AES.block_size:]
        if len(encrypted_message) == 0:
            raise ValueError("No encrypted data after IV")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_message = unpad(cipher.decrypt(encrypted_message), AES.block_size)
        return decrypted_message.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption error: {str(e)}")

def embed_message_lsb(image, message):
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_np = np.array(image)
        image_data = image_np.flatten()
        message_with_terminator = message + '\0'
        message_bits = ''.join(format(ord(char), '08b') for char in message_with_terminator)
        if len(message_bits) > len(image_data):
            raise ValueError(f"Message too long. Max capacity: {len(image_data)//8} characters")
        for i, bit in enumerate(message_bits):
            image_data[i] &= 254
            image_data[i] |= int(bit)
        stego_image_np = image_data.reshape(image_np.shape)
        return Image.fromarray(stego_image_np.astype(np.uint8))
    except Exception as e:
        raise ValueError(f"Embedding failed: {str(e)}")

def extract_message_lsb(image):
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_np = np.array(image)
        image_data = image_np.flatten()
        message_bits = []
        for pixel_value in image_data:
            message_bits.append(pixel_value & 1)
        message = ''
        for i in range(0, len(message_bits), 8):
            byte = message_bits[i:i + 8]
            if len(byte) < 8:
                break
            byte_str = ''.join(str(bit) for bit in byte)
            character = chr(int(byte_str, 2))
            if character == '\0':
                break
            message += character
        return message if message else None
    except Exception as e:
        raise ValueError(f"Extraction failed: {str(e)}")

# Analytics functions
def update_analytics(operation_type, message_length=0, image_size=(0, 0), operation_time=0, success=True):
    timestamp = datetime.now()
    if operation_type == 'embed':
        st.session_state.analytics_data['embed_operations'].append({
            'timestamp': timestamp, 'message_length': message_length,
            'image_size': image_size, 'operation_time': operation_time, 'success': success
        })
    elif operation_type == 'extract':
        st.session_state.analytics_data['extract_operations'].append({
            'timestamp': timestamp, 'message_length': message_length,
            'image_size': image_size, 'operation_time': operation_time, 'success': success
        })
    st.session_state.analytics_data['message_lengths'].append(message_length)
    st.session_state.analytics_data['image_sizes'].append(image_size[0] * image_size[1])
    st.session_state.analytics_data['operation_times'].append(operation_time)

def update_qkd_analytics(key_id, qber, key_length, success, eavesdropper_detected=False):
    st.session_state.analytics_data['qkd_sessions'].append({
        'timestamp': datetime.now(),
        'key_id': key_id,
        'qber': qber,
        'key_length': key_length,
        'success': success,
        'eavesdropper_detected': eavesdropper_detected
    })

def save_quantum_key(key, key_id):
    """Save quantum key to file"""
    filename = f"quantum_keys/quantum_key_{key_id}.key"
    with open(filename, 'wb') as f:
        f.write(key)
    st.session_state.quantum_keys[key_id] = {
        'key': key,
        'filename': filename,
        'created_at': datetime.now()
    }

# Visualization functions for QKD
def create_qkd_metrics_chart(qkd_sessions):
    if not qkd_sessions:
        return None
    
    sessions = qkd_sessions[-10:]  # Last 10 sessions
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # QBER over time
    qbers = [session['qber'] for session in sessions]
    ax1.plot(range(len(qbers)), qbers, marker='o', linewidth=2, color='red')
    ax1.axhline(y=0.11, color='r', linestyle='--', label='Security Threshold (11%)')
    ax1.set_title('Quantum Bit Error Rate (QBER) Over Time')
    ax1.set_xlabel('Session')
    ax1.set_ylabel('QBER')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Success rate
    success_rate = sum(1 for s in sessions if s['success']) / len(sessions) * 100
    ax2.bar(['Success Rate'], [success_rate], color=['green' if success_rate > 80 else 'red'])
    ax2.set_ylim(0, 100)
    ax2.set_title('QKD Success Rate')
    ax2.set_ylabel('Rate (%)')
    
    # Key lengths
    key_lengths = [session['key_length'] for session in sessions]
    ax3.bar(range(len(key_lengths)), key_lengths, color='blue', alpha=0.7)
    ax3.set_title('Generated Key Lengths')
    ax3.set_xlabel('Session')
    ax3.set_ylabel('Key Length (bits)')
    
    # Eavesdropper detection
    eve_detections = sum(1 for s in sessions if s['eavesdropper_detected'])
    ax4.pie([eve_detections, len(sessions) - eve_detections], 
            labels=['Eavesdropper Detected', 'Secure'], 
            colors=['red', 'green'], autopct='%1.1f%%')
    ax4.set_title('Eavesdropper Detection Rate')
    
    plt.tight_layout()
    return fig

def create_quantum_state_visualization(alice_bits, alice_bases, bob_bases, matching_indices):
    """Create visualization of quantum state transmission"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Basis usage
    alice_rect = sum(1 for basis in alice_bases if basis == Basis.RECTILINEAR)
    alice_diag = len(alice_bases) - alice_rect
    bob_rect = sum(1 for basis in bob_bases if basis == Basis.RECTILINEAR)
    bob_diag = len(bob_bases) - bob_rect
    
    ax1.bar(['Alice Rectilinear', 'Alice Diagonal', 'Bob Rectilinear', 'Bob Diagonal'],
            [alice_rect, alice_diag, bob_rect, bob_diag], color=['blue', 'red', 'lightblue', 'pink'])
    ax1.set_title('Basis Selection Distribution')
    ax1.set_ylabel('Count')
    
    # Matching bases
    matching_percentage = (len(matching_indices) / len(alice_bases)) * 100
    ax2.pie([matching_percentage, 100 - matching_percentage], 
            labels=['Matching Bases', 'Different Bases'], 
            colors=['green', 'orange'], autopct='%1.1f%%')
    ax2.set_title('Basis Matching Rate')
    
    plt.tight_layout()
    return fig

# Streamlit UI
st.title(' Quantum Secure Steganography with QKD')


# Sidebar
st.sidebar.header(" Quantum Security Configuration")

# QKD Parameters
st.sidebar.subheader("QKD Settings")
qkd_key_length = st.sidebar.slider("Key Length (bits)", 128, 512, 256, 128)
qkd_error_rate = st.sidebar.slider("Quantum Channel Error Rate", 0.01, 0.15, 0.05, 0.01)
eavesdropper = st.sidebar.checkbox("Simulate Eavesdropper (Eve)")

operation = st.sidebar.selectbox(
    "Select Operation",
    ["Quantum Key Distribution", "Embed Message", "Extract Message", "Quantum Analytics Dashboard"]
)

if operation == "Quantum Key Distribution":
    st.header(" BB84 Quantum Key Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Quantum Protocol Execution")
        
        if st.button(" Execute BB84 Protocol", type="primary"):
            # Initialize QKD system
            qkd = QKDSystem(key_length=qkd_key_length, error_rate=qkd_error_rate)
            qkd.quantum_channel.eavesdropper_present = eavesdropper
            
            # Execute protocol
            final_key, qber, matching_indices = qkd.run_protocol()
            
            # Generate unique key ID
            key_id = f"qkd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if final_key:
                # Convert to bytes and save
                key_bytes = qkd.bits_to_bytes(final_key)
                save_quantum_key(key_bytes, key_id)
                
                st.success(" Quantum Key Successfully Generated!")
                
                # Display key information
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("QBER", f"{qber:.3f}")
                with col2:
                    st.metric("Key Length", f"{len(final_key)} bits")
                with col3:
                    st.metric("Security Status", " Secure" if qber < 0.11 else " Compromised")
                
                # Key preview
                st.subheader("Generated Quantum Key")
                st.code(f"Key ID: {key_id}")
                st.code(f"Key (hex): {key_bytes.hex()[:64]}...")
                
                update_qkd_analytics(key_id, qber, len(final_key), True, qber > 0.11)
                
            else:
                st.error(" Quantum Key Generation Failed - QBER too high!")
                update_qkd_analytics(key_id, qber, 0, False, True)
    
    with col2:
        st.subheader("Available Quantum Keys")
        if st.session_state.quantum_keys:
            for key_id, key_data in list(st.session_state.quantum_keys.items())[-5:]:
                with st.expander(f"Key: {key_id}"):
                    st.write(f"Created: {key_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"Length: {len(key_data['key'])*8} bits")
                    if st.button(f"Use Key", key=f"use_{key_id}"):
                        st.session_state.current_key = key_data['key']
                        st.success(f" Using key {key_id}")
        else:
            st.info("No quantum keys generated yet")

elif operation == "Embed Message":
    st.header(" Embed Encrypted Message with Quantum Key")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        
        # Key selection
        if st.session_state.quantum_keys:
            key_options = list(st.session_state.quantum_keys.keys())
            selected_key = st.selectbox("Select Quantum Key", key_options)
            key = st.session_state.quantum_keys[selected_key]['key']
            st.success(f"Using quantum key: {selected_key}")
        else:
            st.warning("No quantum keys available. Please generate keys first.")
            key = None
        
        message_input = st.text_area("Secret Message:", height=150)
        uploaded_image = st.file_uploader("Choose Cover Image", type=["jpg", "png", "jpeg", "bmp", "tiff"])
        
        if uploaded_image and message_input and key:
            image = Image.open(uploaded_image)
            capacity = (image.size[0] * image.size[1] * 3) // 8
            st.info(f"Capacity: {capacity} chars | Your message: {len(message_input)} chars")
    
    with col2:
        st.subheader("Quantum Encryption & Embedding")
        if uploaded_image and message_input and key:
            if st.button(" Quantum Encrypt & Embed", type="primary"):
                start_time = time.time()
                with st.spinner("Performing quantum-secured encryption and embedding..."):
                    try:
                        image = Image.open(uploaded_image)
                        
                        # Encrypt with quantum key
                        encryption_start = time.time()
                        encrypted_message = encrypt_message(message_input, key)
                        encryption_time = time.time() - encryption_start
                        
                        # Embed using LSB
                        embedding_start = time.time()
                        encrypted_message_str = encrypted_message.decode('latin-1')
                        stego_image = embed_message_lsb(image, encrypted_message_str)
                        embedding_time = time.time() - embedding_start
                        
                        total_time = time.time() - start_time
                        
                        # Save locally
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"stego_images/quantum_stego_{timestamp}.png"
                        stego_image.save(filename, "PNG")
                        
                        # Update analytics
                        update_analytics('embed', len(message_input), image.size, total_time, True)
                        
                        # Display results
                        st.success(" Quantum-secured message embedded successfully!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(image, caption="Original Image", use_container_width=True)
                        with col2:
                            st.image(stego_image, caption="Quantum Stego Image", use_container_width=True)
                        
                        # Performance metrics
                        st.subheader(" Quantum Security Metrics")
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        with metric_col1:
                            st.metric("Encryption Time", f"{encryption_time:.3f}s")
                        with metric_col2:
                            st.metric("Embedding Time", f"{embedding_time:.3f}s")
                        with metric_col3:
                            st.metric("Total Time", f"{total_time:.3f}s")
                        
                        st.info(f" Stego image saved as: {filename}")
                        
                    except Exception as e:
                        total_time = time.time() - start_time
                        update_analytics('embed', len(message_input), image.size, total_time, False)
                        st.error(f" Error: {str(e)}")

elif operation == "Extract Message":
    st.header(" Extract & Decrypt with Quantum Key")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        
        # Key selection
        if st.session_state.quantum_keys:
            key_options = list(st.session_state.quantum_keys.keys())
            selected_key = st.selectbox("Select Quantum Key for Decryption", key_options)
            key = st.session_state.quantum_keys[selected_key]['key']
            st.success(f"Using quantum key: {selected_key}")
        else:
            st.warning("No quantum keys available.")
            key = None
        
        uploaded_stego_image = st.file_uploader("Upload Quantum Stego Image", type=["jpg", "png", "jpeg", "bmp", "tiff"])
        
        if uploaded_stego_image:
            stego_image = Image.open(uploaded_stego_image)
            st.image(stego_image, caption="Quantum Stego Image", use_container_width=True)
    
    with col2:
        st.subheader("Quantum Decryption")
        if uploaded_stego_image and key:
            if st.button(" Quantum Extract & Decrypt", type="primary"):
                start_time = time.time()
                with st.spinner("Extracting and quantum-decrypting message..."):
                    try:
                        stego_image = Image.open(uploaded_stego_image)
                        
                        # Extract from LSB
                        extraction_start = time.time()
                        extracted_message = extract_message_lsb(stego_image)
                        extraction_time = time.time() - extraction_start
                        
                        if extracted_message:
                            # Decrypt with quantum key
                            decryption_start = time.time()
                            extracted_bytes = extracted_message.encode('latin-1')
                            decrypted_message = decrypt_message(extracted_bytes, key)
                            decryption_time = time.time() - decryption_start
                            
                            total_time = time.time() - start_time
                            update_analytics('extract', len(decrypted_message), stego_image.size, total_time, True)
                            
                            st.success(" Quantum-secured message extracted successfully!")
                            st.text_area("Decrypted Message:", decrypted_message, height=200)
                            
                            # Performance metrics
                            st.subheader(" Extraction Metrics")
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            with metric_col1:
                                st.metric("Extraction Time", f"{extraction_time:.3f}s")
                            with metric_col2:
                                st.metric("Decryption Time", f"{decryption_time:.3f}s")
                            with metric_col3:
                                st.metric("Total Time", f"{total_time:.3f}s")
                            
                        else:
                            st.warning(" No hidden message found")
                            
                    except Exception as e:
                        st.error(f" Error: {str(e)}")

elif operation == "Quantum Analytics Dashboard":
    st.header(" Quantum Security Analytics Dashboard")
    
    # Quantum Metrics
    st.subheader(" QKD Protocol Analytics")
    if st.session_state.analytics_data['qkd_sessions']:
        st.pyplot(create_qkd_metrics_chart(st.session_state.analytics_data['qkd_sessions']))
        
        # Recent QKD sessions
        st.subheader("Recent QKD Sessions")
        qkd_data = []
        for session in st.session_state.analytics_data['qkd_sessions'][-10:]:
            qkd_data.append({
                'Timestamp': session['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'Key ID': session['key_id'],
                'QBER': f"{session['qber']:.3f}",
                'Key Length': f"{session['key_length']} bits",
                'Status': ' Success' if session['success'] else ' Failed',
                'Eavesdropper': ' Detected' if session['eavesdropper_detected'] else ' Secure'
            })
        st.dataframe(qkd_data)
    else:
        st.info("No QKD sessions recorded yet")
    
    # Traditional analytics
    st.subheader(" Traditional Operation Analytics")
    # Include traditional analytics charts from previous implementation
    # (Operations chart, message length distribution, etc.)
