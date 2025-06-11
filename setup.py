from setuptools import setup, find_packages

setup(
    name="arche_system",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "Flask",
        "waitress",
        "numpy",
        "pandas",
        "scipy",
        "statsmodels",
        "geopy",
        "ortools"
    ],
    entry_points={
        "console_scripts": [
            "arche-cli = arche_cli.main:cli",
        ],
    },
    author="ArchE Engineering Instance",
    author_email="arche@resonantiA.protocol",
    description="The ArchE Distributed Coordination Framework and Registry.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/arche_system", # Replace with actual URL
) 