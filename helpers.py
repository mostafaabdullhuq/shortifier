from functools import wraps
from string import ascii_lowercase,ascii_uppercase, digits
from random import choice
from flask import redirect, session

lettersList = []
for i in [ascii_lowercase, digits, ascii_uppercase]:
    for char in i:
        lettersList.append(char)


def generateApikey():
    apiKey = ''
    for i in range(40):
        apiKey+=(choice(lettersList))
    return apiKey




def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
