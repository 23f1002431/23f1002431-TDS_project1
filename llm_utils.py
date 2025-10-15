import aiohttp
import base64
import json
from typing import Dict, List, Any
from config.settings import AIPIPE_API_KEY

async def generate_code(brief: str, attachments: List[Dict] = None) -> Dict[str, str]:
    """Generate code files based on the brief and attachments using aipipe API"""
    
    # Prepare the prompt for code generation
    prompt = f"""
    Create a complete web application based on this brief: {brief}
    
    Requirements:
    1. Create a minimal, functional web application
    2. Include HTML, CSS, and JavaScript as needed
    3. Make it responsive and user-friendly
    4. Include proper error handling
    5. Add comments explaining the code
    
    If there are attachments, analyze them and incorporate relevant functionality.
    
    Return the code as a JSON object with file names as keys and file contents as values.
    Include at least: index.html, style.css, script.js, and any necessary backend files.
    """
    
    # Add attachment analysis to prompt if present
    if attachments:
        prompt += "\n\nAttachments to analyze:\n"
        for attachment in attachments:
            prompt += f"- {attachment.get('name', 'unknown')}: {attachment.get('url', '')[:100]}...\n"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {AIPIPE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert web developer. Generate complete, functional web applications based on requirements. Always return valid JSON with file contents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            async with session.post(
                "https://api.aipipe.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse the JSON response
                    try:
                        code_files = json.loads(content)
                        return code_files
                    except json.JSONDecodeError:
                        # If not JSON, create a simple structure
                        return {
                            "index.html": create_default_html(brief),
                            "style.css": create_default_css(),
                            "script.js": create_default_js(),
                            "README.md": create_default_readme(brief)
                        }
                else:
                    raise Exception(f"API request failed with status {response.status}")
                    
    except Exception as e:
        print(f"Error generating code: {e}")
        # Return default code if API fails
        return {
            "index.html": create_default_html(brief),
            "style.css": create_default_css(),
            "script.js": create_default_js(),
            "README.md": create_default_readme(brief)
        }

async def modify_code(modification_request: str, repo_name: str) -> Dict[str, str]:
    """Modify existing code based on modification request"""
    
    prompt = f"""
    Modify the existing code in repository '{repo_name}' based on this request: {modification_request}
    
    Return the updated code as a JSON object with file names as keys and file contents as values.
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {AIPIPE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert web developer. Modify existing code based on requirements. Always return valid JSON with updated file contents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            async with session.post(
                "https://api.aipipe.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse modification response"}
                else:
                    raise Exception(f"API request failed with status {response.status}")
                    
    except Exception as e:
        print(f"Error modifying code: {e}")
        return {"error": f"Modification failed: {str(e)}"}

def create_default_html(brief: str) -> str:
    """Create a default HTML file"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IITM Task - {brief[:50]}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>IITM Task Application</h1>
            <p>{brief}</p>
        </header>
        <main>
            <div class="content">
                <h2>Welcome to the Application</h2>
                <p>This is a generated application based on your task requirements.</p>
                <button id="actionBtn" class="btn">Click Me</button>
                <div id="result" class="result"></div>
            </div>
        </main>
        <footer>
            <p>&copy; 2024 IITM Task Handler</p>
        </footer>
    </div>
    <script src="script.js"></script>
</body>
</html>"""

def create_default_css() -> str:
    """Create a default CSS file"""
    return """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: white;
    margin-top: 20px;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

header {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #eee;
}

header h1 {
    color: #2c3e50;
    margin-bottom: 10px;
}

header p {
    color: #7f8c8d;
    font-size: 1.1em;
}

.content {
    text-align: center;
    padding: 20px 0;
}

.btn {
    background: #3498db;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.3s;
    margin: 20px 0;
}

.btn:hover {
    background: #2980b9;
}

.result {
    margin-top: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 5px;
    min-height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}

footer {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    color: #7f8c8d;
}

@media (max-width: 600px) {
    .container {
        margin: 10px;
        padding: 15px;
    }
}"""

def create_default_js() -> str:
    """Create a default JavaScript file"""
    return """document.addEventListener('DOMContentLoaded', function() {
    const actionBtn = document.getElementById('actionBtn');
    const result = document.getElementById('result');
    
    actionBtn.addEventListener('click', function() {
        result.innerHTML = '<p>Button clicked! Application is working.</p>';
        result.style.background = '#d4edda';
        result.style.color = '#155724';
        result.style.border = '1px solid #c3e6cb';
    });
    
    // Add some interactive features
    console.log('IITM Task Application loaded successfully');
    
    // Example of handling URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const urlParam = urlParams.get('url');
    if (urlParam) {
        result.innerHTML = `<p>URL parameter detected: ${urlParam}</p>`;
    }
});"""

def create_default_readme(brief: str) -> str:
    """Create a default README file"""
    return f"""# IITM Task Application

## Overview
{brief}

## Setup
1. Clone this repository
2. Open `index.html` in a web browser
3. Or serve it using a local web server

## Usage
- Open the application in your browser
- Interact with the interface as designed
- Check browser console for any additional functionality

## Files
- `index.html` - Main HTML file
- `style.css` - Styling
- `script.js` - JavaScript functionality

## License
MIT License - see LICENSE file for details

## Generated by
IITM Task Handler API
"""
