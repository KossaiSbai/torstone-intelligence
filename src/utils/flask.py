from functools import wraps
from flask import abort, redirect
from flask_htmx import HTMX


__all__ = ["htmx"]

htmx = HTMX()


def htmx_only(redirect_url=None):
    """Decorator to mark a view as only accessible via HTMX requests.
    Non HTMX requests will be redirected to the specified URL or will
    return a 404 error"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not htmx:
                if redirect_url:
                    return redirect(redirect_url)
                return abort(404)
            return func(*args, **kwargs)
        return wrapper
    return decorator
