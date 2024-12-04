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

    start_weather = weather_model(start_city)
    end_weather = weather_model(end_city)
    if type(start_weather) == str:
        return error(error_message=start_weather)
    elif type(end_weather) == str:
        return error(error_message=end_weather)
    elif not(start_weather and end_weather):
        return error(error_message='Ошибка: нет данных по погоде')
    else:
        return render_template('result.html',
                               start_city=start_city,
                               start_condition=start_weather['message'],
                               start_r_temperature=start_weather['temperature']['real'],
                               start_f_temperature=start_weather['temperature']['feel'],
                               start_wind_speed=start_weather['wind']['speed'],
                               start_direction=start_weather['wind']['direction'],
                               start_humidity=start_weather['humidity'],
                               start_precib_prob=start_weather['precip_prob'],
                               start_liquid=start_weather['total_liq'],
                               start_cloud_cover=start_weather['cloud_cover'],

                               end_city=end_city,
                               end_condition=end_weather['message'],
                               end_r_temperature=end_weather['temperature']['real'],
                               end_f_temperature=end_weather['temperature']['feel'],
                               end_wind_speed=end_weather['wind']['speed'],
                               end_direction=end_weather['wind']['direction'],
                               end_humidity=end_weather['humidity'],
                               end_precib_prob=end_weather['precip_prob'],
                               end_liquid=end_weather['total_liq'],
                               end_cloud_cover=end_weather['cloud_cover']
                               )

if __name__ == '__main__':
    run_simple('localhost', 5000, app)