import requests
import json

# Test data - sample YouTube channel metadata
sample_data = {
    "videos": [
        {
            "title": "Python Tutorial for Beginners - Learn Programming from Scratch",
            "description": "In this comprehensive Python tutorial, you'll learn programming fundamentals including variables, functions, loops, and data structures. Perfect for beginners who want to start their coding journey with Python programming language. We cover everything from basic syntax to advanced concepts.",
            "tags": ["python", "tutorial", "programming", "beginner", "coding", "learn", "development", "software"]
        },
        {
            "title": "Advanced Python Concepts - Decorators and Generators Explained",
            "description": "Dive deep into advanced Python programming concepts. Learn about decorators, generators, context managers, and metaclasses. This tutorial is designed for intermediate Python developers who want to level up their skills.",
            "tags": ["python", "advanced", "programming", "decorators", "generators", "intermediate", "development"]
        },
        {
            "title": "Build a Web API with FastAPI - Complete Tutorial",
            "description": "Learn how to build modern web APIs using FastAPI framework. We'll cover everything from basic endpoints to advanced features like authentication, database integration, and deployment. Great for web development enthusiasts.",
            "tags": ["fastapi", "web", "api", "tutorial", "python", "backend", "development", "framework"]
        },
        {
            "title": "Machine Learning with Python - Data Science Tutorial",
            "description": "Explore machine learning fundamentals using Python. Learn about data preprocessing, model training, and evaluation. We'll use popular libraries like scikit-learn, pandas, and numpy for hands-on data science projects.",
            "tags": ["machine learning", "python", "data science", "tutorial", "ai", "sklearn", "pandas", "numpy"]
        }
    ],
    "channel_name": "Tech Education Hub",
    "channel_id": "UC_tech_education_test"  # Added for AI features testing
}

def test_api():
    """Test the keyword analysis API"""
    
    # API endpoint
    url = "http://localhost:8000/analyze-keywords"
    
    try:
        print("🚀 Testing Keyword Intelligence Assistant API...")
        print(f"📤 Sending request to {url}")
        print(f"📊 Analyzing {len(sample_data['videos'])} videos from '{sample_data['channel_name']}'")
        print()
        
        # Make POST request
        response = requests.post(url, json=sample_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response Success!")
            print("=" * 50)
            
            # Display results
            print(f"📈 ANALYSIS RESULTS for '{sample_data['channel_name']}'")
            print(f"📺 Videos analyzed: {result['total_videos_analyzed']}")
            print()
            
            # Display top keywords
            print("🔥 TOP KEYWORDS:")
            for i, kw in enumerate(result['top_keywords'][:10], 1):
                print(f"  {i:2}. {kw.keyword} (appears {kw.frequency} times)")
            print()
            
            # Keyword categories
            print("📂 KEYWORD CATEGORIES:")
            for category, keywords in result['keyword_categories'].items():
                print(f"  {category.upper()}: {', '.join(keywords[:5])}")
                if len(keywords) > 5:
                    print(f"    ... and {len(keywords) - 5} more")
            print()
            
            # AI-generated suggestions (if available)
            if result.get('ai_generated_suggestions'):
                print("🤖 AI-GENERATED KEYWORD SUGGESTIONS:")
                for i, suggestion in enumerate(result['ai_generated_suggestions'][:5], 1):
                    print(f"  {i}. {suggestion}")
                print()
            
            # AI-generated content ideas (if available)
            if result.get('content_ideas'):
                print("💭 AI-GENERATED CONTENT IDEAS:")
                for i, idea in enumerate(result['content_ideas'][:3], 1):
                    print(f"  {i}. {idea}")
                print()
            
            # Sentiment analysis
            print("😊 SENTIMENT ANALYSIS:")
            sentiment = result['sentiment_analysis']
            polarity = sentiment['polarity']
            subjectivity = sentiment['subjectivity']
            
            if polarity > 0.1:
                mood = "Positive 😊"
            elif polarity < -0.1:
                mood = "Negative 😔"
            else:
                mood = "Neutral 😐"
                
            print(f"  Overall mood: {mood}")
            print(f"  Polarity: {polarity} (-1=negative, +1=positive)")
            print(f"  Subjectivity: {subjectivity} (0=objective, 1=subjective)")
            print()
            
            # Recommendations
            print("💡 SEO RECOMMENDATIONS:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("💡 Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Health Check: {result['status']}")
            print(f"📍 Service: {result['service']} v{result['version']}")
            print(f"🗄️  Database: {result.get('database_status', 'unknown')}")
            print(f"🤖 GPT-2 Model: {result.get('gpt2_model_status', 'unknown')}")
            print(f"⚡ AI Features: {'Enabled' if result.get('ai_features_enabled') else 'Disabled'}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except:
        print("❌ Cannot connect to API server")
        return False

if __name__ == "__main__":
    print("🧪 Keyword Intelligence Assistant - API Test")
    print("=" * 50)
    
    # Test health check first
    if test_health_check():
        print()
        # Test main functionality
        test_api()
    else:
        print("💡 Make sure to start the API server first:")
        print("   python main.py") 