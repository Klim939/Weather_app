import requests
from flask import Flask, render_template, request
from werkzeug.serving import run_simple
from weather_funcs import load_config, get_location_key, get_weather_data
import folium

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
        forecast, latitude, longitude = get_weather_data(city, days)
        route_forecasts[city] = forecast
        if type(route_forecasts[city]) == str:
            return error(error_message=route_forecasts[city])
        elif not route_forecasts[city]:
            return error(error_message='Ошибка: нет данных по погоде')
        route_coordinates.append((latitude, longitude))
        if route_coordinates:
            route_map = folium.Map(location=route_coordinates[0], zoom_start=6)
            route_map.fit_bounds(route_coordinates)
        else:
            # Если нет координат, используем координаты Москвы
            route_map = folium.Map(location=(55.751244, 37.618423), zoom_start=6)

            # Добавление линии маршрута на карту с более заметным стилем
        if route_coordinates:
            folium.PolyLine(
                locations=route_coordinates,
                color='black',
                weight=3,
                opacity=0.8
            ).add_to(route_map)

            # Добавление маркеров на карту для каждого города с кратким прогнозом
        for idx, (city, forecast) in enumerate(route_forecasts.items()):
            lat, lon = forecast[0].get('latitude'), forecast[0].get('longitude')

            if lat is not None and lon is not None:
                popup_text = f"<b>{city}</b><br>Температура: {forecast[0]['temperature']['feel']}°C<br>Осадки: {forecast[0]['precip_prob']}%<br>Влажность: {forecast[0]['humidity']}%<br>Скорость ветра: {forecast[0]['wind']['speed']} м/c"
                # Используем CircleMarker для выделения городов
                if idx == 0:
                    # Начальный город
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=10,
                        color='red',
                        fill=True,
                        fill_color='red',
                        popup=popup_text,
                        tooltip=city+f" Температура: {forecast[0]['temperature']['feel']}°C"
                    ).add_to(route_map)
                elif idx == len(route_forecasts) - 1:
                    # Конечный город
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=8,
                        color='red',
                        fill=True,
                        fill_color='red',
                        popup=popup_text,
                        tooltip=city+f" Температура: {forecast[0]['temperature']['feel']}°C"
                    ).add_to(route_map)
                else:
                    # Промежуточные города
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        color='black',
                        fill=True,
                        fill_color='black',
                        popup=popup_text,
                        tooltip=city+f" Температура: {forecast[0]['temperature']['feel']}°C"
                    ).add_to(route_map)

        # Получаем HTML-представление карты
    map_html = route_map._repr_html_()
    forecast_data = [{"city": city, "forecasts": forecast} for city, forecast in route_forecasts.items()]
    return render_template('result.html', forecast_data=forecast_data, days=days, folium_map=map_html)

if __name__ == '__main__':
    run_simple('localhost', 5000, app)