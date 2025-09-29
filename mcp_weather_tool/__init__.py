"""
MCP Weather Tool Package

This package provides weather tools for MCP Server applications,
including Google Weather API integration for current conditions,
forecasts, and geocoding.
"""

from .enhanced_base import Tool, ToolConfig
from .google_weather import GoogleWeatherTool, WeatherTool

__version__ = "0.1.0"
__all__ = ["Tool", "ToolConfig", "GoogleWeatherTool", "WeatherTool"]