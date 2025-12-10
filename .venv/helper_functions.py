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
