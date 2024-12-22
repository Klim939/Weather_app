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
        return data.get('Key')
    else:
        return None

def get_weather_data(city_name: str, days=1):
    try:
        location_key = get_location_key(city_name)
        if location_key == None:
            return 'Ошибка: не удалось получить ключ города'
        else:
            forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/{f"{days}day"}/{location_key}?apikey={API_KEY}&metric=true&details=true"
            forecast_response = requests.get(forecast_url)
            print(forecast_response.json())
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
                        'cloud_cover': data['Day']['CloudCover']
                    })
            else:
                return 'Ошибка: не удалось получить данные о погоде'
        return daily_forecasts
    except Exception as e:
        return f'Error, key: {e}'

def weather_model(city_name: str):
    data = get_weather_data(city_name)
    try:
        bad_weather_coef = 0
        temp = data['temperature']['real']
        wind_speed = data['wind']['speed']
        humidity = data['humidity']
        precip_prob = data['precip_prob']
        total_liq = data['total_liq']
        cloud_cover = data['cloud_cover']

        # температура
        if temp < -20:
            bad_weather_coef += 2
        elif temp < -10:
            bad_weather_coef += 1.5
        elif temp < 0:
            bad_weather_coef += 1
        elif temp < 10:
            bad_weather_coef += 0.5
        elif temp > 30:
            bad_weather_coef += 0.5
        elif temp > 35:
            bad_weather_coef += 1
        elif temp > 40:
            bad_weather_coef += 1.5
        elif temp > 45:
            bad_weather_coef += 2

        # ветер
        if wind_speed >= 18.3:
            bad_weather_coef += 10
        elif wind_speed >= 15.3:
            bad_weather_coef += 2
        elif wind_speed >= 12.5:
            bad_weather_coef += 1.5
        elif wind_speed >= 9.9:
            bad_weather_coef += 1
        elif wind_speed >= 7.5:
            bad_weather_coef += 0.5

        #влажность
        if humidity > 80:
            bad_weather_coef += 0.5

        #осадки
        if precip_prob >= 90:
            bad_weather_coef += 1
        elif precip_prob >= 75:
            bad_weather_coef += 0.5
        elif precip_prob >= 50:
            bad_weather_coef += 0.2

        #уровень осадков
        if total_liq >= 50:
            bad_weather_coef += 1.5
        elif total_liq >= 32:
            bad_weather_coef += 1
        elif total_liq >= 15:
            bad_weather_coef += 0.5

        #облачность
        if cloud_cover >= 90:
            bad_weather_coef += 0.3
        if cloud_cover >= 50:
            bad_weather_coef += 0.2
        if cloud_cover >= 25:
            bad_weather_coef += 0.1

        #итог
        if bad_weather_coef >= 6:
            data['message'] = 'Критические условия, не рекомендуем путешествовать'
        elif bad_weather_coef >= 5:
            data['message'] = 'Крайне неблагоприятные условия, не рекомендуем путешествовать'
        elif bad_weather_coef >= 4:
            data['message'] = 'Неблагоприятные условия для путешествия'
        elif bad_weather_coef >= 3:
            data['message'] = 'Не очень благоприятные условия для путешествия'
        elif bad_weather_coef >= 2:
            data['message'] = 'Удовлетворительные уловия для путешествия'
        else:
            data['message'] = 'Благоприятные условия для путешествия'

    except Exception as e:
        return data

    return data

print(weather_model('Москва'))