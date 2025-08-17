import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env")

genai.configure(api_key=API_KEY)

# Create model
model = genai.GenerativeModel("gemini-2.5-pro")

# Force a simple, safe, clear request
response = model.generate_content(
    contents="Write exactly this sentence: Gemini 2.5 Pro API works by default!",
    generation_config={
        "max_output_tokens": 50,
        "temperature": 0.2,
    }
)

# Safely extract text
if hasattr(response, "candidates") and response.candidates:
    parts = getattr(response.candidates[0].content, "parts", [])
    if parts:
        print(parts[0].text)
    else:
        print("⚠️ No text in parts. Raw:", response)
else:
    print("❌ No candidates. Raw:", response)
