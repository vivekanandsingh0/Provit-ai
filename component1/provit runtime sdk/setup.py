from setuptools import setup, find_packages


# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="provit-ai-runtime",
    version="0.1.0",
    description="ProVit AI Runtime SDK - Lightweight evidence capture for AI decisions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ProVit AI",
    author_email="dev@provit.ai", 
    url="https://github.com/provit-ai/runtime-sdk", # Placeholder URL
    project_urls={
        "Bug Tracker": "https://github.com/provit-ai/runtime-sdk/issues",
        "Documentation": "https://docs.provit.ai",
    },
    packages=find_packages(), 
    py_modules=["provit_sdk"],
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Monitoring",
    ],
    python_requires='>=3.6',
)
