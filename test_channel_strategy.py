"""
Test script for Channel Strategy Analysis API
Tests the consolidated channel strategy analysis endpoint
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"  ✅ API Status: {health['status']}")
            print(f"  🗄️  Database: {health['database_status']}")
            print(f"  🤖 GPT-2 Model: {health['gpt2_model_status']}")
            print(f"  ⚡ AI Features: {'Enabled' if health['ai_features_enabled'] else 'Disabled'}")
            return health['ai_features_enabled']
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False

def prepopulate_channel_keyword_analysis():
    """Pre-populate the database with minimal keyword analysis for the test channel."""
    print("\n🔧 Pre-populating channel keyword analysis...")
    channel_id = "UCKWaEZ-_VweaEx1j62do_vQ"
    data = {
        "top_keywords": [
            {"keyword": "Block Chain", "frequency": 5},
            {"keyword": "crypto", "frequency": 2}
        ],
        "keyword_categories": {"technology": ["Block Chain", "crypto"]},
        "sentiment_analysis": {"positive": 0.8, "negative": 0.1, "neutral": 0.1},
        "total_videos_analyzed": 1,
        "recommendations": ["Focus on Block Chain content"]
    }
    payload = {
        "channel_id": channel_id,
        "engagement_type": "keyword_analysis",
        "data": data
    }
    try:
        response = requests.post(f"{BASE_URL}/channel-engagement", json=payload)
        if response.status_code == 200:
            print("  ✅ Pre-population successful.")
        else:
            print(f"  ❌ Pre-population failed: {response.status_code}")
            print(f"  Error details: {response.text}")
    except Exception as e:
        print(f"  ❌ Pre-population error: {e}")

def test_channel_strategy_analysis():
    """Test the main channel strategy analysis endpoint"""
    print("\n🎯 Testing Channel Strategy Analysis...")
    
    test_request = {
        "channel_id": "UCKWaEZ-_VweaEx1j62do_vQ",
        "region": "global",
        "language": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-channel-strategy", json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Channel strategy analysis completed!")
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

def test_database_retrieval():
    """Test retrieving stored strategy analysis"""
    print("\n💾 Testing Database Retrieval...")
    
    channel_id = "UCKWaEZ-_VweaEx1j62do_vQ"
    
    try:
        response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}/channel_strategy")
        
        if response.status_code == 200:
            result = response.json()
            if result['found']:
                data = result['data']
                print("  ✅ Stored strategy analysis found")
                print(f"    📅 Timestamp: {data.get('analysis_timestamp', 'N/A')}")
                print(f"    🌍 Region: {data.get('region', 'N/A')}")
                print(f"    🗣️  Language: {data.get('language', 'N/A')}")
                
                if data.get('strategic_insights'):
                    insights = data['strategic_insights']
                    print(f"    📈 Trending topics stored: {len(insights.get('trending_topics', []))}")
                    print(f"    🔍 Keyword gaps stored: {len(insights.get('keyword_gaps', []))}")
                    print(f"    🎬 Title suggestions stored: {len(insights.get('title_suggestions', []))}")
                    print(f"    🔗 Keyword clusters stored: {len(insights.get('keyword_clusters', {}))}")
                    print(f"    ❓ Viewer questions stored: {len(insights.get('viewer_questions', []))}")
                    print(f"    🌍 Regional keywords stored: {len(insights.get('regional_keywords', []))}")
                else:
                    print("    ⚠️  No strategic insights found in stored record")
            else:
                print("  ⚠️  No stored strategy analysis found")
        else:
            print(f"  ❌ Database query failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Database test error: {e}")

def main():
    """Run all tests"""
    print("🧪 Channel Strategy Analysis - Test Suite")
    print("=" * 60)
    
    # Check if API is available
    ai_enabled = test_health_check()
    
    if not ai_enabled:
        print("\n❌ AI features are not available. Please ensure:")
        print("  • The API server is running")
        print("  • GPT-2 model is properly loaded")
        print("  • All dependencies are installed")
        return
    
    prepopulate_channel_keyword_analysis()
    print("\n🚀 All systems ready! Running strategic analysis tests...")
    
    # Run tests
    success = test_channel_strategy_analysis()
    
    if success:
        test_database_retrieval()
    
    print("\n" + "=" * 60)
    print("🎉 Channel strategy analysis testing completed!")
    print("\n💡 Strategic insights provide:")
    print("  • Trending topics to cover")
    print("  • Keyword gaps vs competitors")
    print("  • Video title suggestions")
    print("  • Content series planning")
    print("  • Viewer question opportunities")
    print("  • Regional keyword optimization")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("💡 Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Test Error: {e}") 