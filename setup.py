#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['webexteamssdk', 'coloredlogs', 'websockets==8.1', 'backoff', 'pyadaptivecards==0.1.1']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Finbarr Brady",
    author_email='finbarr.brady@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Python package for a Webex Bot based on websockets.",
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
    version='0.2.17',
    zip_safe=False,
)
