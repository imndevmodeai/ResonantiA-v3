
    elif language == "python":
        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            script_path = f.name
        
        # Execute the script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env={**os.environ, **environment}
        )
        
        # Clean up the temporary file
        os.remove(script_path)

    elif language == "bash":
        # Execute the bash script
        result = subprocess.run(
            code,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, **environment}
        )

    else:
        raise ValueError(f"Unsupported language: {language}")

    # Process the result
