import os
from datetime import datetime, timezone

import requests


class FortyGuardClient:
    """Client for FortyGuard microclimate temperature data."""

    def __init__(self, api_key: str | None = None, timeout: int = 10) -> None:
        self.api_key = api_key or os.getenv("FORTYGUARD_API_KEY")
        self.timeout = timeout
        self.base_url = "https://api.fortyguard.ai/v1/microclimate/temperature"

    def _mock_temperature(self, lat: float, lon: float) -> dict:
        baseline = 28.0
        variation = ((abs(lat) % 5) * 0.9) + ((abs(lon) % 7) * 0.3)
        temperature_c = round(baseline + variation, 1)
        return {
            "temperature_c": temperature_c,
            "source": "mock",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def fetch_temperature(self, lat: float, lon: float) -> dict:
        """Fetch temperature from FortyGuard API, with reliable fallback mock data."""
        if not self.api_key:
            return self._mock_temperature(lat, lon)

        headers = {"X-API-Key": self.api_key}
        params = {"lat": lat, "lon": lon}

        try:
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()

            temperature_c = payload.get("temperature_c")
            if temperature_c is None and "temperature" in payload:
                temperature_c = payload.get("temperature")

            if temperature_c is None:
                return self._mock_temperature(lat, lon)

            return {
                "temperature_c": float(temperature_c),
                "source": "fortyguard",
                "timestamp": payload.get("timestamp")
                or datetime.now(timezone.utc).isoformat(),
            }
        except (requests.RequestException, ValueError, TypeError):
            return self._mock_temperature(lat, lon)
