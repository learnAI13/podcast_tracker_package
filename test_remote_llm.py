#!/usr/bin/env python3
# test_remote_llm.py - Test connection to remote LLaMA 3.1 server

import requests
import argparse
import json
import os
from dotenv import load_dotenv

def test_llm_connection(url):
    """Test connection to LLM server"""
    print(f"Testing connection to LLM server at: {url}")
    
    # First, try the health endpoint
    try:
        health_response = requests.get(f"{url}/health", timeout=5)
        if health_response.status_code == 200:
            print(f"✅ Health check successful: {health_response.json()}")
        else:
            print(f"❌ Health check failed with status code: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed with error: {str(e)}")
        return False
    
    # Now test the generation endpoint
    try:
        test_prompt = "Hello, I am testing the LLaMA 3.1 connection. Please respond with a short greeting."
        
        payload = {
            "prompt": test_prompt,
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        generate_response = requests.post(
            f"{url}/generate", 
            json=payload,
            timeout=10
        )
        
        if generate_response.status_code == 200:
            result = generate_response.json()
            print("\n✅ Generation test successful!")
            print(f"Model: {result.get('model', 'unknown')}")
            print(f"Response: {result.get('generated_text', '')}")
            return True
        else:
            print(f"❌ Generation test failed with status code: {generate_response.status_code}")
            print(f"Response: {generate_response.text}")
            return False
    except Exception as e:
        print(f"❌ Generation test failed with error: {str(e)}")
        return False

def update_env_file(url):
    """Update the .env file with the new LLM URL"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Replace the LLM URLs
    env_content = env_content.replace('MIXTRAL_URL=http://localhost:8080', f'MIXTRAL_URL={url}')
    env_content = env_content.replace('LLAMA_70B_URL=http://localhost:8080', f'LLAMA_70B_URL={url}')
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Updated .env file with new LLM URL: {url}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Test connection to remote LLaMA 3.1 server")
    parser.add_argument("url", help="URL of the LLaMA 3.1 server (e.g., http://your-server.edu:8080)")
    parser.add_argument("--update-env", action="store_true", help="Update .env file with the new URL if test is successful")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Test the connection
    success = test_llm_connection(args.url)
    
    if success and args.update_env:
        update_env_file(args.url)
        print("\n🎉 Connection test successful and .env file updated!")
        print("You can now restart your system to use the remote LLaMA 3.1 models.")
    elif success:
        print("\n🎉 Connection test successful!")
        print("To use this LLM server, update your .env file or run this script with --update-env")
    else:
        print("\n❌ Connection test failed.")
        print("Please check that your LLaMA 3.1 server is running and accessible.")

if __name__ == "__main__":
    main()