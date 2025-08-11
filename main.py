# main.py
import os
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
import requests

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-test-case-generator-frontend.vercel.app",
                   "https://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GitHub OAuth credentials
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")


@app.get("/")
def root():
    return {"message": "🚀 API is running successfully"}


@app.get("/github/login")
def github_login():
    return RedirectResponse(
        url=f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo"
    )


@app.get("/github/callback")
async def github_callback(code: str):
    print("📩 Received code:", code)

    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        token_json = token_response.json()
        print("🪪 Token response:", token_json)

        access_token = token_json.get("access_token")
        if not access_token:
            return JSONResponse(
                status_code=400,
                content={"error": "bad_verification_code", "details": token_json}
            )

        # Get user info
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_data = user_response.json()

        # Get repos
        repos_response = await client.get(
            "https://api.github.com/user/repos?per_page=100",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        repos_data = repos_response.json()

        return {
            "access_token": access_token,
            "user": user_data,
            "repos": repos_data
        }


def fetch_directory(owner, repo, path, token):
    """Recursive fetch of files/folders from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    items = r.json()

    structure = []
    for item in items:
        if item["type"] == "dir":
            structure.append({
                "name": item["name"],
                "path": item["path"],
                "type": "dir",
                "children": fetch_directory(owner, repo, item["path"], token)
            })
        else:
            structure.append({
                "name": item["name"],
                "path": item["path"],
                "type": "file",
                "download_url": item["download_url"]
            })
    return structure

@app.get("/repo-files")
def get_repo_files(owner: str, repo: str, token: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    files = []
    for item in data["tree"]:
        files.append({
            "path": item["path"],
            "name": item["path"].split("/")[-1],
            "type": "file" if item["type"] == "blob" else "dir"
        })
    return files

@app.post("/generate-testcases")
def generate_testcases(data: dict):
    token = data["token"]
    owner = data["owner"]
    repo = data["repo"]
    files = data["files"]

    testcases = []
    for file_path in files:
        # Fetch file content from GitHub
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        headers = {"Authorization": f"token {token}"}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        file_data = r.json()

        import base64
        file_content = base64.b64decode(file_data["content"]).decode("utf-8")

        # TODO: Replace this placeholder with AI model call
        generated_test = f"// Test cases for {file_path}\n// (Auto-generated)\n\n"

        testcases.append({
            "file": file_path,
            "testContent": generated_test
        })

    return {"testcases": testcases}


