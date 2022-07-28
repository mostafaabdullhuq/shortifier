from functools import wraps
from string import ascii_lowercase,ascii_uppercase, digits
from random import choice
import pyqrcode
from flask import redirect, session

lettersList = []
for i in [ascii_lowercase, digits, ascii_uppercase]:
    for char in i:
        lettersList.append(char)

# generate random api key that consists of 40 random characters
def generateApikey():
    apiKey = ''
    for i in range(40):
        apiKey+=(choice(lettersList))
    return apiKey



# ensure that user is logged in
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


# generate random url id consists of 12 random characters
def shorten_url():
    urlID = ''
    for i in range(12):
        urlID+=(choice(lettersList))
    return urlID


