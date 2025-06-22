import requests
import os
import base64
import markdown
from datetime import datetime, timedelta
import re # For cleaning commit messages
import google.generativeai as genai # Changed from openai

class LogScribe:
    def __init__(self, api_key, github_token=None):
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel('gemini-pro') # Using gemini-pro as a general purpose model
        self.github_token = github_token
        if not api_key: # Check if API key is provided for Gemini
            raise ValueError("Gemini API key is not configured.")

    def _get_github_commits(self, repo_url, days_ago):
        """
        Fetches commit history for a given GitHub repository within a specified timeframe.
        Handles pagination and date filtering.
        """
        parts = repo_url.replace("https://github.com/", "").split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL format.")
        owner = parts[0]
        repo = parts[1]

        since_date = datetime.now() - timedelta(days=days_ago)
        since_iso = since_date.isoformat(timespec='seconds') + 'Z'

        commits = []
        page = 1
        per_page = 100 # Max per page is 100

        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        while True:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?since={since_iso}&per_page={per_page}&page={page}"
            response = requests.get(api_url, headers=headers)
            response.raise_for_status() # Raise an exception for HTTP errors

            page_commits = response.json()
            if not page_commits:
                break # No more commits

            commits.extend(page_commits)

            # Check for Link header for next page
            if 'link' in response.headers:
                links = response.headers['link'].split(',')
                next_link = None
                for link in links:
                    if 'rel="next"' in link:
                        next_link = link.split(';')[0].strip('<> ')
                        break
                if next_link:
                    page += 1
                else:
                    break
            else:
                break # No link header, so no more pages

        return commits

    def _generate_commit_summary_gemini(self, commit_messages):
        """
        Analyzes a list of commit messages using Gemini API to provide a concise summary.
        """
        if not commit_messages:
            return "No relevant commit messages to summarize."

        combined_messages = "\n".join([f"- {msg}" for msg in commit_messages])

        try:
            prompt = f"""Synthesize a concise, human-readable changelog entry from the following GitHub commit messages. Group related changes, highlight new features, bug fixes, and performance improvements. Avoid technical jargon where possible. If there are no significant changes, state that clearly.

Commit Messages:
{combined_messages}

Changelog Entry:"""
            
            # Use Gemini API for text generation
            response = self.client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error summarizing commits with Gemini API: {e}"

    def generate_changelog(self, repo_url, days_ago):
        """
        Generates a changelog for a GitHub repository based on recent commits.
        """
        try:
            commits = self._get_github_commits(repo_url, days_ago)

            if not commits:
                return "No commits found for the specified period."

            commit_messages = [commit['commit']['message'] for commit in commits]

            # Generate high-level summary for the changelog using Gemini
            changelog_content = self._generate_commit_summary_gemini(commit_messages)
            
            return changelog_content

        except requests.exceptions.RequestException as e:
            return f"GitHub API Error: {e}. Please ensure the URL is correct and the repository is public or your GITHUB_TOKEN is valid for private repos."
        except ValueError as e:
            return f"Input Error: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def get_repository_summary_with_gemini(self, repo_url):
        """
        Analyzes a GitHub repository and generates a high-level summary using the configured Gemini client.
        """
        github_token = self.github_token # Use the instance's GitHub token
        gemini_client = self.client # Use the instance's Gemini client
        summary_sections = []

        try:
            repo_contents = get_github_repo_structure(repo_url, github_token)

            readme_content = "No README.md found."
            for item in repo_contents:
                if item['name'].lower() == 'readme.md' and item['type'] == 'file':
                    readme_content = get_file_content(item['url'], github_token)
                    # Basic markdown to text conversion, or use a library for richer parsing
                    readme_content = markdown.markdown(readme_content) # Convert markdown to HTML
                    # Remove HTML tags to get plain text, simple for summary
                    readme_content = ''.join(c for c in readme_content if c.isalnum() or c.isspace() or c in ['.', ',', '!', '?', '(', ')', '-']).strip()
                    break
            summary_sections.append(f"## README Overview\n\n{readme_content}\n")

            # Process a few key files (e.g., .py, .js, .json, .md, Dockerfile, requirements.txt, package.json)
            # Prioritize files that usually give a good overview
            interesting_files = []
            for item in repo_contents:
                if item['type'] == 'file':
                    file_name = item['name'].lower()
                    if file_name in ['requirements.txt', 'package.json', 'dockerfile', 'readme.md', 'app.py'] or \
                    file_name.endswith(('.py', '.js', '.ts', '.json', '.yaml', '.yml')):
                        interesting_files.append(item)

            # Limit to a reasonable number of files to avoid excessive API calls
            # and token usage for OpenAI. Prioritize smaller, config-like files.
            interesting_files.sort(key=lambda x: x['size'])
            files_to_analyze = interesting_files[:5] # Analyze top 5 smallest files

            for file_item in files_to_analyze:
                if file_item['name'].lower() == 'readme.md':
                    continue # Already processed
                file_content = get_file_content(file_item['url'], github_token)
                if len(file_content) > 10000: # Skip very large files to save tokens
                    summary_sections.append(f"### Skipped Large File: {file_item['name']}\n")
                    continue

                file_summary = self._analyze_code_with_gemini(file_content, file_item['name'], gemini_client)
                summary_sections.append(f"## File: {file_item['name']}\n\n{file_summary}\n")

            final_summary_prompt = f"""Based on the following extracted information from a GitHub repository, synthesize a comprehensive, high-level summary of the project. Include its main purpose, key features, and primary technical stack. Ensure the summary is concise and easy to understand for a non-technical audience if possible.

Extracted Information:
{ "\n".join(summary_sections)}

Comprehensive Project Summary:"""
            
            # Final synthesis using a powerful model
            final_synthesis_completion = gemini_client.generate_content(
                final_summary_prompt
            )
            return final_synthesis_completion.text.strip()

        except requests.exceptions.RequestException as e:
            return f"GitHub API Error: {e}. Please ensure the URL is correct and the repository is public or your GITHUB_TOKEN is valid for private repos."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def _analyze_code_with_gemini(self, file_contents, filename, gemini_client):
        """
        Analyzes code snippets using Gemini API to provide a summary.
        """
        try:
            prompt = f"""Analyze the following code from the file '{filename}' and provide a concise summary of its purpose, key functionalities, and technologies used. Focus on high-level understanding rather than line-by-line explanation.
`   
File: {filename}
Content:
```
{file_contents}
```

Summary:"""
            
            response = gemini_client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error analyzing code with Gemini: {e}"

