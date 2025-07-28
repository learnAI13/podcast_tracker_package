# complete_podcast_guest_tracker.py
"""
1-Click Podcast Guest Tracker - Complete Integration System
Combines all components: Guest Analysis + Host Analysis + Relevance Scoring
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

# Import all our components
from guest_analyzer_base import PremiumGuestAnalyzer
# Use the mock host analyzer for testing
from host_channel_analyzer_mock import YouTubeHostAnalyzer
from relevance_scoring_engine import GuestRelevanceScorer

class OneClickPodcastGuestTracker:
    """Complete 1-click podcast guest analysis system"""
    
    def __init__(self, mixtral_url="http://localhost:8080"):
        self.mixtral_url = mixtral_url
        self.guest_analyzer = None
        self.host_analyzer = YouTubeHostAnalyzer(mixtral_url)
        self.relevance_scorer = GuestRelevanceScorer(mixtral_url)
        
        # Cache for host analysis (to avoid re-analyzing same channel)
        self.host_cache = {}
        
    async def analyze_podcast_guest_complete(self, 
                                           guest_name: str, 
                                           guest_url: str, 
                                           host_channel_url: str,
                                           use_cache: bool = True) -> Dict[str, Any]:
        """
        Complete 1-click analysis of podcast guest
        
        Args:
            guest_name: Name of the potential guest
            guest_url: URL of guest's profile (Twitter, LinkedIn, YouTube, etc.)
            host_channel_url: Host's YouTube channel URL
            use_cache: Whether to use cached host analysis
        
        Returns:
            Complete analysis with guest profile, host analysis, and relevance scoring
        """
        
        print(f"🚀 Starting 1-Click Analysis")
        print(f"Guest: {guest_name}")
        print(f"Guest URL: {guest_url}")
        print(f"Host Channel: {host_channel_url}")
        
        analysis_start = time.time()
        
        try:
            # Step 1: Analyze Guest Profile (Premium Analysis)
            print("\n📊 Step 1: Analyzing Guest Profile...")
            guest_start = time.time()
            
            async with PremiumGuestAnalyzer() as guest_analyzer:
                # Extract person name if not provided
                if not guest_name or guest_name == "Unknown":
                    guest_name = guest_analyzer.extract_enhanced_person_name(guest_url)
                
                # Comprehensive guest analysis
                social_data = await guest_analyzer.comprehensive_person_analysis(guest_name, guest_url)
                
                # Extract structured profile
                guest_profile = await guest_analyzer.extract_structured_guest_profile(social_data)
            
            guest_time = time.time() - guest_start
            print(f"✅ Guest analysis complete ({guest_time:.1f}s)")
            
            # Step 2: Analyze Host Channel
            print("\n📺 Step 2: Analyzing Host Channel...")
            host_start = time.time()
            
            # Check cache first
            host_analysis = None
            if use_cache and host_channel_url in self.host_cache:
                cache_age = time.time() - self.host_cache[host_channel_url]['timestamp']
                if cache_age < 86400:  # 24 hours cache
                    host_analysis = self.host_cache[host_channel_url]['data']
                    print("📋 Using cached host analysis")
            
            # Analyze if not cached
            if not host_analysis:
                host_analysis = await self.host_analyzer.analyze_host_channel(host_channel_url)
                
                # Cache the result
                if use_cache and 'error' not in host_analysis:
                    self.host_cache[host_channel_url] = {
                        'data': host_analysis,
                        'timestamp': time.time()
                    }
            
            host_time = time.time() - host_start
            print(f"✅ Host analysis complete ({host_time:.1f}s)")
            
            # Step 3: Calculate Relevance Score
            print("\n🎯 Step 3: Calculating Relevance Score...")
            score_start = time.time()
            
            relevance_analysis = self.relevance_scorer.calculate_overall_relevance_score(
                guest_profile, host_analysis
            )
            
            # Get LLM validation
            llm_validation = self.relevance_scorer.call_llm_for_scoring_validation(
                relevance_analysis, guest_profile, host_analysis
            )
            
            score_time = time.time() - score_start
            print(f"✅ Relevance scoring complete ({score_time:.1f}s)")
            
            # Step 4: Generate Final Report
            print("\n📋 Step 4: Generating Final Report...")
            report_start = time.time()
            
            final_report = await self.generate_comprehensive_report(
                guest_profile, host_analysis, relevance_analysis, llm_validation
            )
            
            report_time = time.time() - report_start
            total_time = time.time() - analysis_start
            
            print(f"✅ Report generation complete ({report_time:.1f}s)")
            print(f"🏁 Total analysis time: {total_time:.1f}s")
            
            # Compile final result
            final_result = {
                "analysis_metadata": {
                    "guest_name": guest_name,
                    "guest_url": guest_url,
                    "host_channel_url": host_channel_url,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "total_analysis_time": round(total_time, 1),
                    "performance_metrics": {
                        "guest_analysis_time": round(guest_time, 1),
                        "host_analysis_time": round(host_time, 1),
                        "scoring_time": round(score_time, 1),
                        "report_time": round(report_time, 1)
                    }
                },
                "guest_profile": guest_profile,
                "host_analysis": host_analysis,
                "relevance_analysis": relevance_analysis,
                "llm_validation": llm_validation,
                "final_report": final_report,
                "recommendation_summary": {
                    "overall_score": relevance_analysis.get('overall_relevance_score', 0),
                    "recommendation": relevance_analysis.get('recommendation', 'UNKNOWN'),
                    "confidence": relevance_analysis.get('confidence_level', 'UNKNOWN'),
                    "key_decision_factors": self.extract_key_decision_factors(relevance_analysis)
                }
            }
            
            print(f"\n🎉 Analysis Complete!")
            print(f"📊 Overall Score: {final_result['recommendation_summary']['overall_score']}/100")
            print(f"💡 Recommendation: {final_result['recommendation_summary']['recommendation']}")
            
            return final_result
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {
                "error": str(e),
                "analysis_metadata": {
                    "guest_name": guest_name,
                    "guest_url": guest_url,
                    "host_channel_url": host_channel_url,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "status": "FAILED"
                }
            }
    
    def extract_key_decision_factors(self, relevance_analysis: Dict[str, Any]) -> List[str]:
        """Extract the key factors that influenced the decision"""
        factors = []
        
        score_breakdown = relevance_analysis.get('score_breakdown', {})
        
        # Find highest scoring factors
        scores = {}
        for factor, data in score_breakdown.items():
            scores[factor] = data.get('score', 0)
        
        # Sort by score
        sorted_factors = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Top 3 factors
        for factor, score in sorted_factors[:3]:
            if score > 60:
                factor_name = factor.replace('_', ' ').title()
                factors.append(f"{factor_name}: {score}/100")
        
        # Add concerns if overall score is low
        overall_score = relevance_analysis.get('overall_relevance_score', 0)
        if overall_score < 60:
            concerns = relevance_analysis.get('areas_of_concern', [])
            if concerns:
                factors.append(f"Main concern: {concerns[0]}")
        
        return factors
    
    async def generate_comprehensive_report(self, 
                                          guest_profile: Dict[str, Any], 
                                          host_analysis: Dict[str, Any], 
                                          relevance_analysis: Dict[str, Any],
                                          llm_validation: str) -> str:
        """Generate a comprehensive human-readable report"""
        
        guest_name = guest_profile.get('name', 'Unknown Guest')
        overall_score = relevance_analysis.get('overall_relevance_score', 0)
        recommendation = relevance_analysis.get('recommendation', 'UNKNOWN')
        
        # Extract key data points
        designation = guest_profile.get('current_designation', 'Unknown Role')
        company = guest_profile.get('company', 'Unknown Company')
        expertise_areas = guest_profile.get('expertise_areas', ['Not specified'])
        
        # Channel performance data
        channel_dna = host_analysis.get('channel_dna', {}).get('channel_dna', {})
        channel_topics = channel_dna.get('primary_topics', ['Unknown'])
        avg_views = host_analysis.get('performance_metrics', {}).get('average_views', 0)
        
        # Score breakdown
        score_breakdown = relevance_analysis.get('score_breakdown', {})
        topic_score = score_breakdown.get('topic_alignment', {}).get('score', 0)
        authority_score = score_breakdown.get('authority_score', {}).get('score', 0)
        
        # Build comprehensive report
        report = f"""
