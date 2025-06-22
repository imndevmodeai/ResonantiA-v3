import os
from flask import Flask, render_template, request
from markdown import markdown
from logscribe_core import LogScribe

app = Flask(__name__)

# It's recommended to set these as environment variables for security
# export GEMINI_API_KEY="your_key_here"
# export GITHUB_TOKEN="your_token_here"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

@app.route('/', methods=['GET', 'POST'])
def index():
    changelog_html = ""
    error_message = ""
    repo_url_form = ""
    days_ago_form = 7  # Default value

    if not GEMINI_API_KEY:
        error_message = "CRITICAL ERROR: GEMINI_API_KEY environment variable is not set. The application cannot function."
        return render_template('index.html', error_message=error_message)

    if request.method == 'POST':
        repo_url = request.form.get('repo_url')
        days_ago_str = request.form.get('days_ago')
        
        # Preserve form state
        repo_url_form = repo_url
        
        try:
            days_ago = int(days_ago_str) if days_ago_str else 7
            days_ago_form = days_ago
            
            if not repo_url:
                raise ValueError("GitHub Repository URL is required.")

            try:
                scribe = LogScribe(api_key=GEMINI_API_KEY, github_token=GITHUB_TOKEN)
                changelog_md = scribe.generate_changelog(repo_url, days_ago=days_ago)
                # Convert markdown to HTML for safe rendering in the template
                changelog_html = markdown(changelog_md, extensions=['fenced_code', 'tables'])
            except Exception as e:
                error_message = f"An error occurred: {e}"

        except ValueError as e:
            error_message = f"Invalid input: {e}"

    return render_template(
        'index.html', 
        changelog_html=changelog_html, 
        error_message=error_message,
        repo_url_form=repo_url_form,
        days_ago_form=days_ago_form
    )

if __name__ == '__main__':
    # For local development, you can run this script directly.
    # For production, use a proper WSGI server like Gunicorn or Waitress.
    app.run(debug=True, port=5001) 