import setuptools

with open("docs/en/index.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

with open("requirements.txt") as f:
    requires = f.read().splitlines()

setuptools.setup(
    name="strict_json_rpc",
    version="0.1.0",
    author="Dmitriy Kiryushchenko",
    description="json-rpc server and client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dmitrijkir/strict-json-rpc",
    install_requires=requires,
    keywords="dmkir",
    license="Apache License 2.0",
    packages=["strict_json_rpc"],
    classifiers=[
        "Environment :: Web Environment",
        "Typing :: Typed",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development",
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