def get_github_repo_structure(repo_url, github_token=None):
    """
    Fetches the repository structure (files and directories) from GitHub.
    """
    parts = repo_url.replace("https://github.com/", "").split('/')
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL format.")
    owner = parts[0]
    repo = parts[1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

def get_file_content(file_url, github_token=None):
    """
    Fetches the content of a file from GitHub.
    """
    headers = {"Accept": "application/vnd.github.v3.raw"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    response = requests.get(file_url, headers=headers)
    response.raise_for_status()
    return response.text

def analyze_code_with_openai(file_contents, filename):
    """
    Analyzes code snippets using OpenAI GPT-4 to provide a summary.
    """
    if not client.api_key:
        return "OpenAI API key not configured."

    try:
        prompt = f"""Analyze the following code from the file '{filename}' and provide a concise summary of its purpose, key functionalities, and technologies used. Focus on high-level understanding rather than line-by-line explanation.

File: {filename}
Content:
```
{file_contents}
```

Summary:"""
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini", # Using a cost-effective model for summaries
            messages=[
                {"role": "system", "content": "You are a highly intelligent AI assistant specialized in code analysis."},
                {"role": "user", "content": prompt}
            ]
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing code with OpenAI: {e}"

def get_repository_summary(repo_url):
    """
    Analyzes a GitHub repository and generates a high-level summary.
    """
    github_token = os.environ.get("GITHUB_TOKEN") # Optional: for private repos or higher rate limits
    summary_sections = []

    try:
        repo_contents = get_github_repo_structure(repo_url, github_token)

        readme_content = "No README.md found."
        for item in repo_contents:
            if item['name'].lower() == 'readme.md' and item['type'] == 'file':
                readme_content = get_file_content(item['url'], github_token)
                # Basic markdown to text conversion, or use a library for richer parsing
                readme_content = markdown.markdown(readme_content) # Convert markdown to HTML
                # Remove HTML tags to get plain text, simple for summary
                readme_content = ''.join(c for c in readme_content if c.isalnum() or c.isspace() or c in ['.', ',', '!', '?', '(', ')', '-']).strip()
                break
        summary_sections.append(f"## README Overview\n\n{readme_content}\n")

        # Process a few key files (e.g., .py, .js, .json, .md, Dockerfile, requirements.txt, package.json)
        # Prioritize files that usually give a good overview
        interesting_files = []
        for item in repo_contents:
            if item['type'] == 'file':
                file_name = item['name'].lower()
                if file_name in ['requirements.txt', 'package.json', 'dockerfile', 'readme.md', 'app.py'] or \
                   file_name.endswith(('.py', '.js', '.ts', '.json', '.yaml', '.yml')):
                    interesting_files.append(item)

        # Limit to a reasonable number of files to avoid excessive API calls
        # and token usage for OpenAI. Prioritize smaller, config-like files.
        interesting_files.sort(key=lambda x: x['size'])
        files_to_analyze = interesting_files[:5] # Analyze top 5 smallest files

        for file_item in files_to_analyze:
            if file_item['name'].lower() == 'readme.md':
                continue # Already processed
            file_content = get_file_content(file_item['url'], github_token)
            if len(file_content) > 10000: # Skip very large files to save tokens
                summary_sections.append(f"### Skipped Large File: {file_item['name']}\n")
                continue

            file_summary = analyze_code_with_openai(file_content, file_item['name'])
            summary_sections.append(f"## File: {file_item['name']}\n\n{file_summary}\n")

        final_summary_prompt = f"""Based on the following extracted information from a GitHub repository, synthesize a comprehensive, high-level summary of the project. Include its main purpose, key features, and primary technical stack. Ensure the summary is concise and easy to understand for a non-technical audience if possible.

Extracted Information:
{ "\n".join(summary_sections)}

Comprehensive Project Summary:"""
        
        # Final synthesis using a powerful model
        final_synthesis_completion = client.chat.completions.create(
            model="gpt-4o", # Using a more capable model for final synthesis
            messages=[
                {"role": "system", "content": "You are an expert AI assistant tasked with summarizing GitHub projects concisely and accurately."},
                {"role": "user", "content": final_summary_prompt}
            ]
        )
        return final_synthesis_completion.choices[0].message.content.strip()

    except requests.exceptions.RequestException as e:
        return f"GitHub API Error: {e}. Please ensure the URL is correct and the repository is public or your GITHUB_TOKEN is valid for private repos."
    except Exception as e:
        return f"An unexpected error occurred: {e}" 