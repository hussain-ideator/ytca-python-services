# Keyword Intelligence Assistant

A FastAPI application that analyzes keywords from YouTube channel metadata to provide insights and optimization recommendations.

## Features

- **Keyword Extraction**: Extract and rank keywords from video titles, descriptions, and tags
- **Sentiment Analysis**: Analyze the overall sentiment of your content
- **Keyword Categorization**: Automatically categorize keywords into different topics
- **SEO Recommendations**: Get actionable recommendations for keyword optimization
- **Database Integration**: Store and retrieve channel engagement data using SQLite
- **RESTful API**: Easy to integrate with other applications
- **Persistent Storage**: Automatically save keyword analysis results to database

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 3. View API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /analyze-keywords

Analyzes YouTube channel metadata and returns keyword insights. If `channel_id` is provided, results are automatically saved to the database.

**Request Body:**
```json
{
  "videos": [
    {
      "title": "How to Learn Python Programming",
      "description": "A comprehensive guide to learning Python programming for beginners...",
      "tags": ["python", "programming", "tutorial", "coding", "beginner"]
    }
  ],
  "channel_name": "Tech Education Channel",
  "channel_id": "UC_example_channel_id"
}
```

**Response:**
```json
{
  "top_keywords": [
    {"keyword": "python", "frequency": 5},
    {"keyword": "programming", "frequency": 3}
  ],
  "keyword_categories": {
    "technology": ["python", "programming", "coding"],
    "education": ["tutorial", "learn", "guide"]
  },
  "sentiment_analysis": {
    "polarity": 0.2,
    "subjectivity": 0.5
  },
  "total_videos_analyzed": 1,
  "recommendations": [
    "Focus on 'python' as it's your most frequent keyword",
    "Educational content keywords detected - consider adding 'tutorial', 'how-to', or 'beginner' tags"
  ]
}
```

### GET /channel-engagement/{channel_id}/{engagement_type}

Retrieve specific engagement data for a channel.

**Parameters:**
- `channel_id`: YouTube channel ID
- `engagement_type`: Type of engagement (e.g., 'comments', 'likes', 'views', 'keyword_analysis')

**Response:**
```json
{
  "channel_id": "UC_example_channel_id",
  "engagement_type": "comments",
  "data": {
    "total_comments": 1500,
    "avg_sentiment": 0.3
  },
  "found": true
}
```

### POST /channel-engagement

Save or update channel engagement data.

**Request Body:**
```json
{
  "channel_id": "UC_example_channel_id",
  "engagement_type": "comments",
  "data": {
    "total_comments": 1500,
    "avg_sentiment": 0.3,
    "top_commenters": ["user1", "user2"]
  }
}
```

### GET /channel-engagement/{channel_id}

Get all engagement types and their data for a specific channel.

**Response:**
```json
{
  "channel_id": "UC_example_channel_id",
  "engagement_data": {
    "comments": {...},
    "likes": {...},
    "keyword_analysis": {...}
  },
  "total_engagement_types": 3
}
```

### GET /health

Returns the health status of the API and database connection.

## Example Usage

### Keyword Analysis with Database Storage

```python
import requests

# Sample data with channel_id for database storage
data = {
    "videos": [
        {
            "title": "Python Tutorial for Beginners",
            "description": "Learn Python programming from scratch. This comprehensive tutorial covers variables, functions, and more.",
            "tags": ["python", "tutorial", "programming", "beginner", "coding"]
        },
        {
            "title": "Advanced Python Concepts",
            "description": "Dive deep into advanced Python concepts like decorators, generators, and metaclasses.",
            "tags": ["python", "advanced", "programming", "decorators", "generators"]
        }
    ],
    "channel_name": "Python Master",
    "channel_id": "UC_python_master_123"
}

# Analyze keywords (results automatically saved to database)
response = requests.post("http://localhost:8000/analyze-keywords", json=data)
result = response.json()

print(f"Top keywords: {result['top_keywords']}")
print(f"Recommendations: {result['recommendations']}")
```

### Database Operations

```python
# Save custom engagement data
engagement_data = {
    "channel_id": "UC_python_master_123",
    "engagement_type": "comments",
    "data": {
        "total_comments": 1500,
        "avg_sentiment": 0.3,
        "top_commenters": ["user1", "user2", "user3"]
    }
}

response = requests.post("http://localhost:8000/channel-engagement", json=engagement_data)
print(response.json())

# Retrieve specific engagement data
response = requests.get("http://localhost:8000/channel-engagement/UC_python_master_123/comments")
result = response.json()

if result['found']:
    print(f"Comments data: {result['data']}")

# Get all engagement data for a channel
response = requests.get("http://localhost:8000/channel-engagement/UC_python_master_123")
all_data = response.json()
print(f"Total engagement types: {all_data['total_engagement_types']}")
```

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API

#### Test Keyword Analysis
```bash
curl -X POST "http://localhost:8000/analyze-keywords" \
     -H "Content-Type: application/json" \
     -d '{
       "videos": [
         {
           "title": "How to Build a Web App",
           "description": "Learn to build modern web applications with Python and FastAPI",
           "tags": ["web", "python", "fastapi", "tutorial"]
         }
       ],
       "channel_id": "UC_test_channel"
     }'
```

#### Test Database Operations
```bash
# Save engagement data
curl -X POST "http://localhost:8000/channel-engagement" \
     -H "Content-Type: application/json" \
     -d '{
       "channel_id": "UC_test_channel",
       "engagement_type": "views",
       "data": {"total_views": 100000, "avg_watch_time": "4:30"}
     }'

# Retrieve engagement data
curl "http://localhost:8000/channel-engagement/UC_test_channel/views"

# Get all engagement data
curl "http://localhost:8000/channel-engagement/UC_test_channel"
```

#### Run Test Scripts
```bash
# Test keyword analysis functionality
python test_api.py

# Test database functionality
python test_database.py
```

## License

MIT License 