# PODCAST GUEST ANALYSIS REPORT
**Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**

## EXECUTIVE SUMMARY
**Guest:** {guest_name}  
**Current Role:** {designation} at {company}  
**Overall Relevance Score:** {overall_score}/100  
**Recommendation:** {recommendation}  

{llm_validation}

---

## GUEST PROFILE

**Professional Background:**
- **Name:** {guest_name}
- **Designation:** {designation}
- **Company:** {company}
- **Industry:** {guest_profile.get('industry', 'Not specified')}

**Expertise Areas:**
{chr(10).join(f'• {area}' for area in expertise_areas[:5])}

**Authority Indicators:**
{chr(10).join(f'• {indicator}' for indicator in guest_profile.get('authority_indicators', ['Not available'])[:3])}

**Social Media Presence:**
{self.format_social_following(guest_profile.get('social_following', {}))}

---

## HOST CHANNEL ANALYSIS

**Channel Performance:**
- **Average Views:** {avg_views:,} per video
- **Primary Topics:** {', '.join(channel_topics)}
- **Content Style:** {channel_dna.get('content_style', 'Not determined')}

**Successful Guest Types:**
{chr(10).join(f'• {guest_type}' for guest_type in channel_dna.get('preferred_guest_types', ['Not specified']))}

---

## RELEVANCE ANALYSIS

