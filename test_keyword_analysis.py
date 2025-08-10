"""
Test script for Keyword Analysis API
Tests the new endpoint that accepts keywords as direct input
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_keyword_analysis():
    """Test the new keyword analysis endpoint"""
    print("🔍 Testing Keyword Analysis Endpoint...")
    
    test_request = {
        "channel_id": "UCKWaEZ-_VweaEx1j62do_vQ",
        "keywords": [
            "Blockchain",
            "Cryptocurrency", 
            "DeFi",
            "NFTs",
            "Web3",
            "Smart Contracts",
            "Ethereum",
            "Bitcoin"
        ],
        "region": "global",
        "language": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-keywords", json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Keyword analysis completed!")
            print(f"    📊 Channel ID: {result['channel_id']}")
            print(f"    🌍 Region: {result['region']}")
            print(f"    🗣️  Language: {result['language']}")
            print(f"    📅 Analysis Time: {result['analysis_timestamp']}")
            
            insights = result['strategic_insights']
            
            # Display strategic insights
            print(f"\n    📈 TRENDING TOPICS ({len(insights['trending_topics'])}):")
            for i, topic in enumerate(insights['trending_topics'], 1):
                print(f"      {i}. {topic}")
            
            print(f"\n    🔍 KEYWORD GAPS ({len(insights['keyword_gaps'])}):")
            for i, gap in enumerate(insights['keyword_gaps'], 1):
                print(f"      {i}. {gap}")
            
            print(f"\n    🎬 TITLE SUGGESTIONS ({len(insights['title_suggestions'])}):")
            for i, title in enumerate(insights['title_suggestions'], 1):
                print(f"      {i}. {title}")
            
            print(f"\n    🔗 KEYWORD CLUSTERS ({len(insights['keyword_clusters'])}):")
            for cluster_name, keywords in insights['keyword_clusters'].items():
                print(f"      📁 {cluster_name.upper()}: {', '.join(keywords[:3])}")
            
            print(f"\n    ❓ VIEWER QUESTIONS ({len(insights['viewer_questions'])}):")
            for i, question in enumerate(insights['viewer_questions'], 1):
                print(f"      {i}. {question}")
            
            print(f"\n    🌍 REGIONAL KEYWORDS ({len(insights['regional_keywords'])}):")
            for i, keyword in enumerate(insights['regional_keywords'], 1):
                print(f"      {i}. {keyword}")
            
            return True
        else:
            print(f"  ❌ Analysis failed: {response.status_code}")
            print(f"  Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Analysis error: {e}")
        return False

def test_different_keywords():
    """Test with different keyword sets"""
    print("\n🎯 Testing Different Keyword Sets...")
    
    test_cases = [
        {
            "name": "Gaming Keywords",
            "keywords": ["Gaming", "Esports", "Streaming", "Twitch", "YouTube Gaming", "Game Reviews"]
        },
        {
            "name": "Tech Keywords", 
            "keywords": ["Programming", "Python", "JavaScript", "Web Development", "AI", "Machine Learning"]
        },
        {
            "name": "Fitness Keywords",
            "keywords": ["Workout", "Fitness", "Nutrition", "Weight Loss", "Muscle Building", "Healthy Living"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  🔍 Testing: {test_case['name']}")
        
        test_request = {
            "channel_id": "UCKWaEZ-_VweaEx1j62do_vQ",
            "keywords": test_case["keywords"],
            "region": "global",
            "language": "en"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/analyze-keywords", json=test_request)
            
            if response.status_code == 200:
                result = response.json()
                insights = result['strategic_insights']
                
                print(f"    ✅ Success! Generated {len(insights['title_suggestions'])} title suggestions")
                print(f"    📈 Found {len(insights['trending_topics'])} trending topics")
                print(f"    🔍 Identified {len(insights['keyword_gaps'])} keyword gaps")
                
                # Show first few results
                if insights['title_suggestions']:
                    print(f"    🎬 Sample title: {insights['title_suggestions'][0]}")
                if insights['trending_topics']:
                    print(f"    📈 Sample trend: {insights['trending_topics'][0]}")
                    
            else:
                print(f"    ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")

def main():
    """Run keyword analysis tests"""
    print("🧪 Keyword Analysis API - Test Suite")
    print("=" * 60)
    
    # Test basic keyword analysis
    success = test_keyword_analysis()
    
    if success:
        # Test different keyword sets
        test_different_keywords()
    
    print("\n" + "=" * 60)
    print("🎉 Keyword analysis testing completed!")
    print("\n💡 This endpoint allows you to:")
    print("  • Provide keywords directly to the LLM")
    print("  • Get strategic insights without pre-existing data")
    print("  • Analyze any keyword set for any channel")
    print("  • Generate content recommendations on-the-fly")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("💡 Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Test Error: {e}") 