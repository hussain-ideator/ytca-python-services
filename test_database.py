import requests
import json

# Test data for database operations
BASE_URL = "http://localhost:8000"

def test_database_operations():
    """Test all database-related endpoints"""
    
    print("🧪 Testing Database Operations")
    print("=" * 50)
    
    # Test data
    channel_id = "UC_test_channel_123"
    test_data = {
        "comments": {
            "total_comments": 1500,
            "avg_sentiment": 0.3,
            "top_commenters": ["user1", "user2", "user3"],
            "comment_keywords": ["awesome", "great", "tutorial"]
        },
        "likes": {
            "total_likes": 25000,
            "like_ratio": 0.95,
            "trending_videos": ["video1", "video2"]
        },
        "views": {
            "total_views": 500000,
            "avg_watch_time": "5:30",
            "demographics": {
                "18-24": 30,
                "25-34": 45,
                "35-44": 20,
                "45+": 5
            }
        }
    }
    
    # Test 1: Save engagement data
    print("📤 Test 1: Saving channel engagement data...")
    for engagement_type, data in test_data.items():
        payload = {
            "channel_id": channel_id,
            "engagement_type": engagement_type,
            "data": data
        }
        
        response = requests.post(f"{BASE_URL}/channel-engagement", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Saved {engagement_type}: {result['message']}")
        else:
            print(f"  ❌ Failed to save {engagement_type}: {response.text}")
    
    print()
    
    # Test 2: Retrieve specific engagement data
    print("📥 Test 2: Retrieving specific engagement data...")
    for engagement_type in test_data.keys():
        response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}/{engagement_type}")
        
        if response.status_code == 200:
            result = response.json()
            if result['found']:
                print(f"  ✅ Retrieved {engagement_type}: {len(str(result['data']))} characters")
            else:
                print(f"  ⚠️  No data found for {engagement_type}")
        else:
            print(f"  ❌ Failed to retrieve {engagement_type}: {response.text}")
    
    print()
    
    # Test 3: Get all engagement data for channel
    print("📊 Test 3: Getting all engagement data for channel...")
    response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ Retrieved {result['total_engagement_types']} engagement types")
        for eng_type in result['engagement_data'].keys():
            print(f"    - {eng_type}")
    else:
        print(f"  ❌ Failed to retrieve all data: {response.text}")
    
    print()
    
    # Test 4: Test keyword analysis with database integration
    print("🔍 Test 4: Testing keyword analysis with database storage...")
    
    analysis_payload = {
        "videos": [
            {
                "title": "Advanced Python Programming Tutorial",
                "description": "Learn advanced Python concepts including decorators, generators, and async programming.",
                "tags": ["python", "programming", "advanced", "tutorial", "coding"]
            }
        ],
        "channel_name": "Test Tech Channel",
        "channel_id": channel_id  # This will trigger database storage
    }
    
    response = requests.post(f"{BASE_URL}/analyze-keywords", json=analysis_payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ Keyword analysis completed")
        print(f"    - Top keywords: {len(result['top_keywords'])}")
        print(f"    - Categories: {len(result['keyword_categories'])}")
        print(f"    - Recommendations: {len(result['recommendations'])}")
        
        # Check if analysis was saved to database
        response = requests.get(f"{BASE_URL}/channel-engagement/{channel_id}/keyword_analysis")
        if response.status_code == 200:
            db_result = response.json()
            if db_result['found']:
                print(f"  ✅ Analysis results saved to database")
            else:
                print(f"  ⚠️  Analysis results not found in database")
    else:
        print(f"  ❌ Keyword analysis failed: {response.text}")
    
    print()
    
    # Test 5: Test non-existent data retrieval
    print("🔍 Test 5: Testing retrieval of non-existent data...")
    response = requests.get(f"{BASE_URL}/channel-engagement/nonexistent_channel/nonexistent_type")
    
    if response.status_code == 200:
        result = response.json()
        if not result['found']:
            print(f"  ✅ Correctly handled non-existent data")
        else:
            print(f"  ⚠️  Unexpected data found")
    else:
        print(f"  ❌ Error handling non-existent data: {response.text}")

def test_health_with_database():
    """Test health check with database status"""
    print("🏥 Testing Health Check with Database...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ API Status: {result['status']}")
        print(f"  🗄️  Database Status: {result['database_status']}")
        print(f"  📁 Database Path: {result['database_path']}")
        print(f"  🔗 Available Endpoints: {len(result['endpoints'])}")
        for endpoint in result['endpoints']:
            print(f"    - {endpoint}")
    else:
        print(f"  ❌ Health check failed: {response.text}")

if __name__ == "__main__":
    print("🧪 Keyword Intelligence Assistant - Database Test Suite")
    print("=" * 60)
    
    try:
        # Test health check first
        test_health_with_database()
        print()
        
        # Test database operations
        test_database_operations()
        
        print("✅ All database tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("💡 Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Test Error: {e}") 