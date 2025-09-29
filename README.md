# MCP Weather Tool

Weather tools for MCP Server applications, providing Google Weather API integration.

## Features

- **Current Conditions**: Get current weather conditions for any location
- **Hourly Forecast**: Retrieve detailed hourly weather forecasts
- **Daily Forecast**: Get multi-day weather forecasts
- **Geocoding**: Convert addresses to coordinates using Google Maps API

## Installation

### For End Users

Install the package directly from PyPI (when published):

```bash
pip install mcp-weather-tool
```

### For Development or Local Installation

#### Option 1: Install from Source (Recommended)

1. Clone or download the project:
   ```bash
   git clone https://github.com/example/mcp-weather-tool.git
   cd mcp-weather-tool
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

#### Option 2: Build and Install Package

1. Navigate to the project directory:
   ```bash
   cd path/to/mcp_weather_tool
   ```

2. Build the package:
   ```bash
   python -m build
   ```
   *Note: You may need to install build tools first: `pip install build`*

3. Install the built package:
   ```bash
   pip install dist/mcp_weather_tool-0.1.0-py3-none-any.whl
   ```

#### Option 3: Direct Installation from Local Directory

If you have the source code locally:

```bash
cd path/to/mcp_weather_tool
pip install .
```

### Verification

To verify the installation was successful:

```bash
python -c "from mcp_weather_tool import GoogleWeatherTool; print('Installation successful!')"
```

## Usage

The package provides the `GoogleWeatherTool` class that can be imported and used in MCP Server applications:

```python
from mcp_weather_tool import GoogleWeatherTool

# Initialize with API configuration
config = {
    "name": "google_weather",
    "params": {
        "api_key": "your-google-weather-api-key",
        "unitsSystem": "imperial",
        "language": "en",
        "geocoding_enabled": True,
        "geocoding_api_key": "your-google-maps-api-key",
        "base_url": "https://weather.googleapis.com/v1"
    }
}

weather_tool = GoogleWeatherTool(config)
```

## Requirements

- Python 3.8+
- pydantic>=2.0.0
- httpx>=0.24.0

## API Keys

You'll need:
- Google Weather API key
- Google Maps Geocoding API key (optional, for address-to-coordinate conversion)

## License

MIT License