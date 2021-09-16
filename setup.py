import codecs
import os
import sys

from setuptools import find_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_definitions(rel_path, *words):
    dwords = {word: None for word in words}
    for line in read(rel_path).splitlines():
        for word in words:
            if line.startswith(f'__{word}__'):
                delim = '"' if '"' in line else "'"
                dwords[word] = line.split(delim)[1]
                break

    return [dwords[word] for word in dwords]


long_description = read('README.md')

_name, _version, _description, _author, _author_email, package_name = get_definitions(
    os.path.join('src', '__init__.py'),
    'tool_name',
    'version',
    'description',
    'author',
    'author_email',
    'package_name')

setup(
    name=package_name,
    version=_version,
    description=_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    url='https://github.com/guionardo/py-servicebus-cli',
    keywords='azure service bus',
    project_urls={
        "Documentation": "https://github.com/guionardo/py-servicebus-cli/wiki",
        "Source": "https://github.com/guionardo/py-servicebus-cli",
    },
    author=_author,
    author_email=_author_email,
    packages=find_packages(
        where=".",
        exclude=["tests"],
    ),
    entry_points={
        "console_scripts": [
            f"{_name}=src.main:main"
        ]
    },
    install_requires=[
        "azure-servicebus",
        "xmltodict"
    ],
    zip_safe=True,
    python_requires='>=3.6.*'
)
