#!/usr/bin/env python3
"""
Test script for the IITM Task Handler API
Tests both Round 1 (initial task) and Round 2 (modifications)

Usage:
    python test_api.py

Configuration:
    1. Update API_BASE_URL to your deployed API URL
    2. Update TEST_SECRET to match your EXPECTED_SECRET
    3. Update TEST_EMAIL if needed

Test Flow:
    1. Health Check - Verify API is running
    2. API Info - Get API information
    3. Security Tests - Test invalid secret and missing fields
    4. Round 1 - Submit initial task (creates repo and GitHub Pages)
    5. Round 2 - Modify existing repo with new features

Expected JSON Structure for Round 1:
{
  "email": "student@example.com",
  "secret": "your_secret",
  "task": "captcha-solver-...",
  "round": 1,
  "nonce": "ab12-...",
  "brief": "Create a captcha solver that handles ?url=https://.../image.png",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [{"name": "sample.png", "url": "data:image/png;base64,..."}]
}

Expected JSON Structure for Round 2:
{
  "secret": "your_secret",
  "modification": "Add support for SVG images and improve error handling",
  "repo_name": "username/repo-name",
  "email": "student@example.com",
  "task": "captcha-solver-...",
  "nonce": "ab12-...",
  "evaluation_url": "https://example.com/notify"
}
"""

import asyncio
import aiohttp
import json
import time
import base64

# Update this to your actual API URL
API_BASE_URL = "http://localhost:8000"  # For local testing
# API_BASE_URL = "https://your-username-iitm-task-handler.hf.space"  # For Hugging Face Spaces

# Test configuration
TEST_SECRET = "test_secret_123"  # Update with your actual secret
TEST_EMAIL = "student@example.com"

