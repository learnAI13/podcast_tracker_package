#!/usr/bin/env python3
# test_ollama.py - Test Ollama connection

from ollama_client import ollama_client

def test_ollama():
    print("Testing Ollama connection...")
    
    # Test 8B model
    print("\n1. Testing LLaMA 3:8b model...")
    result_8b = ollama_client.generate_with_8b("Hello! Please respond with a short greeting.", max_tokens=50)
    print(f"8B Response: {result_8b.get('generated_text', 'No response')}")
    
    # Test 70B model
    print("\n2. Testing LLaMA 3.1:70b model...")
    result_70b = ollama_client.generate_with_70b("Hello! Please respond with a short greeting.", max_tokens=50)
    print(f"70B Response: {result_70b.get('generated_text', 'No response')}")
    
    # Test connection method
    print("\n3. Testing connection method...")
    connection_ok = ollama_client.test_connection()
    print(f"Connection test: {'✅ PASSED' if connection_ok else '❌ FAILED'}")

if __name__ == "__main__":
    test_ollama()
