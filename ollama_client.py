#!/usr/bin/env python3
# ollama_client.py - Client for Ollama LLaMA models

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv('LLAMA_70B_URL', 'http://localhost:11434')
        self.llama_8b_model = "llama3:8b"
        self.llama_70b_model = "llama3.1:70b"
    
    def generate_text(self, prompt, model="llama3.1:70b", max_tokens=1000, temperature=0.7):
        """Generate text using Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return {
                "generated_text": result.get("response", ""),
                "model": model
            }
        except Exception as e:
            print(f"Error calling Ollama API: {str(e)}")
            return {
                "generated_text": f"Error: {str(e)}",
                "model": model
            }
    
    def generate_with_8b(self, prompt, max_tokens=1000, temperature=0.7):
        """Use LLaMA 3:8b model for faster responses"""
        return self.generate_text(prompt, self.llama_8b_model, max_tokens, temperature)
    
    def generate_with_70b(self, prompt, max_tokens=1000, temperature=0.7):
        """Use LLaMA 3.1:70b model for better quality"""
        return self.generate_text(prompt, self.llama_70b_model, max_tokens, temperature)
    
    def test_connection(self):
        """Test connection to Ollama"""
        try:
            result = self.generate_with_8b("Hello, please respond with 'Connection successful!'", max_tokens=50)
            return "Connection successful" in result.get("generated_text", "")
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

# Global client instance
ollama_client = OllamaClient()
