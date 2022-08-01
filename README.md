# LawTech Hackson 2022

### Installation

- (Optional) Install [pyenv](https://github.com/pyenv/pyenv) to easily switch Python.
- Use Python 3.9.2+. Via pyenv: `pyenv install 3.9.2`.
- (Optional) `pyenv local 3.9.2`: Let pyenv to switch 3.9.2 automatically for this project.
- Install [Poetry](https://python-poetry.org/) to manage **dependencies**.
- `poetry shell`: Ask poetry to create a Python virtual environment ([venv](https://docs.python.org/3/library/venv.html)): Everytime you use command line to run this project, execute this command to switch.
- `poetry install`: Install dependencies.

### Formatter

This project uses [yapf](https://github.com/google/yapf).

### Local Dev

Command line ways :

way 1. 

- `poetry run python lawtechhackson/main.py`

way 2. 

1. `poetry shell`
2. `python lawtechhackson/main.py`

VSCode way:

- Make sure that you select Python local poetry interpreter/environment, use cmd+shift+p to select or select on the VSCode UI. Usually the name should include `poetry` or `.venv` 
- Open the target file. Then Use VSCode F5 to launch and debug. 