### Score Breakdown:
- **Topic Alignment:** {topic_score}/100 ({score_breakdown.get('topic_alignment', {}).get('weight', 0)*100}% weight)
- **Authority/Credibility:** {authority_score}/100 ({score_breakdown.get('authority_score', {}).get('weight', 0)*100}% weight)
- **Audience Appeal:** {score_breakdown.get('audience_appeal', {}).get('score', 0)}/100 ({score_breakdown.get('audience_appeal', {}).get('weight', 0)*100}% weight)
- **Uniqueness Factor:** {score_breakdown.get('uniqueness_factor', {}).get('score', 0)}/100 ({score_breakdown.get('uniqueness_factor', {}).get('weight', 0)*100}% weight)
- **Engagement Potential:** {score_breakdown.get('engagement_potential', {}).get('score', 0)}/100 ({score_breakdown.get('engagement_potential', {}).get('weight', 0)*100}% weight)

### Key Strengths:
{chr(10).join(f'• {strength}' for strength in relevance_analysis.get('key_strengths', ['Not identified']))}

### Areas of Concern:
{chr(10).join(f'• {concern}' for concern in relevance_analysis.get('areas_of_concern', ['None identified']))}

---

## INTERVIEW RECOMMENDATIONS

### Suggested Topics:
{chr(10).join(f'• {topic}' for topic in guest_profile.get('potential_interview_topics', ['Topic research needed'])[:5])}

### Interview Preparation:
{chr(10).join(f'• {note}' for note in relevance_analysis.get('interview_recommendations', {}).get('preparation_notes', ['Standard preparation required']))}

### Expected Audience Engagement:
**{relevance_analysis.get('interview_recommendations', {}).get('estimated_audience_engagement', 'MEDIUM')}**

---

## FINAL RECOMMENDATION

**Decision:** {recommendation}  
**Confidence Level:** {relevance_analysis.get('confidence_level', 'MEDIUM')}

{self.generate_recommendation_rationale(recommendation, overall_score, relevance_analysis)}

