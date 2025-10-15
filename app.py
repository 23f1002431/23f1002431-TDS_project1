from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import base64
import asyncio
import aiohttp
import time
from datetime import datetime
from llm_utils import generate_code, modify_code
from github_utils import create_repo, update_repo, enable_github_pages
from config.settings import AIPIPE_API_KEY, GITHUB_TOKEN, EXPECTED_SECRET

app = FastAPI(title="IITM Task Handler", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api-endpoint")
async def handle_iitm_task(request: Request):
    """Handle IITM task submission - Both Round 1 and Round 2"""
    try:
        data = await request.json()
        
        # Validate secret
        provided_secret = data.get("secret")
        if provided_secret != EXPECTED_SECRET:
            raise HTTPException(status_code=401, detail="Invalid secret")
        
        # Extract task details
        email = data.get("email", "")
        task = data.get("task", "")
        round_num = data.get("round", 1)
        nonce = data.get("nonce", "")
        brief = data.get("brief", "")
        checks = data.get("checks", [])
        evaluation_url = data.get("evaluation_url", "")
        attachments = data.get("attachments", [])
        repo_name = data.get("repo_name", "")
        
        if round_num == 1:
            # Round 1: Create new repository
            timestamp = int(time.time())
            repo_name = f"iitm-{task}-{nonce}-{timestamp}".replace(" ", "-").lower()
            
            # Generate code using LLM
            code_files = await generate_code(brief, attachments, checks)
            
            # Create repository with all required files
            repo_url, commit_sha = await create_repo(
                repo_name=repo_name,
                code_files=code_files,
                brief=brief,
                task=task,
                email=email
            )
            
            # Extract username from repo_url for GitHub Pages
            if "github.com/" in repo_url:
                full_repo_name = repo_url.split("github.com/")[1]
            else:
                full_repo_name = repo_name
            
            # Enable GitHub Pages
            pages_url = await enable_github_pages(full_repo_name)
            
            # Prepare evaluation response
            evaluation_response = {
                "email": email,
                "task": task,
                "round": round_num,
                "nonce": nonce,
                "repo_url": repo_url,
                "commit_sha": commit_sha,
                "pages_url": pages_url
            }
            
            # Send evaluation callback if URL provided
            if evaluation_url:
                await send_evaluation_callback_with_retry(evaluation_url, evaluation_response)
            
            return {
                "status": "success",
                "message": "Task completed successfully",
                "repo_url": repo_url,
                "pages_url": pages_url,
                "evaluation_sent": bool(evaluation_url)
            }
            
        elif round_num == 2:
            # Round 2: Modify existing repository
            if not repo_name:
                raise HTTPException(status_code=400, detail="repo_name required for round 2")
            
            # Generate updated code
            updated_files = await modify_code(brief, repo_name, checks)
            
            # Update repository
            commit_sha = await update_repo(repo_name, updated_files)
            
            # Prepare evaluation response for round 2
            if '/' in repo_name:
                username, repo = repo_name.split('/', 1)
                pages_url = f"https://{username}.github.io/{repo}/"
            else:
                pages_url = f"https://{repo_name}.github.io/"
            
            evaluation_response = {
                "email": email,
                "task": task,
                "round": round_num,
                "nonce": nonce,
                "repo_url": f"https://github.com/{repo_name}",
                "commit_sha": commit_sha,
                "pages_url": pages_url
            }
            
            # Send evaluation callback if URL provided
            if evaluation_url:
                await send_evaluation_callback_with_retry(evaluation_url, evaluation_response)
            
            return {
                "status": "success",
                "round": round_num,
                "message": "Code modified and updated in repo",
                "commit_sha": commit_sha
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid round number. Must be 1 or 2")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task processing failed: {str(e)}")

async def send_evaluation_callback_with_retry(evaluation_url: str, response_data: dict):
    """Send evaluation callback with exponential backoff retry"""
    delays = [1, 2, 4, 8, 16, 32]  # seconds
    
    for attempt, delay in enumerate(delays):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    evaluation_url,
                    json=response_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        print(f"Evaluation callback sent successfully to {evaluation_url}")
                        return True
                    else:
                        print(f"Evaluation callback failed with status {response.status}, attempt {attempt + 1}")
        except Exception as e:
            print(f"Failed to send evaluation callback (attempt {attempt + 1}): {e}")
        
        if attempt < len(delays) - 1:  # Don't sleep after last attempt
            print(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
    
    print(f"Failed to send evaluation callback after {len(delays)} attempts")
    return False

async def send_evaluation_callback(evaluation_url: str, response_data: dict):
    """Send evaluation callback to the provided URL (legacy function)"""
    return await send_evaluation_callback_with_retry(evaluation_url, response_data)

@app.get("/")
async def root():
    return {"message": "IITM Task Handler API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Hugging Face Spaces specific endpoint
@app.get("/info")
async def info():
    return {
        "title": "IITM Task Handler API",
        "description": "Automated code generation and GitHub repository management system for IITM tasks",
        "version": "1.0.0",
        "endpoints": {
            "POST /api-endpoint": "Handle IITM task submission (Round 1 & 2)",
            "GET /health": "Health check",
            "GET /info": "API information"
        }
    }
