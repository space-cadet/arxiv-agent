from setuptools import setup, find_packages

setup(
    name="arxiv-agent",
    version="0.1",
    packages=find_packages(include=['backend*', 'worker*']),
    python_requires=">=3.8",
    install_requires=[
        "httpx",
        "backoff",
        "pytest",
        "pytest-asyncio",
        "pytest-mock"
    ],
)