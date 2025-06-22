import os
from flask import Flask, request, render_template, redirect, url_for
from logscribe_core import LogScribe, get_repository_summary # Import necessary functions

app = Flask(__name__)

# Load API key from environment variable for security
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") # Optional GitHub token

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not set. Functionality may be limited.")

@app.route('/')
def index():
    """
    Renders the main page with input forms for changelog and repository summary.
    """
    return render_template('index.html')

@app.route('/generate_changelog_route', methods=['POST'])
def generate_changelog_route():
    """
    Handles changelog generation requests.
    """
    repo_url = request.form.get('repo_url_changelog')
    days_ago_str = request.form.get('days_ago_changelog')

    if not repo_url or not days_ago_str:
        return render_template('results.html', result_title="Error", result_content="Repository URL and days ago are required for changelog generation.")

    try:
        days_ago = int(days_ago_str)
        if days_ago <= 0:
            raise ValueError("Days ago must be a positive integer.")
    except ValueError:
        return render_template('results.html', result_title="Error", result_content="Days ago must be a valid positive integer.")

    try:
        logscribe = LogScribe(api_key=GEMINI_API_KEY, github_token=GITHUB_TOKEN)
        changelog_content = logscribe.generate_changelog(repo_url, days_ago)
        return render_template('results.html', result_title=f"Changelog for {repo_url} (last {days_ago} days)", result_content=changelog_content)
    except Exception as e:
        return render_template('results.html', result_title="Error", result_content=f"An error occurred during changelog generation: {e}")

@app.route('/get_repo_summary_route', methods=['POST'])
def get_repo_summary_route():
    """
    Handles repository summary requests.
    """
    repo_url = request.form.get('repo_url_summary')

    if not repo_url:
        return render_template('results.html', result_title="Error", result_content="Repository URL is required for repository summary.")

    try:
        logscribe = LogScribe(api_key=GEMINI_API_KEY, github_token=GITHUB_TOKEN)
        repo_summary_content = logscribe.get_repository_summary_with_gemini(repo_url)
        return render_template('results.html', result_title=f"Repository Summary for {repo_url}", result_content=repo_summary_content)
    except Exception as e:
        return render_template('results.html', result_title="Error", result_content=f"An error occurred during repository summary: {e}")

if __name__ == '__main__':
    app.run(debug=True) 