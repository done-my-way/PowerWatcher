import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="power-watcher",
    version="0.1.0",
    author="Poima",
    author_email="author@example.com",
    description="Python3 context manager to log power consumption of any ML-pipeline running on a Nvidia-GPU.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WGussev/PowerWatcher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pynvml>=8.0.4"],
    python_requires='>=3.6',
)