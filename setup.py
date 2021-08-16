from setuptools import setup, find_packages

# See note below for more information about classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name="dislevel",
    version="0.0.5",
    description="A leveling cog for discord bots",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shahprog/dislevel/",
    author="Md Shahriyar Alam",
    author_email="mdshahriyaralam552@gmail.com",
    license="MIT", 
    classifiers=classifiers,
    keywords="discord discord-rank discord-profile discord-leveling",
    packages=find_packages(),
    install_requires=[
        "discord.py",
        "databases",
        "easy-pil",
    ],
    include_package_data=True,
)