---
*Report generated by 1-Click Podcast Guest Tracker*
"""
        return report.strip()
    
    def format_social_following(self, social_following: Dict[str, str]) -> str:
        """Format social media following for report"""
        if not social_following:
            return "• Social media data not available"
        
        formatted = []
        for platform, count in social_following.items():
            if count and count != 'unknown':
                formatted.append(f"• {platform.title()}: {count} followers")
        
        return '\n'.join(formatted) if formatted else "• Social media data not available"
    
    def generate_recommendation_rationale(self, recommendation: str, score: float, analysis: Dict[str, Any]) -> str:
        """Generate rationale for the recommendation"""
        
        if recommendation == "HIGHLY_RECOMMENDED":
            return f"With a score of {score}/100, this guest shows excellent alignment across multiple factors. They would likely be a valuable addition to your podcast with high audience appeal and strong topical relevance."
        
        elif recommendation == "RECOMMENDED":
            return f"Scoring {score}/100, this guest demonstrates good potential for your podcast. While there may be some areas for improvement, the overall fit is positive and worth pursuing."
        
        elif recommendation == "CONSIDER":
            return f"At {score}/100, this guest shows moderate potential. Consider whether their unique perspective or expertise in specific areas would add value to your audience despite some limitations."
        
        elif recommendation == "LOW_PRIORITY":
            return f"With a score of {score}/100, this guest may not be the best fit currently. Consider them for future episodes if their relevance increases or if you're exploring new topic areas."
        
        else:  # NOT_RECOMMENDED
            return f"Scoring {score}/100, this guest doesn't appear to be a strong fit for your channel at this time. The analysis suggests limited alignment with your audience and content themes."
    
    async def batch_analyze_guests(self, guest_list: List[Dict[str, str]], host_channel_url: str) -> Dict[str, Any]:
        """Analyze multiple guests in batch"""
        
        print(f"🔄 Starting batch analysis of {len(guest_list)} guests")
        
        results = []
        failed_analyses = []
        
        # Analyze host channel once
        print("📺 Analyzing host channel...")
        host_analysis = await self.host_analyzer.analyze_host_channel(host_channel_url)
        
        # Cache the host analysis
        self.host_cache[host_channel_url] = {
            'data': host_analysis,
            'timestamp': time.time()
        }
        
        # Analyze each guest
        for i, guest_info in enumerate(guest_list, 1):
            print(f"\n👤 Analyzing guest {i}/{len(guest_list)}: {guest_info.get('name', 'Unknown')}")
            
            try:
                result = await self.analyze_podcast_guest_complete(
                    guest_info['name'],
                    guest_info['url'],
                    host_channel_url,
                    use_cache=True  # Use cached host analysis
                )
                
                if 'error' not in result:
                    results.append(result)
                else:
                    failed_analyses.append({
                        'guest_info': guest_info,
                        'error': result['error']
                    })
                    
            except Exception as e:
                failed_analyses.append({
                    'guest_info': guest_info,
                    'error': str(e)
                })
        
        # Sort results by relevance score
        results.sort(key=lambda x: x['recommendation_summary']['overall_score'], reverse=True)
        
        # Generate batch summary
        batch_summary = self.generate_batch_summary(results, failed_analyses)
        
        return {
            'batch_metadata': {
                'total_guests': len(guest_list),
                'successful_analyses': len(results),
                'failed_analyses': len(failed_analyses),
                'host_channel_url': host_channel_url,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'guest_analyses': results,
            'failed_analyses': failed_analyses,
            'batch_summary': batch_summary,
            'ranking': [
                {
                    'rank': i + 1,
                    'name': result['analysis_metadata']['guest_name'],
                    'score': result['recommendation_summary']['overall_score'],
                    'recommendation': result['recommendation_summary']['recommendation']
                }
                for i, result in enumerate(results)
            ]
        }
    
    def generate_batch_summary(self, results: List[Dict], failed: List[Dict]) -> str:
        """Generate summary for batch analysis"""
        
        if not results:
            return "No successful analyses completed."
        
        scores = [r['recommendation_summary']['overall_score'] for r in results]
        recommendations = [r['recommendation_summary']['recommendation'] for r in results]
        
        # Calculate statistics
        avg_score = sum(scores) / len(scores)
        highest_score = max(scores)
        lowest_score = min(scores)
        
        # Count recommendations
        rec_counts = {}
        for rec in recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        summary = f"""
