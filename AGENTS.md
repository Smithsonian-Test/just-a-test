# Weather App — Agent Guidelines

A small command-line Python app that reports the current weather for a city using the free [Open-Meteo](https://open-meteo.com) API.

## Architecture

- [weather.py](weather.py) is the entire app. Flow: `geocode()` resolves a city name to coordinates, `get_current_weather()` fetches the current conditions, and `format_report()` renders the output.
- Two Open-Meteo endpoints are used: the geocoding API (city → lat/lon) and the forecast API (lat/lon → weather). **No API key is required.**
- `WeatherError` signals user-facing problems (e.g. unknown city); network failures surface as `requests.RequestException`. Both are handled in `main()`.

## Build and Test

The macOS system Python is externally managed (PEP 668), so use a virtual environment:

```bash
python3 -m venv .venv                       # one-time setup
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python weather.py "London"        # run (metric by default)
.venv/bin/python weather.py "New York" --units imperial
```

## Code Style

- Runs on Python 3.9+. `from __future__ import annotations` keeps `X | None` type hints valid on 3.9.
- Standard library + `requests` only. Discuss before adding new dependencies.
- Keep functions small and single-purpose; keep network calls out of formatting logic.
- Always pass `timeout=REQUEST_TIMEOUT` to `requests` calls.

## Conventions

- Weather codes map to descriptions via the `WEATHER_CODES` dict (WMO codes). Add new codes there rather than with inline conditionals.
- `main()` returns an exit code and prints errors to `stderr`; it does not raise for expected failures.
