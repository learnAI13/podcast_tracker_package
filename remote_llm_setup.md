# Connecting to Remote LLaMA 3.1 Models

This guide explains how to connect your 1-Click Podcast Guest Tracker to the LLaMA 3.1 models running on your college server.

## Option 1: Expose LLaMA API from College Server

If you want to keep running the podcast tracker locally but use the remote LLaMA models:

1. On your college server where LLaMA 3.1 is running, make sure the API is accessible:
   ```bash
   # Example using FastAPI to serve LLaMA models
   python -m uvicorn llm_server:app --host 0.0.0.0 --port 8080
   ```

2. Set up port forwarding or a reverse proxy if needed to make the API accessible outside the server.

3. Update your `.env` file to point to the remote server:
   ```
   # Replace with your actual server IP/hostname and port
   MIXTRAL_URL=http://your-college-server.edu:8080
   LLAMA_8B_URL=http://your-college-server.edu:8081
   LLAMA_70B_URL=http://your-college-server.edu:8082
   ```

## Option 2: Move Code to College Server

Alternatively, you can move the entire podcast tracker to your college server:

1. Clone the repository on your college server:
   ```bash
   git clone https://github.com/yourusername/podcast-guest-tracker.git
   cd podcast-guest-tracker
   ```

2. Install dependencies:
   ```bash
   ./install_deps.sh
   ```

3. Update the `.env` file to use localhost since the LLaMA models are on the same machine:
   ```
   MIXTRAL_URL=http://localhost:8080
   LLAMA_8B_URL=http://localhost:8081
   LLAMA_70B_URL=http://localhost:8082
   ```

4. Start the system:
   ```bash
   ./start_system.sh
   ```

## LLaMA 3.1 API Format

The podcast tracker expects the LLaMA 3.1 API to have the following endpoints:

1. `/health` - Returns status of the model
2. `/generate` - Text generation endpoint

The `/generate` endpoint should accept POST requests with this JSON format:
```json
{
  "prompt": "Your text prompt here",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

And return responses in this format:
```json
{
  "generated_text": "The model's response text",
  "model": "llama-3.1-70b"
}
```

## Testing the Connection

To test if your connection to the remote LLaMA models is working:

```bash
curl -X POST http://your-college-server.edu:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, I am testing the LLaMA 3.1 connection. Please respond.", "max_tokens": 50, "temperature": 0.7}'
```

If successful, you should receive a generated text response from the model.

## Updating the Code

If your LLaMA API has a different format, you'll need to modify the `llm_client.py` file to match your API's requirements.