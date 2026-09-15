"""Command-line weather app powered by the free Open-Meteo API (no API key required)."""

from __future__ import annotations

import argparse
import sys

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10

# WMO weather interpretation codes: https://open-meteo.com/en/docs
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherError(Exception):
    """Raised when a location cannot be found or the weather cannot be retrieved."""


def geocode(city: str) -> dict:
    """Resolve a city name to a location record with latitude/longitude."""
    response = requests.get(
        GEOCODE_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        raise WeatherError(f"Could not find a location named {city!r}.")
    return results[0]


def get_current_weather(latitude: float, longitude: float, units: str) -> dict:
    """Fetch the current weather for the given coordinates."""
    temperature_unit = "fahrenheit" if units == "imperial" else "celsius"
    wind_speed_unit = "mph" if units == "imperial" else "kmh"
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["current"]


def format_report(location: dict, current: dict, units: str) -> str:
    """Build a human-readable weather report."""
    name_parts = [location["name"], location.get("admin1"), location.get("country")]
    place = ", ".join(part for part in name_parts if part)

    temp_unit = "F" if units == "imperial" else "C"
    speed_unit = "mph" if units == "imperial" else "km/h"
    description = WEATHER_CODES.get(current["weather_code"], "Unknown conditions")

    return "\n".join(
        [
            f"Weather for {place}",
            f"  Conditions:   {description}",
            f"  Temperature:  {current['temperature_2m']}°{temp_unit}"
            f" (feels like {current['apparent_temperature']}°{temp_unit})",
            f"  Humidity:     {current['relative_humidity_2m']}%",
            f"  Wind:         {current['wind_speed_10m']} {speed_unit}",
        ]
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get the current weather for a city.")
    parser.add_argument("city", help="City name, e.g. 'London' or 'San Francisco'")
    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="Unit system for temperature and wind speed (default: metric)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        location = geocode(args.city)
        current = get_current_weather(location["latitude"], location["longitude"], args.units)
    except WeatherError as exc:
        print(exc, file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Network error while fetching weather: {exc}", file=sys.stderr)
        return 1

    print(format_report(location, current, args.units))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
