# relevance_scoring_engine.py
import json
import requests
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class GuestRelevanceScorer:
    """Calculate relevance score between guest and host channel"""
    
    def __init__(self, mixtral_url="http://localhost:11434"):
        self.mixtral_url = mixtral_url
        
        # Default scoring weights (can be adjusted)
        self.weights = {
            'topic_alignment': 0.35,
            'authority_score': 0.25,
            'audience_appeal': 0.20,
            'uniqueness_factor': 0.10,
            'engagement_potential': 0.10
        }
    
    def calculate_overall_relevance_score(self, 
                                        guest_profile: Dict[str, Any], 
                                        host_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall relevance score and recommendation"""
        
        # Extract key data
        guest_name = guest_profile.get('name', 'Unknown Guest')
        
        # Calculate individual scores
        topic_alignment = self.calculate_topic_alignment(guest_profile, host_analysis)
        authority_score = self.calculate_authority_score(guest_profile, host_analysis)
        audience_appeal = self.calculate_audience_appeal(guest_profile, host_analysis)
        uniqueness_factor = self.calculate_uniqueness_factor(guest_profile, host_analysis)
        engagement_potential = self.calculate_engagement_potential(guest_profile, host_analysis)
        
        # Calculate weighted score
        overall_score = (
            topic_alignment * self.weights['topic_alignment'] +
            authority_score * self.weights['authority_score'] +
            audience_appeal * self.weights['audience_appeal'] +
            uniqueness_factor * self.weights['uniqueness_factor'] +
            engagement_potential * self.weights['engagement_potential']
        ) * 100
        
        # Round to integer
        overall_score = round(overall_score)
        
        # Determine recommendation
        recommendation = self.determine_recommendation(overall_score)
        
        # Identify key strengths and concerns
        key_strengths = self.identify_key_strengths({
            'topic_alignment': topic_alignment,
            'authority_score': authority_score,
            'audience_appeal': audience_appeal,
            'uniqueness_factor': uniqueness_factor,
            'engagement_potential': engagement_potential
        })
        
        areas_of_concern = self.identify_areas_of_concern({
            'topic_alignment': topic_alignment,
            'authority_score': authority_score,
            'audience_appeal': audience_appeal,
            'uniqueness_factor': uniqueness_factor,
            'engagement_potential': engagement_potential
        })
        
        # Generate interview recommendations
        interview_recommendations = self.generate_interview_recommendations(
            guest_profile, host_analysis, overall_score
        )
        
        # Determine confidence level
        confidence_level = self.determine_confidence_level(guest_profile, host_analysis)
        
        # Compile results
        return {
            'guest_name': guest_name,
            'overall_relevance_score': overall_score,
            'recommendation': recommendation,
            'confidence_level': confidence_level,
            'score_breakdown': {
                'topic_alignment': {
                    'score': round(topic_alignment * 100),
                    'weight': self.weights['topic_alignment']
                },
                'authority_score': {
                    'score': round(authority_score * 100),
                    'weight': self.weights['authority_score']
                },
                'audience_appeal': {
                    'score': round(audience_appeal * 100),
                    'weight': self.weights['audience_appeal']
                },
                'uniqueness_factor': {
                    'score': round(uniqueness_factor * 100),
                    'weight': self.weights['uniqueness_factor']
                },
                'engagement_potential': {
                    'score': round(engagement_potential * 100),
                    'weight': self.weights['engagement_potential']
                }
            },
            'key_strengths': key_strengths,
            'areas_of_concern': areas_of_concern,
            'interview_recommendations': interview_recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def calculate_topic_alignment(self, guest_profile: Dict[str, Any], host_analysis: Dict[str, Any]) -> float:
        """Calculate alignment between guest expertise and channel topics"""
        
        # Extract guest expertise areas
        guest_expertise = guest_profile.get('expertise_areas', [])
        guest_topics = guest_profile.get('key_topics', [])
        
        # Extract channel topics
        channel_dna = host_analysis.get('channel_dna', {}).get('channel_dna', {})
        channel_topics = channel_dna.get('primary_topics', [])
        
        # If either is empty, return low score
        if not guest_expertise or not channel_topics:
            return 0.5  # Neutral score when data is missing
        
        # Combine guest expertise and topics
        guest_keywords = set()
        for item in guest_expertise + guest_topics:
            # Split multi-word topics into individual words
            words = item.lower().split()
            for word in words:
                if len(word) > 3:  # Only consider meaningful words
                    guest_keywords.add(word)
        
        # Combine channel topics
        channel_keywords = set()
        for item in channel_topics:
            words = item.lower().split()
            for word in words:
                if len(word) > 3:
                    channel_keywords.add(word)
        
        # Calculate overlap
        if not channel_keywords:
            return 0.5
        
        # Count matches
        matches = 0
        for keyword in guest_keywords:
            for channel_keyword in channel_keywords:
                if keyword in channel_keyword or channel_keyword in keyword:
                    matches += 1
                    break
        
        # Calculate alignment score
        alignment_score = min(1.0, matches / max(1, len(channel_keywords)))
        
        # Boost score if there's a direct match with primary topics
        for expertise in guest_expertise:
            for topic in channel_topics:
                if expertise.lower() in topic.lower() or topic.lower() in expertise.lower():
                    alignment_score = min(1.0, alignment_score + 0.2)
        
        return alignment_score
    
    def calculate_authority_score(self, guest_profile: Dict[str, Any], host_analysis: Dict[str, Any]) -> float:
        """Calculate guest's authority/credibility score"""
        
        # Extract authority indicators
        authority_indicators = guest_profile.get('authority_indicators', [])
        
        # Extract social following
        social_following = guest_profile.get('social_following', {})
        
        # Base score
        authority_score = 0.5  # Start neutral
        
        # Adjust based on authority indicators
        if authority_indicators:
            # Count strong indicators
            strong_indicators = 0
            for indicator in authority_indicators:
                indicator = indicator.lower()
                if any(term in indicator for term in ['founder', 'ceo', 'author', 'expert', 'award', 'professor', 'phd', 'leader']):
                    strong_indicators += 1
            
            # Adjust score based on strong indicators
            authority_score += min(0.3, strong_indicators * 0.1)
        
        # Adjust based on social following
        if social_following:
            # Check Twitter followers
            twitter_followers = social_following.get('twitter', 'unknown')
            if twitter_followers != 'unknown':
                try:
                    # Convert K/M to numbers
                    if isinstance(twitter_followers, str):
                        if 'k' in twitter_followers.lower():
                            followers = float(twitter_followers.lower().replace('k', '')) * 1000
                        elif 'm' in twitter_followers.lower():
                            followers = float(twitter_followers.lower().replace('m', '')) * 1000000
                        else:
                            followers = float(twitter_followers.replace(',', ''))
                    else:
                        followers = float(twitter_followers)
                    
                    # Adjust score based on followers
                    if followers > 1000000:  # 1M+
                        authority_score += 0.2
                    elif followers > 100000:  # 100K+
                        authority_score += 0.15
                    elif followers > 10000:   # 10K+
                        authority_score += 0.1
                    elif followers > 1000:    # 1K+
                        authority_score += 0.05
                except:
                    pass
            
            # Check LinkedIn connections
            linkedin = social_following.get('linkedin', 'unknown')
            if linkedin != 'unknown' and '500+' in str(linkedin):
                authority_score += 0.05
        
        # Check for previous podcasts
        previous_podcasts = guest_profile.get('previous_podcasts', [])
        if previous_podcasts and previous_podcasts[0] != 'Unable to determine':
            authority_score += min(0.1, len(previous_podcasts) * 0.02)
        
        # Cap at 1.0
        return min(1.0, authority_score)
    
    def calculate_audience_appeal(self, guest_profile: Dict[str, Any], host_analysis: Dict[str, Any]) -> float:
        """Calculate potential audience appeal"""
        
        # Extract audience profile from channel
        channel_dna = host_analysis.get('channel_dna', {}).get('channel_dna', {})
        audience_profile = channel_dna.get('audience_profile', '')
        
        # Extract guest characteristics
        guest_industry = guest_profile.get('industry', '')
        guest_bio = guest_profile.get('bio_summary', '')
        
        # Base score
        appeal_score = 0.6  # Start slightly positive
        
        # Adjust based on social following (popularity)
        social_following = guest_profile.get('social_following', {})
        if social_following:
            # Check total social presence
            platforms_with_following = 0
            for platform, count in social_following.items():
                if count and count != 'unknown':
                    platforms_with_following += 1
            
            # Adjust score based on social presence
            appeal_score += min(0.2, platforms_with_following * 0.05)
        
        # Adjust based on popularity indicators
        popularity_indicators = guest_profile.get('popularity_indicators', [])
        if popularity_indicators:
            appeal_score += min(0.2, len(popularity_indicators) * 0.05)
        
        # Adjust based on audience alignment
        if audience_profile and (guest_industry or guest_bio):
            # Simple keyword matching
            audience_keywords = audience_profile.lower().split()
            guest_text = (guest_industry + ' ' + guest_bio).lower()
            
            matches = 0
            for keyword in audience_keywords:
                if len(keyword) > 3 and keyword in guest_text:
                    matches += 1
            
            # Adjust score based on matches
            appeal_score += min(0.2, matches * 0.04)
        
        # Cap at 1.0
        return min(1.0, appeal_score)
    
    def calculate_uniqueness_factor(self, guest_profile: Dict[str, Any], host_analysis: Dict[str, Any]) -> float:
        """Calculate how unique/novel the guest would be"""
        
        # Extract recent videos
        recent_videos = host_analysis.get('raw_video_data', [])
        
        # Extract guest name and topics
        guest_name = guest_profile.get('name', '').lower()
        guest_expertise = [area.lower() for area in guest_profile.get('expertise_areas', [])]
        
        # Base uniqueness score (higher is better)
        uniqueness_score = 0.7  # Start positive
        
        # Check if guest has appeared before
        guest_appeared = False
        similar_topics_count = 0
        
        for video in recent_videos:
            title = video.get('title', '').lower()
            
            # Check if guest name appears in title
            if guest_name in title:
                guest_appeared = True
                uniqueness_score -= 0.3  # Significant penalty for repeat guests
                break
            
            # Check for similar topics
            for expertise in guest_expertise:
                if expertise in title:
                    similar_topics_count += 1
                    break
        
        # Adjust for similar topics
        if similar_topics_count > 0:
            # Moderate penalty for common topics
            uniqueness_score -= min(0.3, similar_topics_count * 0.05)
        
        # Bonus for unique industry
        channel_dna = host_analysis.get('channel_dna', {}).get('channel_dna', {})
        primary_topics = [topic.lower() for topic in channel_dna.get('primary_topics', [])]
        
        guest_industry = guest_profile.get('industry', '').lower()
        if guest_industry and not any(guest_industry in topic for topic in primary_topics):
            uniqueness_score += 0.1  # Bonus for new industry
        
        # Cap between 0.1 and 1.0
        return max(0.1, min(1.0, uniqueness_score))
    
    def calculate_engagement_potential(self, guest_profile: Dict[str, Any], host_analysis: Dict[str, Any]) -> float:
        """Calculate potential for audience engagement"""
        
        # Extract engagement drivers
        channel_dna = host_analysis.get('channel_dna', {}).get('channel_dna', {})
        engagement_drivers = channel_dna.get('engagement_drivers', [])
        
        # Extract guest characteristics
        guest_topics = guest_profile.get('key_topics', [])
        guest_activities = guest_profile.get('recent_activities', [])
        
        # Base engagement score
        engagement_score = 0.5  # Start neutral
        
        # Check for timely/trending topics
        timely_topics = []
        for activity in guest_activities:
            activity = activity.lower()
            if any(term in activity for term in ['recent', 'new', 'launch', 'announce', 'publish', 'release']):
                timely_topics.append(activity)
        
        # Bonus for timely content
        engagement_score += min(0.2, len(timely_topics) * 0.05)
        
        # Check alignment with engagement drivers
        if engagement_drivers and guest_topics:
            matches = 0
            for driver in engagement_drivers:
                driver = driver.lower()
                for topic in guest_topics:
                    topic = topic.lower()
                    if driver in topic or topic in driver:
                        matches += 1
                        break
            
            # Adjust score based on matches
            engagement_score += min(0.3, matches * 0.1)
        
        # Check for previous podcast experience
        previous_podcasts = guest_profile.get('previous_podcasts', [])
        if previous_podcasts and previous_podcasts[0] != 'Unable to determine':
            # Bonus for podcast experience (better engagement)
            engagement_score += min(0.1, len(previous_podcasts) * 0.02)
        
        # Cap at 1.0
        return min(1.0, engagement_score)
    
    def determine_recommendation(self, overall_score: int) -> str:
        """Determine recommendation based on overall score"""
        
        if overall_score >= 85:
            return "HIGHLY_RECOMMENDED"
        elif overall_score >= 70:
            return "RECOMMENDED"
        elif overall_score >= 55:
            return "CONSIDER"
        elif overall_score >= 40:
            return "LOW_PRIORITY"
        else:
            return "NOT_RECOMMENDED"
    
    def identify_key_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify key strengths based on scores"""
        
        strengths = []
        
        # Check each score
        for factor, score in scores.items():
            # Convert to 100-point scale
            score_100 = score * 100
            
            if score_100 >= 80:
                if factor == 'topic_alignment':
                    strengths.append("Strong alignment with channel topics")
                elif factor == 'authority_score':
                    strengths.append("High authority/credibility in their field")
                elif factor == 'audience_appeal':
                    strengths.append("Strong potential audience appeal")
                elif factor == 'uniqueness_factor':
                    strengths.append("Brings fresh perspective to the channel")
                elif factor == 'engagement_potential':
                    strengths.append("High potential for audience engagement")
        
        # If no high scores, check for moderate scores
        if not strengths:
            for factor, score in scores.items():
                score_100 = score * 100
                if score_100 >= 70:
                    if factor == 'topic_alignment':
                        strengths.append("Good alignment with channel topics")
                    elif factor == 'authority_score':
                        strengths.append("Solid credentials in their field")
                    elif factor == 'audience_appeal':
                        strengths.append("Appealing to channel audience")
                    elif factor == 'uniqueness_factor':
                        strengths.append("Relatively fresh perspective")
                    elif factor == 'engagement_potential':
                        strengths.append("Good potential for engagement")
        
        return strengths
    
    def identify_areas_of_concern(self, scores: Dict[str, float]) -> List[str]:
        """Identify areas of concern based on scores"""
        
        concerns = []
        
        # Check each score
        for factor, score in scores.items():
            # Convert to 100-point scale
            score_100 = score * 100
            
            if score_100 <= 40:
                if factor == 'topic_alignment':
                    concerns.append("Limited alignment with channel topics")
                elif factor == 'authority_score':
                    concerns.append("Limited authority/credibility in relevant fields")
                elif factor == 'audience_appeal':
                    concerns.append("May not appeal to channel audience")
                elif factor == 'uniqueness_factor':
                    concerns.append("Similar to previous guests/content")
                elif factor == 'engagement_potential':
                    concerns.append("Limited potential for audience engagement")
        
        return concerns
    
    def generate_interview_recommendations(self, 
                                         guest_profile: Dict[str, Any], 
                                         host_analysis: Dict[str, Any],
                                         overall_score: int) -> Dict[str, Any]:
        """Generate interview recommendations"""
        
        # Extract key data
        guest_topics = guest_profile.get('potential_interview_topics', [])
        guest_expertise = guest_profile.get('expertise_areas', [])
        
        # Channel data
        channel_dna = host_analysis.get('channel_dna', {}).get('channel_dna', {})
        channel_topics = channel_dna.get('primary_topics', [])
        
        # Preparation notes
        preparation_notes = []
        
        # Determine estimated audience engagement
        if overall_score >= 80:
            estimated_engagement = "HIGH"
        elif overall_score >= 60:
            estimated_engagement = "MEDIUM"
        else:
            estimated_engagement = "LOW"
        
        # Generate preparation notes
        if overall_score >= 70:
            # High-scoring guests
            preparation_notes.append("Research guest's recent work and publications")
            
            # Add topic-specific notes
            if guest_topics and channel_topics:
                for topic in guest_topics[:2]:
                    for channel_topic in channel_topics:
                        if topic.lower() in channel_topic.lower() or channel_topic.lower() in topic.lower():
                            preparation_notes.append(f"Focus on {topic} which aligns with channel interests")
                            break
        else:
            # Lower-scoring guests
            preparation_notes.append("Carefully prepare to bridge guest expertise with channel topics")
            
            if 'Limited alignment with channel topics' in self.identify_areas_of_concern({
                'topic_alignment': self.calculate_topic_alignment(guest_profile, host_analysis),
                'authority_score': 0.5,
                'audience_appeal': 0.5,
                'uniqueness_factor': 0.5,
                'engagement_potential': 0.5
            }):
                preparation_notes.append("Consider narrowing interview focus to most relevant topics")
        
        # Add general notes based on guest profile
        if guest_profile.get('previous_podcasts', ['Unknown'])[0] == 'Unable to determine':
            preparation_notes.append("Guest may have limited podcast experience - prepare accordingly")
        
        return {
            'estimated_audience_engagement': estimated_engagement,
            'preparation_notes': preparation_notes,
            'focus_topics': guest_topics[:3] if guest_topics else guest_expertise[:3]
        }
    
    def determine_confidence_level(self, guest_profile: Dict[str, Any], host_analysis: Dict[str, Any]) -> str:
        """Determine confidence level in the analysis"""
        
        # Check data quality
        data_quality = guest_profile.get('extraction_metadata', {}).get('data_quality_score', 0)
        confidence_score = guest_profile.get('extraction_metadata', {}).get('confidence_score', 0)
        
        # Check host analysis quality
        host_videos_analyzed = host_analysis.get('videos_analyzed', 0)
        
        # Calculate overall confidence
        if data_quality >= 70 and confidence_score >= 70 and host_videos_analyzed >= 20:
            return "HIGH"
        elif data_quality >= 50 and confidence_score >= 50 and host_videos_analyzed >= 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def call_llm_for_scoring_validation(self, 
                                      relevance_analysis: Dict[str, Any],
                                      guest_profile: Dict[str, Any],
                                      host_analysis: Dict[str, Any]) -> str:
        """Use Ollama LLaMA to validate and explain the scoring"""
        from ollama_client import ollama_client
        
        prompt = f"""
        You are an expert podcast consultant. Validate and explain this podcast guest relevance score.

        GUEST PROFILE:
        {json.dumps(guest_profile, indent=2)[:1000]}

        HOST CHANNEL ANALYSIS:
        {json.dumps(host_analysis.get('channel_dna', {}), indent=2)[:1000]}

        RELEVANCE ANALYSIS:
        {json.dumps(relevance_analysis, indent=2)}

        Based on this data, provide a brief, insightful explanation of the relevance score and recommendation. 
        Explain why the guest received this score and whether you agree with the recommendation.
        Keep your response to 3-4 sentences maximum, focusing on the most important factors.
        """

        try:
            # Use 70B model for better analysis quality
            response = ollama_client.generate_with_70b(prompt, max_tokens=500, temperature=0.7)
            validation = response.get("generated_text", "").strip()
            
            if validation:
                return validation
            else:
                return self.generate_fallback_validation(relevance_analysis)
            
        except Exception as e:
            print(f"LLM validation failed: {e}")
            return self.generate_fallback_validation(relevance_analysis)
    
    def generate_fallback_validation(self, relevance_analysis: Dict[str, Any]) -> str:
        """Generate fallback validation when LLM fails"""
        
        score = relevance_analysis.get('overall_relevance_score', 0)
        recommendation = relevance_analysis.get('recommendation', 'UNKNOWN')
        
        strengths = relevance_analysis.get('key_strengths', [])
        concerns = relevance_analysis.get('areas_of_concern', [])
        
        if recommendation in ["HIGHLY_RECOMMENDED", "RECOMMENDED"]:
            if strengths:
                return f"This guest scored {score}/100, resulting in a {recommendation} rating. The analysis highlights {strengths[0].lower()} as a key strength. Based on the data, this appears to be a good match for the channel."
            else:
                return f"This guest scored {score}/100, resulting in a {recommendation} rating. The overall alignment between guest expertise and channel content appears strong. This seems to be a suitable match for the podcast."
        
        elif recommendation == "CONSIDER":
            if strengths and concerns:
                return f"With a score of {score}/100, this guest falls into the CONSIDER category. While {strengths[0].lower()}, there are concerns about {concerns[0].lower()}. This guest may be worth considering but isn't an obvious perfect match."
            else:
                return f"With a score of {score}/100, this guest falls into the CONSIDER category. The analysis shows moderate alignment with the channel, with both strengths and limitations. Further consideration is recommended."
        
        else:  # LOW_PRIORITY or NOT_RECOMMENDED
            if concerns:
                return f"This guest scored {score}/100, resulting in a {recommendation} rating. The primary concern is {concerns[0].lower()}. Based on the analysis, there may be better candidates for this channel."
            else:
                return f"This guest scored {score}/100, resulting in a {recommendation} rating. The overall alignment between guest and channel appears limited. There may be better candidates to prioritize."
