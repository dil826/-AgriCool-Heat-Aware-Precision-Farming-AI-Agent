import requests


class WeatherClient:
    """Supplementary weather/environmental data fetcher."""

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def fetch_conditions(self, lat: float, lon: float) -> dict:
        """Fetch humidity/wind/precipitation from Open-Meteo with offline-safe fallback."""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "relative_humidity_2m,wind_speed_10m,precipitation",
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json().get("current", {})
            return {
                "humidity": float(payload.get("relative_humidity_2m", 55.0)),
                "wind_speed": float(payload.get("wind_speed_10m", 2.5)),
                "precipitation": float(payload.get("precipitation", 0.0)),
                "source": "open-meteo",
            }
        except (requests.RequestException, ValueError, TypeError):
            return {
                "humidity": 55.0,
                "wind_speed": 2.5,
                "precipitation": 0.0,
                "source": "fallback",
            }
