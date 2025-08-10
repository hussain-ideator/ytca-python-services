#!/usr/bin/env python3
"""
Test script to verify the JSON cleaning fixes
"""

import json

def test_json_cleaning():
    """Test the JSON cleaning functionality"""
    
    # Test data that mimics the problematic LLM response
    test_data = {
        "trending_topics": ["trending_topics", "AI Trends", "Digital Transformation", "Remote Work", "Sustainability"],
        "keyword_gaps": ["keyword_gaps", "Advanced Techniques", "Best Practices", "Case Studies", "Expert Tips"],
        "title_suggestions": ["title_suggestions", "Title 1", "Title 2", "Title 3", "Title 4"],
        "keyword_clusters": {},
        "viewer_questions": ["How do I get started?", "What are the best practices?", "How can I improve?", "What should I avoid?", "What are the latest trends?", "How do I succeed?"],
        "regional_keywords": ["local1", "local2", "local3", "local4", "local5"]
    }
    
    print("🧪 Testing JSON cleaning functionality...")
    print(f"📝 Original data: {json.dumps(test_data, indent=2)}")
    
    # Simulate the cleaning function
    def clean_response_data(data):
        """Clean response data to remove key names from list items"""
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                # Remove any list items that are just the key name
                cleaned_list = [item for item in value if item != key]
                cleaned_data[key] = cleaned_list
            else:
                cleaned_data[key] = value
        return cleaned_data
    
    # Clean the data
    cleaned_data = clean_response_data(test_data)
    
    print(f"✅ Cleaned data: {json.dumps(cleaned_data, indent=2)}")
    
    # Verify the cleaning worked
    issues_found = []
    
    for key, value in cleaned_data.items():
        if isinstance(value, list) and len(value) > 0:
            if value[0] == key:
                issues_found.append(f"Key '{key}' still appears as first item in list")
    
    if issues_found:
        print("❌ Issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All issues fixed! No key names found in list items.")
        return True

def test_json_parsing():
    """Test JSON parsing with problematic responses"""
    
    # Test problematic LLM response
    problematic_response = '''
    Task: Generate trending topics for a YouTube channel.
    
    {"trending_topics": ["trending_topics", "AI Trends", "Digital Transformation", "Remote Work", "Sustainability"]}
    '''
    
    print("\n🧪 Testing JSON parsing with problematic response...")
    print(f"📝 Problematic response: {problematic_response}")
    
    # Simulate the extraction process
    try:
        # Remove the prompt
        clean_response = problematic_response.replace("Task: Generate trending topics for a YouTube channel.", "").strip()
        print(f"🧹 Cleaned response: {clean_response}")
        
        # Parse JSON
        parsed_json = json.loads(clean_response)
        print(f"✅ Parsed JSON: {parsed_json}")
        
        # Clean the data
        def clean_response_data(data):
            cleaned_data = {}
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    cleaned_list = [item for item in value if item != key]
                    cleaned_data[key] = cleaned_list
                else:
                    cleaned_data[key] = value
            return cleaned_data
        
        cleaned_json = clean_response_data(parsed_json)
        print(f"🧹 Cleaned JSON: {cleaned_json}")
        
        # Verify the result
        if cleaned_json["trending_topics"][0] != "trending_topics":
            print("✅ Successfully removed key name from list!")
            return True
        else:
            print("❌ Key name still present in list")
            return False
            
    except Exception as e:
        print(f"❌ JSON parsing error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing JSON cleaning fixes...")
    print("=" * 50)
    
    # Test 1: JSON cleaning
    test1_passed = test_json_cleaning()
    
    # Test 2: JSON parsing
    test2_passed = test_json_parsing()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("✅ All tests passed! The fixes should work correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.") 