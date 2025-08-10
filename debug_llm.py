"""
Step-by-step LLM Debug Script
Tests each component of the LLM pipeline to identify failure points
"""

import asyncio
import json
from transformers import pipeline
import time

def test_llm_initialization():
    """Test 1: Check if LLM model loads properly"""
    print("🔍 Test 1: LLM Model Initialization")
    print("=" * 50)
    
    try:
        print("🤖 Loading GPT-2 model...")
        start_time = time.time()
        
        text_generator = pipeline("text-generation", model="openai-community/gpt2", device="cpu")
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded successfully in {load_time:.2f}s")
        
        # Test basic generation
        test_prompt = "Hello world"
        print(f"🧪 Testing basic generation with prompt: '{test_prompt}'")
        
        start_time = time.time()
        result = text_generator(test_prompt, max_new_tokens=10, num_return_sequences=1)
        gen_time = time.time() - start_time
        
        print(f"✅ Basic generation successful in {gen_time:.2f}s")
        print(f"📝 Generated text: {result[0]['generated_text'][:100]}...")
        
        return text_generator
        
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        return None

def test_simple_prompt(text_generator):
    """Test 2: Test simple prompt generation"""
    print("\n🔍 Test 2: Simple Prompt Generation")
    print("=" * 50)
    
    try:
        prompt = "Generate a list of 3 topics:"
        print(f"📝 Testing prompt: '{prompt}'")
        
        start_time = time.time()
        result = text_generator(prompt, max_new_tokens=50, num_return_sequences=1)
        gen_time = time.time() - start_time
        
        print(f"✅ Generation successful in {gen_time:.2f}s")
        print(f"📝 Full response: {result[0]['generated_text']}")
        
        return result[0]['generated_text']
        
    except Exception as e:
        print(f"❌ Simple prompt failed: {e}")
        return None

def test_json_prompt(text_generator):
    """Test 3: Test JSON-specific prompt"""
    print("\n🔍 Test 3: JSON Prompt Generation")
    print("=" * 50)
    
    try:
        prompt = """Task: Generate trending topics for a YouTube channel.

Channel content: Channel with 5 videos covering topics like Bitcoin, Ethereum, DeFi
Target region: global
Target language: en

Instructions:
1. Identify 5 trending topics this channel hasn't covered yet
2. Focus on high-search-volume topics in this niche
3. Return ONLY a JSON object with this exact structure

Required JSON format:
{"trending_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"]}

Example valid response:
{"trending_topics": ["AI Trends", "Digital Transformation", "Remote Work", "Sustainability", "Health Tech"]}

Do not include any explanations, examples, or additional text. Only return the JSON object."""
        
        print(f"📝 Testing JSON prompt (length: {len(prompt)} characters)")
        
        start_time = time.time()
        result = text_generator(prompt, max_new_tokens=100, num_return_sequences=1)
        gen_time = time.time() - start_time
        
        print(f"✅ JSON generation successful in {gen_time:.2f}s")
        print(f"📝 Full response: {result[0]['generated_text']}")
        
        return result[0]['generated_text']
        
    except Exception as e:
        print(f"❌ JSON prompt failed: {e}")
        return None

def test_json_parsing(response):
    """Test 4: Test JSON parsing from response"""
    print("\n🔍 Test 4: JSON Parsing")
    print("=" * 50)
    
    if not response:
        print("❌ No response to parse")
        return None
    
    try:
        print(f"📝 Attempting to parse: {response}")
        
        # Remove the prompt from response
        clean_response = response.replace("Task: Generate trending topics for a YouTube channel.", "").strip()
        print(f"🧹 Cleaned response: {clean_response}")
        
        # Try to find JSON object
        json_start = clean_response.find('{')
        json_end = clean_response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = clean_response[json_start:json_end]
            print(f"📋 Extracted JSON: {json_str}")
            
            # Try to parse
            parsed = json.loads(json_str)
            print(f"✅ JSON parsing successful: {parsed}")
            return parsed
        else:
            print("❌ No JSON braces found in response")
            return None
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        return None

def test_timeout_handling(text_generator):
    """Test 5: Test timeout handling"""
    print("\n🔍 Test 5: Timeout Handling")
    print("=" * 50)
    
    try:
        # Test with different token limits
        token_limits = [50, 100, 200, 300]
        
        for tokens in token_limits:
            print(f"🧪 Testing with {tokens} tokens...")
            
            start_time = time.time()
            result = text_generator("Generate a simple response", max_new_tokens=tokens, num_return_sequences=1)
            gen_time = time.time() - start_time
            
            print(f"✅ {tokens} tokens generated in {gen_time:.2f}s")
            
            if gen_time > 30:
                print(f"⚠️  Warning: {tokens} tokens took {gen_time:.2f}s (slow)")
        
        return True
        
    except Exception as e:
        print(f"❌ Timeout test failed: {e}")
        return False

def main():
    """Run all debug tests"""
    print("🧪 LLM Step-by-Step Debug")
    print("=" * 60)
    
    # Test 1: Model initialization
    text_generator = test_llm_initialization()
    if not text_generator:
        print("❌ Cannot proceed without LLM model")
        return
    
    # Test 2: Simple prompt
    simple_response = test_simple_prompt(text_generator)
    if not simple_response:
        print("❌ Simple prompt failed")
        return
    
    # Test 3: JSON prompt
    json_response = test_json_prompt(text_generator)
    if not json_response:
        print("❌ JSON prompt failed")
        return
    
    # Test 4: JSON parsing
    parsed_json = test_json_parsing(json_response)
    if not parsed_json:
        print("❌ JSON parsing failed")
        return
    
    # Test 5: Timeout handling
    timeout_ok = test_timeout_handling(text_generator)
    if not timeout_ok:
        print("❌ Timeout handling failed")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All debug tests completed!")
    print("\n📊 Summary:")
    print("  ✅ LLM model loads correctly")
    print("  ✅ Basic generation works")
    print("  ✅ JSON prompts work")
    print("  ✅ JSON parsing works")
    print("  ✅ Timeout handling works")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Debug script failed: {e}")
        import traceback
        traceback.print_exc() 