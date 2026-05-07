# Quantum Secure Steganography with QKD

This project is a Streamlit-based web application that combines Quantum Key Distribution (QKD) using the BB84 protocol simulation with Image Steganography to provide a highly secure method for embedding and extracting hidden messages.

## Features

- **Quantum Key Distribution (BB84 Protocol)**: Simulates the BB84 quantum key distribution protocol to securely generate cryptographic keys. Includes options to set key length, simulate quantum channel error rates, and simulate the presence of an eavesdropper.
- **Quantum Secure Steganography**: 
  - Uses the quantum-generated keys to encrypt your secret messages using AES encryption.
  - Embeds the encrypted messages into images using Least Significant Bit (LSB) steganography.
- **Message Extraction & Decryption**: Securely extracts hidden messages from stego images and decrypts them using the correct quantum key.
- **Quantum Analytics Dashboard**: Visualizes QKD metrics such as Quantum Bit Error Rate (QBER) over time, success rates, key lengths, and eavesdropper detection.

## Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Cryptography**: `pycryptodome` for AES encryption and decryption.
- **Image Processing**: `Pillow` (PIL) and `numpy` for LSB steganography.
- **Data Visualization**: `matplotlib`, `seaborn`, and `pandas` for the analytics dashboard.

## Prerequisites

Make sure you have Python 3 installed. Then, install the required dependencies using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Dependencies
- `streamlit`
- `pycryptodome`
- `numpy`
- `Pillow`
- `pandas`
- `matplotlib`
- `seaborn`

## How to Run

1. Clone the repository and navigate to the project directory.
2. Run the Streamlit application:

```bash
streamlit run main.py
```

3. Open your web browser and navigate to the URL provided in the terminal (usually `http://localhost:8501`).

## Usage Guide

1. **Generate a Quantum Key**: Navigate to the "Quantum Key Distribution" tab. Adjust your settings (key length, error rate, eavesdropper simulation) and execute the BB84 protocol to generate a secure key.
2. **Embed a Message**: Go to the "Embed Message" tab. Select the quantum key you just generated, upload a cover image, write your secret message, and click "Quantum Encrypt & Embed". The resulting image will be saved locally.
3. **Extract a Message**: Switch to the "Extract Message" tab. Upload the stego image and select the corresponding quantum key to extract and decrypt your hidden message.
4. **Analytics**: Check out the "Quantum Analytics Dashboard" to view the statistics and success metrics of your QKD sessions and operations.
