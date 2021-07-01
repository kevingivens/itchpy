from setuptools import setup

import versioneer

install_requires = [
    "sly",
]

test_requirements = ["pytest-cov", "pytest-mock", "pytest>=3"]

packages = ["itchpy"]

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Operating System :: POSIX",
    "Development Status :: 3 - Alpha",
]

setup(
    name="fxtrader",
    classifiers=classifiers,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Python based parser generator for ITCH messages",
    platforms=["POSIX"],
    author="Kevin Givens",
    author_email="givenskevinm@gmail.com",
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    tests_require=test_requirements,
    license="MIT",
    zip_safe=False,
)
