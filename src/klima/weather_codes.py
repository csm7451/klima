"""WMO weather interpretation codes and styling for display."""

# WMO Weather interpretation codes (WW) → description and color theme
# Colors chosen for terminal: condition-appropriate and readable
WMO_CODES: dict[int, tuple[str, str]] = {
    0: ("Clear sky", "#EAB308"),           # yellow (sun)
    1: ("Mainly clear", "#A3A3A3"),        # gray
    2: ("Partly cloudy", "#737373"),       # darker gray
    3: ("Overcast", "#525252"),            # dark gray
    45: ("Fog", "#A8A29E"),                # stone
    48: ("Depositing rime fog", "#78716C"),
    51: ("Light drizzle", "#38BDF8"),      # sky blue
    53: ("Moderate drizzle", "#0EA5E9"),
    55: ("Dense drizzle", "#0284C7"),
    56: ("Light freezing drizzle", "#67E8F9"),
    57: ("Dense freezing drizzle", "#22D3EE"),
    61: ("Slight rain", "#38BDF8"),
    63: ("Moderate rain", "#0EA5E9"),
    65: ("Heavy rain", "#0369A1"),
    66: ("Light freezing rain", "#7DD3FC"),
    67: ("Heavy freezing rain", "#0EA5E9"),
    71: ("Slight snow", "#E0F2FE"),
    73: ("Moderate snow", "#BAE6FD"),
    75: ("Heavy snow", "#7DD3FC"),
    77: ("Snow grains", "#BAE6FD"),
    80: ("Slight rain showers", "#38BDF8"),
    81: ("Moderate rain showers", "#0EA5E9"),
    82: ("Violent rain showers", "#0369A1"),
    85: ("Slight snow showers", "#E0F2FE"),
    86: ("Heavy snow showers", "#7DD3FC"),
    95: ("Thunderstorm", "#A78BFA"),       # violet
    96: ("Thunderstorm, slight hail", "#8B5CF6"),
    99: ("Thunderstorm, heavy hail", "#7C3AED"),
}


def get_weather_description(code: int) -> str:
    """Return human-readable description for WMO weather code."""
    return WMO_CODES.get(code, ("Unknown", "#A3A3A3"))[0]


def get_weather_color(code: int) -> str:
    """Return hex color for weather condition (for styling)."""
    return WMO_CODES.get(code, ("Unknown", "#A3A3A3"))[1]
