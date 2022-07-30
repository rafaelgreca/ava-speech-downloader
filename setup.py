from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name="ava-speech-downloader",
    version="1.0",
    author="Rafael Greca",
    author_email="rafaelgreca97@hotmail.com",
    description="Toolkit for downloading the audio files from the AVA Speech dataset.",
    long_description=readme,
    url="https://github.com/rafaelgreca/ava-speech-downloader",
    packages=find_packages(),
    license=license,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8.10'
    ],
    python_requires='>=3.8.10',
    install_requires=[
        'wheel',
        'pandas',
        'youtube-dl',
        'ffmpeg'
    ],
)