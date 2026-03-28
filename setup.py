cat > setup.py << 'EOF'
"""Mimir - Intelligent Linux Companion"""
from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="mimir-ai",
    version="4.0.0",
    author="Chioma Obiagboso",
    author_email="chiomadebie@gmail.com",
    description="Intelligent Linux Companion with AI - Monitor, predict, and heal your system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/debiey/mimir",
    project_urls={
        "Bug Reports": "https://github.com/debiey/mimir/issues",
        "Source": "https://github.com/debiey/mimir",
        "Documentation": "https://github.com/debiey/mimir#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Terminals",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "ai": ["ollama-python>=0.1.0"],
        "dev": ["pytest>=7.0.0", "black", "flake8", "build", "twine"],
    },
    entry_points={
        "console_scripts": [
            "mimir=mimir:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="linux, monitoring, ai, ollama, terminal, system, health, dashboard",
)

