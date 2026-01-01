from flask import render_template, session, redirect
from functools import wraps
from datetime import datetime
from zoneinfo import ZoneInfo

# Format currency
def usd(value):
    """
    Format a numeric value as US dollars.
    Positive: $1,234.56
    Negative: ($1,234.56)
    """
    try:
        value = float(value)
        if value < 0:
            return f"(${abs(value):,.2f})"
        else:
            return f"${value:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

# Show errors front end
def apology(message):
    return render_template("apology.html", message=message)

# Decorate routes to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function

# Convert to user's timezone
def format_local_time(utc_string, tz):
    if not utc_string:
        return ""
    
    utc_dt = datetime.fromisoformat(utc_string)
    utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))

    local_dt = utc_dt.astimezone(ZoneInfo(tz))
    return local_dt.strftime("%m/%d %H:%M:%S")

# List of timezones 
timezones = [
    ("UTC", "UTC"),
    
    # North America
    ("America/New_York", "Eastern Time (New York)"),
    ("America/Chicago", "Central Time (Chicago)"),
    ("America/Denver", "Mountain Time (Denver)"),
    ("America/Phoenix", "Mountain Time (Phoenix, no DST)"),
    ("America/Los_Angeles", "Pacific Time (Los Angeles)"),
    ("America/Anchorage", "Alaska"),
    ("America/Halifax", "Atlantic Time (Halifax)"),
    
    # Europe
    ("Europe/London", "London"),
    ("Europe/Paris", "Paris"),
    ("Europe/Berlin", "Berlin"),
    ("Europe/Moscow", "Moscow"),
    
    # Asia
    ("Asia/Tokyo", "Tokyo"),
    ("Asia/Shanghai", "Shanghai"),
    ("Asia/Kolkata", "India Standard Time (Kolkata)"),
    ("Asia/Dubai", "Dubai"),
    
    # Australia & Oceania
    ("Australia/Sydney", "Sydney"),
    ("Australia/Perth", "Perth"),
    ("Pacific/Auckland", "Auckland"),
    
    # Africa
    ("Africa/Johannesburg", "Johannesburg"),
    ("Africa/Cairo", "Cairo")
]
