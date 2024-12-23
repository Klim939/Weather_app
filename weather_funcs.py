import requests

def load_config():
    with open('data/config.txt', 'r') as f:
        data = f.read().split('\n')
        global API_KEY
        API_KEY = data[0].split()[1]

def get_location_key(city_name: str):
    city_name = city_name.capitalize()
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}&details=true'
    response = requests.get(url)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data.get('Key'), data['GeoPosition']['Latitude'], data['GeoPosition']['Longitude'],
    else:
        return None

def get_weather_data(city_name: str, days=1):
    try:
        location_key, latitude, longitude = get_location_key(city_name)
        if location_key == None:
            return 'Ошибка: не удалось получить ключ города'
        else:
            forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/{f"{days}day"}/{location_key}?apikey={API_KEY}&metric=true&details=true"
            forecast_response = requests.get(forecast_url)
            daily_forecasts = []
            if forecast_response.status_code == 200 and forecast_response.json():
                for day in forecast_response.json()['DailyForecasts']:
                    data = day
                    daily_forecasts.append({
                        "date": data["Date"],
                        'temperature': {'real': round((data['Temperature']['Minimum']['Value'] + data['Temperature']['Maximum']['Value']) / 2),
                                        'feel': round((data['RealFeelTemperature']['Minimum']['Value'] + data['RealFeelTemperature']['Maximum']['Value']) / 2)},
                        'wind': {'speed': data['Day']['Wind']['Speed']['Value'],
                                 'direction': data['Day']['Wind']['Direction']['Localized'].replace('N', 'С').replace('S',
                                                                                                               'Ю').replace(
                                     'W', 'З').replace('E', 'В')},
                        'humidity': data['Day']['RelativeHumidity']['Average'],
                        'precip_prob': data['Day']['PrecipitationProbability'],
                        'total_liq': data['Day']['TotalLiquid']['Value'],
                        'cloud_cover': data['Day']['CloudCover'],
                        'latitude': latitude,
                        'longitude': longitude
                    })
            else:
                return 'Ошибка: не удалось получить данные о погоде'
        return daily_forecasts, latitude, longitude
    except Exception as e:
        return f'Error, key: {e}', None, None

