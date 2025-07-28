#!/usr/bin/env python3
# main.py - Command Line Interface for 1-Click Podcast Guest Tracker

import asyncio
import argparse
import json
import sys
from datetime import datetime
from podcast_guest_tracker import OneClickPodcastGuestTracker

def print_banner():
    """Print welcome banner"""
    banner = """
╔══════════════════════════════════════════════╗
║        1-Click Podcast Guest Tracker         ║
║              Powered by Llama 3.1            ║
╚══════════════════════════════════════════════╝
"""
    print(banner)

def save_result_to_file(result: dict, filename: str = None):
    """Save analysis result to file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        guest_name = result.get('analysis_metadata', {}).get('guest_name', 'unknown').replace(' ', '_')
        filename = f"analysis_{guest_name}_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"📁 Analysis saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")

async def single_guest_analysis(guest_name: str, guest_url: str, host_channel: str, save_file: bool = False):
    """Run single guest analysis"""
    print(f"\n🔍 Analyzing Guest: {guest_name}")
    print(f"🔗 Guest URL: {guest_url}")
    print(f"📺 Host Channel: {host_channel}")
    print("-" * 60)
    
    tracker = OneClickPodcastGuestTracker()
    
    try:
        result = await tracker.analyze_podcast_guest_complete(
            guest_name=guest_name,
            guest_url=guest_url,
            host_channel_url=host_channel
        )
        
        if 'error' in result:
            print(f"❌ Analysis failed: {result['error']}")
            return
        
        # Display key results
        summary = result['recommendation_summary']
        print(f"\n🎯 ANALYSIS RESULTS")
        print(f"📊 Overall Score: {summary['overall_score']}/100")
        print(f"💡 Recommendation: {summary['recommendation']}")
        print(f"🔑 Key Factors: {', '.join(summary['key_decision_factors'])}")
        
        # Show detailed report
        print(f"\n📋 DETAILED REPORT:")
        print("-" * 60)
        print(result['final_report'])
        
        # Save to file if requested
        if save_file:
            save_result_to_file(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Analysis failed with error: {e}")
        return None

async def batch_analysis(guest_file: str, host_channel: str, save_file: bool = False):
    """Run batch analysis from file"""
    try:
        with open(guest_file, 'r') as f:
            guest_list = json.load(f)
        
        print(f"\n📊 Starting batch analysis of {len(guest_list)} guests")
        print(f"📺 Host Channel: {host_channel}")
        print("-" * 60)
        
        tracker = OneClickPodcastGuestTracker()
        
        result = await tracker.batch_analyze_guests(guest_list, host_channel)
        
        if 'error' in result:
            print(f"❌ Batch analysis failed: {result['error']}")
            return
        
        # Display results
        print(f"\n🎯 BATCH ANALYSIS RESULTS")
        print(result['batch_summary'])
        
        print(f"\n🏆 GUEST RANKING:")
        for rank_info in result['ranking'][:10]:  # Top 10
            print(f"{rank_info['rank']}. {rank_info['name']} - {rank_info['score']}/100 ({rank_info['recommendation']})")
        
        # Save to file if requested
        if save_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_analysis_{timestamp}.json"
            save_result_to_file(result, filename)
        
        return result
        
    except FileNotFoundError:
        print(f"❌ Guest file not found: {guest_file}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in file: {guest_file}")
    except Exception as e:
        print(f"❌ Batch analysis failed: {e}")

def interactive_mode():
    """Interactive command-line mode"""
    print("\n🎮 Interactive Mode")
    print("Enter guest details for analysis:")
    
    guest_name = input("👤 Guest Name: ").strip()
    if not guest_name:
        print("❌ Guest name is required")
        return
    
    guest_url = input("🔗 Guest URL (Twitter/LinkedIn/YouTube): ").strip()
    if not guest_url:
        print("❌ Guest URL is required")
        return
    
    host_channel = input("📺 Host YouTube Channel URL: ").strip()
    if not host_channel:
        print("❌ Host channel URL is required")
        return
    
    save_file = input("💾 Save results to file? (y/n): ").strip().lower() == 'y'
    
    return asyncio.run(single_guest_analysis(guest_name, guest_url, host_channel, save_file))

def create_sample_batch_file():
    """Create a sample batch file for testing"""
    sample_guests = [
        {"name": "Naval Ravikant", "url": "https://twitter.com/naval"},
        {"name": "Tim Ferriss", "url": "https://twitter.com/tferriss"},
        {"name": "Gary Vaynerchuk", "url": "https://twitter.com/garyvee"},
        {"name": "Seth Godin", "url": "https://twitter.com/ThisIsSethsBlog"},
        {"name": "Reid Hoffman", "url": "https://twitter.com/reidhoffman"}
    ]
    
    filename = "sample_guests.json"
    with open(filename, 'w') as f:
        json.dump(sample_guests, f, indent=2)
    
    print(f"📄 Created sample batch file: {filename}")
    print("Edit this file to add your own guests, then run with --batch")

async def quick_test():
    """Quick system test"""
    print("\n⚡ Quick System Test")
    print("Testing with Elon Musk -> Lex Fridman channel")
    
    result = await single_guest_analysis(
        guest_name="Elon Musk",
        guest_url="https://twitter.com/elonmusk", 
        host_channel="https://youtube.com/@lexfridman",
        save_file=False
    )
    
    if result:
        print("\n✅ System test completed successfully!")
    else:
        print("\n❌ System test failed!")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="1-Click Podcast Guest Tracker - Analyze podcast guest relevance using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py -i
  
  # Single guest analysis
  python main.py -n "Tim Ferriss" -u "https://twitter.com/tferriss" -c "https://youtube.com/@lexfridman"
  
  # Batch analysis
  python main.py --batch guests.json -c "https://youtube.com/@lexfridman"
  
  # Quick test
  python main.py --test
  
  # Create sample batch file
  python main.py --create-sample
        """
    )
    
    parser.add_argument('-n', '--name', help='Guest name')
    parser.add_argument('-u', '--url', help='Guest URL (Twitter/LinkedIn/YouTube)')
    parser.add_argument('-c', '--channel', help='Host YouTube channel URL')
    parser.add_argument('-s', '--save', action='store_true', help='Save results to file')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--batch', help='Batch analysis from JSON file')
    parser.add_argument('--test', action='store_true', help='Run quick system test')
    parser.add_argument('--create-sample', action='store_true', help='Create sample batch file')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Handle different modes
    if args.create_sample:
        create_sample_batch_file()
        
    elif args.test:
        asyncio.run(quick_test())
        
    elif args.interactive:
        interactive_mode()
        
    elif args.batch:
        if not args.channel:
            print("❌ Host channel URL required for batch analysis")
            sys.exit(1)
        asyncio.run(batch_analysis(args.batch, args.channel, args.save))
        
    elif args.name and args.url and args.channel:
        asyncio.run(single_guest_analysis(args.name, args.url, args.channel, args.save))
        
    else:
        print("🤔 No valid arguments provided. Use -h for help or -i for interactive mode.")
        print("\nQuick start options:")
        print("  python main.py -i              # Interactive mode")
        print("  python main.py --test          # Quick test")
        print("  python main.py --create-sample # Create sample file")

if __name__ == "__main__":
    main()