import requests
from flask import Flask, render_template, request
from werkzeug.serving import run_simple
from weather_funcs import load_config, get_location_key, get_weather_data, weather_model

API_KEY = ''
app = Flask(__name__, template_folder='templates')
load_config()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error')
def error(error_message):
    return render_template('error.html', error_message=error_message)

@app.route('/result', methods=['POST'])
def results():
    start_city = request.form.get('start_city')
    end_city = request.form.get('end_city')
    stop_cities = request.form.getlist('stop_city')
    days = int(request.form.get('days', 5))
    cities = [start_city] + stop_cities + [end_city]
    route_forecasts = {}
    route_coordinates = []

    for city in cities:
        route_forecasts[city] = get_weather_data(city, days)
        print(route_forecasts[city])
        if type(route_forecasts[city]) == str:
            return error(error_message=route_forecasts[city])
        elif not route_forecasts[city]:
            return error(error_message='Ошибка: нет данных по погоде')
    forecast_data = [{"city": city, "forecasts": forecast} for city, forecast in route_forecasts.items()]
    print(1)
    return render_template('result.html', forecast_data=forecast_data, days=days)

if __name__ == '__main__':
    run_simple('localhost', 5000, app)