BATCH ANALYSIS SUMMARY

📊 Score Statistics:
• Average Score: {avg_score:.1f}/100
• Highest Score: {highest_score}/100
• Lowest Score: {lowest_score}/100

📈 Recommendations Breakdown:
{chr(10).join(f'• {rec}: {count} guests' for rec, count in rec_counts.items())}

🎯 Top 3 Recommendations:
{chr(10).join(f'{i+1}. {results[i]["analysis_metadata"]["guest_name"]} - {results[i]["recommendation_summary"]["overall_score"]}/100' for i in range(min(3, len(results))))}

{f"⚠️ Failed Analyses: {len(failed)}" if failed else "✅ All analyses completed successfully"}
"""
        return summary.strip()

# API Layer for external integration
class PodcastGuestTrackerAPI:
    """REST API wrapper for the podcast guest tracker"""
    
    def __init__(self):
        self.tracker = OneClickPodcastGuestTracker()
    
    async def analyze_single_guest(self, request_data: Dict[str, str]) -> Dict[str, Any]:
        """API endpoint for single guest analysis"""
        
        required_fields = ['guest_name', 'guest_url', 'host_channel_url']
        for field in required_fields:
            if field not in request_data:
                return {'error': f'Missing required field: {field}'}
        
        try:
            result = await self.tracker.analyze_podcast_guest_complete(
                request_data['guest_name'],
                request_data['guest_url'],
                request_data['host_channel_url']
            )
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_batch_guests(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint for batch guest analysis"""
        
        if 'guest_list' not in request_data or 'host_channel_url' not in request_data:
            return {'error': 'Missing guest_list or host_channel_url'}
        
        try:
            result = await self.tracker.batch_analyze_guests(
                request_data['guest_list'],
                request_data['host_channel_url']
            )
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Usage Examples and Test Functions
async def example_single_guest_analysis():
    """Example of single guest analysis"""
    
    tracker = OneClickPodcastGuestTracker()
    
    result = await tracker.analyze_podcast_guest_complete(
        guest_name="Elon Musk",
        guest_url="https://twitter.com/elonmusk",
        host_channel_url="https://youtube.com/@lexfridman"
    )
    
    print("=== SINGLE GUEST ANALYSIS RESULT ===")
    print(f"Guest: {result['analysis_metadata']['guest_name']}")
    print(f"Score: {result['recommendation_summary']['overall_score']}/100")
    print(f"Recommendation: {result['recommendation_summary']['recommendation']}")
    print("\nFull Report:")
    print(result['final_report'])

async def example_batch_analysis():
    """Example of batch guest analysis"""
    
    tracker = OneClickPodcastGuestTracker()
    
    guest_list = [
        {"name": "Naval Ravikant", "url": "https://twitter.com/naval"},
        {"name": "Tim Ferriss", "url": "https://twitter.com/tferriss"},
        {"name": "Gary Vaynerchuk", "url": "https://twitter.com/garyvee"}
    ]
    
    result = await tracker.batch_analyze_guests(
        guest_list, 
        "https://youtube.com/@lexfridman"
    )
    
    print("=== BATCH ANALYSIS RESULT ===")
    print(result['batch_summary'])
    print("\nRanking:")
    for rank_info in result['ranking']:
        print(f"{rank_info['rank']}. {rank_info['name']} - {rank_info['score']}/100 ({rank_info['recommendation']})")

# Main execution
if __name__ == "__main__":
    # Run example analyses
    asyncio.run(example_single_guest_analysis())
    # asyncio.run(example_batch_analysis())