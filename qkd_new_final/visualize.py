import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from quantum_qkd import Basis

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

def create_qkd_metrics_chart(qkd_sessions):
    if not qkd_sessions:
        return None
    
    sessions = qkd_sessions[-10:]
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

def create_operations_chart():
    embed_count = len(st.session_state.analytics_data['embed_operations'])
    extract_count = len(st.session_state.analytics_data['extract_operations'])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    operations = ['Embed Operations', 'Extract Operations']
    counts = [embed_count, extract_count]
    
    bars = ax.bar(operations, counts, color=['#FF6B6B', '#4ECDC4'])
    ax.set_title('Operations Overview', fontsize=16, fontweight='bold')
    ax.set_ylabel('Number of Operations')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    return fig