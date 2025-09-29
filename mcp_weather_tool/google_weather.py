from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import re
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from .enhanced_base import Tool, ToolConfig


class WeatherTool(Tool):
    """Base class for weather-related tools."""
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        params = config.params
        self.api_key = params.get("api_key")
        self.base_url = params.get("base_url", "")
        self.units_default = params.get("unitsSystem", "imperial")
        self.language_default = params.get("language", "en")
    
    def get_schema(self) -> Dict[str, Any]:
        """Default schema for weather tools."""
        return {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude in decimal degrees"
                },
                "longitude": {
                    "type": "number", 
                    "description": "Longitude in decimal degrees"
                },
                "unitsSystem": {
                    "type": "string",
                    "enum": ["imperial", "metric"],
                    "description": "Unit system to use"
                },
                "language": {
                    "type": "string",
                    "description": "Language code for localized output"
                }
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": True
        }


class GoogleWeatherTool(WeatherTool):
    """
    Google Weather API tool.

    This tool provides access to current conditions, hourly forecast, and daily (up to 10-day)
    forecast for a specific location using the Google Weather API.

    Actions (use via invoke(action=..., ...)):
    - current_conditions
      Required: one of
        • latitude and longitude (float)
        • location (string). Accepts "lat,lon" (e.g., "47.6062,-122.3321"). If geocoding is enabled in params,
          also accepts place names like "Seattle, WA".
      Optional: units ("metric" or "imperial"), language (IETF code, default from params)

    - hourly_forecast
      Required: same location parameters as above
      Optional: hours (int, default 24), units, language

    - daily_forecast
      Required: same location parameters as above
      Optional: days (int, default 10), units, language

    Configuration (config.tools.yaml under params):
      api_key: Google Weather API key (or set env GOOGLE_WEATHER_API_KEY and reference as "${GOOGLE_WEATHER_API_KEY}")
      base_url: Base URL for Weather API (default: https://weather.googleapis.com/v1)
      units: Default units: "imperial" or "metric" (default: "imperial")
      language: Default language code like "en" (default: "en")
      geocoding_enabled: If true, resolves non-lat/lon locations via Google Maps Geocoding (default: true)
      geocoding_api_key: Optional; if not set, api_key or env GOOGLE_MAPS_API_KEY will be used
      geocoding_base_url: Default https://maps.googleapis.com/maps/api/geocode/json

    Notes for LLMs/Agents:
    - Always include action. Provide either (latitude and longitude) or a string location.
    - For natural language like "Paris, France", rely on geocoding by keeping geocoding_enabled true and ensuring a valid
      API key. For precise results, prefer numeric latitude/longitude.
    - Example calls:
      • action="current_conditions", location="Austin, TX"
      • action="hourly_forecast", latitude=37.7749, longitude=-122.4194, hours=12
      • action="daily_forecast", location="48.8566,2.3522", days=7, units="metric"
    """

    def __init__(self, conf: Dict[str, Any]) -> None:
        import os
        
        # Convert legacy config format to ToolConfig
        if isinstance(conf, dict) and "params" in conf:
            # Legacy format
            config = ToolConfig(
                name=conf.get("name", "google_weather"),
                description=conf.get("description") or (
                    "Google Weather tool: current conditions, hourly, and daily forecasts. "
                    "Actions: current_conditions, hourly_forecast, daily_forecast. "
                    "Params: provide 'action' and either (latitude & longitude) or 'location' string. "
                    "Optional: units ('imperial'|'metric'), language, hours (hourly), days (daily)."
                ),
                params=conf.get("params", {})
            )
        else:
            # Assume it's already a ToolConfig or dict that can be converted
            config = ToolConfig(**conf) if isinstance(conf, dict) else conf
        
        super().__init__(config)

        params = conf.get("params", {})

        def _expand_env(val: Any) -> Any:
            if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
                return os.getenv(val[2:-1])
            return val

        self.base_url = str(_expand_env(params.get("base_url", "https://weather.googleapis.com/v1"))).rstrip("/")
        # API keys: Weather and optional Geocoding
        api_key = _expand_env(params.get("api_key")) or os.getenv("GOOGLE_WEATHER_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.api_key: Optional[str] = api_key if api_key else None

        self.units_default = str(params.get("units", "imperial")).lower()
        self.language_default = str(params.get("language", "en"))

        self.geocoding_enabled = bool(params.get("geocoding_enabled", True))
        geo_key = _expand_env(params.get("geocoding_api_key")) or os.getenv("GOOGLE_MAPS_API_KEY") or self.api_key
        self.geocoding_api_key: Optional[str] = geo_key if geo_key else None
        self.geocoding_base_url = str(
            _expand_env(params.get("geocoding_base_url", "https://maps.googleapis.com/maps/api/geocode/json"))
        ).rstrip("/")

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute weather tool action."""
        action = kwargs.get("action")
        if not action:
            return {"error": "Missing required 'action' parameter"}
        
        # Resolve location to lat/lon
        location_result = await self._resolve_location(kwargs)
        if isinstance(location_result, dict) and "error" in location_result:
            return location_result
        
        lat, lon = location_result
        units = kwargs.get("unitsSystem", self.units_default)
        language = kwargs.get("language", self.language_default)
        
        try:
            if action == "current_conditions":
                return await self._current_conditions(lat, lon, units, language)
            elif action == "hourly_forecast":
                hours = int(kwargs.get("hours", 24))
                return await self._hourly_forecast(lat, lon, units, language, hours)
            elif action == "daily_forecast":
                days = int(kwargs.get("days", 10))
                return await self._daily_forecast(lat, lon, units, language, days)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}

    async def _current_conditions(self, latitude: float, longitude: float, unitsSystem: str, language: str) -> Dict[str, Any]:
        params = {
            "key": self.api_key,
            "location.latitude": latitude,
            "location.longitude": longitude,
            "unitsSystem": unitsSystem,
            "languageCode": language,
        }
        return await self._get("/currentConditions:lookup", params)

    async def _hourly_forecast(self, latitude: float, longitude: float, unitsSystem: str, language: str, hours: int) -> Dict[str, Any]:
        params = {
            "key": self.api_key,
            "location.latitude": latitude,
            "location.longitude": longitude,
            "unitsSystem": unitsSystem,
            "languageCode": language,
            "hours": hours,
        }
        return await self._get("/forecast/hours:lookup", params)

    async def _daily_forecast(self, lat: float, lon: float, unitsSystem: str, language: str, days: int) -> Dict[str, Any]:
        params = {
            "key": self.api_key,
            "location.latitude": lat,
            "location.longitude": lon,
            "unitsSystem": unitsSystem,
            "languageCode": language,
            "days": days,
        }
        return await self._get("/dailyForecast:lookup", params)

    async def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        import httpx
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            content_type = resp.headers.get("content-type", "")
            try:
                body = resp.json()
            except Exception:
                body = await resp.aread()
            return {
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "body": body,
            }

    async def _resolve_location(self, kwargs: Dict[str, Any]) -> Tuple[float, float] | Dict[str, str]:
        # Direct numeric coordinates
        if kwargs.get("latitude") is not None and kwargs.get("longitude") is not None:
            try:
                return float(kwargs["latitude"]), float(kwargs["longitude"])
            except Exception:
                return {"error": "Invalid latitude/longitude values; must be numeric."}

        # Try common synonyms
        if kwargs.get("lat") is not None and kwargs.get("lon") is not None:
            try:
                return float(kwargs["lat"]), float(kwargs["lon"])
            except Exception:
                return {"error": "Invalid lat/lon values; must be numeric."}

        # Parse from a location string
        loc_str = kwargs.get("location")
        if isinstance(loc_str, str):
            parsed = self._parse_lat_lon(loc_str)
            if parsed:
                return parsed
            # Geocode if enabled
            if self.geocoding_enabled:
                geo = await self._geocode(loc_str)
                if isinstance(geo, tuple):
                    return geo
                return {"error": f"Could not geocode location '{loc_str}'. {geo.get('error', '')}"}
            return {"error": "Provide latitude and longitude or enable geocoding with a resolvable location string."}

        return {"error": "Missing location. Provide latitude and longitude or a 'location' string."}

    def _parse_lat_lon(self, value: str) -> Optional[Tuple[float, float]]:
        # Accept formats like "47.6062,-122.3321" with optional whitespace
        m = re.match(r"^\s*([+-]?[0-9]*\.?[0-9]+)\s*,\s*([+-]?[0-9]*\.?[0-9]+)\s*$", value)
        if not m:
            return None
        try:
            return float(m.group(1)), float(m.group(2))
        except Exception:
            return None

    async def _geocode(self, address: str) -> Tuple[float, float] | Dict[str, str]:
        import httpx
        if not self.geocoding_api_key:
            return {"error": "Geocoding is enabled but no geocoding_api_key is configured."}
        params = {"address": address, "key": self.geocoding_api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(self.geocoding_base_url, params=params)
            try:
                data = resp.json()
            except Exception:
                return {"error": "Geocoding response was not JSON."}
            status = data.get("status")
            if status != "OK" or not data.get("results"):
                return {"error": f"Geocoding failed with status {status}"}
            loc = data["results"][0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])  # type: ignore[return-value]
