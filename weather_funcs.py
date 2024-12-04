import requests

def load_config():
    with open('data/config.txt', 'r') as f:
        data = f.read().split('\n')
        global API_KEY
        API_KEY = data[0].split()[1]