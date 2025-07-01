#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['webexpythonsdk==2.0.4', 'coloredlogs', 'websockets==11.0.3', 'backoff']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

extras_requirements = {
    "proxy": ["websockets_proxy>=0.1.1"]
}

setup(
    author="Finbarr Brady",
    author_email='finbarr@somemail.com',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    description="Python package for a Webex Bot based on websockets.",
    extras_require=extras_requirements,
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    long_description_content_type="text/markdown",
    keywords='webex_bot',
    name='webex_bot',
    packages=find_packages(include=['webex_bot', 'webex_bot.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/fbradyirl/webex_bot',
    version='1.0.4',
    zip_safe=False,
)
