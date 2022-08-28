# LawTech Hackson 2022

## Installation

- (Optional) Install [pyenv](https://github.com/pyenv/pyenv) to easily switch Python.
- Use Python 3.9.2+. Via pyenv: `pyenv install 3.9.2`.
- (Optional) `pyenv local 3.9.2`: Let pyenv to switch 3.9.2 automatically for this project.
- Install [Poetry](https://python-poetry.org/) to manage **dependencies**.
- ~~`poetry shell`: Ask poetry to create a Python virtual environment ([venv](https://docs.python.org/3/library/venv.html)): Everytime you use command line to run this project, execute this command to switch.~~
- `poetry install`: Install dependencies.

### Formatter

This project uses [yapf](https://github.com/google/yapf).

## Local Dev

Command line ways :

way 1. 

- ~~`poetry run python lawtechhackson/server_main.py`~~ `poetry run uvicorn lawtechhackson.server_main:app --reload`

way 2. 

1. `poetry shell`
2. ~~`python lawtechhackson/server_main.py`~~ `uvicorn lawtechhackson.server_main:app --reload`


VSCode way:

- Make sure that you select Python local poetry interpreter/environment, use cmd+shift+p to select or select on the VSCode UI. Usually the name should include `poetry` or `.venv` 
- Open the target file. Then Use VSCode F5 to launch and debug. 

## Docker 

### Backend: Python API server (use Python 3.9.2 base image)

Please fill `mongo_connect_str` in `.env` first, then the built docker image will use it. Or `-e mongo_connect_str=value` while `docker run`

```
docker build -f Dockerfile.backend -t perfect-match-backend .
docker run -p 8000:8000 --name perfect-match-backend  perfect-match-backend 
```

You can open http://localhost:8000 to check. 

### Frontend: React + Node.js Dev Server 

docker build -f Dockerfile.frontend -t perfect-match-frontend .
docker run -p 3000:3000 --name perfect-match-frontend perfect-match-frontend

### Run 

open http://localhost:3000

## Docker: Mount the current folder to live Change + Run
Frontend: 
- docker run -ti -p 3000:3000 -v ${PWD}/lawtechhackson_client:/workspace/lawtechhackson_client --name perfect-match-frontend.dev node:16.13.0-stretch-slim /bin/bash
- cd workspace/lawtechhackson_client
- `yarn install` (first time)
- yarn start

Backend: 
1. docker build -f Dockerfile.backend.base -t perfect-match-backend.dev .
2. docker run -ti -p 8000:8000 -v ${PWD}:/workspace --name perfect-match-backend.dev perfect-match-backend.dev /bin/bash
3. poetry install
5. ~~`poetry run python lawtechhackson/server_main.py`~~ (<-somehow it does not work. Only `LawyerService init` printed, and terminated, no `start to init module` printed). Use this to start: `poetry run uvicorn lawtechhackson.server_main:app --port 8000 --host 0.0.0.0 --timeout-keep-alive 180`