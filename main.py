from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
import re
from collections import Counter
import nltk
from textblob import TextBlob
import uvicorn
import pandas as pd
from database import db_manager
from config import settings
import warnings
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import threading
import requests

# Suppress transformer warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Channel Strategy Analyzer",
    description="AI-powered channel analysis and strategic recommendations",
    version="2.0.0"
)

# URL normalization middleware to handle double slashes
@app.middleware("http")
async def normalize_path_middleware(request, call_next):
    """Normalize URL paths to handle double slashes and trailing slashes"""
    # Normalize double slashes to single slashes
    if "//" in str(request.url.path) and str(request.url.path) != "/":
        normalized_path = str(request.url.path).replace("//", "/")
        # Rebuild the URL with normalized path
        request.scope["path"] = normalized_path
        request.scope["raw_path"] = normalized_path.encode()
    
    response = await call_next(request)
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def check_ollama_connection():
    """Check if Ollama is running and the model is available"""
    try:
        response = requests.get(f"{settings.ollama_base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            if settings.ollama_model in model_names:
                print(f"✅ Ollama connection successful! Model {settings.ollama_model} is available")
                return True
            else:
                print(f"⚠️  Model {settings.ollama_model} not found in available models: {model_names}")
                return False
        else:
            print(f"❌ Ollama connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False

# Check Ollama connection on startup
ollama_available = check_ollama_connection()

# Pydantic Models
class ChannelStrategyRequest(BaseModel):
    channel_id: str = Field(..., description="YouTube channel ID")
    region: str = Field("global", description="Target region for analysis")
    language: str = Field("en", description="Target language for analysis")

class StrategicInsights(BaseModel):
    trending_topics: List[str] = Field(..., description="Trending topics not covered by channel")
    keyword_gaps: List[str] = Field(..., description="Keywords competitors cover but channel doesn't")
    title_suggestions: List[str] = Field(..., description="Video title suggestions based on keywords")
    keyword_clusters: Dict[str, List[str]] = Field(..., description="Related keywords grouped for content series")
    viewer_questions: List[str] = Field(..., description="Questions viewers might search for")
    regional_keywords: List[str] = Field(..., description="Keywords tailored for target region/language")

class ChannelStrategyResponse(BaseModel):
    channel_id: str = Field(..., description="YouTube channel ID")
    analysis_timestamp: str = Field(..., description="When analysis was performed")
    region: str = Field(..., description="Target region analyzed")
    language: str = Field(..., description="Target language analyzed")
    strategic_insights: StrategicInsights = Field(..., description="Comprehensive strategic recommendations")

class ChannelEngagementSave(BaseModel):
    channel_id: str = Field(..., description="YouTube channel ID")
    engagement_type: str = Field(..., description="Type of engagement")
    data: Dict[str, Any] = Field(..., description="JSON data to store")

class ChannelEngagementResponse(BaseModel):
    channel_id: str = Field(..., description="YouTube channel ID")
    engagement_type: str = Field(..., description="Type of engagement")
    data: Optional[Dict[str, Any]] = Field(None, description="Retrieved JSON data")
    found: bool = Field(..., description="Whether data was found")

class KeywordAnalysisRequest(BaseModel):
    channel_id: str = Field(..., description="YouTube channel ID")
    keywords: List[str] = Field(..., description="List of keywords to analyze")
    region: str = Field("global", description="Target region for analysis")
    language: str = Field("en", description="Target language for analysis")

class LLMPrompts:
    """Centralized prompts for strategic analysis"""
    
    @staticmethod
    def trending_topics_prompt(channel_data: str, region: str, language: str) -> str:
        return f"""Generate trending topics for YouTube channel analysis.

Channel content: {channel_data}
Target region: {region}
Target language: {language}

Return ONLY a valid JSON object with this exact format:
{{"trending_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"]}}

Do not include any explanations, examples, or additional text. Only return the JSON object."""

    @staticmethod
    def keyword_gaps_prompt(channel_keywords: List[str], region: str, language: str) -> str:
        return f"""Find keyword gaps for YouTube channel analysis.

Channel currently covers: {', '.join(channel_keywords[:8])}
Target region: {region}
Target language: {language}

Return ONLY a valid JSON object with this exact format:
{{"keyword_gaps": ["gap1", "gap2", "gap3", "gap4", "gap5"]}}

Do not include any explanations, examples, or additional text. Only return the JSON object."""

    @staticmethod
    def title_suggestions_prompt(top_keywords: List[str], region: str, language: str) -> str:
        return f"""Generate YouTube video title suggestions.

Keywords: {', '.join(top_keywords[:5])}
Target region: {region}
Target language: {language}

Return ONLY a valid JSON object with this exact format:
{{"title_suggestions": ["Title 1", "Title 2", "Title 3", "Title 4", "Title 5"]}}

Do not include any explanations, examples, or additional text. Only return the JSON object."""

    @staticmethod
    def keyword_clusters_prompt(keywords: List[str]) -> str:
        return f"""Group keywords into content clusters.

Keywords: {', '.join(keywords[:12])}

Return ONLY a valid JSON object with this exact format:
{{"keyword_clusters": {{"series1": ["kw1", "kw2"], "series2": ["kw3", "kw4"], "series3": ["kw5", "kw6"]}}}}

Do not include any explanations, examples, or additional text. Only return the JSON object."""

    @staticmethod
    def viewer_questions_prompt(keywords: List[str], region: str, language: str) -> str:
        return f"""Generate viewer questions for YouTube content.

Keywords: {', '.join(keywords[:6])}
Target region: {region}
Target language: {language}

Return ONLY a valid JSON object with this exact format:
{{"viewer_questions": ["Q1?", "Q2?", "Q3?", "Q4?", "Q5?", "Q6?"]}}

Do not include any explanations, examples, or additional text. Only return the JSON object."""

    @staticmethod
    def regional_keywords_prompt(keywords: List[str], region: str, language: str) -> str:
        return f"""Generate regional keywords for YouTube content.

Base keywords: {', '.join(keywords[:6])}
Target region: {region}
Target language: {language}

Return ONLY a valid JSON object with this exact format:
{{"regional_keywords": ["local1", "local2", "local3", "local4", "local5"]}}

Do not include any explanations, examples, or additional text. Only return the JSON object."""


class AsyncLLMService:
    """Async service for LLM operations with Ollama integration"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)  # Reduced from 2 to 1 to avoid conflicts
        self.max_retries = 2
        self.timeout = 60  # Increased from 30s to 60s
        self.model_lock = threading.Lock()  # Add lock to prevent concurrent access
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
    
    async def generate_text_async(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> Optional[str]:
        """Async wrapper for text generation with Ollama"""
        if not ollama_available:
            print("⚠️  Ollama not available")
            return None
        
        try:
            print(f"🤖 Ollama: Generating with {max_tokens} tokens, temp={temperature}")
            print(f"📝 LLM Prompt: {prompt[:100]}...")
            
            # Run the synchronous Ollama request in a thread pool with lock
            loop = asyncio.get_event_loop()
            
            def generate_text():
                with self.model_lock:  # Use lock to prevent concurrent access
                    try:
                        # Prepare the request for Ollama
                        payload = {
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": temperature,
                                "num_predict": max_tokens
                            }
                        }
                        
                        response = requests.post(
                            f"{self.base_url}/api/generate",
                            json=payload,
                            timeout=self.timeout
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            return result.get("response", "")
                        else:
                            print(f"❌ Ollama API error: {response.status_code} - {response.text}")
                            return None
                            
                    except Exception as e:
                        print(f"❌ Ollama generation error: {e}")
                        return None
            
            # Execute with timeout
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, generate_text),
                timeout=self.timeout
            )
            
            if result:
                print(f"✅ Ollama Response: {result[:200]}...")
                return result
            return None
            
        except asyncio.TimeoutError:
            print(f"❌ Ollama generation timed out after {self.timeout}s")
            return None
        except asyncio.CancelledError:
            print(f"❌ Ollama generation was cancelled")
            return None
        except Exception as e:
            print(f"❌ Ollama generation error: {e}")
            return None
    
    async def generate_structured_response(self, prompt: str, max_tokens: int = 150, 
                                         temperature: float = 0.7, retries: int = None) -> Optional[Dict]:
        """Generate structured JSON response with retries"""
        if retries is None:
            retries = self.max_retries
        
        # Determine expected key from prompt
        expected_key = None
        if "trending_topics" in prompt:
            expected_key = "trending_topics"
        elif "keyword_gaps" in prompt:
            expected_key = "keyword_gaps"
        elif "title_suggestions" in prompt:
            expected_key = "title_suggestions"
        elif "keyword_clusters" in prompt:
            expected_key = "keyword_clusters"
        elif "viewer_questions" in prompt:
            expected_key = "viewer_questions"
        elif "regional_keywords" in prompt:
            expected_key = "regional_keywords"
        
        for attempt in range(retries + 1):
            try:
                print(f"🔍 LLM Attempt {attempt + 1}: Generating response...")
                raw_response = await self.generate_text_async(prompt, max_tokens, temperature)
                if not raw_response:
                    print(f"❌ LLM Attempt {attempt + 1}: No response generated")
                    continue
                
                print(f"📝 LLM Raw Response: {raw_response[:200]}...")
                
                # Validate response relevance
                if expected_key and not self._validate_llm_response(raw_response, expected_key):
                    print(f"❌ LLM Attempt {attempt + 1}: Response is irrelevant, retrying...")
                    continue
                
                # Extract JSON from response
                json_response = self._extract_json_from_response(raw_response, prompt)
                if json_response:
                    print(f"✅ LLM Attempt {attempt + 1}: JSON extracted successfully")
                    return json_response
                
                print(f"❌ LLM Attempt {attempt + 1}: Failed to extract JSON")
                
            except Exception as e:
                print(f"❌ LLM Attempt {attempt + 1} failed: {e}")
                
            if attempt < retries:
                await asyncio.sleep(1.0)  # Longer delay before retry
        
        print(f"❌ All {retries + 1} attempts failed for prompt")
        return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> Dict:
        """Generate fallback response when LLM fails"""
        print("🔄 Generating fallback response...")
        
        # Extract keywords from prompt for more relevant fallbacks
        keywords = []
        if "Keywords:" in prompt:
            try:
                keywords_section = prompt.split("Keywords:")[1].split("\n")[0]
                keywords = [kw.strip() for kw in keywords_section.split(",") if kw.strip()]
            except:
                keywords = ["content", "youtube", "videos"]
        
        fallback_response = None
        
        if "trending_topics" in prompt:
            if keywords:
                trending_list = []
                for kw in keywords[:5]:
                    trending_list.extend([f"{kw} Trends", f"Latest {kw} News", f"{kw} Innovation"])
                fallback_response = {"trending_topics": trending_list[:5]}
            else:
                fallback_response = {"trending_topics": ["AI Trends", "Digital Transformation", "Remote Work", "Sustainability", "Health Tech"]}
        elif "keyword_gaps" in prompt:
            if keywords:
                gaps_list = []
                for kw in keywords[:5]:
                    gaps_list.extend([f"Advanced {kw}", f"{kw} Best Practices", f"{kw} Case Studies"])
                fallback_response = {"keyword_gaps": gaps_list[:5]}
            else:
                fallback_response = {"keyword_gaps": ["Emerging Technology", "Industry Insights", "Best Practices", "Case Studies", "Expert Tips"]}
        elif "title_suggestions" in prompt:
            if keywords:
                titles_list = []
                for kw in keywords[:5]:
                    titles_list.extend([f"Top 5 {kw} Tips", f"How to Master {kw}", f"The Ultimate {kw} Guide"])
                fallback_response = {"title_suggestions": titles_list[:5]}
            else:
                fallback_response = {"title_suggestions": ["Top 5 Trends in 2024", "How to Master This Skill", "The Ultimate Guide", "Secrets Revealed", "What You Need to Know"]}
        elif "keyword_clusters" in prompt:
            if keywords:
                clusters = {}
                for i, kw in enumerate(keywords[:6]):
                    cluster_name = f"series{i+1}"
                    clusters[cluster_name] = [kw, f"{kw} tips", f"{kw} guide"]
                fallback_response = {"keyword_clusters": clusters}
            else:
                fallback_response = {"keyword_clusters": {"Beginner": ["Basics", "Introduction", "Getting Started"], "Advanced": ["Expert Tips", "Advanced Techniques", "Pro Strategies"]}}
        elif "viewer_questions" in prompt:
            if keywords:
                questions_list = []
                for kw in keywords[:6]:
                    questions_list.extend([f"How do I get started with {kw}?", f"What are the best {kw} practices?", f"How can I improve my {kw} skills?"])
                fallback_response = {"viewer_questions": questions_list[:6]}
            else:
                fallback_response = {"viewer_questions": ["How do I get started?", "What are the best practices?", "How can I improve?", "What should I avoid?", "What are the latest trends?", "How do I succeed?"]}
        elif "regional_keywords" in prompt:
            if keywords:
                regional_list = []
                for kw in keywords[:5]:
                    regional_list.extend([f"Local {kw}", f"{kw} in your region", f"Regional {kw} trends"])
                fallback_response = {"regional_keywords": regional_list[:5]}
            else:
                fallback_response = {"regional_keywords": ["Local Trends", "Regional Insights", "Cultural Relevance", "Local Best Practices", "Regional Success Stories"]}
        else:
            fallback_response = {"result": ["Sample response 1", "Sample response 2", "Sample response 3"]}
        
        # Clean the fallback response to ensure no key names are in list items
        cleaned_response = self._clean_response_data(fallback_response)
        print(f"🧹 Cleaned fallback response: {cleaned_response}")
        
        return cleaned_response
    
    def _clean_response_data(self, data: Dict) -> Dict:
        """Clean response data to remove key names from list items"""
        print(f"🧹 Cleaning response data: {data}")
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                # Remove any list items that are just the key name
                cleaned_list = [item for item in value if item != key]
                print(f"🧹 Cleaned {key}: {value} -> {cleaned_list}")
                cleaned_data[key] = cleaned_list
            else:
                cleaned_data[key] = value
        print(f"🧹 Final cleaned data: {cleaned_data}")
        return cleaned_data

    def _extract_json_from_response(self, response: str, prompt: str) -> Optional[Dict]:
        """Extract and validate JSON from LLM response"""
        try:
            print(f"🔍 Extracting JSON from response...")
            print(f"📝 Full response: {response}")
            
            # Remove the prompt from response
            clean_response = response.replace(prompt, "").strip()
            print(f"🧹 Cleaned response: {clean_response}")
            
            # Check if response contains expected keys
            expected_keys = ["trending_topics", "keyword_gaps", "title_suggestions", "keyword_clusters", "viewer_questions", "regional_keywords"]
            has_expected_key = any(key in clean_response for key in expected_keys)
            
            if not has_expected_key:
                print(f"❌ Response does not contain expected JSON keys")
                return None
            
            # Try to find JSON object in response
            json_start = clean_response.find('{')
            json_end = clean_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = clean_response[json_start:json_end]
                print(f"📋 Extracted JSON string: {json_str}")
                
                # Try to fix common JSON issues
                json_str = json_str.replace("'", '"')  # Replace single quotes
                json_str = json_str.replace("None", "null")  # Replace Python None
                json_str = json_str.replace("True", "true")  # Replace Python True
                json_str = json_str.replace("False", "false")  # Replace Python False
                
                # Remove any trailing text after the JSON
                if json_str.count('{') == json_str.count('}'):
                    # Balanced braces, try to parse
                    try:
                        parsed_json = json.loads(json_str)
                        print(f"✅ Successfully parsed JSON: {parsed_json}")
                        
                        # Clean the response data
                        cleaned_json = self._clean_response_data(parsed_json)
                        print(f"🧹 Cleaned JSON: {cleaned_json}")
                        
                        return cleaned_json
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        # Try to repair the JSON
                        return self._attempt_json_repair(json_str)
                else:
                    print(f"❌ Unbalanced braces in JSON")
                    return None
            
            # If no braces found, try to parse the whole response
            print(f"⚠️  No braces found, trying to parse whole response")
            clean_response = clean_response.replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")
            
            # Try to extract any JSON-like structure
            try:
                parsed_json = json.loads(clean_response)
                print(f"✅ Successfully parsed whole response: {parsed_json}")
                
                # Clean the response data
                cleaned_json = self._clean_response_data(parsed_json)
                print(f"🧹 Cleaned JSON: {cleaned_json}")
                
                return cleaned_json
            except json.JSONDecodeError:
                print(f"❌ Could not parse as JSON")
                return self._attempt_json_repair(clean_response)
            
        except Exception as e:
            print(f"❌ Unexpected error in JSON extraction: {e}")
            return None
    
    def _attempt_json_repair(self, text: str) -> Optional[Dict]:
        """Attempt to repair malformed JSON"""
        try:
            print(f"🔧 Attempting to repair JSON: {text[:100]}...")
            
            # First, try to extract just the JSON part by looking for the last valid JSON structure
            import re
            
            # Look for JSON patterns with the expected keys
            json_patterns = [
                r'\{[^}]*"trending_topics"[^}]*\}',
                r'\{[^}]*"keyword_gaps"[^}]*\}',
                r'\{[^}]*"title_suggestions"[^}]*\}',
                r'\{[^}]*"keyword_clusters"[^}]*\}',
                r'\{[^}]*"viewer_questions"[^}]*\}',
                r'\{[^}]*"regional_keywords"[^}]*\}'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # Take the last match (most likely to be the actual response)
                    json_str = matches[-1]
                    print(f"🔧 Found JSON pattern: {json_str}")
                    
                    try:
                        # Try to parse the extracted JSON
                        json_str = json_str.replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")
                        parsed_json = json.loads(json_str)
                        print(f"✅ Successfully parsed extracted JSON: {parsed_json}")
                        
                        # Clean the response data
                        cleaned_json = self._clean_response_data(parsed_json)
                        print(f"🧹 Cleaned extracted JSON: {cleaned_json}")
                        
                        return cleaned_json
                    except json.JSONDecodeError:
                        print(f"❌ Could not parse extracted JSON")
                        continue
            
            # If no JSON patterns found, try to extract list-like content
            if '"trending_topics"' in text or '"keyword_gaps"' in text or '"title_suggestions"' in text:
                # Extract content between quotes as list items
                quoted_items = re.findall(r'"([^"]*)"', text)
                
                if quoted_items:
                    # Determine the key based on content
                    repaired_json = None
                    if 'trending' in text.lower():
                        repaired_json = {"trending_topics": quoted_items[:5]}
                    elif 'gap' in text.lower():
                        repaired_json = {"keyword_gaps": quoted_items[:5]}
                    elif 'title' in text.lower():
                        repaired_json = {"title_suggestions": quoted_items[:5]}
                    elif 'cluster' in text.lower():
                        repaired_json = {"keyword_clusters": {"series1": quoted_items[:3], "series2": quoted_items[3:6]}}
                    elif 'question' in text.lower():
                        repaired_json = {"viewer_questions": quoted_items[:6]}
                    elif 'regional' in text.lower():
                        repaired_json = {"regional_keywords": quoted_items[:5]}
                    
                    if repaired_json:
                        # Clean the repaired JSON
                        cleaned_json = self._clean_response_data(repaired_json)
                        print(f"🧹 Cleaned repaired JSON: {cleaned_json}")
                        return cleaned_json
            
            # If no structured content found, try to extract any list-like content
            # Look for patterns like: ["item1", "item2", "item3"]
            list_pattern = r'\[([^\]]*)\]'
            matches = re.findall(list_pattern, text)
            
            if matches:
                # Extract items from the first list found
                items_str = matches[0]
                # Split by comma and clean up
                items = [item.strip().strip('"\'') for item in items_str.split(',') if item.strip()]
                
                if items:
                    # Determine the type based on the prompt content
                    repaired_json = None
                    if 'trending' in text.lower():
                        repaired_json = {"trending_topics": items[:5]}
                    elif 'gap' in text.lower():
                        repaired_json = {"keyword_gaps": items[:5]}
                    elif 'title' in text.lower():
                        repaired_json = {"title_suggestions": items[:5]}
                    elif 'cluster' in text.lower():
                        repaired_json = {"keyword_clusters": {"series1": items[:3], "series2": items[3:6]}}
                    elif 'question' in text.lower():
                        repaired_json = {"viewer_questions": items[:6]}
                    elif 'regional' in text.lower():
                        repaired_json = {"regional_keywords": items[:5]}
                    
                    if repaired_json:
                        # Clean the repaired JSON
                        cleaned_json = self._clean_response_data(repaired_json)
                        print(f"🧹 Cleaned repaired JSON: {cleaned_json}")
                        return cleaned_json
            
            print(f"❌ Could not repair JSON from: {text[:100]}...")
            return None
        except Exception as e:
            print(f"❌ JSON repair error: {e}")
            return None

    def _validate_llm_response(self, response: str, expected_key: str) -> bool:
        """Validate if LLM response is relevant to the task"""
        # Check if response contains the expected JSON key
        if expected_key not in response:
            return False
        
        # Check if response contains irrelevant content (more specific patterns)
        irrelevant_patterns = [
            "please help me", "pull requests", "improve this code", "will not provide",
            "i cannot", "i'm sorry", "i don't have", "i am not able",
            "json object is created", "json endpoint", "json function",
            "markup", "html", "xml", "javascript", "function"
        ]
        
        response_lower = response.lower()
        for pattern in irrelevant_patterns:
            if pattern in response_lower:
                print(f"❌ Response contains irrelevant content: {pattern}")
                return False
        
        # Check if response has proper JSON structure
        if "{" not in response or "}" not in response:
            return False
        
        # Check if response contains the expected key in a JSON-like structure
        if f'"{expected_key}"' not in response and f"'{expected_key}'" not in response:
            return False
        
        return True


class ChannelStrategyAnalyzer:
    """Main analyzer for channel strategic insights"""
    
    def __init__(self):
        self.llm_service = AsyncLLMService()
        self.prompts = LLMPrompts()
    
    async def analyze_channel_strategy(self, channel_id: str, region: str = "global", 
                                     language: str = "en") -> Optional[ChannelStrategyResponse]:
        """Analyze channel strategy using LLM"""
        try:
            print(f"🎯 Starting channel strategy analysis for {channel_id}")
            print(f"🌍 Region: {region}, Language: {language}")
            
            if not ollama_available:
                print("⚠️  Ollama not available for strategic analysis")
                return None
            
            # Get existing channel data from database
            print("📊 Getting channel data from database...")
            channel_data = await self._get_channel_data(channel_id)
            
            # If no channel data exists, create fallback data
            if not channel_data:
                print(f"⚠️  No channel data found for {channel_id}, using fallback data")
                channel_data = {
                    "titles": ["general content", "youtube", "content creation"],
                    "total_videos_analyzed": 0,
                    "video_count": 3
                }
            
            print(f"✅ Channel data retrieved: {len(str(channel_data))} characters")
            
            # Extract keywords from existing analysis
            print("🔍 Extracting keywords from channel data...")
            existing_keywords = self._extract_keywords_from_data(channel_data)
            print(f"📝 Found {len(existing_keywords)} keywords: {existing_keywords[:5]}")
            
            # Create context for LLM
            context = self._create_channel_context(channel_data, existing_keywords)
            print(f"📋 Created context: {context}")
            
            # Run all strategic analysis sequentially to avoid model conflicts
            print("🚀 Starting sequential LLM analysis...")
            
            try:
                trending_topics = await self._analyze_trending_topics(context, region, language)
                keyword_gaps = await self._analyze_keyword_gaps(existing_keywords, region, language)
                title_suggestions = await self._analyze_title_suggestions(existing_keywords[:5], region, language)
                keyword_clusters = await self._analyze_keyword_clusters(existing_keywords)
                viewer_questions = await self._analyze_viewer_questions(existing_keywords[:8], region, language)
                regional_keywords = await self._analyze_regional_keywords(existing_keywords[:8], region, language)
                
                print(f"✅ LLM analysis completed, processing 6 results")
                
                print(f"📊 Results summary:")
                print(f"  - Trending topics: {len(trending_topics)}")
                print(f"  - Keyword gaps: {len(keyword_gaps)}")
                print(f"  - Title suggestions: {len(title_suggestions)}")
                print(f"  - Keyword clusters: {len(keyword_clusters)}")
                print(f"  - Viewer questions: {len(viewer_questions)}")
                print(f"  - Regional keywords: {len(regional_keywords)}")
                
                # Create strategic insights
                print("🏗️  Creating strategic insights object...")
                strategic_insights = StrategicInsights(
                    trending_topics=trending_topics,
                    keyword_gaps=keyword_gaps,
                    title_suggestions=title_suggestions,
                    keyword_clusters=keyword_clusters,
                    viewer_questions=viewer_questions,
                    regional_keywords=regional_keywords
                )
                
                print("🏗️  Creating channel strategy response...")
                response = ChannelStrategyResponse(
                    channel_id=channel_id,
                    analysis_timestamp=str(pd.Timestamp.now()),
                    region=region,
                    language=language,
                    strategic_insights=strategic_insights
                )
                
                print("✅ Channel strategy analysis completed successfully")
                return response
                
            except asyncio.CancelledError:
                print("❌ Analysis was cancelled")
                return None
            except Exception as e:
                print(f"❌ Analysis error: {e}")
                return None
            
        except asyncio.CancelledError:
            print("❌ Channel strategy analysis was cancelled")
            return None
        except Exception as e:
            print(f"💥 Channel strategy analysis error: {e}")
            print(f"📋 Error type: {type(e).__name__}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            return None
    
    async def _get_channel_data(self, channel_id: str) -> Optional[Dict]:
        """Get existing channel analysis data from database"""
        try:
            await db_manager.create_table_if_not_exists()
            data = await db_manager.get_channel_engagement(channel_id, "keyword_analysis")
            
            if data:
                # Extract only titles from the stored data to optimize LLM input
                titles = []
                if 'top_keywords' in data:
                    for kw in data['top_keywords']:
                        if isinstance(kw, dict) and 'keyword' in kw:
                            titles.append(kw['keyword'])
                        elif hasattr(kw, 'keyword'):
                            titles.append(kw.keyword)
                
                # Return optimized data structure with only essential information
                return {
                    "titles": titles,
                    "total_videos_analyzed": data.get('total_videos_analyzed', 0),
                    "video_count": len(titles)
                }
            
            return None
        except Exception as e:
            print(f"❌ Error getting channel data: {e}")
            return None
    
    def _extract_keywords_from_data(self, channel_data: Dict) -> List[str]:
        """Extract keywords from stored channel data (optimized for titles only)"""
        if channel_data and 'titles' in channel_data:
            return channel_data['titles']
        return []
    
    def _create_channel_context(self, channel_data: Dict, keywords: List[str]) -> str:
        """Create context summary for LLM analysis (optimized for titles only)"""
        video_count = channel_data.get('total_videos_analyzed', 0)
        top_titles = ', '.join(keywords[:5]) if keywords else 'general content'
        return f"Channel with {video_count} videos covering topics like {top_titles}"
    
    async def _analyze_trending_topics(self, context: str, region: str, language: str) -> List[str]:
        """Analyze trending topics using LLM"""
        try:
            prompt = self.prompts.trending_topics_prompt(context, region, language)
            result = await self.llm_service.generate_structured_response(prompt, max_tokens=150, temperature=0.8)
            
            if result and 'trending_topics' in result:
                return result['trending_topics'][:5]
            
            print("⚠️  No valid trending topics structure returned from LLM")
            return []
            
        except Exception as e:
            print(f"❌ Trending topics analysis error: {e}")
            return []
    
    async def _analyze_keyword_gaps(self, keywords: List[str], region: str, language: str) -> List[str]:
        """Analyze keyword gaps using LLM"""
        try:
            prompt = self.prompts.keyword_gaps_prompt(keywords, region, language)
            result = await self.llm_service.generate_structured_response(prompt, max_tokens=150, temperature=0.7)
            
            if result and 'keyword_gaps' in result:
                return result['keyword_gaps'][:5]
            
            print("⚠️  No valid keyword gaps structure returned from LLM")
            return []
            
        except Exception as e:
            print(f"❌ Keyword gaps analysis error: {e}")
            return []
    
    async def _analyze_title_suggestions(self, keywords: List[str], region: str, language: str) -> List[str]:
        """Analyze title suggestions using LLM"""
        try:
            prompt = self.prompts.title_suggestions_prompt(keywords, region, language)
            result = await self.llm_service.generate_structured_response(prompt, max_tokens=200, temperature=0.9)
            
            if result and 'title_suggestions' in result:
                return result['title_suggestions'][:5]
            
            print("⚠️  No valid title suggestions structure returned from LLM")
            return []
            
        except Exception as e:
            print(f"❌ Title suggestions analysis error: {e}")
            return []
    
    async def _analyze_keyword_clusters(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Analyze keyword clusters using LLM"""
        try:
            if not keywords or len(keywords) < 3:
                return {}
            
            prompt = self.prompts.keyword_clusters_prompt(keywords)
            result = await self.llm_service.generate_structured_response(prompt, max_tokens=180, temperature=0.6)
            
            if result and 'keyword_clusters' in result:
                return result['keyword_clusters']
            
            print("⚠️  No valid keyword clusters structure returned from LLM")
            return {}
            
        except Exception as e:
            print(f"❌ Keyword clusters analysis error: {e}")
            return {}
    
    async def _analyze_viewer_questions(self, keywords: List[str], region: str, language: str) -> List[str]:
        """Analyze viewer questions using LLM"""
        try:
            prompt = self.prompts.viewer_questions_prompt(keywords, region, language)
            result = await self.llm_service.generate_structured_response(prompt, max_tokens=150, temperature=0.7)
            
            if result and 'viewer_questions' in result:
                # Ensure all questions end with question marks
                questions = []
                for q in result['viewer_questions'][:6]:
                    if q and len(q) > 5:
                        if not q.endswith('?'):
                            q += '?'
                        questions.append(q)
                return questions
            
            print("⚠️  No valid viewer questions structure returned from LLM")
            return []
            
        except Exception as e:
            print(f"❌ Viewer questions analysis error: {e}")
            return []
    
    async def _analyze_regional_keywords(self, keywords: List[str], region: str, language: str) -> List[str]:
        """Analyze regional keywords using LLM"""
        try:
            prompt = self.prompts.regional_keywords_prompt(keywords, region, language)
            result = await self.llm_service.generate_structured_response(prompt, max_tokens=120, temperature=0.8)
            
            if result and 'regional_keywords' in result:
                return result['regional_keywords'][:5]
            
            print("⚠️  No valid regional keywords structure returned from LLM")
            return []
            
        except Exception as e:
            print(f"❌ Regional keywords analysis error: {e}")
            return []


# Initialize analyzer
analyzer = ChannelStrategyAnalyzer()

# API Endpoints
@app.post("/analyze-channel-strategy", response_model=ChannelStrategyResponse)
async def analyze_channel_strategy(request: ChannelStrategyRequest):
    """
    Analyze channel strategy and provide comprehensive strategic recommendations
    
    This endpoint:
    1. Reads existing channel analysis from database using channel_id
    2. Uses LLM to analyze gaps and opportunities
    3. Provides strategic insights including:
        * Trending topics not covered
        * Keyword gaps vs competitors
        * Video title suggestions
        * Keyword clustering for content series
        * Viewer question analysis
        * Regional/language-specific keywords
    """
    try:
        logger.info(f"🎯 Starting channel strategy analysis for {request.channel_id}")
        logger.info(f"🌍 Region: {request.region}, Language: {request.language}")
        
        result = await analyzer.analyze_channel_strategy(
            request.channel_id,
            request.region,
            request.language
        )
        
        logger.info(f"📊 Analysis result type: {type(result)}")
        logger.info(f"📊 Analysis result: {result is not None}")
        
        if result:
            logger.info("💾 Saving analysis results to database...")
            # Save analysis results to database
            save_success = await db_manager.save_channel_engagement(
                request.channel_id,
                "channel_strategy",
                result.dict()
            )
            logger.info(f"💾 Save success: {save_success}")
            
            logger.info(f"✅ Channel strategy analysis completed for {request.channel_id}")
            return result
        else:
            logger.error("❌ Analysis returned None")
            raise HTTPException(status_code=500, detail="Channel strategy analysis failed")
    
    except Exception as e:
        logger.error(f"💥 Analysis error: {e}")
        logger.error(f"📋 Error type: {type(e).__name__}")
        import traceback
        logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/channel-engagement/{channel_id}/{engagement_type}", response_model=ChannelEngagementResponse)
async def get_channel_engagement(channel_id: str, engagement_type: str):
    """
    Retrieve channel engagement data by channel_id and engagement_type
    """
    try:
        await db_manager.create_table_if_not_exists()
        data = await db_manager.get_channel_engagement(channel_id, engagement_type)
        
        return ChannelEngagementResponse(
            channel_id=channel_id,
            engagement_type=engagement_type,
            data=data,
            found=data is not None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database retrieval failed: {str(e)}")

@app.post("/channel-engagement", response_model=Dict[str, str])
async def save_channel_engagement(engagement_data: ChannelEngagementSave):
    """
    Save or update channel engagement data
    """
    try:
        logger.info(f"🔧 Attempting to save engagement data for channel: {engagement_data.channel_id}")
        logger.info(f"📊 Engagement type: {engagement_data.engagement_type}")
        logger.info(f"📝 Data size: {len(str(engagement_data.data))} characters")
        
        await db_manager.create_table_if_not_exists()
        logger.info("✅ Table creation/check completed")
        
        success = await db_manager.save_channel_engagement(
            engagement_data.channel_id,
            engagement_data.engagement_type,
            engagement_data.data
        )
        
        logger.info(f"💾 Database save result: {success}")
        
        if success:
            return {
                "message": "Channel engagement data saved successfully",
                "channel_id": engagement_data.channel_id,
                "engagement_type": engagement_data.engagement_type
            }
        else:
            logger.error("❌ Database save returned False")
            raise HTTPException(status_code=500, detail="Failed to save data")
    
    except Exception as e:
        logger.error(f"💥 Save engagement error: {e}")
        logger.error(f"📋 Error type: {type(e).__name__}")
        import traceback
        logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")

@app.post("/analyze-keywords", response_model=ChannelStrategyResponse)
@app.post("//analyze-keywords", response_model=ChannelStrategyResponse)  # Handle double slash variant
async def analyze_keywords(request: KeywordAnalysisRequest):
    """
    Analyze keywords directly using LLM without requiring pre-existing database data
    
    This endpoint:
    1. Takes keywords as direct input
    2. Uses LLM to analyze strategic insights
    3. Provides comprehensive recommendations based on provided keywords
    """
    try:
        print(f"🎯 Starting keyword analysis for {request.channel_id}")
        print(f"🔍 Keywords provided: {request.keywords}")
        print(f"🌍 Region: {request.region}, Language: {request.language}")
        
        if not ollama_available:
            print("⚠️  Ollama not available for keyword analysis")
            raise HTTPException(status_code=500, detail="LLM model not available")
        
        if not request.keywords:
            raise HTTPException(status_code=400, detail="At least one keyword is required")
        
        # Create context from provided keywords
        context = f"Channel covering topics like {', '.join(request.keywords[:5])}"
        print(f"📋 Created context: {context}")
        
        # Run all strategic analysis concurrently using provided keywords
        print("🚀 Starting concurrent LLM analysis with provided keywords...")
        results = await asyncio.gather(
            analyzer._analyze_trending_topics(context, request.region, request.language),
            analyzer._analyze_keyword_gaps(request.keywords, request.region, request.language),
            analyzer._analyze_title_suggestions(request.keywords[:5], request.region, request.language),
            analyzer._analyze_keyword_clusters(request.keywords),
            analyzer._analyze_viewer_questions(request.keywords[:8], request.region, request.language),
            analyzer._analyze_regional_keywords(request.keywords[:8], request.region, request.language),
            return_exceptions=True
        )
        
        print(f"✅ LLM analysis completed, processing {len(results)} results")
        
        # Extract results with fallbacks
        trending_topics = results[0] if not isinstance(results[0], Exception) else []
        keyword_gaps = results[1] if not isinstance(results[1], Exception) else []
        title_suggestions = results[2] if not isinstance(results[2], Exception) else []
        keyword_clusters = results[3] if not isinstance(results[3], Exception) else {}
        viewer_questions = results[4] if not isinstance(results[4], Exception) else []
        regional_keywords = results[5] if not isinstance(results[5], Exception) else []
        
        print(f"📊 Results summary:")
        print(f"  - Trending topics: {len(trending_topics)}")
        print(f"  - Keyword gaps: {len(keyword_gaps)}")
        print(f"  - Title suggestions: {len(title_suggestions)}")
        print(f"  - Keyword clusters: {len(keyword_clusters)}")
        print(f"  - Viewer questions: {len(viewer_questions)}")
        print(f"  - Regional keywords: {len(regional_keywords)}")
        
        # Log any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                operation_names = ["trending_topics", "keyword_gaps", "title_suggestions", 
                                 "keyword_clusters", "viewer_questions", "regional_keywords"]
                print(f"❌ LLM operation '{operation_names[i]}' failed: {result}")
        
        # Create strategic insights
        print("🏗️  Creating strategic insights object...")
        strategic_insights = StrategicInsights(
            trending_topics=trending_topics,
            keyword_gaps=keyword_gaps,
            title_suggestions=title_suggestions,
            keyword_clusters=keyword_clusters,
            viewer_questions=viewer_questions,
            regional_keywords=regional_keywords
        )
        
        print("🏗️  Creating channel strategy response...")
        response = ChannelStrategyResponse(
            channel_id=request.channel_id,
            analysis_timestamp=str(pd.Timestamp.now()),
            region=request.region,
            language=request.language,
            strategic_insights=strategic_insights
        )
        
        print("✅ Keyword analysis completed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Keyword analysis error: {e}")
        print(f"📋 Error type: {type(e).__name__}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Keyword analysis failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "YouTube Channel Strategy Analyzer API",
        "version": "2.0.0",
        "description": "AI-powered channel analysis and strategic recommendations",
        "endpoints": {
            "POST /analyze-channel-strategy": "Main channel strategy analysis (uses stored data)",
            "POST /analyze-keywords": "Direct keyword analysis (accepts keywords as input)",
            "GET /channel-engagement/{channel_id}/{engagement_type}": "Retrieve stored data",
            "POST /channel-engagement": "Save analysis data",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = "connected"
        try:
            await db_manager.create_table_if_not_exists()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Check Ollama connection
        ollama_status = "available" if ollama_available else "unavailable"
        
        return {
            "status": "healthy",
            "database_status": db_status,
            "ollama_model_status": ollama_status,
            "ai_features_enabled": ollama_available,
            "version": "2.0.0",
            "configuration": settings.get_config_summary()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": "2.0.0"
        }

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight"""
    return {"message": "OK"}

if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal, shutting down gracefully...")
        sys.exit(0)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🚀 Starting YouTube Channel Strategy Analyzer...")
        print(f"📊 Server will be available at: http://{settings.api_host}:{settings.api_port}")
        print(f"📚 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
        print(f"🔍 Health Check: http://{settings.api_host}:{settings.api_port}/health")
        print(f"⚙️  Environment: {settings.environment}")
        print(f"🗄️  Database: {settings.database_url}")
        print("=" * 60)
        
        uvicorn.run(
            "main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=False,  # Disable reload to prevent issues
            log_level=settings.api_log_level,
            access_log=True,
            workers=settings.api_workers,  # Use configured workers
            timeout_keep_alive=30,  # Reduce keep-alive timeout
            timeout_graceful_shutdown=10  # Add graceful shutdown timeout
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1) 