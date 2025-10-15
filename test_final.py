#!/usr/bin/env python3
"""
Final Test Script for IITM Task Handler API
Tests both Round 1 and Round 2 with exact JSON structure
"""

import asyncio
import aiohttp
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()
# Set environment variables for testing
API_KEY = os.getenv("AIPIPE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
EXPECTED_SECRET = os.getenv("EXPECTED_SECRET")
# Configuration
API_BASE_URL = "http://localhost:8000"  # Update to your API URL
TEST_SECRET = EXPECTED_SECRET  # Update to match your EXPECTED_SECRET
TEST_EMAIL = "23f1002431@ds.study.iitm.ac.in"
    
async def test_round1():
    """Test Round 1 - Initial task submission"""
    print("🧪 Testing Round 1 - Initial Task Submission")
    print("-" * 50)
    
    timestamp = int(time.time())
    task_id = f"captcha-solver-{timestamp}"
    nonce = f"ab12-{timestamp}"
    
    # Test image (1x1 pixel PNG)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    payload = {
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
        "evaluation_url": "https://httpbin.org/post",
        "attachments": [
            {
                "name": "sample.png",
                "url": f"data:image/png;base64,{test_image}"
            }
        ]
    }
    
    print(f"📤 Sending Round 1 request...")
    print(f"Task: {task_id}")
    print(f"Nonce: {nonce}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/api-endpoint",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Round 1 PASSED!")
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    # Extract repo info for Round 2
                    if "repo_url" in data:
                        repo_url = data["repo_url"]
                        if "github.com/" in repo_url:
                            repo_name = repo_url.split("github.com/")[1]
                            return {"success": True, "repo_name": repo_name, "task_id": task_id, "nonce": nonce}
                    
                    return {"success": True, "repo_name": None, "task_id": task_id, "nonce": nonce}
                else:
                    error = await response.text()
                    print(f"❌ Round 1 FAILED: {response.status}")
                    print(f"Error: {error}")
                    return {"success": False, "error": error}
        except Exception as e:
            print(f"❌ Round 1 ERROR: {str(e)}")
            return {"success": False, "error": str(e)}

async def test_round2(repo_name, task_id, nonce):
    """Test Round 2 - Code modifications"""
    print("\n🧪 Testing Round 2 - Code Modifications")
    print("-" * 50)
    
    if not repo_name:
        print("❌ Cannot test Round 2: No repository name from Round 1")
        return False
    
    payload = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": task_id,
        "round": 2,
        "nonce": nonce,
        "brief": "Add support for SVG images, improve error handling, and add a dark mode toggle",
        "checks": [
            "Maintain existing functionality",
            "Add SVG support",
            "Improve error handling",
            "Add dark mode toggle"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "repo_name": repo_name,
        "attachments": []
    }
    
    print(f"📤 Sending Round 2 request...")
    print(f"Repo: {repo_name}")
    print(f"Task: {task_id}")
    print(f"Nonce: {nonce}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/api-endpoint",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Round 2 PASSED!")
                    print(f"Response: {json.dumps(data, indent=2)}")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ Round 2 FAILED: {response.status}")
                    print(f"Error: {error}")
                    return False
        except Exception as e:
            print(f"❌ Round 2 ERROR: {str(e)}")
            return False

async def test_health():
    """Test health endpoint"""
    print("🧪 Testing Health Check")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Health check PASSED!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Health check FAILED: {response.status}")
                return False

async def main():
    """Run all tests"""
    print("🚀 IITM Task Handler API - Final Test")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print(f"Secret: {TEST_SECRET}")
    print(f"Email: {TEST_EMAIL}")
    print("=" * 60)
    
    # Test health
    health_ok = await test_health()
    if not health_ok:
        print("❌ Health check failed. Stopping tests.")
        return
    
    # Test Round 1
    round1_result = await test_round1()
    
    if round1_result["success"]:
        print("\n✅ Round 1 completed successfully!")
        
        # Wait before Round 2
        print("\n⏳ Waiting 5 seconds before Round 2...")
        await asyncio.sleep(5)
        
        # Test Round 2
        if round1_result["repo_name"]:
            round2_ok = await test_round2(
                round1_result["repo_name"],
                round1_result["task_id"],
                round1_result["nonce"]
            )
            if round2_ok:
                print("\n✅ Round 2 completed successfully!")
            else:
                print("\n❌ Round 2 failed!")
        else:
            print("\n⚠️ Skipping Round 2: No repository name from Round 1")
    else:
        print(f"\n❌ Round 1 failed: {round1_result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
