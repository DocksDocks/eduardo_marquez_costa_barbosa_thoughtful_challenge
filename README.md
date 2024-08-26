# Linux Guide

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

### You can follow instructions to Robocorp client [here](https://github.com/robocorp/rcc?tab=readme-ov-file#getting-started).
