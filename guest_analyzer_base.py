# guest_analyzer_base.py - Base Guest Analysis System

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import re
import json
from datetime import datetime
from urllib.parse import urlparse, urljoin
import time

class PremiumGuestAnalyzer:
    """Enhanced guest analyzer with comprehensive social media and web analysis"""
    
    def __init__(self, mixtral_url="http://localhost:11434"):
        self.mixtral_url = mixtral_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def extract_enhanced_person_name(self, url: str) -> str:
        """Extract person name from various URL formats"""
        try:
            # Twitter URL patterns
            if 'twitter.com' in url or 'x.com' in url:
                match = re.search(r'(?:twitter\.com/|x\.com/)([^/?]+)', url)
                if match:
                    username = match.group(1)
                    return username.replace('_', ' ').title()
            
            # LinkedIn URL patterns
            elif 'linkedin.com' in url:
                match = re.search(r'linkedin\.com/in/([^/?]+)', url)
                if match:
                    name_slug = match.group(1)
                    return name_slug.replace('-', ' ').title()
            
            # YouTube patterns
            elif 'youtube.com' in url:
                match = re.search(r'youtube\.com/(@[^/?]+|c/[^/?]+|channel/[^/?]+)', url)
                if match:
                    channel_name = match.group(1).replace('@', '').replace('c/', '')
                    return channel_name.replace('-', ' ').title()
            
            # Generic extraction from URL path
            else:
                parsed = urlparse(url)
                path_parts = parsed.path.strip('/').split('/')
                if path_parts:
                    return path_parts[-1].replace('-', ' ').replace('_', ' ').title()
                    
        except Exception as e:
            print(f"Name extraction failed: {e}")
        
        return "Unknown Person"
    
    async def scrape_twitter_profile(self, url: str) -> Dict[str, Any]:
        """Scrape Twitter profile (basic version without API)"""
        try:
            # Use requests for basic scraping (Twitter limits this)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract basic info from meta tags
                title = soup.find('title')
                description = soup.find('meta', {'name': 'description'})
                
                return {
                    'platform': 'twitter',
                    'url': url,
                    'title': title.text if title else '',
                    'bio': description.get('content', '') if description else '',
                    'content_snippet': 'Twitter scraping limited - consider API integration',
                    'followers': 'unknown',
                    'following': 'unknown',
                    'recent_tweets': ['Twitter API required for tweets']
                }
        except Exception as e:
            print(f"Twitter scraping failed: {e}")
        
        return {
            'platform': 'twitter',
            'url': url,
            'error': 'Scraping failed - Twitter limits access',
            'bio': 'Manual verification required',
            'content_snippet': 'Unable to extract content'
        }
    
    async def scrape_linkedin_profile(self, url: str) -> Dict[str, Any]:
        """Scrape LinkedIn profile (basic version)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract basic info
                title = soup.find('title')
                
                return {
                    'platform': 'linkedin',
                    'url': url,
                    'title': title.text if title else '',
                    'bio': 'LinkedIn requires authentication for full access',
                    'content_snippet': 'Professional profile detected',
                    'connections': 'unknown',
                    'current_position': 'Manual extraction needed'
                }
        except Exception as e:
            print(f"LinkedIn scraping failed: {e}")
        
        return {
            'platform': 'linkedin',
            'url': url,
            'error': 'LinkedIn blocks automated access',
            'bio': 'Manual verification required'
        }
    
    async def scrape_youtube_profile(self, url: str) -> Dict[str, Any]:
        """Scrape YouTube channel/profile"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract channel info
                title = soup.find('title')
                description = soup.find('meta', {'name': 'description'})
                
                # Try to find subscriber count in page content
                page_text = soup.get_text().lower()
                subscriber_match = re.search(r'(\d+(?:\.\d+)?[km]?)\s*subscribers?', page_text)
                
                return {
                    'platform': 'youtube',
                    'url': url,
                    'title': title.text if title else '',
                    'bio': description.get('content', '') if description else '',
                    'content_snippet': 'YouTube channel detected',
                    'subscribers': subscriber_match.group(1) if subscriber_match else 'unknown',
                    'recent_videos': ['Use yt-dlp for detailed video analysis']
                }
        except Exception as e:
            print(f"YouTube scraping failed: {e}")
        
        return {
            'platform': 'youtube',
            'url': url,
            'error': 'YouTube scraping failed',
            'bio': 'Manual verification required'
        }
    
    async def web_search_person(self, person_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform web search for person information"""
        # This is a simplified version - you might want to integrate with proper search APIs
        search_results = []
        
        try:
            # Use DuckDuckGo search (no API key required)
            search_query = f"{person_name} bio background"
            search_url = f"https://duckduckgo.com/html/?q={search_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract search results
                results = soup.find_all('div', class_='result')[:max_results]
                
                for result in results:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and snippet_elem:
                        search_results.append({
                            'title': title_elem.get_text().strip(),
                            'url': title_elem.get('href', ''),
                            'content': snippet_elem.get_text().strip()
                        })
            
        except Exception as e:
            print(f"Web search failed: {e}")
            search_results = [{
                'title': f'Search for {person_name}',
                'content': 'Web search failed - manual research required',
                'url': 'manual_research_needed'
            }]
        
        return search_results
    
    async def comprehensive_person_analysis(self, person_name: str, primary_url: str) -> Dict[str, Any]:
        """Comprehensive analysis combining all data sources"""
        
        print(f"🔍 Analyzing: {person_name}")
        print(f"🔗 Primary URL: {primary_url}")
        
        analysis_data = {
            'person_name': person_name,
            'primary_url': primary_url,
            'profiles': [],
            'search_results': [],
            'data_sources': [],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Scrape primary profile
        domain = urlparse(primary_url).netloc.lower()
        
        if 'twitter.com' in domain or 'x.com' in domain:
            print("📱 Scraping Twitter profile...")
            twitter_data = await self.scrape_twitter_profile(primary_url)
            analysis_data['profiles'].append(twitter_data)
            analysis_data['data_sources'].append('twitter')
            
        elif 'linkedin.com' in domain:
            print("💼 Scraping LinkedIn profile...")
            linkedin_data = await self.scrape_linkedin_profile(primary_url)
            analysis_data['profiles'].append(linkedin_data)
            analysis_data['data_sources'].append('linkedin')
            
        elif 'youtube.com' in domain:
            print("📺 Scraping YouTube channel...")
            youtube_data = await self.scrape_youtube_profile(primary_url)
            analysis_data['profiles'].append(youtube_data)
            analysis_data['data_sources'].append('youtube')
        
        else:
            print("🌐 Scraping generic web profile...")
            # Generic web scraping
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(primary_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.find('title')
                    description = soup.find('meta', {'name': 'description'})
                    
                    analysis_data['profiles'].append({
                        'platform': 'web',
                        'url': primary_url,
                        'title': title.text if title else '',
                        'bio': description.get('content', '') if description else '',
                        'content_snippet': soup.get_text()[:500] if soup else ''
                    })
                    analysis_data['data_sources'].append('web')
            except Exception as e:
                print(f"Generic web scraping failed: {e}")
        
        # Perform web search
        print("🔍 Performing web search...")
        search_results = await self.web_search_person(person_name, max_results=5)
        analysis_data['search_results'] = search_results
        analysis_data['data_sources'].append('web_search')
        
        # Calculate data quality scores
        analysis_data['overall_quality_score'] = self.calculate_data_quality(analysis_data)
        analysis_data['confidence_score'] = self.calculate_confidence_score(analysis_data)
        
        print(f"✅ Analysis complete. Quality: {analysis_data['overall_quality_score']}/100")
        
        return analysis_data
    
    def calculate_data_quality(self, analysis_data: Dict[str, Any]) -> int:
        """Calculate data quality score"""
        score = 0
        
        # Profile data quality
        for profile in analysis_data.get('profiles', []):
            if profile.get('bio') and 'manual' not in profile['bio'].lower():
                score += 30
            if profile.get('content_snippet') and len(profile['content_snippet']) > 50:
                score += 20
        
        # Search results quality
        search_results = analysis_data.get('search_results', [])
        if search_results and len(search_results) > 0:
            score += 25
        
        # Data source diversity
        sources = analysis_data.get('data_sources', [])
        score += len(set(sources)) * 5
        
        return min(score, 100)
    
    def calculate_confidence_score(self, analysis_data: Dict[str, Any]) -> int:
        """Calculate confidence in the analysis"""
        confidence = 0
        
        profiles = analysis_data.get('profiles', [])
        if profiles:
            valid_profiles = [p for p in profiles if 'error' not in p]
            confidence += len(valid_profiles) * 20
        
        search_results = analysis_data.get('search_results', [])
        if search_results and not any('manual' in str(r).lower() for r in search_results):
            confidence += 30
        
        return min(confidence, 100)
        
    async def extract_structured_guest_profile(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured guest profile using Ollama LLaMA"""
        from ollama_client import ollama_client
        
        # Prepare the raw data for analysis
        raw_data = json.dumps(social_data, indent=2)
        
        prompt = f"""
        Analyze the following data about a potential podcast guest and extract structured information.
        
        Raw Data:
        {raw_data}
        
        Please provide a structured analysis in the following format:
        
        NAME: [Full name]
        DESIGNATION: [Job title/role]
        COMPANY: [Current company/organization]
        EXPERTISE: [Main areas of expertise, comma-separated]
        PREVIOUS_PODCASTS: [List any podcast appearances mentioned]
        SOCIAL_MEDIA_FOLLOWERS: [Approximate follower count if mentioned]
        AUTHORITY_SCORE: [Rate 1-10 based on credentials and influence]
        KEY_TOPICS: [Main topics they discuss, comma-separated]
        NOTABLE_ACHIEVEMENTS: [Key accomplishments mentioned]
        
        Be concise and extract only factual information from the provided data.
        """
        
        try:
            # Use 8B model for initial extraction (faster)
            response = ollama_client.generate_with_8b(prompt, max_tokens=800, temperature=0.3)
            extracted_text = response.get("generated_text", "")
            
            # Parse the structured response
            profile = {}
            for line in extracted_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    if value and value != '[' and value != 'N/A':
                        profile[key] = value
            
            # Add metadata
            profile["extraction_metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "data_quality_score": social_data.get("overall_quality_score", 0),
                "confidence_score": social_data.get("confidence_score", 0),
                "sources_used": social_data.get("data_sources", [])
            }
            
            return profile
            
        except Exception as e:
            print(f"Error extracting guest profile: {str(e)}")
            return {
                "name": social_data.get('person_name', 'Unknown'),
                "designation": "Unknown", 
                "company": "Unknown",
                "expertise": "Unknown",
                "authority_score": "5",
                "extraction_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "data_quality_score": social_data.get("overall_quality_score", 0),
                    "confidence_score": social_data.get("confidence_score", 0),
                    "sources_used": social_data.get("data_sources", []),
                    "error": str(e)
                }
            }

# Function for backwards compatibility
async def analyze_guest_premium(guest_name: str, guest_url: str) -> Dict[str, Any]:
    """Backwards compatible function"""
    async with PremiumGuestAnalyzer() as analyzer:
        return await analyzer.comprehensive_person_analysis(guest_name, guest_url)
