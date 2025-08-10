"""
Test script for LLM-powered features in the Keyword Intelligence Assistant
Tests GPT-2 text generation, keyword suggestions, and enhanced analysis
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_with_llm():
    """Test health check to verify LLM model status"""
    print("🏥 Testing Health Check with LLM Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"  ✅ API Status: {health['status']}")
            print(f"  🗄️  Database: {health['database_status']}")
            print(f"  🤖 GPT-2 Model: {health['gpt2_model_status']}")
            print(f"  ⚡ AI Features: {'Enabled' if health['ai_features_enabled'] else 'Disabled'}")
            
            if not health['ai_features_enabled']:
                print("  ⚠️  Warning: AI features are disabled. Some tests may fail.")
            
            return health['ai_features_enabled']
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_text_generation():
    """Test basic text generation endpoint"""
    print("\n🤖 Test 1: Basic Text Generation...")
    
    test_prompts = [
        {
            "prompt": "YouTube video about Python programming",
            "max_length": 80,
            "temperature": 0.7,
            "num_return_sequences": 1
        },
        {
            "prompt": "Best practices for content creation",
            "max_length": 100,
            "temperature": 0.8,
            "num_return_sequences": 2
        }
    ]
    
    for i, prompt_data in enumerate(test_prompts, 1):
        try:
            response = requests.post(f"{BASE_URL}/generate-text", json=prompt_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Test {i} - Generated {len(result['generated_texts'])} text(s)")
                print(f"    📝 Original prompt: '{result['original_prompt'][:50]}...'")
                print(f"    🎯 Model used: {result['model_used']}")
                
                for j, text in enumerate(result['generated_texts']):
                    print(f"    📄 Text {j+1}: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            else:
                print(f"  ❌ Test {i} failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Test {i} error: {e}")

def test_keyword_suggestions():
    """Test AI-powered keyword suggestions"""
    print("\n🎯 Test 2: AI Keyword Suggestions...")
    
    test_requests = [
        {
            "topic": "Python programming",
            "target_audience": "beginners",
            "content_type": "tutorial"
        },
        {
            "topic": "machine learning",
            "target_audience": "intermediate",
            "content_type": "course"
        },
        {
            "topic": "web development",
            "target_audience": "advanced",
            "content_type": "project"
        }
    ]
    
    for i, request_data in enumerate(test_requests, 1):
        try:
            response = requests.post(f"{BASE_URL}/generate-keyword-suggestions", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Test {i} - Topic: {result['topic']}")
                print(f"    👥 Audience: {result['target_audience']}")
                print(f"    📺 Type: {result['content_type']}")
                print(f"    🔑 Keywords generated: {len(result['keywords'])}")
                print(f"    💡 Content ideas: {len(result['content_ideas'])}")
                
                if result['keywords']:
                    print(f"    📋 Sample keywords: {', '.join(result['keywords'][:3])}")
                if result['content_ideas']:
                    print(f"    💭 Sample ideas: {result['content_ideas'][0][:60]}...")
                    
            else:
                print(f"  ❌ Test {i} failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Test {i} error: {e}")

def test_video_description_generation():
    """Test video description generation"""
    print("\n📝 Test 3: Video Description Generation...")
    
    test_cases = [
        {
            "title": "Complete Python Course for Beginners",
            "keywords": ["python", "programming", "tutorial", "beginner", "coding"],
            "target_length": 150
        },
        {
            "title": "React.js vs Vue.js Comparison",
            "keywords": ["react", "vue", "javascript", "frontend", "comparison"],
            "target_length": 200
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        try:
            # Use query parameters for this endpoint
            params = {
                "title": case["title"],
                "keywords": case["keywords"],
                "target_length": case["target_length"]
            }
            
            response = requests.post(f"{BASE_URL}/generate-video-description", params=params)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Test {i} - Title: '{result['title']}'")
                print(f"    📏 Description length: {result['description_length']} chars")
                print(f"    🔑 Keywords used: {', '.join(result['keywords_used'])}")
                print(f"    📄 Description: '{result['generated_description'][:80]}...'")
                    
            else:
                print(f"  ❌ Test {i} failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Test {i} error: {e}")

def test_enhanced_keyword_analysis():
    """Test enhanced keyword analysis with AI suggestions"""
    print("\n🔍 Test 4: Enhanced Keyword Analysis with AI...")
    
    channel_data = {
        "videos": [
            {
                "title": "Machine Learning Fundamentals with Python",
                "description": "Learn the basics of machine learning using Python. We'll cover supervised learning, unsupervised learning, and neural networks with practical examples.",
                "tags": ["machine learning", "python", "AI", "data science", "neural networks", "tutorial"]
            },
            {
                "title": "Deep Learning with TensorFlow",
                "description": "Advanced deep learning concepts using TensorFlow framework. Build neural networks, CNNs, and RNNs for real-world applications.",
                "tags": ["deep learning", "tensorflow", "python", "neural networks", "CNN", "RNN", "AI"]
            }
        ],
        "channel_name": "AI Education Hub",
        "channel_id": "UC_ai_education_test"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-keywords", json=channel_data)
        
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Enhanced keyword analysis completed!")
            print(f"    📊 Videos analyzed: {result['total_videos_analyzed']}")
            print(f"    🔥 Top keywords found: {len(result['top_keywords'])}")
            print(f"    📂 Categories: {len(result['keyword_categories'])}")
            print(f"    💡 Recommendations: {len(result['recommendations'])}")
            
            # Check AI-generated features
            if result.get('ai_generated_suggestions'):
                print(f"    🤖 AI keyword suggestions: {len(result['ai_generated_suggestions'])}")
                print(f"       Sample: {', '.join(result['ai_generated_suggestions'][:3])}")
            else:
                print("    ⚠️  No AI keyword suggestions generated")
                
            if result.get('content_ideas'):
                print(f"    💭 AI content ideas: {len(result['content_ideas'])}")
                print(f"       Sample: {result['content_ideas'][0][:60]}..." if result['content_ideas'] else "")
            else:
                print("    ⚠️  No AI content ideas generated")
                
                         # Display top keywords
             print("    🔥 Top 3 keywords:")
             for i, kw in enumerate(result['top_keywords'][:3], 1):
                 print(f"       {i}. {kw.keyword} ({kw.frequency} times)")
                
        else:
            print(f"  ❌ Enhanced analysis failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"  ❌ Enhanced analysis error: {e}")

def test_database_integration_with_ai():
    """Test database storage of AI-enhanced analysis"""
    print("\n💾 Test 5: Database Integration with AI Features...")
    
    channel_id = "UC_ai_test_channel_llm"
    
    try:
        # Retrieve the AI-enhanced analysis from database
        response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}/keyword_analysis")
        
        if response.status_code == 200:
            result = response.json()
            if result['found']:
                data = result['data']
                print("  ✅ Retrieved AI-enhanced analysis from database")
                print(f"    📅 Timestamp: {data.get('analysis_timestamp', 'N/A')}")
                print(f"    🔥 Stored keywords: {len(data.get('top_keywords', []))}")
                print(f"    🤖 AI suggestions: {len(data.get('ai_generated_suggestions', []))}")
                print(f"    💭 Content ideas: {len(data.get('content_ideas', []))}")
                
                if data.get('ai_generated_suggestions'):
                    print(f"    📋 Sample AI suggestions: {', '.join(data['ai_generated_suggestions'][:2])}")
                    
            else:
                print("  ⚠️  No stored analysis found (run enhanced analysis first)")
        else:
            print(f"  ❌ Database retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Database test error: {e}")

def performance_test():
    """Test performance of LLM operations"""
    print("\n⚡ Test 6: Performance Testing...")
    
    # Test response times for different operations
    operations = [
        {
            "name": "Quick text generation",
            "url": f"{BASE_URL}/generate-text",
            "data": {"prompt": "YouTube tutorial about", "max_length": 50, "temperature": 0.7}
        },
        {
            "name": "Keyword suggestions",
            "url": f"{BASE_URL}/generate-keyword-suggestions",
            "data": {"topic": "programming", "target_audience": "beginners", "content_type": "tutorial"}
        }
    ]
    
    for operation in operations:
        try:
            start_time = time.time()
            response = requests.post(operation["url"], json=operation["data"])
            end_time = time.time()
            
            duration = end_time - start_time
            
            if response.status_code == 200:
                print(f"  ✅ {operation['name']}: {duration:.2f} seconds")
            else:
                print(f"  ❌ {operation['name']}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"  ❌ {operation['name']}: Error - {e}")

def main():
    """Run all LLM feature tests"""
    print("🧪 Keyword Intelligence Assistant - LLM Features Test Suite")
    print("=" * 70)
    
    # Check if API is running and LLM is available
    ai_enabled = test_health_with_llm()
    
    if not ai_enabled:
        print("\n❌ AI features are not available. Tests may be limited.")
        print("💡 Make sure the GPT-2 model is properly loaded.")
        return
    
    print("\n🚀 AI features are available! Running comprehensive tests...")
    
    # Run all tests
    test_text_generation()
    test_keyword_suggestions()
    test_video_description_generation()
    test_enhanced_keyword_analysis()
    test_database_integration_with_ai()
    performance_test()
    
    print("\n" + "=" * 70)
    print("✅ LLM feature testing completed!")
    print("\n💡 Next steps:")
    print("  • Explore the interactive API docs at: http://localhost:8000/docs")
    print("  • Try different prompts and parameters")
    print("  • Integrate AI features into your YouTube workflow")
    print("  • Monitor performance with larger datasets")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("💡 Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Test Error: {e}") 