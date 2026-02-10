"""UI components for the weather dashboard."""

from klima.widgets.current_weather import CurrentWeather
from klima.widgets.city_info import CityInfo
from klima.widgets.daily_forecast import DailyForecast
from klima.widgets.location_input import LocationInputScreen
from klima.widgets.dashboard import WeatherDashboard

__all__ = [
    "CurrentWeather",
    "CityInfo",
    "DailyForecast",
    "LocationInputScreen",
    "WeatherDashboard",
]
