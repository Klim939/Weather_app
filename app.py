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

if __name__ == '__main__':
    run_simple('localhost', 5000, app)