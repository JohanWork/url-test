import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="url-test",
    version="0.0.3.3",
    author="Johan Hansson",
    author_email="johan.eric.hansson@gmail.com",
    description="This package check urls in the directory and sub directories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JohanWork/url-test",
    scripts=['url-test', 'main.py'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires=['pyyaml', 'regex', 'PyYAML']
)
