import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import generateApikey


# define flask application
app = Flask(__name__)



# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


# Configure after request cookies configurations
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# index page ( home page)
@app.route("/")
def index():
    return render_template('index.html')


# registeration page
@app.route("/register", methods=["GET","POST"])
def register():
    
    """ if user used GET method """
    
    if request.method == "GET":

        # redirect user to registeration form
        return render_template('register.html')

    # initialize response object
    response = {"status":"", "code": 0, "message": "", "data": {}}

    """ if user used JSON POST method """

    # extract post request data
    firstName = request.form.get("firstName")
    lastName = request.form.get("lastName")
    userName = request.form.get("userName")
    emailAddress = request.form.get("emailAddress")
    passWord = request.form.get("passWord")
    passWordConfirmation = request.form.get("passwordConfirmation")

    # ensure that post data is not blank
    if not firstName and not lastName and not userName and not emailAddress and not passWord and not passWordConfirmation:
        # configure json response
        response["status"] = "failed"
        response["code"] = 400
        response["message"] = "Missing required fields."
    else:

        # check for username and email address in database
        userNameExist = db.execute("SELECT * FROM users WHERE username LIKE ?", userName)
        emailExist = db.execute("SELECT * FROM users WHERE email LIKE ?", emailAddress)

        # if username already exists in database
        if len(userNameExist) > 0 :
            response["status"] = "failed"
            response["code"] = 400
            response["message"] = "Username already in use."
        
        # if email already exists in database
        elif len(emailExist ) > 0:
            response["status"] = "failed"
            response["code"] = 400
            response["message"] = "Email adress already in use."

        else:
            # check if api key already exists in database
            while True:
                # generate api key
                apiKey = generateApikey()
                apiExist = db.execute("SELECT * FROM users WHERE api_key = ?", apiKey)
                if (len(apiExist) == 0):
                    break

            # try to add the user details to dabase
            try:
                userID = db.execute("INSERT INTO users(first_name, last_name, email, username, password, api_key, is_verified) VALUES(?,?,?,?,?,?,?)", firstName, lastName, emailAddress, userName, passWord, apiKey, False)
                response["status"] = "success"
                response["code"] = 200
                response["message"] = "Account was created successfully."
                response["data"] = {"user_id":f"{userID}", "api_key":f"{apiKey}", "firstName":f"{firstName}", "lastName":f"{lastName}", "userName":f"{userName}", "emailAddress":f"{emailAddress}", "passWord":f"{passWord}","is_verified": "False"}

            # if error happends while adding user to database
            except Exception as databaseError:
                response["status"] = "failed"
                response["code"] = 400
                response["message"] = str(databaseError)
    
    # return json response
    return jsonify(response)



# login page
@app.route("/login", methods=["GET","POST"])
def login():
    pass

@app.route("/api/shorten", methods=["POST"])
def shorten():
    apiKey = request.form.get("api_key")
    url = request.form.get("url")
    if not apiKey or not url:
        return redirect("/")

    # check if api key exists in the database

    apiFound = db.execute("SELECT * FROM api WHERE api_key = ?", apiKey)
    if len(apiFound) > 0:
        shortenedURL = ""
        return jsonify({"status": "success", "code": 200, "data": {"message": "URL shortened successfully.", "url": shortenedURL}})
    else:
        return jsonify({"status": "failed", "code": 401, "data": {"message": "Api Key not found."}})
    


