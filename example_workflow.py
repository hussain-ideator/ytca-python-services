"""
Example workflow demonstrating the complete Keyword Intelligence Assistant functionality
including database integration for channel engagement data.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def example_workflow():
    """Complete workflow example"""
    
    print("🚀 Keyword Intelligence Assistant - Complete Workflow Example")
    print("=" * 70)
    
    # Sample YouTube channel data
    channel_id = "UC_tech_education_2024"
    channel_data = {
        "videos": [
            {
                "title": "Complete Python Course 2024 - From Beginner to Advanced",
                "description": "Master Python programming with this comprehensive course. Learn variables, functions, OOP, web development, and data science. Perfect for beginners and intermediate developers.",
                "tags": ["python", "programming", "course", "tutorial", "beginner", "advanced", "web development", "data science"]
            },
            {
                "title": "React.js Full Tutorial - Build Modern Web Apps",
                "description": "Learn React.js from scratch and build amazing web applications. Covers components, hooks, state management, and deployment. Great for frontend developers.",
                "tags": ["react", "javascript", "frontend", "web development", "tutorial", "components", "hooks"]
            },
            {
                "title": "Machine Learning with Python - Complete Guide",
                "description": "Dive into machine learning using Python. Learn scikit-learn, pandas, numpy, and build real ML projects. Data science made easy for everyone.",
                "tags": ["machine learning", "python", "data science", "AI", "scikit-learn", "pandas", "numpy"]
            }
        ],
        "channel_name": "Tech Education Pro",
        "channel_id": channel_id
    }
    
    print("📊 Step 1: Performing keyword analysis with database storage...")
    
    # Analyze keywords (will automatically save to database)
    response = requests.post(f"{BASE_URL}/analyze-keywords", json=channel_data)
    
    if response.status_code == 200:
        analysis = response.json()
        print("✅ Keyword analysis completed!")
        print(f"   📈 Found {len(analysis['top_keywords'])} keywords")
        print(f"   📂 Categorized into {len(analysis['keyword_categories'])} categories")
        print(f"   💡 Generated {len(analysis['recommendations'])} recommendations")
        
        # Display top 5 keywords
        print("\n🔥 Top 5 Keywords:")
        for i, kw in enumerate(analysis['top_keywords'][:5], 1):
            print(f"   {i}. {kw.keyword} ({kw.frequency} times)")
        
    else:
        print(f"❌ Keyword analysis failed: {response.text}")
        return
    
    print("\n" + "="*50)
    print("📁 Step 2: Saving additional engagement data...")
    
    # Sample engagement data to save
    engagement_datasets = {
        "comments": {
            "total_comments": 2850,
            "avg_sentiment": 0.4,
            "top_commenters": ["@techfan2024", "@pythonlover", "@reactdev"],
            "most_common_words": ["amazing", "helpful", "tutorial", "great"],
            "engagement_rate": 0.12,
            "timestamp": datetime.now().isoformat()
        },
        "likes": {
            "total_likes": 45600,
            "total_dislikes": 1200,
            "like_ratio": 0.974,
            "trending_videos": ["Complete Python Course 2024", "React.js Full Tutorial"],
            "monthly_growth": 0.15,
            "timestamp": datetime.now().isoformat()
        },
        "views": {
            "total_views": 892000,
            "avg_watch_time": "8:45",
            "retention_rate": 0.68,
            "demographics": {
                "18-24": 35,
                "25-34": 40,
                "35-44": 20,
                "45+": 5
            },
            "top_countries": ["US", "India", "UK", "Canada", "Germany"],
            "timestamp": datetime.now().isoformat()
        },
        "subscribers": {
            "total_subscribers": 125000,
            "monthly_growth": 2500,
            "subscriber_sources": {
                "youtube_search": 45,
                "suggested_videos": 30,
                "external": 15,
                "direct": 10
            },
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Save each engagement type
    for engagement_type, data in engagement_datasets.items():
        payload = {
            "channel_id": channel_id,
            "engagement_type": engagement_type,
            "data": data
        }
        
        response = requests.post(f"{BASE_URL}/channel-engagement", json=payload)
        
        if response.status_code == 200:
            print(f"✅ Saved {engagement_type} data")
        else:
            print(f"❌ Failed to save {engagement_type}: {response.text}")
    
    print("\n" + "="*50)
    print("🔍 Step 3: Retrieving and displaying stored data...")
    
    # Get all engagement data for the channel
    response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}")
    
    if response.status_code == 200:
        all_data = response.json()
        print(f"📊 Retrieved data for channel: {all_data['channel_id']}")
        print(f"📈 Total engagement types: {all_data['total_engagement_types']}")
        
        print("\n📋 Available data types:")
        for eng_type in all_data['engagement_data'].keys():
            print(f"   • {eng_type}")
        
        # Display specific data examples
        print("\n📊 Sample Data Insights:")
        
        if 'views' in all_data['engagement_data']:
            views_data = all_data['engagement_data']['views']
            print(f"   👀 Total Views: {views_data.get('total_views', 'N/A'):,}")
            print(f"   ⏱️  Avg Watch Time: {views_data.get('avg_watch_time', 'N/A')}")
            
        if 'likes' in all_data['engagement_data']:
            likes_data = all_data['engagement_data']['likes']
            print(f"   👍 Total Likes: {likes_data.get('total_likes', 'N/A'):,}")
            print(f"   📈 Like Ratio: {likes_data.get('like_ratio', 'N/A'):.1%}")
            
        if 'subscribers' in all_data['engagement_data']:
            subs_data = all_data['engagement_data']['subscribers']
            print(f"   👥 Subscribers: {subs_data.get('total_subscribers', 'N/A'):,}")
            print(f"   📈 Monthly Growth: +{subs_data.get('monthly_growth', 'N/A'):,}")
        
    else:
        print(f"❌ Failed to retrieve channel data: {response.text}")
    
    print("\n" + "="*50)
    print("🔍 Step 4: Retrieving keyword analysis from database...")
    
    # Retrieve the keyword analysis that was automatically saved
    response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}/keyword_analysis")
    
    if response.status_code == 200:
        result = response.json()
        if result['found']:
            saved_analysis = result['data']
            print("✅ Retrieved saved keyword analysis")
            print(f"   📅 Analysis timestamp: {saved_analysis.get('analysis_timestamp', 'N/A')}")
            print(f"   🎯 Top keyword: {saved_analysis['top_keywords'][0]['keyword'] if saved_analysis['top_keywords'] else 'N/A'}")
            print(f"   📊 Total videos analyzed: {saved_analysis.get('total_videos_analyzed', 'N/A')}")
        else:
            print("⚠️  No keyword analysis found in database")
    else:
        print(f"❌ Failed to retrieve keyword analysis: {response.text}")
    
    print("\n" + "="*50)
    print("✅ Workflow completed successfully!")
    print("\n💡 What you can do next:")
    print("   • View API documentation at: http://localhost:8000/docs")
    print("   • Monitor channel performance trends over time")
    print("   • Compare engagement metrics across different channels")
    print("   • Use the data for YouTube SEO optimization")
    print("   • Build dashboards using the stored data")

def check_api_health():
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Status: {health['status']}")
            print(f"🗄️  Database: {health['database_status']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running!")
        print("💡 Start the server with: python main.py")
        return False

if __name__ == "__main__":
    print("🧪 Keyword Intelligence Assistant - Example Workflow")
    print("=" * 60)
    
    # Check API health first
    if check_api_health():
        print()
        example_workflow()
    else:
        print("\n❌ Cannot proceed without a healthy API connection.")
        print("Please start the API server and try again.") 