# LogScribe Utility

The `LogScribe` utility is a powerful, self-contained Python script designed to automate the creation of human-readable changelogs from a GitHub repository's commit history. It leverages the OpenAI API (specifically, the `gpt-4` model) to analyze, categorize, and summarize commit messages into a well-structured Markdown document.

This tool is invaluable for developers and project managers who need to quickly generate release notes or track project progress without manually sifting through raw git logs.

## Key Features

- **Automated Categorization**: Automatically groups commits into logical sections:
    - `🚀 New Features`
    - `🐛 Bug Fixes`
    - `🔧 Maintenance & Refactoring`
    - `📚 Documentation`
- **Intelligent Summarization**: Uses AI to transform technical commit messages into concise, user-friendly descriptions.
- **Trivial Commit Filtering**: Ignores insignificant commits (e.g., merge commits, minor style fixes) to keep the changelog clean and focused.
- **Configurable Timeframe**: Allows you to specify the number of days back to look for commits.
- **GitHub Integration**: Fetches commit data directly from public or private GitHub repositories using the GitHub API.

## How to Use

The `LogScribe` utility can be run as a standalone script.

### Prerequisites

Before running the script, you must configure the following environment variables:

1.  **OpenAI API Key**: The script requires a valid OpenAI API key to make requests to the GPT-4 model.
    ```bash
    export OPENAI_API_KEY="your_openai_api_key_here"
    ```

2.  **GitHub Token (Optional but Recommended)**: To interact with the GitHub API, especially for private repositories or to avoid rate limiting, a personal access token is highly recommended.
    ```bash
    export GITHUB_TOKEN="your_github_personal_access_token_here"
    ```

### Running the Script

You can execute the script directly from the command line. The main execution block in `logscribe_core.py` is configured to run with an example repository.

1.  **Navigate** to the root directory of the project.
2.  **Modify** the `repo_to_analyze` variable in `logscribe_core.py` to point to your target GitHub repository URL.
3.  **Run** the script:
    ```bash
    python logscribe_core.py
    ```

The generated changelog will be printed directly to the console.

## Core Implementation

The utility is implemented in the `logscribe_core.py` file and consists of the `LogScribe` class.

-   **`__init__(self, api_key, github_token)`**: Initializes the class, setting up the necessary API keys and headers for both OpenAI and GitHub requests.
-   **`_parse_repo_url(self, repo_url)`**: A helper method to extract the repository owner and name from a standard GitHub URL.
-   **`_fetch_commits(self, owner, repo, since_date)`**: Handles the API calls to GitHub to retrieve all commits from a specified date. It includes pagination to fetch all results.
-   **`_generate_changelog_prompt(self, commit_messages)`**: Constructs the detailed prompt that is sent to the OpenAI API. This prompt instructs the AI on how to process the raw commit messages and format the output.
-   **`generate_changelog(self, repo_url, days_ago)`**: The main public method that orchestrates the entire process: parsing the URL, fetching commits, and calling the AI to generate the final changelog. It also includes robust error handling for API failures or invalid inputs.

## Testing

The utility is accompanied by a suite of unit tests located in `tests/logscribe/test_logscribe_core.py`. These tests use `unittest.mock` to patch external API calls (GitHub, OpenAI), ensuring that the script's logic can be tested reliably and in isolation without making actual network requests. This allows for verification of URL parsing, error handling, and prompt generation logic. 