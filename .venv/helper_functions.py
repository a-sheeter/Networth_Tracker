from flask import render_template, session, redirect
from functools import wraps

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

def apology(message):
    return render_template("apology.html", message=message)

def login_required(f):
    # Decorate routes to require login
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function