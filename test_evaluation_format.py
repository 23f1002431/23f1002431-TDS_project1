#!/usr/bin/env python3
"""
Test script to show the exact evaluation callback response format
"""

import asyncio
import aiohttp
import json

API_BASE_URL = "http://localhost:8000"

async def test_evaluation_format():
    """Test the evaluation callback format"""
    test_data = {
        "email": "student@example.com",
        "secret": "your_expected_secret_here",
        "task": "captcha-solver-demo",
        "round": 1,
        "nonce": "demo123",
        "brief": "Create a simple captcha solver that displays an image and solves it",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays captcha URL passed at ?url=...",
            "Page displays solved captcha text within 15 seconds"
        ],
        "evaluation_url": "https://httpbin.org/post",  # This will show us the exact format
        "attachments": []
    }
    
    print("Testing evaluation callback format...")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/iitm-task",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("✅ API Response:")
                print(json.dumps(data, indent=2))
                print("\n" + "=" * 60)
                print("📤 Evaluation Callback Format:")
                print("The evaluation callback will be sent to the evaluation_url with this exact structure:")
                print(json.dumps({
                    "email": "student@example.com",
                    "task": "captcha-solver-demo", 
                    "round": 1,
                    "nonce": "demo123",
                    "repo_url": "https://github.com/username/repo-name",
                    "commit_sha": "abc123def456",
                    "pages_url": "https://username.github.io/repo-name/"
                }, indent=2))
                return True
            else:
                error_text = await response.text()
                print(f"❌ Test failed: {response.status} - {error_text}")
                return False

if __name__ == "__main__":
    asyncio.run(test_evaluation_format())
