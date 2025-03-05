from setuptools import setup, find_packages

setup(
    name="rpi-can-monitor",
    version="0.1.0",
    description="A versatile CAN bus monitoring tool with multiple UI options",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/rpi-can-monitor",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-can>=4.1.0",
        "PyQt6>=6.4.0",
    ],
    extras_require={
        "modern": ["PySide6>=6.5.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "can-monitor=app:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
)