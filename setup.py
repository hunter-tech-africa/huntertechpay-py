"""Setup script for HunterTechPay Python SDK."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="huntertechpay",
    version="1.0.1",
    author="HunterTechPay",
    author_email="support@huntertechpay.com",
    description="Official Python SDK for HunterTechPay mobile money API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hunter-tech-africa/huntertechpay-py",
    project_urls={
        "Documentation": "https://huntertechpay.com/merchant-api/documentation",
        "Source": "https://github.com/hunter-tech-africa/huntertechpay-py",
        "Issue Tracker": "https://github.com/hunter-tech-africa/huntertechpay-py/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="huntertechpay mobile money payment africa moala orange mtn wave",
    license="MIT",
)
