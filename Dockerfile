FROM python:3.11
workdir /bot
copy requirements.txt /bot/
run pip install -r requirements.txt
copy . /bot
cmd python main.py
