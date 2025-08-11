#!/usr/bin/env python3
"""Simple health check test"""

import requests
import json

try:
    response = requests.get('http://localhost:8000/health')
    if response.status_code == 200:
        print("✅ Health check successful!")
        data = response.json()
        print(f"📊 Status: {data.get('status')}")
        print(f"🗄️  Database: {data.get('database_status')}")
        print(f"🤖 Ollama: {data.get('ollama_model_status')}")
        
        if 'configuration' in data:
            print("\n🔧 Configuration from environment:")
            config = data['configuration']
            for key, value in config.items():
                print(f"  • {key}: {value}")
        else:
            print("⚠️  No configuration in response")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

