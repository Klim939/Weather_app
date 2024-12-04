import requests
from app import error


def load_config():
    with open('data/config.txt', 'r') as f:
        data = f.read().split('\n')
        global API_KEY
        API_KEY = data[0].split()[1]

load_config()

def get_location_key(city_name: str):
    city_name = city_name.capitalize()
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}&details=true'
    response = requests.get(url)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data.get('Key')
    else:
        return None

def get_weather_data(city_name: str):
    try:
        location_key = get_location_key(city_name)
        if location_key == None:
            error(error_message='Не удалось получить ключ города')
            return None
        else:
            weather_url = f'http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{location_key}?apikey={API_KEY}&details=true&metric=true'
            weather_response = requests.get(weather_url)
            if weather_response.status_code == 200 and weather_response.json():
                data = weather_response.json()[0]
                return {
                    'temperature': {'real': data['Temperature']['Value'],
                                    'feel': data['RealFeelTemperature']['Value']},
                    'wind': {'speed': data['Wind']['Speed']['Value'],
                             'direction': data['Wind']['Direction']['Localized'].replace('N','С').replace('S','Ю').replace('W','З').replace('E','В')},
                    'humidity': data['RelativeHumidity'],
                    'precip_prob': data['PrecipitationProbability'],
                    'total_liq': data['TotalLiquid'],
                    'cloud_cover': data['CloudCover']
                }
            else:
                error(error_message='Не удалось получить данные о погоде')
                return None
    except Exception as e:
        error(error_message=e)
        return None


print(get_weather_data('Москва'))