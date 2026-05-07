import streamlit as st
from key_manage import initialize_directories, initialize_session_state
from ui_comp import *

# Set page configuration
st.set_page_config(
    page_title="Quantum Secure Steganography",
    layout="wide"
)

# Initialize application
initialize_directories()
initialize_session_state()

# Main UI
st.title('Quantum Secure Steganography with QKD')


# Sidebar configuration
st.sidebar.header("Quantum Security Configuration")
st.sidebar.subheader("QKD Settings")
st.session_state.qkd_key_length = st.sidebar.slider("Key Length (bits)", 128, 512, 256, 128)
st.session_state.qkd_error_rate = st.sidebar.slider("Quantum Channel Error Rate", 0.01, 0.15, 0.05, 0.01)
st.session_state.eavesdropper = st.sidebar.checkbox("Simulate Eavesdropper (Eve)")

# Main operation routing
operation = st.sidebar.selectbox(
    "Select Operation",
    ["Quantum Key Distribution", "Embed Message", "Extract Message", "Quantum Analytics Dashboard"]
)

if operation == "Quantum Key Distribution":
    render_qkd_interface()
elif operation == "Embed Message":
    render_embed_interface()
elif operation == "Extract Message":
    render_extract_interface()
elif operation == "Quantum Analytics Dashboard":
    render_analytics_dashboard()
