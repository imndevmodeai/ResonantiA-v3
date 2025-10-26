# 1. Prerequisites

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
List the necessary software and versions. Link to installation guides where appropriate.
-->

Before setting up Arche, ensure you have the following prerequisites installed and configured:

*   **Python**
    *   Version: Python 3.9+ is recommended.
    *   Installation: You can download Python from the [official website](https://www.python.org/downloads/).
*   **Git**
    *   Installation: You can download Git from the [official website](https://git-scm.com/downloads). For Debian-based Linux distributions like Ubuntu, you can install it from the command line.

        **Debian/Ubuntu Installation**

        For the latest stable version in your distribution's repository:
        ```bash
        sudo apt-get update
        sudo apt-get install git
        ```

        For the latest stable upstream Git version (requires adding a PPA on Ubuntu):
        ```bash
        sudo add-apt-repository ppa:git-core/ppa
        sudo apt update
        sudo apt install git
        ```
*   **Docker Desktop/Engine**
    *   Importance: Docker is crucial for sandboxing code execution via the `CodeExecutor` tool, providing a secure and isolated environment for running untrusted code. This prevents any executed code from affecting the host system.
    *   Installation: You can download Docker from the [official website](https://www.docker.com/products/docker-desktop/).
*   **Required Python Libraries**
    *   Overview: The project relies on a set of Python libraries for its core functionality, including data analysis, machine learning, and interaction with various APIs.
    *   Link to `requirements.txt`: All required libraries are listed in the `requirements.txt` file. You can install them using pip:
        ```bash
        pip install -r requirements.txt
        ```
        You can view the full list here: [`requirements.txt`](../../requirements.txt) 