import os
import requests
import openai
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogScribe:
    """
    A class to generate human-readable changelogs from GitHub repository commits.
    """

    def __init__(self, api_key: str, github_token: Optional[str] = None):
        """
        Initializes the LogScribe instance.

        Args:
            api_key (str): The OpenAI API key.
            github_token (str, optional): A GitHub personal access token for higher
                                         API rate limits. Defaults to None.
        """
        if not api_key:
            raise ValueError("OpenAI API key is required.")
        openai.api_key = api_key
        self.github_headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if github_token:
            self.github_headers["Authorization"] = f"token {github_token}"
        logger.info("LogScribe instance initialized")

    def _parse_repo_url(self, repo_url: str) -> Optional[Dict[str, str]]:
        """Parses a GitHub URL to extract owner and repo name."""
        try:
            parts = repo_url.strip().split('/')
            if "github.com" not in parts[-3]:
                logger.error(f"Invalid GitHub URL format: {repo_url}")
                return None
            owner = parts[-2]
            repo = parts[-1].replace('.git', '')
            logger.debug(f"Parsed repository: {owner}/{repo}")
            return {"owner": owner, "repo": repo}
        except IndexError:
            logger.error(f"Failed to parse repository URL: {repo_url}")
            return None

    def _fetch_commits(self, owner: str, repo: str, since_date: str) -> List[Dict[str, Any]]:
        """Fetches all commits from a repository since a given date."""
        commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"since": since_date, "per_page": 100}
        all_commits = []
        page = 1

        while True:
            params['page'] = page
            try:
                response = requests.get(commits_url, headers=self.github_headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                all_commits.extend(data)
                logger.debug(f"Fetched {len(data)} commits from page {page}")
                page += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching commits: {str(e)}")
                raise
        
        logger.info(f"Total commits fetched: {len(all_commits)}")
        return all_commits

    def _generate_changelog_prompt(self, commit_messages: str) -> str:
        """Creates the prompt for the OpenAI API."""
        return f"""
        You are an expert technical writer specializing in software release notes.
        Your task is to analyze the following raw commit messages from a GitHub repository
        and generate a clean, well-structured, and human-readable changelog in Markdown format.

        **Instructions:**
        1.  **Categorize each meaningful commit** into one of the following sections:
            - `🚀 New Features`: For commits that introduce new functionality.
            - `🐛 Bug Fixes`: For commits that fix bugs.
            - `🔧 Maintenance & Refactoring`: For code cleanup, dependency updates, and internal improvements.
            - `📚 Documentation`: For changes to READMEs, guides, or comments.
        2.  **Summarize each commit message** into a concise, user-friendly list item.
        3.  **Ignore trivial commits**, such as "Merge branch '...'", "Update README.md" (unless it's a significant doc change), or style fixes.
        4.  **Format the output** as a Markdown document with a main title "Changelog" and the categorized sections as H2 headings.
        5.  If no meaningful commits are found in a category, omit that section entirely.

        **Raw Commit Messages:**
        ---
        {commit_messages}
        ---
        """

    def generate_changelog(self, repo_url: str, days_ago: int = 7) -> str:
        """
        Generates a changelog for a given GitHub repository.

        Args:
            repo_url (str): The full URL of the GitHub repository.
            days_ago (int, optional): How many days back to look for commits. Defaults to 7.

        Returns:
            str: A formatted Markdown string of the changelog.
        
        Raises:
            ValueError: If the repository URL is invalid.
            requests.exceptions.RequestException: If there's an issue with the GitHub API request.
        """
        logger.info(f"Generating changelog for {repo_url} (last {days_ago} days)")
        
        repo_info = self._parse_repo_url(repo_url)
        if not repo_info:
            raise ValueError("Invalid GitHub repository URL provided.")

        since_date_dt = datetime.utcnow() - timedelta(days=days_ago)
        since_date_iso = since_date_dt.isoformat()

        logger.info(f"Fetching commits for {repo_info['owner']}/{repo_info['repo']} since {since_date_iso}")
        
        try:
            commits = self._fetch_commits(repo_info['owner'], repo_info['repo'], since_date_iso)
            if not commits:
                logger.warning(f"No commits found in the last {days_ago} days")
                return f"## Changelog\n\nNo new commits found in the last {days_ago} days."

            commit_messages = "\n".join([f"- {c['commit']['message']}" for c in commits])
            
            logger.info("Generating changelog with AI...")
            prompt = self._generate_changelog_prompt(commit_messages)
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert technical writer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )
                
                changelog = response.choices[0].message.content
                logger.info("Changelog generated successfully")
                return changelog.strip()
            except openai.error.OpenAIError as e:
                logger.error(f"OpenAI API error: {str(e)}")
                raise RuntimeError(f"Failed to generate changelog: {str(e)}")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Repository not found: {repo_url}")
                raise ValueError("Repository not found. Please check the URL.")
            else:
                logger.error(f"GitHub API error: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    # --- Keyholder: Replace with your actual data for testing ---
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") # Optional, but recommended
    
    # Example usage:
    # repo_to_analyze = "https://github.com/imndevmodeai/ResonantiA-v3"
    repo_to_analyze = "https://github.com/facebook/react"
    
    if OPENAI_API_KEY == "YOUR_API_KEY_HERE":
        logger.error("OpenAI API key not set")
        print("ERROR: Please set your OpenAI API key in the script or as an environment variable.")
    else:
        try:
            scribe = LogScribe(api_key=OPENAI_API_KEY, github_token=GITHUB_TOKEN)
            final_changelog = scribe.generate_changelog(repo_to_analyze, days_ago=7)
            print("\n--- Generated Changelog ---")
            print(final_changelog)
        except (ValueError, RuntimeError, requests.exceptions.RequestException) as e:
            logger.error(f"Error during execution: {str(e)}")
            print(f"\nERROR: {e}") 