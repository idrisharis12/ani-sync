from setuptools import setup

setup(
    name="ani-sync",
    version="2.4.0",
    description="Stream anime from your terminal and automatically sync watch progress to MyAnimeList",
    author="Idris Haris",
    url="https://github.com/idrisharis12/ani-sync",
    py_modules=["ani_sync"],
    install_requires=[
        "requests>=2.28.0",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "ani-sync = ani_sync:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)
