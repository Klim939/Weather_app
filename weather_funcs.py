import requests

def load_config():
    with open('data/config.txt', 'r') as f:
        data = f.read().split('\n')
        global API_KEY
        API_KEY = data[0].split()[1]

load_config()

def get_location_key(city_name):
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}&details=true'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()[0]
        return data.get('Key')
    else:
        return None