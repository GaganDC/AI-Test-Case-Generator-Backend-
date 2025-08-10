import os
import httpx

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_test_summaries(code: str):
    prompt = f"""
You are a senior QA engineer. Given the following code, generate a list of test case summaries.

Code:
{code}
    """

    # Replace this with Gemini API or OpenAI
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )
    result = response.json()
    return {"summaries": result["candidates"][0]["content"]["parts"][0]["text"]}

def generate_test_code(code: str, summary: str):
    prompt = f"""
You are an expert test engineer.

Generate a Pytest test for:
'{summary}'

Based on this code:
{code}
    """
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )
    result = response.json()
    return {"test_code": result["candidates"][0]["content"]["parts"][0]["text"]}
