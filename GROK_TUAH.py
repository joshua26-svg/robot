import requests
import os
from typing import Dict, Optional

# Configuration (set these via environment variables or a config file)
GITHUB_TOKEN = os.getenv("SHA256:bfu8/mTRyhme4lg+fx/lgot1y7jRFH6jIENrnVxPhog")
XAI_API_KEY = os.getenv("xai-1nXeVSwlF6gMwNPyDtoV4olVg90ygunwZcPIaaSIkD9yV2EqNczx0p4N9S29CEi5vrzy1Rm96AKxYRL1") 
REPO_OWNER = "your-username"  # Replace with your GitHub username/org
REPO_NAME = "your-repo"       # Replace with your repository name
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
XAI_API_URL = "https://api.xai.com/v1/grok"  # Hypothetical; replace with real endpoint

# Headers
github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
xai_headers = {
    "Authorization": f"Bearer {XAI_API_KEY}",
    "Content-Type": "application/json"
}

class GitHubClient:
    """Handles GitHub API interactions."""
    def __init__(self):
        self.base_url = GITHUB_API_URL

    def get_pull_request(self, pr_number: int) -> Dict:
        url = f"{self.base_url}/pulls/{pr_number}"
        response = requests.get(url, headers=github_headers)
        response.raise_for_status()
        return response.json()

    def get_pr_diff(self, pr_number: int) -> str:
        url = f"{self.base_url}/pulls/{pr_number}"
        headers = github_headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def post_review_comment(self, pr_number: int, commit_id: str, body: str, path: str, position: int) -> None:
        url = f"{self.base_url}/pulls/{pr_number}/comments"
        payload = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "position": position
        }
        response = requests.post(url, headers=github_headers, json=payload)
        response.raise_for_status()
        print(f"Review comment posted to PR #{pr_number}")

class GrokClient:
    """Handles interactions with Grok via xAI API."""
    def __init__(self):
        self.api_url = XAI_API_URL

    def analyze_diff(self, diff: str) -> str:
        payload = {
            "prompt": (
                "You are an expert code reviewer. Analyze this diff and provide detailed suggestions "
                "for improvement. Include specific line references if possible:\n\n" + diff
            ),
            "max_tokens": 600,
            "temperature": 0.7
        }
        response = requests.post(self.api_url, headers=xai_headers, json=payload)
        response.raise_for_status()
        return response.json().get("response", "No suggestions provided.")

def parse_diff_for_comments(diff: str, grok_response: str) -> list:
    """Simple parsing to map Grok's suggestions to diff lines (rudimentary)."""
    comments = []
    diff_lines = diff.splitlines()
    
    # Hypothetical: Assume Grok mentions line numbers in its response (e.g., "Line 5: ...")
    for line in grok_response.splitlines():
        if "Line" in line:
            try:
                line_num = int(line.split("Line")[1].split(":")[0].strip())
                if 0 < line_num <= len(diff_lines):
                    # Find the file path and position from diff (simplified)
                    for i, diff_line in enumerate(diff_lines, 1):
                        if i == line_num and diff_line.startswith("+"):
                            comments.append({
                                "body": line,
                                "path": "file.txt",  # Placeholder; extract actual path from diff
                                "position": line_num
                            })
                            break
            except (ValueError, IndexError):
                continue
    
    if not comments:
        comments.append({"body": grok_response, "path": "file.txt", "position": 1})  # Fallback
    return comments

def automate_pr_review(pr_number: int) -> None:
    """Automate PR review with GitHub and Grok."""
    github = GitHubClient()
    grok = GrokClient()

    try:
        # Fetch PR details
        pr_data = github.get_pull_request(pr_number)
        print(f"Reviewing PR #{pr_number}: {pr_data['title']}")
        commit_id = pr_data["head"]["sha"]  # Use the latest commit SHA

        # Fetch diff
        diff = github.get_pr_diff(pr_number)

        # Analyze with Grok
        grok_response = grok.analyze_diff(diff)

        # Parse suggestions into review comments
        comments = parse_diff_for_comments(diff, grok_response)

        # Post comments to PR
        for comment in comments:
            github.post_review_comment(
                pr_number=pr_number,
                commit_id=commit_id,
                body=comment["body"],
                path=comment["path"],
                position=comment["position"]
            )

    except requests.RequestException as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    # Example usage
    pr_number = 1  # Replace with your PR number
    if not GITHUB_TOKEN or not XAI_API_KEY:
        print("Please set GITHUB_TOKEN and XAI_API_KEY environment variables.")
    else:
        automate_pr_review(pr_number)