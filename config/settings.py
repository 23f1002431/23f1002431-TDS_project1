import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Tokens
AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
EXPECTED_SECRET = os.getenv("EXPECTED_SECRET")

# Debug print (optional, for verification)
print("🔍 Loaded ENV variables:")
print("AIPIPE_API_KEY:", bool(AIPIPE_API_KEY))
print("GITHUB_TOKEN:", GITHUB_TOKEN[:6] + "..." if GITHUB_TOKEN else "None")
print("EXPECTED_SECRET:", EXPECTED_SECRET)
