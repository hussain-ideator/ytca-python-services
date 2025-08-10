#!/usr/bin/env python3
"""
Test script to verify that the API returns clean responses
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_clean_response():
    """Test that the API returns clean responses without key names in list items"""
    
    print("🧪 Testing API response cleaning...")
    print("=" * 50)
    
    # Test data
    test_request = {
        "channel_id": "UCx8Thl4BbkOwslTGXzPJx0A",
        "region": "global",
        "language": "en"
    }
    
    try:
        print("📡 Making API request...")
        response = requests.post(f"{BASE_URL}/analyze-channel-strategy", json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API request successful!")
            
            # Check for key names in list items
            issues_found = []
            
            strategic_insights = result.get('strategic_insights', {})
            
            # Check trending_topics
            if 'trending_topics' in strategic_insights:
                topics = strategic_insights['trending_topics']
                if topics and topics[0] == 'trending_topics':
                    issues_found.append("trending_topics contains key name as first item")
            
            # Check keyword_gaps
            if 'keyword_gaps' in strategic_insights:
                gaps = strategic_insights['keyword_gaps']
                if gaps and gaps[0] == 'keyword_gaps':
                    issues_found.append("keyword_gaps contains key name as first item")
            
            # Check title_suggestions
            if 'title_suggestions' in strategic_insights:
                titles = strategic_insights['title_suggestions']
                if titles and titles[0] == 'title_suggestions':
                    issues_found.append("title_suggestions contains key name as first item")
            
            # Check viewer_questions
            if 'viewer_questions' in strategic_insights:
                questions = strategic_insights['viewer_questions']
                if questions and questions[0] == 'viewer_questions':
                    issues_found.append("viewer_questions contains key name as first item")
            
            # Check regional_keywords
            if 'regional_keywords' in strategic_insights:
                regional = strategic_insights['regional_keywords']
                if regional and regional[0] == 'regional_keywords':
                    issues_found.append("regional_keywords contains key name as first item")
            
            if issues_found:
                print("❌ Issues found:")
                for issue in issues_found:
                    print(f"  - {issue}")
                print("\n📝 Full response:")
                print(json.dumps(result, indent=2))
                return False
            else:
                print("✅ No key names found in list items!")
                print("\n📝 Clean response structure:")
                for key, value in strategic_insights.items():
                    if isinstance(value, list):
                        print(f"  {key}: {len(value)} items")
                        if value:
                            print(f"    First item: {value[0]}")
                    elif isinstance(value, dict):
                        print(f"  {key}: {len(value)} clusters")
                return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("💡 Start the server with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing API response cleaning...")
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    success = test_clean_response()
    
    if success:
        print("\n✅ Test passed! The API now returns clean responses.")
    else:
        print("\n❌ Test failed. The API still has issues.") 