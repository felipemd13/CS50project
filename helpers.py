from flask import redirect, session
from functools import wraps

def cop(value):
    """Format value as COP."""
    if value >= 0:
        return f"${value:,.0f}"
    else:
        return f"-${-value:,.0f}"

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
