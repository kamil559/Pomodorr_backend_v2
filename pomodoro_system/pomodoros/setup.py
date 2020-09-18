from setuptools import find_packages, setup

setup(
    name="pomodoros",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["injector", "foundation"],
    extras_require={"dev": ["pytest"]},
)
