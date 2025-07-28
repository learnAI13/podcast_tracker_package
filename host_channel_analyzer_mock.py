# host_channel_analyzer_mock.py - Mock version for testing
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics
import re
from collections import Counter, defaultdict

class YouTubeHostAnalyzer:
    """Analyze host's YouTube channel performance and extract successful patterns"""
    
    def __init__(self, mixtral_url="http://localhost:8080"):
        self.mixtral_url = mixtral_url
    
    async def analyze_host_channel(self, channel_url: str) -> Dict[str, Any]:
        """Complete host channel analysis using mock data"""
        print(f"Analyzing host channel: {channel_url}")
        print("Using mock data for channel analysis")
        
        # Create mock videos data
        videos = [
            {
                "title": "AI and the Future of Technology with Dr. Smith",
                "video_id": "abc123",
                "view_count": 250000,
                "like_count": 15000,
                "comment_count": 2000,
                "duration": 5400,
                "upload_date": "20240601",
                "description": "Discussion about artificial intelligence and future technology trends",
                "tags": ["AI", "technology", "future"],
                "url": "https://youtube.com/watch?v=abc123"
            },
            {
                "title": "Building Successful Startups with Jane Doe",
                "video_id": "def456",
                "view_count": 180000,
                "like_count": 12000,
                "comment_count": 1500,
                "duration": 4800,
                "upload_date": "20240520",
                "description": "Entrepreneurship discussion with successful founder",
                "tags": ["startup", "entrepreneurship", "business"],
                "url": "https://youtube.com/watch?v=def456"
            },
            {
                "title": "The Science of Learning with Prof. Johnson",
                "video_id": "ghi789",
                "view_count": 200000,
                "like_count": 14000,
                "comment_count": 1800,
                "duration": 5100,
                "upload_date": "20240510",
                "description": "Discussion about cognitive science and learning techniques",
                "tags": ["science", "learning", "education"],
                "url": "https://youtube.com/watch?v=ghi789"
            }
        ]
        
        print(f"Mock data: {len(videos)} videos to analyze")
        
        # Create mock performance analysis
        performance_analysis = {
            'total_videos_analyzed': 3,
            'average_views': 210000,
            'median_views': 200000,
            'view_threshold_75th': 250000,
            'high_performers_count': 1,
            'average_engagement_rate': 8.5,
            'successful_title_patterns': {
                'common_title_starters': [
                    {'pattern': 'ai and', 'frequency': 1},
                    {'pattern': 'building successful', 'frequency': 1},
                    {'pattern': 'the science', 'frequency': 1}
                ],
                'frequent_keywords': [
                    {'keyword': 'technology', 'frequency': 1},
                    {'keyword': 'science', 'frequency': 1},
                    {'keyword': 'business', 'frequency': 1}
                ]
            },
            'content_themes': {
                'theme_distribution': {
                    'business_tech': 40.5,
                    'personal_development': 25.3,
                    'finance_investing': 10.2,
                    'health_wellness': 5.0,
                    'other': 19.0
                },
                'dominant_theme': 'business_tech',
                'total_theme_mentions': 35
            },
            'high_performing_videos': [
                {
                    'title': 'AI and the Future of Technology with Dr. Smith',
                    'views': 250000,
                    'engagement': 6.8
                }
            ],
            'performance_insights': [
                "Longer videos tend to perform better (90 min vs 75 min average)",
                "Technology and AI topics receive higher engagement",
                "Expert guests with strong credentials perform better"
            ]
        }
        
        # Create mock channel DNA
        channel_dna = {
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
        
        return {
            "channel_url": channel_url,
            "analysis_timestamp": datetime.now().isoformat(),
            "videos_analyzed": len(videos),
            "performance_metrics": performance_analysis,
            "channel_dna": channel_dna,
            "raw_video_data": videos
        }
    
    def call_llm_for_channel_analysis(self, performance_data: Dict[str, Any], channel_url: str) -> Dict[str, Any]:
        """Use LLM to analyze channel DNA and extract insights"""
        
        prompt = f"""<s>[INST] Analyze this YouTube podcast channel's performance data and extract the channel's DNA for guest selection.

CHANNEL URL: {channel_url}

PERFORMANCE DATA:
{json.dumps(performance_data, indent=2)}

Based on this data, determine:

1. What topics/themes work best for this channel?
2. What type of guests would be most successful?
3. What content angles drive engagement?
4. What are the audience preferences?

Respond with structured JSON:
{{
    "channel_dna": {{
        "primary_topics": ["topic1", "topic2", "topic3"],
        "audience_profile": "Description of target audience",
        "successful_content_types": ["type1", "type2"],
        "preferred_guest_types": ["guest type 1", "guest type 2"],
        "engagement_drivers": ["driver1", "driver2"],
        "content_style": "Description of successful content style"
    }},
    "guest_selection_criteria": {{
        "ideal_expertise_areas": ["area1", "area2"],
        "authority_level_required": "HIGH|MEDIUM|LOW",
        "personality_fit": "Description of personality that works",
        "topic_alignment_importance": 85,
        "audience_size_importance": 60
    }},
    "content_recommendations": {{
        "optimal_video_length": "X minutes",
        "best_title_patterns": ["pattern1", "pattern2"],
        "topics_to_focus_on": ["focus topic 1", "focus topic 2"],
        "topics_to_avoid": ["avoid topic 1"]
    }}
}}

Respond with ONLY valid JSON. [/INST]"""

        try:
            payload = {
                "prompt": prompt,
                "n_predict": 2500,
                "temperature": 0.2,
                "stop": ["</s>", "[/INST]"],
                "stream": False
            }
            
            response = requests.post(
                f"{self.mixtral_url}/completion",
                json=payload,
                timeout=120,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "").strip()
                
                # Extract JSON
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
            
            return self.create_fallback_channel_analysis(performance_data)
            
        except Exception as e:
            print(f"LLM channel analysis failed: {e}")
            return self.create_fallback_channel_analysis(performance_data)
    
    def create_fallback_channel_analysis(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic channel analysis when LLM fails"""
        
        themes = performance_data.get('content_themes', {})
        dominant_theme = themes.get('dominant_theme', 'general')
        
        return {
            "channel_dna": {
                "primary_topics": [dominant_theme, "general content"],
                "audience_profile": "Unable to determine - manual analysis needed",
                "successful_content_types": ["Manual analysis required"],
                "preferred_guest_types": ["Requires manual review"],
                "engagement_drivers": ["Check performance data manually"],
                "content_style": "Analyze manually from video data"
            },
            "guest_selection_criteria": {
                "ideal_expertise_areas": [dominant_theme],
                "authority_level_required": "MEDIUM",
                "personality_fit": "Manual assessment needed",
                "topic_alignment_importance": 70,
                "audience_size_importance": 50
            },
            "content_recommendations": {
                "optimal_video_length": "90 minutes",
                "best_title_patterns": ["Manual analysis needed"],
                "topics_to_focus_on": [dominant_theme],
                "topics_to_avoid": ["Manual analysis required"]
            }
        }