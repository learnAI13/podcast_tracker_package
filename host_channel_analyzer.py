# host_channel_analyzer.py
import os
import json
import requests
import yt_dlp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics
import re
from collections import Counter, defaultdict

class YouTubeHostAnalyzer:
    """Analyze host's YouTube channel performance and extract successful patterns"""
    
    def __init__(self, mixtral_url="http://localhost:8080"):
        self.mixtral_url = mixtral_url
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')  # Get from environment
        
    def extract_channel_id_from_url(self, channel_url: str) -> Optional[str]:
        """Extract channel ID from various YouTube URL formats"""
        try:
            # Handle different URL formats
            if 'youtube.com/channel/' in channel_url:
                return channel_url.split('/channel/')[1].split('/')[0].split('?')[0]
            elif 'youtube.com/c/' in channel_url or 'youtube.com/@' in channel_url:
                # Use yt-dlp to resolve channel ID
                ydl_opts = {'quiet': True, 'extract_flat': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(channel_url, download=False)
                    return info.get('channel_id')
            elif 'youtube.com/user/' in channel_url:
                # Legacy user URL - need to resolve to channel ID
                ydl_opts = {'quiet': True, 'extract_flat': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(channel_url, download=False)
                    return info.get('channel_id')
        except Exception as e:
            print(f"Failed to extract channel ID: {e}")
        return None
    
    def get_channel_videos_with_ytdlp(self, channel_url: str, max_videos: int = 50) -> List[Dict[str, Any]]:
        """Get recent videos using yt-dlp (no API key required)"""
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': False,
                'playlistend': max_videos,  # Limit number of videos
                'ignoreerrors': True,
                'writesubtitles': False,
                'writeautomaticsub': False
            }
            
            videos = []
            
            # Add /videos to get all channel videos
            if not channel_url.endswith('/videos'):
                if channel_url.endswith('/'):
                    channel_url += 'videos'
                else:
                    channel_url += '/videos'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(channel_url, download=False)
                    
                    if 'entries' in info:
                        for entry in info['entries'][:max_videos]:
                            if entry:
                                video_data = {
                                    'title': entry.get('title', ''),
                                    'video_id': entry.get('id', ''),
                                    'view_count': entry.get('view_count', 0),
                                    'like_count': entry.get('like_count', 0),
                                    'comment_count': entry.get('comment_count', 0),
                                    'duration': entry.get('duration', 0),
                                    'upload_date': entry.get('upload_date', ''),
                                    'description': entry.get('description', '')[:500] if entry.get('description') else '',
                                    'tags': entry.get('tags', [])[:10] if entry.get('tags') else [],
                                    'uploader': entry.get('uploader', ''),
                                    'thumbnail': entry.get('thumbnail', ''),
                                    'url': f"https://youtube.com/watch?v={entry.get('id', '')}"
                                }
                                videos.append(video_data)
                                
                except Exception as e:
                    print(f"Error extracting videos: {e}")
            
            return videos
            
        except Exception as e:
            print(f"Failed to get channel videos: {e}")
            return []
    
    def analyze_video_performance_patterns(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze what types of content perform well"""
        if not videos:
            return {}
        
        # Filter out videos with 0 views (probably errors)
        valid_videos = [v for v in videos if v.get('view_count', 0) > 0]
        
        if not valid_videos:
            return {}
        
        # Calculate performance metrics
        view_counts = [v['view_count'] for v in valid_videos]
        like_counts = [v.get('like_count', 0) for v in valid_videos]
        comment_counts = [v.get('comment_count', 0) for v in valid_videos]
        
        avg_views = statistics.mean(view_counts)
        median_views = statistics.median(view_counts)
        
        # Identify high-performing videos (above 75th percentile)
        view_threshold = statistics.quantiles(view_counts, n=4)[2]  # 75th percentile
        high_performers = [v for v in valid_videos if v['view_count'] >= view_threshold]
        
        # Analyze titles of high performers
        high_performer_titles = [v['title'] for v in high_performers]
        
        # Extract common title patterns
        title_patterns = self.extract_title_patterns(high_performer_titles)
        
        # Analyze topics/themes
        all_titles = [v['title'] for v in valid_videos]
        topic_analysis = self.analyze_content_themes(all_titles)
        
        # Calculate engagement rates
        engagement_rates = []
        for video in valid_videos:
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)
            
            if views > 0:
                engagement_rate = ((likes + comments * 2) / views) * 100  # Weight comments more
                engagement_rates.append(engagement_rate)
        
        avg_engagement = statistics.mean(engagement_rates) if engagement_rates else 0
        
        return {
            'total_videos_analyzed': len(valid_videos),
            'average_views': int(avg_views),
            'median_views': int(median_views),
            'view_threshold_75th': int(view_threshold),
            'high_performers_count': len(high_performers),
            'average_engagement_rate': round(avg_engagement, 3),
            'successful_title_patterns': title_patterns,
            'content_themes': topic_analysis,
            'high_performing_videos': [
                {
                    'title': v['title'],
                    'views': v['view_count'],
                    'engagement': ((v.get('like_count', 0) + v.get('comment_count', 0) * 2) / v['view_count'] * 100) if v['view_count'] > 0 else 0
                } for v in high_performers[:10]
            ],
            'performance_insights': self.generate_performance_insights(valid_videos, high_performers)
        }
    
    def extract_title_patterns(self, titles: List[str]) -> List[Dict[str, Any]]:
        """Extract common patterns from successful video titles"""
        patterns = []
        
        # Common podcast title patterns
        title_starters = defaultdict(int)
        title_keywords = defaultdict(int)
        
        for title in titles:
            # Extract first few words
            words = title.lower().split()
            if len(words) >= 2:
                starter = ' '.join(words[:2])
                title_starters[starter] += 1
            
            # Extract keywords (words longer than 3 chars, not common words)
            common_words = {'the', 'and', 'with', 'from', 'this', 'that', 'have', 'will', 'they', 'been', 'have', 'their', 'said', 'each', 'which', 'more', 'very', 'what', 'know', 'just', 'first', 'time', 'over', 'think', 'also', 'back', 'after', 'come', 'most', 'where'}
            
            for word in words:
                word = re.sub(r'[^\w]', '', word.lower())
                if len(word) > 3 and word not in common_words:
                    title_keywords[word] += 1
        
        # Get top patterns
        top_starters = sorted(title_starters.items(), key=lambda x: x[1], reverse=True)[:5]
        top_keywords = sorted(title_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        patterns = {
            'common_title_starters': [{'pattern': k, 'frequency': v} for k, v in top_starters],
            'frequent_keywords': [{'keyword': k, 'frequency': v} for k, v in top_keywords]
        }
        
        return patterns
    
    def analyze_content_themes(self, titles: List[str]) -> Dict[str, Any]:
        """Analyze content themes using keyword clustering"""
        
        # Business/Tech themes
        business_keywords = ['business', 'startup', 'entrepreneur', 'ceo', 'founder', 'company', 'tech', 'technology', 'ai', 'marketing', 'sales', 'strategy']
        
        # Personal development themes  
        personal_keywords = ['success', 'mindset', 'motivation', 'life', 'career', 'growth', 'habits', 'productivity', 'leadership']
        
        # Industry-specific themes
        finance_keywords = ['money', 'invest', 'crypto', 'finance', 'wealth', 'bitcoin', 'stock', 'trading']
        health_keywords = ['health', 'fitness', 'wellness', 'mental', 'meditation', 'diet']
        
        theme_counts = {
            'business_tech': 0,
            'personal_development': 0,
            'finance_investing': 0,
            'health_wellness': 0,
            'other': 0
        }
        
        all_text = ' '.join(titles).lower()
        
        # Count theme occurrences
        for keyword in business_keywords:
            theme_counts['business_tech'] += all_text.count(keyword)
            
        for keyword in personal_keywords:
            theme_counts['personal_development'] += all_text.count(keyword)
            
        for keyword in finance_keywords:
            theme_counts['finance_investing'] += all_text.count(keyword)
            
        for keyword in health_keywords:
            theme_counts['health_wellness'] += all_text.count(keyword)
        
        # Normalize and get percentages
        total_mentions = sum(theme_counts.values())
        if total_mentions > 0:
            theme_percentages = {k: round((v/total_mentions)*100, 1) for k, v in theme_counts.items()}
        else:
            theme_percentages = theme_counts
        
        return {
            'theme_distribution': theme_percentages,
            'dominant_theme': max(theme_percentages.items(), key=lambda x: x[1])[0],
            'total_theme_mentions': total_mentions
        }
    
    def generate_performance_insights(self, all_videos: List[Dict], high_performers: List[Dict]) -> List[str]:
        """Generate actionable insights about what works"""
        insights = []
        
        if not high_performers:
            return ["Not enough data to generate insights"]
        
        # Title length analysis
        high_perf_titles = [len(v['title']) for v in high_performers]
        all_titles = [len(v['title']) for v in all_videos]
        
        avg_high_perf = statistics.mean(high_perf_titles)
        avg_all = statistics.mean(all_titles)
        
        if avg_high_perf > avg_all + 5:
            insights.append(f"Longer titles perform better (high performers avg: {int(avg_high_perf)} chars vs overall: {int(avg_all)} chars)")
        elif avg_high_perf < avg_all - 5:
            insights.append(f"Shorter titles perform better (high performers avg: {int(avg_high_perf)} chars vs overall: {int(avg_all)} chars)")
        
        # Upload timing (if data available)
        high_perf_dates = [v.get('upload_date', '') for v in high_performers if v.get('upload_date')]
        if high_perf_dates:
            # Extract days of week if possible
            insights.append("Upload timing data available for further analysis")
        
        # Duration analysis
        high_perf_durations = [v.get('duration', 0) for v in high_performers if v.get('duration', 0) > 0]
        all_durations = [v.get('duration', 0) for v in all_videos if v.get('duration', 0) > 0]
        
        if high_perf_durations and all_durations:
            avg_high_dur = statistics.mean(high_perf_durations)
            avg_all_dur = statistics.mean(all_durations)
            
            if avg_high_dur > avg_all_dur + 300:  # 5 minutes difference
                insights.append(f"Longer videos tend to perform better ({int(avg_high_dur/60)} min vs {int(avg_all_dur/60)} min average)")
            elif avg_high_dur < avg_all_dur - 300:
                insights.append(f"Shorter videos tend to perform better ({int(avg_high_dur/60)} min vs {int(avg_all_dur/60)} min average)")
        
        return insights
    
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
                "optimal_video_length": f"{performance_data.get('avg_duration', 1800) // 60} minutes",
                "best_title_patterns": ["Manual analysis needed"],
                "topics_to_focus_on": [dominant_theme],
                "topics_to_avoid": ["Manual analysis required"]
            }
        }
    
    async def analyze_host_channel(self, channel_url: str) -> Dict[str, Any]:
        """Complete host channel analysis"""
        print(f"Analyzing host channel: {channel_url}")
        
        try:
            # For testing purposes, use mock data instead of scraping
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
            
            # Analyze performance patterns
            performance_analysis = self.analyze_video_performance_patterns(videos)
            
            # Get LLM insights
            channel_dna = self.call_llm_for_channel_analysis(performance_analysis, channel_url)
            
            return {
                "channel_url": channel_url,
                "analysis_timestamp": datetime.now().isoformat(),
                "videos_analyzed": len(videos),
                "performance_metrics": performance_analysis,
                "channel_dna": channel_dna,
                "raw_video_data": videos  # Include sample of raw data
            }
            
        except Exception as e:
            print(f"Host channel analysis failed: {e}")
            return {"error": str(e)}

# Test function
async def test_host_analyzer():
    analyzer = YouTubeHostAnalyzer()
    result = await analyzer.analyze_host_channel("https://youtube.com/@lexfridman")
    print(json.dumps(result, indent=2))