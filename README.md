---
title: IITM Task Handler API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
short_description: Automated code generation and GitHub repository management system for IITM tasks
---

# IITM Task Handler API

An automated system that generates web applications based on task descriptions using AI and creates GitHub repositories with GitHub Pages deployment.

## Features

- 🤖 **AI-Powered Code Generation**: Uses GPT-4 to generate complete web applications
- 📁 **GitHub Integration**: Automatically creates repositories and manages files
- 🌐 **GitHub Pages**: Enables automatic deployment to GitHub Pages
- 🔄 **Round 2 Support**: Handles code modifications and updates
- 📊 **Evaluation Callbacks**: Sends results back to evaluation systems
- 🔒 **Secret Validation**: Secure API endpoints with secret validation

## API Endpoints

### POST `/iitm-task`
Handles IITM task submission and generates complete web applications.

**Request Body:**
```json
{
  "secret": "your_secret_key",
  "brief": "Task description",
  "task": "task_name",
  "email": "user@example.com",
  "nonce": "unique_identifier",
  "evaluation_url": "https://evaluation.example.com/callback",
  "attachments": [],
  "checks": []
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Task completed successfully",
  "repo_url": "https://github.com/username/repo-name",
  "pages_url": "https://username.github.io/repo-name/",
  "evaluation_sent": true
}
```

### POST `/iitm-round2`
Handles round 2 modifications to existing repositories.

**Request Body:**
```json
{
  "secret": "your_secret_key",
  "modification": "Modification description",
  "repo_name": "username/repo-name",
  "email": "user@example.com",
  "task": "task_name",
  "nonce": "unique_identifier",
  "evaluation_url": "https://evaluation.example.com/callback"
}
```

### GET `/health`
Health check endpoint.

### GET `/info`
API information and available endpoints.

## Environment Variables

Set these in your Hugging Face Space settings:

- `AIPIPE_API_KEY`: Your AIPipe API key for AI code generation
- `GITHUB_TOKEN`: Your GitHub personal access token
- `EXPECTED_SECRET`: Secret key for API authentication

## How It Works

1. **Task Submission**: Client submits task details via `/iitm-task`
2. **AI Generation**: System uses GPT-4 to generate complete web application code
3. **Repository Creation**: Creates a new GitHub repository with all generated files
4. **GitHub Pages**: Enables GitHub Pages for automatic deployment
5. **Callback**: Sends results back to evaluation system (if provided)

## Generated Applications

Each generated application includes:
- `index.html` - Main HTML structure
- `style.css` - Modern CSS styling
- `script.js` - JavaScript functionality
- `README.md` - Comprehensive documentation
- `LICENSE` - MIT License

## Security

- All endpoints require secret validation
- GitHub token is used for repository operations
- CORS enabled for cross-origin requests
- Input validation and error handling

## Deployment

This application is deployed on Hugging Face Spaces using Docker. The Dockerfile includes:
- Python 3.11 slim base image
- All required dependencies
- Non-root user for security
- Health checks
- Port 7860 for Hugging Face Spaces

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions, please check the logs in the Hugging Face Space or contact the development team.
