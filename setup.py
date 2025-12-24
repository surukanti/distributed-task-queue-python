from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="distributed-task-queue",
    version="1.0.0",
    author="Surukanti",
    author_email="surukanti@example.com",
    description="Production-ready distributed task queue system with retry, DLQ, metrics, and tracing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/surukanti/distributed-task-queue-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "task-queue-gateway=gateway.server:main",
            "task-queue-worker=worker.worker:main",
            "task-queue-dashboard=dashboard.app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
