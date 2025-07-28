#!/usr/bin/env python3
# Mock LLM Server for testing the Podcast Guest Tracker

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
import random
from typing import Dict, List, Any, Optional

app = FastAPI(title="Mock LLaMA API Server")

class CompletionRequest(BaseModel):
    prompt: str
    n_predict: int = 128
    temperature: float = 0.8
    stop: List[str] = []
    stream: bool = False
    top_p: Optional[float] = None

class CompletionResponse(BaseModel):
    content: str
    model: str = "mock-llama-3.1"
    
@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "mock-llama-3.1"}

@app.post("/completion")
async def completion(request: CompletionRequest):
    # Extract the prompt
    prompt = request.prompt
    
    # Generate a mock response based on the prompt content
    if "guest profile extraction" in prompt.lower() or "Extract structured information" in prompt:
        # Return a mock guest profile
        response = generate_mock_guest_profile()
    elif "podcast channel" in prompt.lower() and "performance data" in prompt.lower():
        # Return a mock channel analysis
        response = generate_mock_channel_analysis()
    elif "validate" in prompt.lower() and "relevance score" in prompt.lower():
        # Return a mock validation
        response = generate_mock_validation()
    else:
        # Generic response
        response = "This is a mock response from the LLaMA 3.1 model. In a real environment, this would be an actual model-generated response."
    
    return CompletionResponse(content=response)

def generate_mock_guest_profile():
    """Generate a mock guest profile JSON"""
    profile = {
        "name": "John Smith",
        "current_designation": "CEO",
        "company": "Tech Innovations Inc.",
        "industry": "Technology",
        "expertise_areas": ["Artificial Intelligence", "Entrepreneurship", "Product Development"],
        "previous_podcasts": ["Tech Talk", "Founder Stories"],
        "social_following": {
            "twitter": "45K",
            "linkedin": "500+",
            "youtube": "10K"
        },
        "authority_indicators": ["Founded 3 successful startups", "Published author", "Industry speaker"],
        "key_topics": ["AI Ethics", "Startup Growth", "Technology Trends"],
        "recent_activities": ["Launched new AI product", "Spoke at Tech Conference"],
        "credibility_score": 85,
        "popularity_indicators": ["Regular media appearances", "Growing social following"],
        "potential_interview_topics": ["Future of AI", "Building Tech Companies", "Innovation Strategy"],
        "bio_summary": "John Smith is a technology entrepreneur and AI expert with over 15 years of experience building innovative products. He currently leads Tech Innovations Inc., focusing on ethical AI solutions."
    }
    return json.dumps(profile, indent=2)

def generate_mock_channel_analysis():
    """Generate a mock channel analysis JSON"""
    analysis = {
        "channel_dna": {
            "primary_topics": ["Technology", "Entrepreneurship", "Science"],
            "audience_profile": "Tech-savvy professionals and entrepreneurs interested in innovation and cutting-edge ideas",
            "successful_content_types": ["Long-form interviews", "Deep technical discussions"],
            "preferred_guest_types": ["Industry experts", "Successful entrepreneurs", "Academic researchers"],
            "engagement_drivers": ["Technical depth", "Practical insights", "Thought leadership"],
            "content_style": "In-depth, thoughtful conversations exploring complex topics with a focus on practical applications"
        },
        "guest_selection_criteria": {
            "ideal_expertise_areas": ["Technology", "Business", "Science"],
            "authority_level_required": "HIGH",
            "personality_fit": "Articulate, thoughtful speakers who can explain complex topics clearly",
            "topic_alignment_importance": 85,
            "audience_size_importance": 60
        },
        "content_recommendations": {
            "optimal_video_length": "90-120 minutes",
            "best_title_patterns": ["Guest Name | Topic, Topic", "Topic Discussion with Guest Name"],
            "topics_to_focus_on": ["AI and machine learning", "Entrepreneurship", "Future technology trends"],
            "topics_to_avoid": ["Highly political content"]
        }
    }
    return json.dumps(analysis, indent=2)

def generate_mock_validation():
    """Generate a mock validation response"""
    validations = [
        "This guest scored 82/100, resulting in a RECOMMENDED rating. Their expertise in technology and entrepreneurship aligns well with the channel's focus, and their strong authority indicators suggest they would provide valuable insights for the audience.",
        
        "With a score of 75/100, this guest falls into the RECOMMENDED category. Their background in AI and business innovation matches the channel's content themes, though their moderate social following might limit audience expansion.",
        
        "This guest received a score of 65/100, placing them in the CONSIDER category. While they have relevant expertise in technology, their limited previous podcast experience and niche focus may not resonate with the broader channel audience.",
        
        "The guest scored 45/100, resulting in a LOW_PRIORITY rating. Despite some relevant expertise, their limited authority in the field and minimal social presence suggest they may not be the best fit for this channel at this time."
    ]
    return random.choice(validations)

if __name__ == "__main__":
    print("Starting Mock LLaMA API Server on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)