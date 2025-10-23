#!/usr/bin/env python3
"""
Test script for the /ai/mentor endpoint
Run with: python test_mentor_endpoint.py
"""
import requests
import json

# Base URL (adjust if your server runs on a different port)
BASE_URL = "http://localhost:8000"

def test_mentor_endpoint():
    url = f"{BASE_URL}/ai/mentor"
    
    # Test case 1: Python developer looking to expand
    test_data = {
        "skills": ["python", "web3", "solidity"],
        "focus_areas": ["blockchain", "smart contracts"]
    }
    
    print("🧑‍🏫 Testing /ai/mentor endpoint")
    print(f"📝 Request: {json.dumps(test_data, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Here are the recommendations:")
            print(f"🎯 Input Skills: {data['input_skills']}")
            print(f"🔍 Focus Areas: {data['focus_areas']}")
            print(f"📚 Found {data['total_found']} course recommendations:")
            print()
            
            for i, course in enumerate(data['recommendations'], 1):
                print(f"{i}. 📖 {course['title']}")
                print(f"   🏫 {course['provider']} • {course['instructor']}")
                print(f"   📈 Level: {course['level']}")
                print(f"   🎯 Skill Match: {course['skill_match']}")
                print(f"   📝 {course['description']}")
                print(f"   🔗 {course['url']}")
                if course.get('reasons'):
                    print(f"   💡 Why: {', '.join(course['reasons'])}")
                print()
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure your FastAPI server is running on localhost:8000")
        print("Start server with: uvicorn main:app --reload")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_mentor_endpoint()