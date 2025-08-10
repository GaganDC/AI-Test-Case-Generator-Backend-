import httpx

async def fetch_github_files(token: str, repo: str):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        repo_info = await client.get(f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1", headers=headers)
        tree = repo_info.json()["tree"]
        code_files = [f for f in tree if f["path"].endswith(('.py', '.js', '.jsx'))]
        return {"files": code_files}
