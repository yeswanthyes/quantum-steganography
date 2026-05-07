import streamlit as st
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime

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

def save_stego_image_local(image, filename_prefix="quantum_stego"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stego_images/{filename_prefix}_{timestamp}.png"
    image.save(filename, "PNG")
    return filename

def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href