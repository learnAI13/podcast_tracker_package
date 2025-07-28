#!/usr/bin/env python3
# test_system.py - Test the complete 1-Click Podcast Guest Tracker

import asyncio
import json
import sys
from config_setup import Config

# Import your main components
try:
    from podcast_guest_tracker import OneClickPodcastGuestTracker
    from guest_analyzer_base import PremiumGuestAnalyzer
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all files are in the same directory")
    sys.exit(1)

async def test_guest_analyzer():
    """Test the guest analyzer component"""
    print("\n🧪 Testing Guest Analyzer...")
    
    try:
        async with PremiumGuestAnalyzer() as analyzer:
            # Test with a simple URL
            result = await analyzer.comprehensive_person_analysis(
                "Test Person", 
                "https://twitter.com/elonmusk"  # Using a known public profile
            )
            
            print(f"✅ Guest analyzer working. Quality score: {result.get('overall_quality_score', 0)}/100")
            return True
    except Exception as e:
        print(f"❌ Guest analyzer failed: {e}")
        return False

async def test_complete_system():
    """Test the complete system"""
    print("\n🧪 Testing Complete System...")
    
    try:
        tracker = OneClickPodcastGuestTracker()
        
        # Test with sample data
        result = await tracker.analyze_podcast_guest_complete(
            guest_name="Elon Musk",
            guest_url="https://twitter.com/elonmusk",
            host_channel_url="https://youtube.com/@lexfridman"
        )
        
        if 'error' not in result:
            print("✅ Complete system test passed!")
            print(f"📊 Overall Score: {result['recommendation_summary']['overall_score']}/100")
            print(f"🎯 Recommendation: {result['recommendation_summary']['recommendation']}")
            return True
        else:
            print(f"❌ System test failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Complete system test failed: {e}")
        return False

def test_llm_connection():
    """Test LLM connection"""
    print("\n🧪 Testing LLM Connection...")
    
    import requests
    
    try:
        # Test connection to local LLM
        response = requests.get(f"{Config.MIXTRAL_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ LLM connection successful")
            return True
    except:
        pass
    
    # Try basic completion endpoint
    try:
        payload = {
            "prompt": "Hello, this is a test. Respond with 'Connection successful'.",
            "n_predict": 50,
            "temperature": 0.1
        }
        
        response = requests.post(
            f"{Config.MIXTRAL_URL}/completion",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ LLM completion endpoint working")
            return True
        else:
            print(f"❌ LLM responded with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        print(f"Make sure your LLM is running on {Config.MIXTRAL_URL}")
    
    return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting 1-Click Podcast Guest Tracker Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: LLM Connection
    if test_llm_connection():
        tests_passed += 1
    
    # Test 2: Guest Analyzer
    if await test_guest_analyzer():
        tests_passed += 1
    
    # Test 3: Complete System
    if await test_complete_system():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🏁 Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\n📋 Next steps:")
        print("1. Run: python podcast_guest_tracker.py")
        print("2. Or use the API: python -m uvicorn api:app --reload")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
        if tests_passed == 0:
            print("\n🔧 Quick fixes to try:")
            print("1. Make sure your LLM is running")
            print("2. Check that all dependencies are installed")
            print("3. Verify your .env configuration")

def quick_demo():
    """Run a quick demo"""
    print("\n🎬 Quick Demo Mode")
    print("Testing with sample data...")
    
    # Sample guest data
    sample_guest = {
        "name": "Tim Ferriss",
        "url": "https://twitter.com/tferriss",
        "host_channel": "https://youtube.com/@lexfridman"
    }
    
    print(f"👤 Guest: {sample_guest['name']}")
    print(f"🔗 URL: {sample_guest['url']}")
    print(f"📺 Host: {sample_guest['host_channel']}")
    
    return asyncio.run(test_complete_system())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        quick_demo()
    else:
        asyncio.run(run_all_tests())