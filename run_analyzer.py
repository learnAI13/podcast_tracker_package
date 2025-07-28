#!/usr/bin/env python3
# run_analyzer.py - Simple CLI for the 1-Click Podcast Guest Tracker

import asyncio
import argparse
import json
from podcast_guest_tracker import OneClickPodcastGuestTracker

async def analyze_guest(guest_name, guest_url, host_channel):
    """Run the complete analysis"""
    print(f"\n🚀 Starting 1-Click Podcast Guest Analysis")
    print(f"Guest: {guest_name}")
    print(f"Guest URL: {guest_url}")
    print(f"Host Channel: {host_channel}")
    print("-" * 50)
    
    tracker = OneClickPodcastGuestTracker()
    
    result = await tracker.analyze_podcast_guest_complete(
        guest_name=guest_name,
        guest_url=guest_url,
        host_channel_url=host_channel
    )
    
    # Print summary
    print("\n📊 Analysis Results:")
    print(f"Overall Score: {result['recommendation_summary']['overall_score']}/100")
    print(f"Recommendation: {result['recommendation_summary']['recommendation']}")
    print(f"Confidence: {result['recommendation_summary']['confidence_level']}")
    
    # Print detailed explanation
    print("\n💡 Recommendation Explanation:")
    for point in result['recommendation_summary']['explanation_points']:
        print(f"- {point}")
    
    # Save full results to file
    output_file = f"{guest_name.replace(' ', '_').lower()}_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Full analysis saved to: {output_file}")
    
    return result

def main():
    parser = argparse.ArgumentParser(description="1-Click Podcast Guest Analyzer")
    parser.add_argument("guest_name", help="Name of the potential podcast guest")
    parser.add_argument("guest_url", help="URL to guest's social profile (Twitter, LinkedIn, etc.)")
    parser.add_argument("host_channel", help="URL to host's YouTube channel")
    
    args = parser.parse_args()
    
    asyncio.run(analyze_guest(args.guest_name, args.guest_url, args.host_channel))

if __name__ == "__main__":
    main()