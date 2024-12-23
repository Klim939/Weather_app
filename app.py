import requests
from flask import Flask, render_template, request
from werkzeug.serving import run_simple
from weather_funcs import load_config, get_location_key, get_weather_data
import folium
import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

API_KEY = ''
app = Flask(__name__, template_folder='templates')
load_config()
app_dash = dash.Dash(__name__, server=app, url_base_pathname='/dash/')
app_dash.layout = html.Div("Загрузка данных")
route_forecasts = {}


def update_layout():
    app_dash.layout = html.Div([
        html.H1('Визуализация погодных данных по маршруту'),

        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in route_forecasts.keys()],
            value=list(route_forecasts.keys())[0] if route_forecasts else None,
            clearable=False,
            placeholder="Выберите город"
        ),

        dcc.Checklist(
            id='parameter-checklist',
            options=[
                {'label': 'Температура (реальная)', 'value': 'temperature_real'},
                {'label': 'Температура (чувствуется)', 'value': 'temperature_feel'},
                {'label': 'Скорость ветра', 'value': 'wind_speed'},
                {'label': 'Влажность', 'value': 'humidity'},
                {'label': 'Вероятность осадков', 'value': 'precip_prob'},
                {'label': 'Уровень осадков', 'value': 'total_liq'},
                {'label': 'Облачность', 'value': 'cloud_cover'}
            ],
            value=['temperature_real', 'wind_speed'],
            inline=True
        ),

        dcc.Graph(id='weather-graph')
    ])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error')
def error(error_message):
    return render_template('error.html', error_message=error_message)

@app.route('/result', methods=['POST'])
def results():
    global route_forecasts
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
            route_map = folium.Map(location=(55.751244, 37.618423), zoom_start=6)
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
                popup_text = f"<b>{city}</b><br>Температура: {forecast[0]['temperature']['feel']}°C<br>Вероятность осадков: {forecast[0]['precip_prob']}%<br>Влажность: {forecast[0]['humidity']}%<br>Скорость ветра: {forecast[0]['wind']['speed']} м/c"
                if idx == 0:
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
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        color='black',
                        fill=True,
                        fill_color='black',
                        popup=popup_text,
                        tooltip=city+f" Температура: {forecast[0]['temperature']['feel']}°C"
                    ).add_to(route_map)
    map_html = route_map._repr_html_()
    update_layout()
    forecast_data = [{"city": city, "forecasts": forecast} for city, forecast in route_forecasts.items()]
    return render_template('result.html', forecast_data=forecast_data, days=days, folium_map=map_html)


@app_dash.callback(
    Output('weather-graph', 'figure'),
    [Input('city-dropdown', 'value'), Input('parameter-checklist', 'value')]
)
def update_graph(selected_city, selected_parameters):
    print(route_forecasts, selected_city, selected_parameters)
    if selected_city not in route_forecasts:
        return {'data': [], 'layout': go.Layout(title='Нет данных для выбранного города')}

    forecast = route_forecasts[selected_city]
    dates = [day['date'] for day in forecast]
    traces = []

    if 'temperature_real' in selected_parameters:
        max_temps = [day['temperature']['real'] for day in forecast]
        traces.append(go.Scatter(x=dates, y=max_temps, mode='lines+markers', name='Температура (реальная)'))

    if 'temperature_feel' in selected_parameters:
        min_temps = [day['temperature']['feel'] for day in forecast]
        traces.append(go.Scatter(x=dates, y=min_temps, mode='lines+markers', name='Температура (чувствуется)'))

    if 'wind_speed' in selected_parameters:
        wind_speeds = [day['wind']['speed'] for day in forecast]
        traces.append(go.Scatter(x=dates, y=wind_speeds, mode='lines+markers', name='Скорость ветра', line=dict(dash='dash')))

    if 'precip_prob' in selected_parameters:
        precip_probs = [day['precip_prob'] for day in forecast]
        traces.append(go.Bar(x=dates, y=precip_probs, name='Вероятность осадков', yaxis='y2', opacity=0.5))

    if 'total_liq' in selected_parameters:
        uv_indexes = [day['total_liq'] for day in forecast]
        traces.append(go.Scatter(x=dates, y=uv_indexes, name='Уровень осадков', yaxis='y3', mode='lines+markers', line=dict(dash='dash')))

    if 'humidity' in selected_parameters:
        humid_pers = [day['humidity'] for day in forecast]
        traces.append(go.Bar(x=dates, y=humid_pers, name='Влажность', yaxis='y4', opacity=0.5))

    if 'cloud_cover' in selected_parameters:
        humid_pers = [day['cloud_cover'] for day in forecast]
        traces.append(go.Bar(x=dates, y=humid_pers, name='Облачность', yaxis='y5', opacity=0.5))

    layout = go.Layout(
        title=f'Прогноз Погоды для {selected_city}',
        xaxis=dict(title='Дата'),
        yaxis=dict(title='Температура (°C) / Скорость ветра (км/ч)'),
        yaxis2=dict(title='Вероятность осадков (%)', overlaying='y', side='right'),
        yaxis3=dict(title='Уровень осадков (mm)', overlaying='y', side='right'),
        yaxis4=dict(title='Влажность (%)', overlaying='y', side='right'),
        yaxis5=dict(title='Облачность', overlaying='y', side='right'),

        barmode='overlay',
        legend=dict(x=0, y=1.1, orientation='h'),
        hovermode='closest'
    )

    return {'data': traces, 'layout': layout}


if __name__ == '__main__':
    run_simple('localhost', 5000, app_dash.server, use_reloader=False, use_debugger=True)