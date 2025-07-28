#!/usr/bin/env python3
# web_app.py - Web interface for the 1-Click Podcast Guest Tracker with Ollama integration

import asyncio
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import traceback
from datetime import datetime

# Import our modules
from guest_analyzer_base import PremiumGuestAnalyzer
from host_channel_analyzer_mock import MockHostChannelAnalyzer
from relevance_scoring_engine import GuestRelevanceScorer
from ollama_client import ollama_client

# Create FastAPI app
app = FastAPI(title="1-Click Podcast Guest Tracker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create templates
templates = Jinja2Templates(directory="templates")

# Create the HTML template (same as before)
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>1-Click Podcast Guest Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .score {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .recommendation {
            font-size: 20px;
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 4px;
        }
        .HIGHLY_RECOMMENDED {
            background-color: #d4edda;
            color: #155724;
        }
        .RECOMMENDED {
            background-color: #dff0d8;
            color: #3c763d;
        }
        .CONSIDER {
            background-color: #fcf8e3;
            color: #8a6d3b;
        }
        .LOW_PRIORITY {
            background-color: #f8d7da;
            color: #721c24;
        }
        .NOT_RECOMMENDED {
            background-color: #f2dede;
            color: #a94442;
        }
        .explanation {
            margin-top: 20px;
        }
        .explanation h3 {
            margin-bottom: 10px;
        }
        .explanation ul {
            margin-top: 0;
        }
        .loading {
            text-align: center;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 2s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .score-breakdown {
            margin-top: 20px;
        }
        .score-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 5px;
            background-color: #f8f9fa;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>🎙️ 1-Click Podcast Guest Tracker</h1>
    <p style="text-align: center; color: #666;">Powered by LLaMA 3.1 70B & 8B Models</p>
    
    <form id="analyzeForm" action="/analyze" method="post">
        <div class="form-group">
            <label for="guest_name">Guest Name:</label>
            <input type="text" id="guest_name" name="guest_name" required placeholder="e.g., Elon Musk">
        </div>
        
        <div class="form-group">
            <label for="guest_url">Guest URL (Twitter, LinkedIn, YouTube, etc.):</label>
            <input type="text" id="guest_url" name="guest_url" required placeholder="e.g., https://twitter.com/elonmusk">
        </div>
        
        <div class="form-group">
            <label for="host_channel">Host YouTube Channel (optional):</label>
            <input type="text" id="host_channel" name="host_channel" placeholder="e.g., https://youtube.com/@lexfridman">
        </div>
        
        <button type="submit">🔍 Analyze Guest</button>
    </form>
    
    <div id="loading" class="loading">
        <p>🤖 Analyzing guest with LLaMA models... This may take 1-2 minutes.</p>
        <div class="spinner"></div>
        <p><small>Loading models and processing social media data...</small></p>
    </div>
    
    <div id="error" class="error" style="display: none;">
        <h3>❌ Error</h3>
        <p id="error_message"></p>
    </div>
    
    <div id="results" class="results" style="display: none;">
        <div id="score" class="score"></div>
        <div id="recommendation" class="recommendation"></div>
        
        <div class="score-breakdown">
            <h3>📊 Score Breakdown:</h3>
            <div id="score_details"></div>
        </div>
        
        <div class="explanation">
            <h3>💡 Key Strengths:</h3>
            <ul id="strengths"></ul>
            
            <h3>⚠️ Areas of Concern:</h3>
            <ul id="concerns"></ul>
        </div>
        
        <div class="guest-profile">
            <h3>👤 Guest Profile:</h3>
            <div id="guest_profile_summary"></div>
        </div>
        
        <div class="llm-validation">
            <h3>🧠 AI Analysis:</h3>
            <p id="llm_explanation"></p>
        </div>
    </div>
    
    <script>
        document.getElementById('analyzeForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading spinner
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            
            // Get form data
            const formData = new FormData(this);
            
            // Send request with longer timeout
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Hide loading spinner
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    // Show error
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error_message').textContent = data.error;
                    return;
                }
                
                // Show results
                document.getElementById('results').style.display = 'block';
                
                // Update score and recommendation
                document.getElementById('score').textContent = `Overall Score: ${data.overall_relevance_score}/100`;
                
                const recElem = document.getElementById('recommendation');
                recElem.textContent = `Recommendation: ${data.recommendation}`;
                recElem.className = `recommendation ${data.recommendation}`;
                
                // Update score breakdown
                const scoreDetails = document.getElementById('score_details');
                scoreDetails.innerHTML = '';
                if (data.score_breakdown) {
                    Object.entries(data.score_breakdown).forEach(([key, value]) => {
                        const div = document.createElement('div');
                        div.className = 'score-item';
                        div.innerHTML = `<span>${key.replace('_', ' ').toUpperCase()}</span><span>${value.score}/100 (${Math.round(value.weight * 100)}%)</span>`;
                        scoreDetails.appendChild(div);
                    });
                }
                
                // Update strengths
                const strengthsList = document.getElementById('strengths');
                strengthsList.innerHTML = '';
                (data.key_strengths || []).forEach(strength => {
                    const li = document.createElement('li');
                    li.textContent = strength;
                    strengthsList.appendChild(li);
                });
                
                // Update concerns
                const concernsList = document.getElementById('concerns');
                concernsList.innerHTML = '';
                (data.areas_of_concern || []).forEach(concern => {
                    const li = document.createElement('li');
                    li.textContent = concern;
                    concernsList.appendChild(li);
                });
                
                // Update guest profile summary
                const profileSummary = document.getElementById('guest_profile_summary');
                if (data.guest_profile) {
                    profileSummary.innerHTML = `
                        <p><strong>Name:</strong> ${data.guest_profile.name || 'Unknown'}</p>
                        <p><strong>Company:</strong> ${data.guest_profile.company || 'Unknown'}</p>
                        <p><strong>Expertise:</strong> ${data.guest_profile.expertise || 'Unknown'}</p>
                        <p><strong>Authority Score:</strong> ${data.guest_profile.authority_score || 'Unknown'}/10</p>
                    `;
                }
                
                // Update LLM explanation
                document.getElementById('llm_explanation').textContent = 
                    data.llm_validation || 'AI analysis not available';
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error_message').textContent = 
                    `Analysis failed: ${error.message}. Please check that Ollama is running and try again.`;
            });
        });
    </script>
