import streamlit as st
import random
import hashlib
import time
from enum import Enum
from datetime import datetime

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
        received_states = []
        for state in states:
            if self.eavesdropper_present and random.random() < 0.5:
                eve_basis = random.choice([Basis.RECTILINEAR, Basis.DIAGONAL])
                if eve_basis == state.basis:
                    eve_bit = state.bit
                else:
                    eve_bit = random.randint(0, 1)
                resent_basis = random.choice([Basis.RECTILINEAR, Basis.DIAGONAL])
                received_states.append(QuantumState(eve_bit, resent_basis))
            else:
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
        self.alice_bits = [random.randint(0, 1) for _ in range(self.key_length * 2)]
        self.alice_bases = [random.choice([Basis.RECTILINEAR, Basis.DIAGONAL]) 
                           for _ in range(self.key_length * 2)]
        states = []
        for bit, basis in zip(self.alice_bits, self.alice_bases):
            states.append(QuantumState(bit, basis))
        return states
    
    def bob_measure_states(self, states):
        self.bob_bases = [random.choice([Basis.RECTILINEAR, Basis.DIAGONAL]) 
                         for _ in range(len(states))]
        self.bob_measurements = []
        for state, bob_basis in zip(states, self.bob_bases):
            if state.basis == bob_basis:
                self.bob_measurements.append(state.bit)
            else:
                self.bob_measurements.append(random.randint(0, 1))
        return self.bob_measurements
    
    def sift_key(self):
        self.sifted_key = []
        matching_indices = []
        for i, (alice_basis, bob_basis) in enumerate(zip(self.alice_bases, self.bob_bases)):
            if alice_basis == bob_basis and len(self.sifted_key) < self.key_length:
                self.sifted_key.append(self.alice_bits[i])
                matching_indices.append(i)
        return matching_indices
    
    def estimate_error_rate(self, test_fraction=0.5):
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
        matching_count = 0
        for i, (alice_basis, bob_basis) in enumerate(zip(self.alice_bases, self.bob_bases)):
            if alice_basis == bob_basis:
                if matching_count == sifted_idx:
                    return i
                matching_count += 1
        return -1
    
    def privacy_amplification(self, initial_key, target_length, qber):
        if qber > 0.11:
            return None
        key_str = ''.join(str(bit) for bit in initial_key)
        hashed = hashlib.sha256(key_str.encode()).digest()
        final_key_bits = []
        for byte in hashed:
            for i in range(8):
                if len(final_key_bits) < target_length:
                    final_key_bits.append((byte >> i) & 1)
        self.final_key = final_key_bits
        return self.final_key
    
    def bits_to_bytes(self, bits):
        byte_array = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= (bits[i + j] << j)
            byte_array.append(byte)
        return bytes(byte_array)
    
    def run_protocol(self):
        st.info("🔐 Starting BB84 Quantum Key Distribution Protocol...")
        
        with st.spinner("Alice preparing quantum states..."):
            states = self.alice_prepare_states()
            time.sleep(1)
        
        with st.spinner("Transmitting quantum states through quantum channel..."):
            received_states = self.quantum_channel.transmit(states)
            time.sleep(1)
        
        with st.spinner("Bob measuring quantum states..."):
            bob_results = self.bob_measure_states(received_states)
            time.sleep(1)
        
        with st.spinner("Performing basis reconciliation (sifting)..."):
            matching_indices = self.sift_key()
            time.sleep(1)
        
        with st.spinner("Estimating Quantum Bit Error Rate (QBER)..."):
            qber = self.estimate_error_rate()
            time.sleep(1)
        
        with st.spinner("Applying privacy amplification..."):
            final_key = self.privacy_amplification(self.sifted_key, 256, qber)
            time.sleep(1)
        
        return final_key, qber, matching_indices