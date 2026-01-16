"""Setup script for codebase-analyst CLI tool."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="codebase-analyst",
    version="1.2.0",
    description="AI-powered codebase analysis and documentation generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Codebase Analyst Team",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.3.0",
        "langchain-openai>=0.3.0",
        "langgraph>=0.2.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "langfuse>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "codebase-analyst=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="codebase analysis documentation ai langchain",
)
