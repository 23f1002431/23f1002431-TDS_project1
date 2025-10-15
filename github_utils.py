import aiohttp
import base64
import json
from typing import Dict, List, Any
from config.settings import GITHUB_TOKEN

GITHUB_API_BASE = "https://api.github.com"

async def create_repo(repo_name: str, code_files: Dict[str, str], brief: str, task: str, email: str) -> tuple[str, str]:
    """Create a GitHub repository with all required files"""
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "IITM-Task-Handler/1.0"
    }
    
    # Create repository
    repo_data = {
        "name": repo_name,
        "description": f"IITM Task: {brief[:100]}",
        "private": False,
        "auto_init": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True
    }
    
    async with aiohttp.ClientSession() as session:
        # Create the repository
        async with session.post(
            f"{GITHUB_API_BASE}/user/repos",
            json=repo_data,
            headers=headers
        ) as response:
            if response.status == 201:
                repo_info = await response.json()
                repo_url = repo_info["html_url"]
                
                # Add all files to the repository and get commit SHA
                commit_sha = await add_files_to_repo(session, headers, repo_name, code_files, brief, task, email)
                
                return repo_url, commit_sha
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create repository: {error_text}")

async def add_files_to_repo(session: aiohttp.ClientSession, headers: Dict, repo_name: str, 
                          code_files: Dict[str, str], brief: str, task: str, email: str) -> str:
    """Add all files to the repository and return commit SHA"""
    
    # Create MIT License
    mit_license = create_mit_license()
    
    # Create comprehensive README
    readme_content = create_comprehensive_readme(brief, task, email, repo_name)
    
    # Files to add
    files_to_add = {
        **code_files,
        "LICENSE": mit_license,
        "README.md": readme_content
    }
    
    commit_sha = None
    
    # Add each file
    for filename, content in files_to_add.items():
        sha = await add_file_to_repo(session, headers, repo_name, filename, content)
        if sha and not commit_sha:  # Get SHA from first file commit
            commit_sha = sha
    
    return commit_sha or "unknown"

async def add_file_to_repo(session: aiohttp.ClientSession, headers: Dict, 
                          repo_name: str, filename: str, content: str) -> str:
    """Add a single file to the repository and return commit SHA"""
    
    file_data = {
        "message": f"Add {filename}",
        "content": base64.b64encode(content.encode()).decode(),
        "branch": "main"
    }
    
    async with session.put(
        f"{GITHUB_API_BASE}/repos/{repo_name}/contents/{filename}",
        json=file_data,
        headers=headers
    ) as response:
        if response.status in [200, 201]:
            result = await response.json()
            return result.get("commit", {}).get("sha", "unknown")
        else:
            error_text = await response.text()
            print(f"Warning: Failed to add {filename}: {error_text}")
            return "unknown"

async def update_repo(repo_name: str, updated_files: Dict[str, str]) -> str:
    """Update files in the repository and return commit SHA"""
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "IITM-Task-Handler/1.0"
    }
    
    commit_sha = None
    
    async with aiohttp.ClientSession() as session:
        for filename, content in updated_files.items():
            if filename == "error":
                continue
                
            # Get current file info
            async with session.get(
                f"{GITHUB_API_BASE}/repos/{repo_name}/contents/{filename}",
                headers=headers
            ) as response:
                if response.status == 200:
                    file_info = await response.json()
                    sha = file_info["sha"]
                    
                    # Update file
                    update_data = {
                        "message": f"Update {filename}",
                        "content": base64.b64encode(content.encode()).decode(),
                        "sha": sha,
                        "branch": "main"
                    }
                    
                    async with session.put(
                        f"{GITHUB_API_BASE}/repos/{repo_name}/contents/{filename}",
                        json=update_data,
                        headers=headers
                    ) as update_response:
                        if update_response.status in [200, 201]:
                            result = await update_response.json()
                            if not commit_sha:  # Get SHA from first successful update
                                commit_sha = result.get("commit", {}).get("sha", "unknown")
                        else:
                            error_text = await update_response.text()
                            print(f"Warning: Failed to update {filename}: {error_text}")
    
    return commit_sha or "unknown"

async def enable_github_pages(repo_name: str) -> str:
    """Enable GitHub Pages for the repository"""
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "IITM-Task-Handler/1.0"
    }
    
    # Enable GitHub Pages
    pages_data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GITHUB_API_BASE}/repos/{repo_name}/pages",
            json=pages_data,
            headers=headers
        ) as response:
            if response.status in [200, 201]:
                # Extract username from repo_name (format: username/repo-name)
                if '/' in repo_name:
                    username, repo = repo_name.split('/', 1)
                    pages_url = f"https://{username}.github.io/{repo}/"
                else:
                    pages_url = f"https://{repo_name}.github.io/"
                print(f"GitHub Pages enabled: {pages_url}")
                return pages_url
            else:
                error_text = await response.text()
                print(f"Warning: Failed to enable GitHub Pages: {error_text}")
                return f"https://github.com/{repo_name}"

def create_mit_license() -> str:
    """Create MIT License content"""
    return """MIT License

Copyright (c) 2024 IITM Task Handler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

def create_comprehensive_readme(brief: str, task: str, email: str, repo_name: str) -> str:
    """Create a comprehensive README.md file"""
    return f"""# {task.replace('-', ' ').title()}

## Overview
{brief}

## Project Details
- **Task**: {task}
- **Generated for**: {email}
- **Repository**: {repo_name}
- **Generated by**: IITM Task Handler API

## Setup Instructions

### Prerequisites
- A modern web browser
- Optional: Local web server (for development)

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/{repo_name}.git
   cd {repo_name}
   ```

2. Open the application:
   - **Option 1**: Open `index.html` directly in your browser
   - **Option 2**: Serve using a local web server:
     ```bash
     # Using Python
     python -m http.server 8000
     
     # Using Node.js
     npx serve .
     
     # Using PHP
     php -S localhost:8000
     ```

3. Navigate to `http://localhost:8000` (if using a server) or open the HTML file directly

## Usage

### Basic Usage
1. Open the application in your web browser
2. Follow the on-screen instructions
3. Interact with the interface as designed

### URL Parameters
The application supports URL parameters for enhanced functionality:
- `?url=<image_url>` - Pass an image URL for processing
- `?data=<json_data>` - Pass JSON data for processing

### Features
- Responsive design that works on desktop and mobile
- Modern, clean user interface
- Error handling and user feedback
- Cross-browser compatibility

## Code Structure

### Files
- `index.html` - Main HTML structure
- `style.css` - CSS styling and responsive design
- `script.js` - JavaScript functionality and interactions
- `README.md` - This documentation file
- `LICENSE` - MIT License

### Key Components
- **HTML**: Semantic structure with accessibility in mind
- **CSS**: Modern styling with CSS Grid and Flexbox
- **JavaScript**: Vanilla JS with modern ES6+ features

## Development

### Local Development
1. Make changes to the source files
2. Refresh your browser to see changes
3. Test across different browsers and devices

### Customization
- Modify `style.css` for visual changes
- Update `script.js` for functionality changes
- Edit `index.html` for structural changes

## Browser Support
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Troubleshooting

### Common Issues
1. **Page not loading**: Check if all files are present
2. **Styling issues**: Ensure CSS file is linked correctly
3. **JavaScript errors**: Check browser console for errors

### Getting Help
- Check the browser console for error messages
- Ensure all files are in the same directory
- Verify file permissions

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
This is an automatically generated project. For modifications, please contact the IITM Task Handler.

## Generated by
IITM Task Handler API - Automated code generation and repository management system.

---
*This README was automatically generated as part of the IITM task submission process.*
"""
