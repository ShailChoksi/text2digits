import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="text2digits",
    version="0.1.0",
    author="Shail Choksi",
    author_email="choksishail@gmail.com",
    description="A small library to convert text numbers to digits in a string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/careless25/text2digits",
    packages=setuptools.find_packages(),
    keywords="text2numbers words2numbers digits numbers",
    project_urls={
        'Funding': "https://www.paypal.me/careless25",
        'Source': "https://github.com/careless25/text2digits"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