async def test_health():
    """Test the health endpoint"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                print("Health check passed:", data)
                return True
            else:
                print("Health check failed:", response.status)
                return False

async def test_round1():
    """Test Round 1 - Initial task submission"""
    print("\n🧪 Testing Round 1 - Initial Task Submission")
    print("-" * 50)
    
    timestamp = int(time.time())
    task_id = f"captcha-solver-{timestamp}"
    nonce = f"ab12-{timestamp}"
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    test_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": nonce,
        "brief": "Create a captcha solver that handles ?url=https://.../image.png. Default to attached sample.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays captcha URL passed at ?url=...",
            "Page displays solved captcha text within 15 seconds"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Test callback URL
        "attachments": [
            {
                "name": "sample.png",
                "url": f"data:image/png;base64,{test_image_data}"
            }
        ]
    }
    
    print(f"📤 Sending Round 1 request for task: {task_id}")
    print(f"📧 Email: {TEST_EMAIL}")
    print(f"🔑 Nonce: {nonce}")
    print(f"📝 Brief: {test_data['brief']}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/iitm-task",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minute timeout for task processing
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Round 1 test PASSED!")
                    print(f"📊 Response: {json.dumps(data, indent=2)}")
                    
                    # Store repo info for round 2 testing
                    if "repo_url" in data:
                        repo_url = data["repo_url"]
                        # Extract repo name from URL for round 2
                        if "github.com/" in repo_url:
                            repo_name = repo_url.split("github.com/")[1]
                            return {"success": True, "repo_name": repo_name, "task_id": task_id, "nonce": nonce}
                    
                    return {"success": True, "repo_name": None, "task_id": task_id, "nonce": nonce}
                else:
                    error_text = await response.text()
                    print(f"❌ Round 1 test FAILED!")
                    print(f"Status: {response.status}")
                    print(f"Error: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except asyncio.TimeoutError:
            print("❌ Round 1 test TIMEOUT!")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            print(f"❌ Round 1 test ERROR: {str(e)}")
            return {"success": False, "error": str(e)}

async def test_round2(repo_name, task_id, nonce):
    """Test Round 2 - Code modifications"""
    print("\n🧪 Testing Round 2 - Code Modifications")
    print("-" * 50)
    
    if not repo_name:
        print("❌ Cannot test Round 2: No repository name from Round 1")
        return False
    
    test_data = {
        "secret": TEST_SECRET,
        "modification": "Add support for SVG images, improve error handling, and add a dark mode toggle",
        "repo_name": repo_name,
        "email": TEST_EMAIL,
        "task": task_id,
        "nonce": nonce,
        "evaluation_url": "https://httpbin.org/post"
    }
    
    print(f"📤 Sending Round 2 request for repo: {repo_name}")
    print(f"📧 Email: {TEST_EMAIL}")
    print(f"🔑 Nonce: {nonce}")
    print(f"🔧 Modification: {test_data['modification']}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/iitm-round2",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minute timeout for modifications
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Round 2 test PASSED!")
                    print(f"📊 Response: {json.dumps(data, indent=2)}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Round 2 test FAILED!")
                    print(f"Status: {response.status}")
                    print(f"Error: {error_text}")
                    return False
        except asyncio.TimeoutError:
            print("❌ Round 2 test TIMEOUT!")
            return False
        except Exception as e:
            print(f"❌ Round 2 test ERROR: {str(e)}")
            return False

async def test_api_info():
    """Test the API info endpoint"""
    print("\n🧪 Testing API Info Endpoint")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/info") as response:
            if response.status == 200:
                data = await response.json()
                print("✅ API Info test PASSED!")
                print(f"📊 Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ API Info test FAILED: {response.status}")
                return False

async def test_invalid_secret():
    """Test with invalid secret to ensure security"""
    print("\n🧪 Testing Invalid Secret (Security Test)")
    print("-" * 50)
    
    test_data = {
        "email": TEST_EMAIL,
        "secret": "invalid_secret",
        "task": "security-test",
        "round": 1,
        "nonce": "security123",
        "brief": "This should fail due to invalid secret",
        "checks": [],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/iitm-task",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 401:
                print("✅ Invalid secret test PASSED! (Correctly rejected)")
                return True
            else:
                print(f"❌ Invalid secret test FAILED! (Should be 401, got {response.status})")
                return False

async def test_missing_fields():
    """Test with missing required fields"""
    print("\n🧪 Testing Missing Required Fields")
    print("-" * 50)
    
    test_data = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        # Missing task, round, nonce, brief
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/iitm-task",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 500:  # Should fail due to missing fields
                print("✅ Missing fields test PASSED! (Correctly failed)")
                return True
            else:
                print(f"❌ Missing fields test FAILED! (Should be 500, got {response.status})")
                return False

async def main():
    """Run all tests"""
    print("🚀 Testing IITM Task Handler API")
    print("=" * 60)
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"🔑 Test Secret: {TEST_SECRET}")
    print(f"📧 Test Email: {TEST_EMAIL}")
    print("=" * 60)
    
    # Test health endpoint
    print("\n1️⃣ Testing Health Check...")
    health_ok = await test_health()
    
    if not health_ok:
        print("❌ Health check failed. Stopping tests.")
        return
    
    # Test API info
    print("\n2️⃣ Testing API Info...")
    await test_api_info()
    
    # Test security features
    print("\n3️⃣ Testing Security Features...")
    await test_invalid_secret()
    await test_missing_fields()
    
    # Test Round 1 (initial task)
    print("\n4️⃣ Testing Round 1 - Initial Task...")
    round1_result = await test_round1()
    
    if round1_result["success"]:
        print(f"✅ Round 1 completed successfully!")
        
        # Wait a bit before testing Round 2
        print("\n⏳ Waiting 5 seconds before Round 2 test...")
        await asyncio.sleep(5)
        
        # Test Round 2 (modifications)
        print("\n5️⃣ Testing Round 2 - Code Modifications...")
        if round1_result["repo_name"]:
            round2_ok = await test_round2(
                round1_result["repo_name"], 
                round1_result["task_id"], 
                round1_result["nonce"]
            )
            if round2_ok:
                print("✅ Round 2 completed successfully!")
            else:
                print("❌ Round 2 failed!")
        else:
            print("⚠️ Skipping Round 2: No repository name from Round 1")
    else:
        print(f"❌ Round 1 failed: {round1_result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
