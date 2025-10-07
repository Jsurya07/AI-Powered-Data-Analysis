#!/usr/bin/env python3
"""
Quick test script to verify the Gemini model is working correctly
"""
import requests
import json

# Test data
test_request = {
    "columns": ["Name", "Age", "Salary", "Department"],
    "question": "What is the average salary?",
    "dataset_name": "test_dataset"
}

print("🧪 Testing FastAPI + Gemini Integration...")
print(f"📋 Question: {test_request['question']}")
print(f"📊 Columns: {test_request['columns']}")
print("\n" + "="*60 + "\n")

try:
    # Make request to FastAPI
    response = requests.post(
        "http://localhost:8000/generate_code/",
        json=test_request,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("✅ SUCCESS! Model is working correctly!\n")
        print("📝 Generated Code:")
        print("-" * 60)
        print(result.get("generated_code", "No code generated"))
        print("-" * 60)
        print(f"\n⏱️  Execution Time: {result.get('execution_time', 0):.2f} seconds")
        print(f"🆔 Query ID: {result.get('query_id', 'N/A')}")
        
    else:
        print(f"❌ ERROR: Status Code {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to FastAPI service")
    print("Make sure the service is running: docker ps")
    
except requests.exceptions.Timeout:
    print("❌ ERROR: Request timed out (>30 seconds)")
    print("The model might be taking too long to respond")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "="*60)
print("\n💡 If successful, you can now use your Streamlit app!")
print("   Open: http://localhost:8501")
