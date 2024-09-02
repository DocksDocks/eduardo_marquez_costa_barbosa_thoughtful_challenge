# Linux Guide

### Recommmended versions
python=3.10+

pip=23.2.1+

## There are multiple ways of running the code

## 1 - Using Robocorp Code extension in VSCODE

### You can download the Robocorp Code extension [here](https://marketplace.visualstudio.com/items?itemName=robocorp.robocorp-code).

### After downloading the extension just connect your Robocorp account and you will have a function inside the dropdown in Python Task, called "Run Task"

### Run "Run Task"

## 2 - Setting up your own environment

### Set up virtual environment
```
sudo apt update
sudo apt install python3-venv
python3 -m venv robocorp-env
source robocorp-env/bin/activate
```

### Update pip inside environment and install dependencies
```
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Create .env file based on .env.example

### Run code inside environment
```
python tasks.py
```

