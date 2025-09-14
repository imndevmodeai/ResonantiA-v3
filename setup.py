from setuptools import setup, find_packages

setup(
    name="Three_PointO_ArchE",
    version="3.1.0",
    author="Keyholder B.J. Lewis & ArchE",
    author_email="[email protected]",
    description="The core components of the ResonantiA Protocol v3.1-CA ArchE System.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="[Awaiting public repository URL]",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'requests',
        'networkx',
        'google-generativeai',
        'docker',
        'mesa',
        'matplotlib',
        'statsmodels',
        'scikit-learn',
        'joblib',
        'ortools',
        'dowhy',
        'numexpr',
        'pytest',
        'pytest-mock',
        'beautifulsoup4',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'arche-cli=arche_cli.main:cli',
        ],
    },
) 