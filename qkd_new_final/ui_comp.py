import streamlit as st
from quantum_qkd import QKDSystem
from crypto_steganography import *
from visualize import *
from key_manage import save_quantum_key, update_qkd_analytics
import time
from datetime import datetime

def render_qkd_interface():
    st.header("BB84 Quantum Key Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Quantum Protocol Execution")
        
        if st.button("Execute BB84 Protocol", type="primary"):
            qkd_key_length = st.session_state.get('qkd_key_length', 256)
            qkd_error_rate = st.session_state.get('qkd_error_rate', 0.05)
            eavesdropper = st.session_state.get('eavesdropper', False)
            
            qkd = QKDSystem(key_length=qkd_key_length, error_rate=qkd_error_rate)
            qkd.quantum_channel.eavesdropper_present = eavesdropper
            
            final_key, qber, matching_indices = qkd.run_protocol()
            key_id = f"qkd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if final_key:
                key_bytes = qkd.bits_to_bytes(final_key)
                save_quantum_key(key_bytes, key_id)
                
                st.success("Quantum key successfully generated.")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("QBER", f"{qber:.3f}")
                with col2:
                    st.metric("Key Length", f"{len(final_key)} bits")
                with col3:
                    st.metric("Security Status", "Secure" if qber < 0.11 else "Compromised")
                
                st.subheader("Generated Quantum Key")
                st.code(f"Key ID: {key_id}")
                st.code(f"Key (hex): {key_bytes.hex()[:64]}...")
                
                update_qkd_analytics(key_id, qber, len(final_key), True, qber > 0.11)
            else:
                st.error("Quantum Key Generation Failed - QBER too high!")
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
                        st.success(f"Using key {key_id}")
        else:
            st.info("No quantum keys generated yet")

def render_embed_interface():
    st.header("Embed Encrypted Message with Quantum Key")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        
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
            if st.button("Quantum Encrypt & Embed", type="primary"):
                start_time = time.time()
                with st.spinner("Performing quantum-secured encryption and embedding..."):
                    try:
                        image = Image.open(uploaded_image)
                        
                        encryption_start = time.time()
                        encrypted_message = encrypt_message(message_input, key)
                        encryption_time = time.time() - encryption_start
                        
                        embedding_start = time.time()
                        encrypted_message_str = encrypted_message.decode('latin-1')
                        stego_image = embed_message_lsb(image, encrypted_message_str)
                        embedding_time = time.time() - embedding_start
                        
                        total_time = time.time() - start_time
                        filename = save_stego_image_local(stego_image)
                        update_analytics('embed', len(message_input), image.size, total_time, True)
                        
                        st.success("Message embedded successfully.")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(image, caption="Original Image", use_container_width=True)
                        with col2:
                            st.image(stego_image, caption="Quantum Stego Image", use_container_width=True)
                        
                        st.subheader("Quantum Security Metrics")
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        with metric_col1:
                            st.metric("Encryption Time", f"{encryption_time:.3f}s")
                        with metric_col2:
                            st.metric("Embedding Time", f"{embedding_time:.3f}s")
                        with metric_col3:
                            st.metric("Total Time", f"{total_time:.3f}s")
                        
                        st.info(f"Stego image saved as: {filename}")
                        
                    except Exception as e:
                        total_time = time.time() - start_time
                        update_analytics('embed', len(message_input), image.size, total_time, False)
                        st.error(f"Error: {str(e)}")

def render_extract_interface():
    st.header("Extract & Decrypt with Quantum Key")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        
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
            if st.button("Quantum Extract & Decrypt", type="primary"):
                start_time = time.time()
                with st.spinner("Extracting and quantum-decrypting message..."):
                    try:
                        stego_image = Image.open(uploaded_stego_image)
                        
                        extraction_start = time.time()
                        extracted_message = extract_message_lsb(stego_image)
                        extraction_time = time.time() - extraction_start
                        
                        if extracted_message:
                            decryption_start = time.time()
                            extracted_bytes = extracted_message.encode('latin-1')
                            decrypted_message = decrypt_message(extracted_bytes, key)
                            decryption_time = time.time() - decryption_start
                            
                            total_time = time.time() - start_time
                            update_analytics('extract', len(decrypted_message), stego_image.size, total_time, True)
                            
                            st.success("Message extracted successfully.")
                            st.text_area("Decrypted Message:", decrypted_message, height=200)
                            
                            st.subheader("Extraction Metrics")
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            with metric_col1:
                                st.metric("Extraction Time", f"{extraction_time:.3f}s")
                            with metric_col2:
                                st.metric("Decryption Time", f"{decryption_time:.3f}s")
                            with metric_col3:
                                st.metric("Total Time", f"{total_time:.3f}s")
                            
                        else:
                            st.warning("No hidden message found")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

def render_analytics_dashboard():
    st.header("Quantum Security Analytics Dashboard")
    
    st.subheader("QKD Protocol Analytics")
    if st.session_state.analytics_data['qkd_sessions']:
        st.pyplot(create_qkd_metrics_chart(st.session_state.analytics_data['qkd_sessions']))
        
        st.subheader("Recent QKD Sessions")
        qkd_data = []
        for session in st.session_state.analytics_data['qkd_sessions'][-10:]:
            qkd_data.append({
                'Timestamp': session['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'Key ID': session['key_id'],
                'QBER': f"{session['qber']:.3f}",
                'Key Length': f"{session['key_length']} bits",
                'Status': 'Success' if session['success'] else 'Failed',
                'Eavesdropper': 'Detected' if session['eavesdropper_detected'] else 'Secure'
            })
        st.dataframe(qkd_data)
    else:
        st.info("No QKD sessions recorded yet")
