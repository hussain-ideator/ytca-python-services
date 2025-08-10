"""
Test Async LLM Service - Check if the async implementation works
"""

import asyncio
import time
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor

class AsyncLLMService:
    """Async service for LLM operations with error handling"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.max_retries = 2
        self.timeout = 30
    
    async def generate_text_async(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Async wrapper for text generation with error handling"""
        try:
            print(f"🔍 Generating text with {max_tokens} tokens...")
            print(f"📝 Prompt: {prompt[:50]}...")
            
            # Run the synchronous text generation in a thread pool
            loop = asyncio.get_event_loop()
            
            def generate_text():
                text_generator = pipeline("text-generation", model="openai-community/gpt2", device="cpu")
                return text_generator(
                    prompt,
                    max_new_tokens=max_tokens,
                    num_return_sequences=1,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=50256,
                    truncation=True
                )
            
            # Execute with timeout
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, generate_text),
                timeout=self.timeout
            )
            
            if result and len(result) > 0:
                generated_text = result[0]['generated_text']
                print(f"✅ Generated: {generated_text[:100]}...")
                return generated_text
            return None
            
        except asyncio.TimeoutError:
            print(f"❌ LLM generation timed out after {self.timeout}s")
            return None
        except Exception as e:
            print(f"❌ LLM generation error: {e}")
            return None

async def test_async_llm():
    """Test the async LLM service"""
    print("🧪 Testing Async LLM Service...")
    
    llm_service = AsyncLLMService()
    
    # Test 1: Simple prompt
    print("\n🔍 Test 1: Simple Prompt")
    prompt1 = "Generate a list of 3 topics:"
    result1 = await llm_service.generate_text_async(prompt1, max_tokens=50)
    
    if result1:
        print(f"✅ Test 1 passed: {result1[:100]}...")
    else:
        print("❌ Test 1 failed")
        return False
    
    # Test 2: JSON prompt
    print("\n🔍 Test 2: JSON Prompt")
    prompt2 = """Task: Generate trending topics.

Instructions:
1. Identify 3 trending topics
2. Return ONLY a JSON object

Required format:
{"trending_topics": ["topic1", "topic2", "topic3"]}"""
    
    result2 = await llm_service.generate_text_async(prompt2, max_tokens=100)
    
    if result2:
        print(f"✅ Test 2 passed: {result2[:100]}...")
    else:
        print("❌ Test 2 failed")
        return False
    
    # Test 3: Multiple concurrent requests
    print("\n🔍 Test 3: Concurrent Requests")
    prompts = [
        "Generate topic 1:",
        "Generate topic 2:", 
        "Generate topic 3:"
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*[
        llm_service.generate_text_async(prompt, max_tokens=30) 
        for prompt in prompts
    ])
    end_time = time.time()
    
    successful_results = [r for r in results if r]
    print(f"✅ Test 3 passed: {len(successful_results)}/{len(prompts)} successful in {end_time - start_time:.2f}s")
    
    return len(successful_results) == len(prompts)

async def main():
    """Run async LLM tests"""
    print("🧪 Async LLM Service Test")
    print("=" * 50)
    
    success = await test_async_llm()
    
    if success:
        print("\n🎉 All async LLM tests passed!")
    else:
        print("\n❌ Some async LLM tests failed!")

if __name__ == "__main__":
    asyncio.run(main()) 