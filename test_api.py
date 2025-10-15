#!/usr/bin/env python3
"""
Test script for the IITM Task Handler API
"""

import asyncio
import aiohttp
import json

API_BASE_URL = "http://localhost:8000"

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

async def test_iitm_task():
    """Test the IITM task endpoint"""
    import time
    timestamp = int(time.time())
    
    test_data = {
        "email": "test@example.com",
        "secret": "your_expected_secret_here",  # Update this with actual secret
        "task": f"test-captcha-solver-{timestamp}",
        "round": 1,
        "nonce": f"test{timestamp}",
        "brief": "Create a simple captcha solver that displays an image and solves it",
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
                "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/iitm-task",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("IITM task test passed:", data)
                return True
            else:
                error_text = await response.text()
                print("IITM task test failed:", response.status, error_text)
                return False

async def test_round2():
    """Test the round 2 endpoint"""
    test_data = {
        "secret": "your_expected_secret_here",
        "modification": "Add support for SVG images and improve error handling",
        "repo_name": "23f1002431/iitm-test-captcha-solver-test123-1736865600",  # Use actual repo name
        "email": "test@example.com",
        "task": "test-captcha-solver",
        "nonce": "test123",
        "evaluation_url": "https://httpbin.org/post"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/iitm-round2",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("Round 2 test passed:", data)
                return True
            else:
                error_text = await response.text()
                print("Round 2 test failed:", response.status, error_text)
                return False

async def main():
    """Run all tests"""
    print("Testing IITM Task Handler API...")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = await test_health()
    
    if health_ok:
        # Test IITM task endpoint
        task_ok = await test_iitm_task()
        
        if task_ok:
            # Test round 2 endpoint
            await test_round2()
    
    print("=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
