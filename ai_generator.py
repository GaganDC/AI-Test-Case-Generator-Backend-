import httpx
import json

API_KEY = "YOUR_API_KEY_HERE"
MODEL = "gemini-2.5-pro"

def safe_generate(prompt):
    print("🧪 Starting Gemini test...")

    for model in [MODEL, "gemini-pro"]:
        print(f"→ Trying model: {model}")
        
        # Make the API request
        r = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": API_KEY},
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                # Increase tokens to avoid MAX_TOKENS before any visible text
                "generationConfig": {"maxOutputTokens": 256, "temperature": 0}
            }
        )

        if r.status_code != 200:
            print(f"❌ {model} request failed: {r.status_code} {r.text}")
            continue

        data = r.json()

        # Try to safely extract text
        try:
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts")
            if parts and len(parts) > 0 and "text" in parts[0]:
                return model, parts[0]["text"]
            else:
                print(f"⚠️ {model} returned no visible text, trying next model...")
        except Exception as e:
            print(f"⚠️ Error parsing {model} response: {e}")

        # If here, print full API response for debugging
        print("🔍 Full API response:", json.dumps(data, indent=2))

    print("❌ No models returned visible text")
    return None, None


# Example usage
if __name__ == "__main__":
    model_used, output_text = safe_generate("Write a short haiku about coding in Python.")
    if output_text:
        print(f"\n✅ Model used: {model_used}\nOutput:\n{output_text}")
    else:
        print("\n⚠️ No output generated.")
