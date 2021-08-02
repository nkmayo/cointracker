from setuptools import setup, find_packages

#call setup function
setup(
    author = "Nathanael Mayo",
    description = "work-in-progress package that organizes cryptocurrency transactions for taxes.",
    name = "cointracker",
    version = "0.1.0",
    packages = find_packages(include=["cointracker", "cointracker.*"]),
    install_requires=['pandas', 'requests'],
)