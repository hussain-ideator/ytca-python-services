"""
Test script for the comprehensive LLM analysis features
Tests all new LLM-powered insights including suggested keywords, clusters, content gaps, etc.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_comprehensive_llm_analysis():
    """Test the enhanced keyword analysis with comprehensive LLM features"""
    
    print("🚀 Testing Comprehensive LLM Analysis Features")
    print("=" * 60)
    
    # Sample YouTube channel data for testing
    test_channel_data = {
        "videos": [
            {
                "title": "Python Machine Learning Tutorial - Complete Guide for Beginners",
                "description": "Learn machine learning with Python from scratch. This comprehensive tutorial covers supervised learning, unsupervised learning, neural networks, and practical projects using scikit-learn, pandas, and numpy.",
                "tags": ["python", "machine learning", "tutorial", "AI", "data science", "beginner", "scikit-learn", "neural networks"]
            },
            {
                "title": "Deep Learning with TensorFlow - Advanced Concepts",
                "description": "Dive deep into advanced neural networks using TensorFlow. Learn about CNNs, RNNs, GANs, and transformer models. Perfect for intermediate to advanced practitioners.",
                "tags": ["tensorflow", "deep learning", "neural networks", "CNN", "RNN", "GAN", "transformers", "advanced"]
            },
            {
                "title": "Data Science Project Walkthrough - Real World Analysis",
                "description": "Complete data science project from data collection to deployment. Learn data cleaning, exploratory analysis, feature engineering, model selection, and deployment strategies.",
                "tags": ["data science", "project", "data cleaning", "EDA", "feature engineering", "model deployment", "python"]
            },
            {
                "title": "Python Web Development with FastAPI",
                "description": "Build modern web APIs with FastAPI. Learn about async programming, database integration, authentication, and deployment. Great for backend developers.",
                "tags": ["fastapi", "web development", "python", "API", "backend", "async", "database", "authentication"]
            }
        ],
        "channel_name": "AI & Tech Learning Hub",
        "channel_id": "UC_test_comprehensive_analysis"
    }
    
    print(f"📊 Analyzing {len(test_channel_data['videos'])} videos from '{test_channel_data['channel_name']}'")
    print(f"🎯 Testing comprehensive LLM analysis features...")
    print()
    
    try:
        # Make request to analyze keywords endpoint
        response = requests.post(f"{BASE_URL}/analyze-keywords", json=test_channel_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis completed successfully!")
            print("=" * 50)
            
            # Display basic analysis results
            print(f"📈 BASIC ANALYSIS RESULTS")
            print(f"📺 Videos analyzed: {result['total_videos_analyzed']}")
            print(f"🔥 Top keywords found: {len(result['top_keywords'])}")
            print(f"📂 Categories: {len(result['keyword_categories'])}")
            print()
            
            # Display top 5 keywords
            print("🔥 TOP 5 KEYWORDS:")
            for i, kw in enumerate(result['top_keywords'][:5], 1):
                print(f"  {i}. {kw.keyword} (appears {kw.frequency} times)")
            print()
            
            # Check if LLM analysis is available
            if result.get('llm_analysis'):
                llm_data = result['llm_analysis']
                
                print("🤖 COMPREHENSIVE LLM ANALYSIS RESULTS")
                print("=" * 50)
                
                # 1. Suggested Keywords
                if llm_data.get('suggested_keywords'):
                    print("💡 SUGGESTED KEYWORDS TO TARGET:")
                    for i, keyword in enumerate(llm_data['suggested_keywords'], 1):
                        print(f"  {i}. {keyword}")
                    print()
                
                # 2. Keyword Clusters
                if llm_data.get('keyword_clusters'):
                    print("🔗 KEYWORD CLUSTERS:")
                    for cluster_name, keywords in llm_data['keyword_clusters'].items():
                        print(f"  📁 {cluster_name.upper()}:")
                        print(f"     {', '.join(keywords[:6])}")
                        if len(keywords) > 6:
                            print(f"     ... and {len(keywords) - 6} more")
                    print()
                
                # 3. Content Gaps
                if llm_data.get('content_gaps'):
                    print("🔍 CONTENT GAPS ANALYSIS:")
                    print("  Topics missing from your channel that viewers want:")
                    for i, gap in enumerate(llm_data['content_gaps'], 1):
                        print(f"  {i}. {gap}")
                    print()
                
                # 4. Title Ideas
                if llm_data.get('title_ideas'):
                    print("🎬 NEW VIDEO TITLE IDEAS:")
                    for i, title in enumerate(llm_data['title_ideas'], 1):
                        print(f"  {i}. {title}")
                    print()
                
                # 5. Questions People Ask
                if llm_data.get('questions_people_ask'):
                    print("❓ QUESTIONS VIEWERS ARE SEARCHING FOR:")
                    for i, question in enumerate(llm_data['questions_people_ask'], 1):
                        print(f"  {i}. {question}")
                    print()
                
                # Summary statistics
                print("📊 LLM ANALYSIS SUMMARY:")
                print(f"  • Suggested keywords: {len(llm_data.get('suggested_keywords', []))}")
                print(f"  • Keyword clusters: {len(llm_data.get('keyword_clusters', {}))}")
                print(f"  • Content gaps identified: {len(llm_data.get('content_gaps', []))}")
                print(f"  • New title ideas: {len(llm_data.get('title_ideas', []))}")
                print(f"  • Viewer questions: {len(llm_data.get('questions_people_ask', []))}")
                
            else:
                print("⚠️  LLM analysis not available (model may not be loaded)")
            
            print("\n" + "=" * 60)
            print("✅ Comprehensive analysis test completed!")
            
            # Additional insights
            print("\n💡 ACTIONABLE INSIGHTS:")
            if result.get('llm_analysis'):
                llm = result['llm_analysis']
                
                if llm.get('suggested_keywords'):
                    print(f"  🎯 Focus on these new keywords: {', '.join(llm['suggested_keywords'][:3])}")
                
                if llm.get('content_gaps'):
                    print(f"  📈 Create content about: {llm['content_gaps'][0] if llm['content_gaps'] else 'N/A'}")
                
                if llm.get('title_ideas'):
                    print(f"  🎬 Next video idea: {llm['title_ideas'][0] if llm['title_ideas'] else 'N/A'}")
                
                if llm.get('questions_people_ask'):
                    print(f"  ❓ Address this question: {llm['questions_people_ask'][0] if llm['questions_people_ask'] else 'N/A'}")
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("💡 Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Test Error: {e}")

def test_health_check_llm():
    """Test health check to verify LLM features are available"""
    print("🏥 Checking API Health and LLM Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"  ✅ API Status: {health['status']}")
            print(f"  🗄️  Database: {health.get('database_status', 'unknown')}")
            print(f"  🤖 GPT-2 Model: {health.get('gpt2_model_status', 'unknown')}")
            print(f"  ⚡ AI Features: {'Enabled' if health.get('ai_features_enabled') else 'Disabled'}")
            
            return health.get('ai_features_enabled', False)
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False

def test_database_storage():
    """Test if the comprehensive analysis is properly stored in database"""
    print("\n💾 Testing Database Storage of LLM Analysis...")
    
    channel_id = "UC_test_comprehensive_analysis"
    
    try:
        response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}/keyword_analysis")
        
        if response.status_code == 200:
            result = response.json()
            if result['found']:
                data = result['data']
                print("  ✅ LLM analysis found in database")
                print(f"    📅 Timestamp: {data.get('analysis_timestamp', 'N/A')}")
                
                if data.get('llm_analysis'):
                    llm_data = data['llm_analysis']
                    print(f"    🎯 Suggested keywords stored: {len(llm_data.get('suggested_keywords', []))}")
                    print(f"    🔗 Keyword clusters stored: {len(llm_data.get('keyword_clusters', {}))}")
                    print(f"    🔍 Content gaps stored: {len(llm_data.get('content_gaps', []))}")
                    print(f"    🎬 Title ideas stored: {len(llm_data.get('title_ideas', []))}")
                    print(f"    ❓ Questions stored: {len(llm_data.get('questions_people_ask', []))}")
                else:
                    print("    ⚠️  No LLM analysis data found in stored record")
            else:
                print("  ⚠️  No analysis record found in database")
        else:
            print(f"  ❌ Database query failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Database test error: {e}")

if __name__ == "__main__":
    print("🧪 Comprehensive LLM Analysis - Test Suite")
    print("=" * 60)
    
    # Check if API and LLM are available
    ai_enabled = test_health_check_llm()
    
    if not ai_enabled:
        print("\n❌ AI features are not available. Please ensure:")
        print("  • The API server is running")
        print("  • GPT-2 model is properly loaded")
        print("  • All dependencies are installed")
        exit(1)
    
    print("\n🚀 All systems ready! Running comprehensive tests...")
    
    # Run comprehensive analysis test
    test_comprehensive_llm_analysis()
    
    # Test database storage
    test_database_storage()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("\n📚 What you can do next:")
    print("  • Use the suggested keywords for your next videos")
    print("  • Create content to fill the identified gaps")
    print("  • Implement the generated title ideas")
    print("  • Answer the questions viewers are searching for")
    print("  • Explore keyword clusters for content series ideas") 