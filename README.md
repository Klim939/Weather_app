
## About The Project

Этот проект - разработанное на Python с использованием модулей Flask и requests с подключением Accuweather API веб-приложение для узнавания погоды на маршруте путешествия.


### Built With

Проект разработан на языке Python с использованием библиотек:

blinker==1.9.0

certifi==2024.8.30

charset-normalizer==3.4.0

click==8.1.7

colorama==0.4.6

Flask==3.1.0

idna==3.10

itsdangerous==2.2.0

Jinja2==3.1.4

MarkupSafe==3.0.2

requests==2.32.3

urllib3==2.2.3

Werkzeug==3.1.3

И использованием AccuWeather Api
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Этот блок посвящен инструкции, как запустить проект

### Prerequisites

Для начала, установите Python с официального сайта, если он не установлен.
Затем, на официальном сайте AccuWeatherAPI получите ключ для приложения и вставьте его в data/config.txt

### Installation

Установите библиотеки из data/requirements.txt с помощью команды
   ```sh
   pip install requirements.txt
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
Запустите файл app.py, после этого приложением можно пользоваться.

Как работают функции:
1. load_config() - загружает данные из data/config.txt
2. get_location_key(city_name) - получает название города и возвращает ключ города по названию
3. get_weather_data(city_name) - получает название города и возвращает прогноз погоды по названию города
4. weather_model(city_name) - получает имя города и возвращает словарь с прогнозом и сообщением
5. index() - рендерит главную страницу
6. result() - рендерит страницу результата
7. error(error_message) - рендерит страницу результата с error_message
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Борисов Клим - Telegram: @klim_borisovv - klimborisov9552@gmail.com

Project Link: [https://github.com/Klim939/Weather_app](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>