</body>
</html>
    """)

class PodcastGuestTracker:
    """Main tracker class that coordinates all components"""
    
    def __init__(self):
        self.guest_analyzer = None
        self.host_analyzer = MockHostChannelAnalyzer()
        self.relevance_scorer = GuestRelevanceScorer()
    
    async def analyze_podcast_guest_complete(self, guest_name: str, guest_url: str, host_channel_url: str = None):
        """Complete analysis of a podcast guest"""
        try:
            print(f"🔍 Starting analysis for {guest_name}")
            
            # Test Ollama connection first
            if not ollama_client.test_connection():
                return {
                    "error": "Cannot connect to Ollama. Please ensure 'ollama serve' is running.",
                    "guest_name": guest_name
                }
            
            # Step 1: Analyze guest
            print("📱 Analyzing guest social media...")
            async with PremiumGuestAnalyzer() as analyzer:
                guest_data = await analyzer.comprehensive_person_analysis(guest_name, guest_url)
                guest_profile = await analyzer.extract_structured_guest_profile(guest_data)
            
            print(f"✅ Guest analysis complete. Quality: {guest_data.get('overall_quality_score', 0)}/100")
            
            # Step 2: Analyze host channel (mock for now)
            print("📺 Analyzing host channel...")
            if host_channel_url:
                host_analysis = self.host_analyzer.analyze_channel_mock(host_channel_url)
            else:
                host_analysis = self.host_analyzer.get_default_analysis()
            
            print("✅ Host analysis complete")
            
            # Step 3: Calculate relevance score
            print("🧮 Calculating relevance scores...")
            relevance_analysis = self.relevance_scorer.calculate_overall_relevance_score(
                guest_profile, host_analysis
            )
            
            print(f"✅ Relevance analysis complete. Score: {relevance_analysis['overall_relevance_score']}/100")
            
            # Step 4: Get LLM validation
            print("🤖 Getting AI validation...")
            try:
                llm_validation = self.relevance_scorer.call_llm_for_scoring_validation(
                    relevance_analysis, guest_profile, host_analysis
                )
            except Exception as e:
                print(f"⚠️ LLM validation failed: {str(e)}")
                llm_validation = f"AI validation unavailable: {str(e)}"
            
            print("✅ Analysis complete!")
            
            # Combine all results
            result = {
                **relevance_analysis,
                "guest_profile": guest_profile,
                "host_analysis_summary": {
                    "channel_name": host_analysis.get("channel_name", "Mock Channel"),
                    "videos_analyzed": host_analysis.get("videos_analyzed", 50),
                    "primary_topics": host_analysis.get("channel_dna", {}).get("channel_dna", {}).get("primary_topics", [])
                },
                "llm_validation": llm_validation,
                "analysis_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "guest_data_quality": guest_data.get('overall_quality_score', 0),
                    "confidence_level": guest_data.get('confidence_score', 0)
                }
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            print(traceback.format_exc())
            return {
                "error": f"Analysis failed: {str(e)}",
                "guest_name": guest_name,
                "details": traceback.format_exc()
            }

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_guest(
    guest_name: str = Form(...),
    guest_url: str = Form(...),
    host_channel: str = Form("")
):
    """Analyze a podcast guest"""
    tracker = PodcastGuestTracker()
    
    result = await tracker.analyze_podcast_guest_complete(
        guest_name=guest_name,
        guest_url=guest_url,
        host_channel_url=host_channel if host_channel else None
    )
    
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = ollama_client.test_connection()
    return {
        "status": "healthy" if ollama_status else "unhealthy",
        "ollama_connected": ollama_status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting 1-Click Podcast Guest Tracker...")
    print("🔗 Web interface will be available at: http://localhost:12000")
    print("🤖 Make sure Ollama is running: ollama serve")
    uvicorn.run(app, host="0.0.0.0", port=12000)
