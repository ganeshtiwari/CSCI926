# CSCI926
Project Repo for CSCI926 (Software Testing)

# Resources 
[Week 1 slide](https://docs.google.com/presentation/d/1BnmPHccQ5xg8k5IJvG6wIy1oJznhBIennWBR5TcS-5c/edit#slide=id.p)

# Task 2 
1. Tools Choice 
  - [Unit Test - Pytest](https://docs.pytest.org/en/8.0.x/)
  - [Unit Test - UnitTest](https://docs.python.org/3/library/unittest.html)
  - [Mock Test - Mock](https://pypi.org/project/mock/)
  - [Ui Test - PyAutoGUI](https://pypi.org/project/PyAutoGUI/)
  - [Code Analysis - Ruff](https://github.com/astral-sh/ruff)

2. Application Choice
  - [Exaile](https://github.com/exaile/exaile?tab=readme-ov-file) [site](https://exaile.org/)


## Setting up the project 
```
sudo apt install python3 python3-pip python3-gi python3-gi-cairo gir1.2-gtk-3.0 libdb-dev
pip install berkeleydb mutagen pytest pytest-mock
```

## Running tests
```
export EXAILE_DIR=<your exaile dir>
/bin/python3 -m pytest tests/xl/
```