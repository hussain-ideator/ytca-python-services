"""
Simple LLM Test - Check if basic LLM functionality works
"""

print("🧪 Starting Simple LLM Test...")

try:
    print("1. Importing transformers...")
    from transformers import pipeline
    print("✅ Transformers imported successfully")
    
    print("2. Loading GPT-2 model...")
    text_generator = pipeline("text-generation", model="openai-community/gpt2", device="cpu")
    print("✅ GPT-2 model loaded successfully")
    
    print("3. Testing basic generation...")
    result = text_generator("Hello", max_new_tokens=10, num_return_sequences=1)
    print(f"✅ Basic generation successful: {result[0]['generated_text']}")
    
    print("4. Testing with longer prompt...")
    result = text_generator("Generate a list:", max_new_tokens=20, num_return_sequences=1)
    print(f"✅ Longer prompt successful: {result[0]['generated_text']}")
    
    print("🎉 All tests passed! LLM is working correctly.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 