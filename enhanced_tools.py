from typing import Dict, Any, Callable, Optional, List
import numpy as np
import requests
import json # Import the json module
import os
import io
import sys # For execute_code stdout/stderr redirection

# Attempt to import from local package structure first
try:
    from .cfp_framework import comparative_flux_density, potential_function # For exploit_potential_action
    from .scalable_framework import ScalableAgent # For type hinting if actions are methods or need agent context
except ImportError:
    # Fallback if running script directly or modules are in the same flat directory
    # This is less ideal for package distribution but useful for standalone script testing.
    # Ensure that if these are not found, the script might partially fail if those specific
    # functions from cfp_framework or ScalableAgent type hints are strictly needed at import time.
    # For now, the direct dependencies in this file are mostly on external libraries or standard Python.
    pass # Allow to pass if not found, as they are for type hinting or specific advanced tools not core to these search functions


def web_search(query: str, num_results: int = 5) -> list[str]:
    """
    Performs a web search using a simplified, placeholder implementation.
    This function simulates a web search and returns a list of dummy URLs
    related to the query. In a real-world application, this would be replaced
    with actual web search API calls (e.g., Google Search API, DuckDuckGo API).
    Args:
        query (str): The search query string.
        num_results (int): The number of search results to return (default: 5).
    Returns:
        list[str]: A list of dummy URLs as strings.
    Example:
        >>> results = web_search("quantum computing", num_results=3)
        >>> print(results) # doctest: +SKIP
        ['https://example.com/search?q=quantum_computing&result=1', 'https://example.com/search?q=quantum_computing&result=2', 'https://example.com/search?q=quantum_computing&result=3']
    """
    # A slightly more descriptive dummy URL
    dummy_urls = [f"https://example.com/search?q={query.replace(' ', '_')}&result={i+1}" for i in range(num_results)]
    return dummy_urls


def huggingface_dataset_search(query: str, num_results: int = 3) -> list[Dict[str, str]]:
    """
    Searches for datasets on Hugging Face Datasets using the Hugging Face API.
    This function queries the Hugging Face Datasets API to search for datasets
    related to the given query. It returns a list of dictionaries, where each
    dictionary contains information about a dataset, including its id and URL.
    Args:
        query (str): The search query string (e.g., "natural language processing").
        num_results (int): The number of search results to return (default: 3).
    Returns:
        list[Dict[str, str]]: A list of dictionaries, each containing dataset info ('id', 'url', 'description').
                              Returns an empty list if no datasets are found or if there is an error.
    Example:
        >>> datasets = huggingface_dataset_search("natural language processing", num_results=1) # doctest: +SKIP
        >>> for dataset in datasets: # doctest: +SKIP
        ...     print(f"Dataset ID: {dataset['id']}, URL: {dataset['url']}") # doctest: +SKIP
        Dataset ID: acl, URL: https://huggingface.co/datasets/acl # Example, actual ID will vary
    """
    HF_API_BASE_URL = "https://huggingface.co/api/datasets"

    params = {'search': query, 'limit': num_results, 'full': 'false'}

    try:
        response = requests.get(HF_API_BASE_URL, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        search_results = response.json()

        datasets_info = []
        for dataset_result in search_results[:num_results]:
            dataset_id = dataset_result.get('id')
            if not dataset_id and 'repoId' in dataset_result:
                dataset_id = dataset_result['repoId']
            elif not dataset_id and 'name' in dataset_result:
                 dataset_id = dataset_result['name']
            
            if not dataset_id: # If no usable ID found, use N/A or skip
                dataset_id = "N/A"

            dataset_url = f"https://huggingface.co/datasets/{dataset_id}"
            description = dataset_result.get('description', 'N/A')
            if description and len(description) > 100:
                description = description[:100] + '...'
            datasets_info.append({'id': dataset_id, 'url': dataset_url, 'description': description})
        return datasets_info
    except requests.exceptions.RequestException as e:
        print(f"Error during Hugging Face Dataset search: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Hugging Face API: {e}")
        return[]


def github_project_search(query: str, num_results: int = 3, sort: str = "best-match", order: str = "desc") -> list[Dict[str, str]]:
    """
    Searches for GitHub projects using the GitHub API.
    Args:
        query (str): The search query string (e.g., "quantum machine learning").
        num_results (int): The number of search results to return (default: 3, max usually 100 per page).
        sort (str): The sort field. Can be 'stars', 'forks', 'help-wanted-issues', 'updated', or 'best-match'.
        order (str): The sort order, 'asc' or 'desc'.
    Returns:
        list[Dict[str, str]]: A list of dictionaries, each containing project info ('name', 'url', 'description', 'stars').
                              Returns an empty list if no projects are found or in case of error.
    Example:
        >>> projects = github_project_search("tetris python", num_results=1) # doctest: +SKIP
        >>> for project in projects: # doctest: +SKIP
        ...     print(f"Project: {project['name']}, URL: {project['url']}, Stars: {project['stars']}") # doctest: +SKIP
        Project: PythonTetris, URL: https://github.com/chvin/PythonTetris, Stars: ...
    """
    GITHUB_API_URL = "https://api.github.com/search/repositories"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    # GitHub API token can be added for higher rate limits:
    # token = os.environ.get("GITHUB_TOKEN")
    # if token:
    #     headers['Authorization'] = f"token {token}"

    params = {'q': query, 'per_page': num_results, 'sort': sort, 'order': order}

    try:
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json().get('items', [])
        projects_info = []
        for item in search_results:
            description = item.get('description', 'N/A')
            if description and len(description) > 150: # Check if description is not None before slicing
                description_truncated = description[:150] + '...'
            elif description is None:
                description_truncated = 'N/A' # Explicitly set to 'N/A' if None
            else:
                description_truncated = description

            projects_info.append({
                'name': item.get('full_name', 'N/A'),
                'url': item.get('html_url', 'N/A'),
                'description': description_truncated,
                'stars': item.get('stargazers_count', 0)
            })
        return projects_info
    except requests.exceptions.RequestException as e:
        print(f"Error during GitHub Project search: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from GitHub API: {e}")
        return []