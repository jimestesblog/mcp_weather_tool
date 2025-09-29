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

### MCP Server Integration

The primary use case for this package is as a tool within an MCP Server. Add the GoogleWeatherTool to your MCP server configuration:

#### Configuration Example (`config/tools.yaml`)

```yaml
Domains:
  - Name: WEATHER
    Description: Weather information tools

mcp_classes:
  - Domain: WEATHER
    class_type: mcp_weather_tool.GoogleWeatherTool
    class_name: google_weather
    class_description: Google Weather API integration
    class_initialization_params:
      params:
        api_key: "${GOOGLE_WEATHER_API_KEY}"
        geocoding_api_key: "${GOOGLE_MAPS_API_KEY}"
        unitsSystem: "imperial"
        language: "en"
        base_url: "https://weather.googleapis.com/v1"
    tools:
      - function: current_conditions
        function_description: Get current weather conditions
        tool_parameters:
          - name: latitude
            description: Latitude coordinate
            allowed_values: string
          - name: longitude
            description: Longitude coordinate
            allowed_values: string
          - name: unitsSystem
            description: Unit system (imperial/metric)
            allowed_values: ["imperial", "metric"]
          - name: language
            description: Language code
            allowed_values: string
      - function: hourly_forecast
        function_description: Get hourly weather forecast
        tool_parameters:
          - name: latitude
            description: Latitude coordinate
            allowed_values: string
          - name: longitude
            description: Longitude coordinate
            allowed_values: string
          - name: hours
            description: Number of hours (max 48)
            allowed_values: number
      - function: daily_forecast
        function_description: Get daily weather forecast
        tool_parameters:
          - name: latitude
            description: Latitude coordinate
            allowed_values: string
          - name: longitude
            description: Longitude coordinate
            allowed_values: string
          - name: days
            description: Number of days (max 10)
            allowed_values: number
```

#### Environment Variables

Set up required environment variables:

```bash
# Windows
set GOOGLE_WEATHER_API_KEY=your-google-weather-api-key
set GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Linux/macOS
export GOOGLE_WEATHER_API_KEY=your-google-weather-api-key
export GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

#### Running with MCP Server

```bash
# Install MCP server (if not already installed)
pip install mcp-server

# Run MCP server with your configuration
python -m mcp_server --config config/tools.yaml
```

### Direct Python Usage

For standalone usage or testing, you can also use the tool directly:

```python
from mcp_weather_tool import GoogleWeatherTool
from mcp_weather_tool.enhanced_base import ToolConfig

# Initialize with API configuration
config = ToolConfig(
    name="google_weather",
    params={
        "api_key": "your-google-weather-api-key",
        "unitsSystem": "imperial",
        "language": "en",
        "geocoding_enabled": True,
        "geocoding_api_key": "your-google-maps-api-key",
        "base_url": "https://weather.googleapis.com/v1"
    }
)

weather_tool = GoogleWeatherTool(config)

# Example usage
import asyncio

async def example():
    result = await weather_tool.invoke("current_conditions", latitude=37.7749, longitude=-122.4194)
    print(result)

# Run the example
asyncio.run(example())
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