import unittest
from unittest.mock import patch, MagicMock
import os
import json
from datetime import datetime, timedelta

# Import the LogScribe class
from Three_PointO_ArchE.logscribe_core import LogScribe

class TestLogScribe(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_openai_key"
        self.github_token = "test_github_token"
        self.scribe = LogScribe(api_key=self.api_key, github_token=self.github_token)
        
        # Sample commit data
        self.sample_commits = [
            {
                "commit": {
                    "message": "feat: Add new authentication system",
                    "author": {"name": "Test Author"}
                }
            },
            {
                "commit": {
                    "message": "fix: Resolve login bug",
                    "author": {"name": "Test Author"}
                }
            }
        ]

    def test_init_without_api_key(self):
        """Test initialization without API key raises ValueError."""
        with self.assertRaises(ValueError):
            LogScribe(api_key="")

    def test_parse_repo_url_valid(self):
        """Test parsing valid GitHub repository URL."""
        url = "https://github.com/owner/repo"
        result = self.scribe._parse_repo_url(url)
        self.assertEqual(result["owner"], "owner")
        self.assertEqual(result["repo"], "repo")

    def test_parse_repo_url_invalid(self):
        """Test parsing invalid GitHub repository URL."""
        url = "https://not-github.com/owner/repo"
        result = self.scribe._parse_repo_url(url)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_fetch_commits_success(self, mock_get):
        """Test successful commit fetching."""
        # Mock the GitHub API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_commits
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        commits = self.scribe._fetch_commits("owner", "repo", "2024-01-01")
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["commit"]["message"], "feat: Add new authentication system")

    @patch('requests.get')
    def test_fetch_commits_error(self, mock_get):
        """Test error handling in commit fetching."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        with self.assertRaises(requests.exceptions.RequestException):
            self.scribe._fetch_commits("owner", "repo", "2024-01-01")

    def test_generate_changelog_prompt(self):
        """Test changelog prompt generation."""
        commit_messages = "- feat: Add new feature\n- fix: Fix bug"
        prompt = self.scribe._generate_changelog_prompt(commit_messages)
        self.assertIn("You are an expert technical writer", prompt)
        self.assertIn(commit_messages, prompt)

    @patch('openai.chat.completions.create')
    @patch('requests.get')
    def test_generate_changelog_success(self, mock_get, mock_openai):
        """Test successful changelog generation."""
        # Mock GitHub API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_commits
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock OpenAI API response
        mock_openai_response = MagicMock()
        mock_openai_response.choices = [
            MagicMock(message=MagicMock(content="## Changelog\n\n### 🚀 New Features\n- Added new authentication system"))
        ]
        mock_openai.return_value = mock_openai_response

        changelog = self.scribe.generate_changelog("https://github.com/owner/repo")
        self.assertIn("Changelog", changelog)

    @patch('requests.get')
    def test_generate_changelog_invalid_url(self, mock_get):
        """Test changelog generation with invalid URL."""
        with self.assertRaises(ValueError):
            self.scribe.generate_changelog("https://not-github.com/owner/repo")

    @patch('requests.get')
    def test_generate_changelog_no_commits(self, mock_get):
        """Test changelog generation with no commits."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        changelog = self.scribe.generate_changelog("https://github.com/owner/repo")
        self.assertIn("No new commits found", changelog)

if __name__ == '__main__':
    unittest.main()

