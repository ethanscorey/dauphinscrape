# Dauphin Scrape
This is a simple package for scraping prisoner information from the [Dauphin County IML database](https://www.dauphinc.org:9443/IML).

## Installation
To install this package and its dependencies, you must have Python ^3.9 installed, as well as the [latest version of Poetry](https://python-poetry.org/docs/#installation).

Once Poetry and Python are properly set up, create and activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html) for the package.

After activating the virtual, clone/download this repository, then run the following command:
```sh
python -m pip install PATH_TO_THIS_REPOSITORY
```

## Usage
Once the project and its dependencies are installed, you can immediately run it without further configuration by first navigating to the directory holding the repository (the top-level directory, which contains the sub-directory `src`) then running:
```sh
python -m src.dauphin_scrape
```

Custom configuration would require you to edit the `src/dauphin_scrape.py` file itself. At some point in the future, I might refactor the code to allow for better customization (e.g., starting the scrape at a certain page). Unfortunately for you, today is not that day, but you're welcome to take a crack at it yourself.
