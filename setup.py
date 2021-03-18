import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytesturl",
    version="0.0.1",
    author="Johan Hansson",
    author_email="johan.eric.hansson@gmail.com",
    description="This package check urls in the directory and sub directories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JohanWork/pytesturl",
    scripts=['pytesturl'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires=['pyyaml']
)
