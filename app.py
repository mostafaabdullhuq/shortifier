from http.client import responses
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import INTEGER
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import generateApikey, login_required, shorten_url





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


# after each request check if user is logged in
@app.context_processor
def get_user_details():
    if session["user_id"] and session["api_key"]:
        try:
            userDetails = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
        except:
            userDetails = False
    else:
        userDetails = False
    return dict(userDetails=userDetails)



# index page ( home page)
@app.route("/")
def index():

    # render the home page
    return render_template('index.html')


# registeration page
@app.route("/register", methods=["GET","POST"])
def register():

    response = {"status":"", "code": 0, "message": "", "data": {}}

    """ if user used GET method """
    
    if request.method == "GET":
        
        # if user already logged in
        if session["user_id"] and session["api_key"]:
            return redirect("/")

        # redirect user to registeration form
        return render_template('register.html')

    # initialize response object

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
                userID = db.execute("INSERT INTO users(first_name, last_name, email, username, password, api_key, is_verified) VALUES(?,?,?,?,?,?,?)", firstName.lower().capitalize(), lastName.lower().capitalize(), emailAddress.lower(), userName.lower(), passWord, apiKey, False)
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

    response = {"status":"", "code": 0, "message": "", "data": {}}

    """ if user used get method """
    if request.method == "GET":

        # if user already logged in
        if session["user_id"] and session["api_key"]:
            return redirect("/")

        return render_template("login.html")
    

    """ if user request is post """

    # get user inputs
    identifier = request.form.get("identifier")
    passWord = request.form.get("passWord")

    # if any input is empty
    if not identifier or not passWord:
        response["status"] = "failed"
        response["code"] = 400
        response["message"] = "Please fill all fields."
    
    else:

        # check for user credentials in database
        isUserFound = db.execute("SELECT * FROM users WHERE (username LIKE ? OR email LIKE ? AND password = ?)", identifier, identifier, passWord)
        if len(isUserFound) > 0:
            userDetails = isUserFound[0]
            userID = userDetails["id"]
            apiKey = userDetails["api_key"]
            response["status"] = "success"
            response["message"] = "Logged in successfully."
            response["code"] = 200
            for eachKey in userDetails:
                response["data"][eachKey] = userDetails[eachKey]
            response["data"]["destination"] = '/'
            session["user_id"] = userID
            session["api_key"] = apiKey

        else:
            response["status"] = "failed"
            response["code"] = 401
            response["message"] = "Wrong Email/Username or Password."

    return jsonify(response)


@app.route("/api/shorten", methods=["POST"])
def shorten():

    response = {"status":"", "code": 0, "message": "", "data": {}}

    print(request.form)

    # get url that will be shortened
    url = request.form.get("url")

    # if no url provided
    if not url:
        response["status"] = "failed"
        response["code"] = 400
        response["message"] = "Please fill the URL field."
    else:

        # shorten the url
        while True:
            shortenURL = shorten_url()
            
            # check if shorten url already exists
            isExist = db.execute("SELECT * FROM urls WHERE short_id LIKE ?", shortenURL)
            if len(isExist) == 0:
                break

        # update the response
        response["status"] = "success"
        response["code"] = 200
        response["message"] = "URL shortened successfully."
        response["data"]["full_url"] = url
        response["data"]["shortened_url_id"] = shortenURL
        
        # if user is logged in
        if session["api_key"] and session["user_id"]:
            apiKey = session["api_key"]
            userID = session["user_id"]

            # ensure that id and api key are correct
            apiFound = db.execute("SELECT * FROM users WHERE api_key = ? AND id = ?", apiKey, userID)
            if len(apiFound) > 0:

                # add url to user dashboard
                addURL = db.execute("INSERT INTO urls (full_url, short_id, user_id) VALUES (?,?,?)", url, shortenURL, userID)
                response["data"]["url_id"] = addURL

    return jsonify(response)


@login_required
@app.route("/logout")
def logout():
    session["user_id"] = None
    session["api_key"] = None
    return redirect("/")


@login_required 
@app.route("/settings", methods=["GET", "POST"])
def settings():
    
    """ user profile and settings"""

    if request.method == "GET":
        return render_template("settings.html")


@login_required
@app.route("/dashboard")
def dashboard():

    userID = session["user_id"]
    apiKey = session["api_key"]

    if not userID or not apiKey:
        return redirect("/login")
    else:
    # get user urls 
        userURLS = db.execute("SELECT * FROM urls WHERE user_id = ?", userID)
        print(userURLS)
        return render_template("dashboard.html", userURLS=userURLS)



@login_required
@app.route("/api/change_key", methods=["GET"])
def change_key():
    response = {"status":"", "code": 0, "message": "", "data": {}}

    # if user not logged in
    if not session["user_id"] or not session["api_key"] or session["api_key"] == None or session["user_id"] == None:
        response["status"] = "failed"
        response["code"] = 401
        response["message"] = "You are not logged in, please login and try again."
    else:

        # check if user session details is correct
        isInfoValid = db.execute("SELECT * FROM users WHERE id = ? AND api_key = ?", session["user_id"], session["api_key"])
        if len(isInfoValid) == 0:
            response["status"] = "failed"
            response["code"] = 401
            response["message"] = "You are not logged in, please login and try again."
        else:

            # if user is logged in generate a new api key
            newApiKey = generateApikey()

            # update the api key value in database
            addApi = db.execute("UPDATE users SET api_key = ? WHERE id = ? AND api_key = ?", newApiKey, session["user_id"], session["api_key"])
            response["status"] = "success"
            response["code"] = 200
            response["message"] = "Api Key Changed Successfully."
            response["data"]["api_key"] = newApiKey

            # change session api key
            session["api_key"] = newApiKey

    return jsonify(response)



@login_required
@app.route("/api/update_profile", methods=["POST"])
def update_profile():
    response = {"status":"", "code": 0, "message": "", "data": {}}

    # get user id from session
    userID = session["user_id"]


    # if user not logged in
    if not userID or userID == None:
        response["status"] = "failed"
        response["code"] = 401
        response["message"] = "You are not logged in, please login and try again."
    
    # if user is logged in
    else:

        # check if user id is correct
        userDetails = db.execute("SELECT * FROM users WHERE id = ?", userID)
        if len(userDetails) == 0:
            response["status"] = "failed"
            response["code"] = 401
            response["message"] = "You are not logged in, please login and try again."
        
        else:
            firstNameChanged = lastNameChanged = userNameChanged = emailChanged = False
            # extract user inputs
            newFirstName = request.form.get("first_name")
            newLastName = request.form.get("last_name")
            newUserName = request.form.get("username")
            newEmail = request.form.get("email_address")

            # if any input is blank
            if not newFirstName or not newLastName or not newEmail or not newUserName:
                response["status"] = "failed"
                response["code"] = 400
                response["message"] = "Please fill all fields."

            else:
                # get old user details
                oldFirstName = userDetails[0]["first_name"]
                oldLastName = userDetails[0]["last_name"]
                oldUserName = userDetails[0]["username"]
                oldEmail = userDetails[0]["email"]

                # if user not changed first name
                if (oldFirstName.lower().strip() != newFirstName.lower().strip()):
                    firstNameChanged = True

                # if user not changed last name
                if (oldLastName.lower().strip() != newLastName.lower().strip()):
                    lastNameChanged = True

                # if user not changed username
                if (oldUserName.lower().strip() != newUserName.lower().strip()):
                    userNameChanged = True
                

                # if user not changed email address
                if (oldEmail.lower().strip() != newEmail.lower().strip()):
                    emailChanged = True

                # if user made any changes
                if userNameChanged or emailChanged or firstNameChanged or lastNameChanged:
                    # if user changed username
                    if userNameChanged:

                        # check for new username dupplication
                        userNameExist = db.execute("SELECT * FROM users where username LIKE ?", newUserName)
                        if len(userNameExist) > 0:
                            response["status"] = "failed"
                            response["code"] = 400
                            response["message"] = "username already exists."
                            newUserName = oldUserName
                            userNameChanged = False
                        
                        # check for email dupplication
                        emailExist = db.execute("SELECT * FROM users WHERE email LIKE ?", newEmail)
                        if len(emailExist) > 0:
                            response["status"] = "failed"
                            response["code"] = 400
                            response["message"] = "email already exists."
                            newEmail = oldEmail
                            emailChanged = False
                        

                    # if user changed any profile detail
                    if userNameChanged or emailChanged or firstNameChanged or lastNameChanged:
                        
                        # update the user details in database
                        changeDetails    = db.execute("UPDATE users SET first_name = ? , last_name = ?, email = ?, username = ? WHERE id = ?", newFirstName, newLastName, newEmail, newUserName, userID)

                        # get new user details from database
                        userDetails = db.execute("SELECT * FROM users WHERE id = ?", userID)[0]
                        response["status"] = "success"
                        response["code"] = 200
                        response["message"] = "Your Details Changed Successfully."
                        for eachKey in userDetails:
                            response["data"][eachKey] = userDetails[eachKey]
                else:
                    response["status"] = "failed"
                    response["code"] = 400
                    response["message"] = "No edits to change."

    return jsonify(response)



@login_required
@app.route("/api/change_password", methods=["POST"])
def change_password():
    response = {"status":"", "code": 0, "message": "", "data": {}}

    # get user id from the session
    userID = session["user_id"]

    # check if user is correct
    userExist = db.execute("SELECT * FROM users WHERE id = ?", userID)

    # if id is correct and user is logged in
    if len(userExist) > 1:

        # get user inputs
        currentPassword = request.form.get("current_password")
        newPassword = request.form.get("new_password")
        newPasswordConfirmation = request.form.get("new_password_confirmation")

        # if any input is empty
        if not currentPassword or not newPassword or not newPasswordConfirmation:
            response["status"] = "failed"
            response["code"] = 400
            response["message"] = "Please fill all fields."
        else:

            # check if current password is correct
            checkPassword = db.execute("SELECT * FROM users WHERE password = ? AND id = ?", currentPassword, userID)
            if len(checkPassword) > 0:
                
                # check if password confirmation is the same as new password
                if newPassword == newPasswordConfirmation:

                    # update password in database
                    changePassword = db.execute("UPDATE users SET password = ? WHERE id = ?", newPassword, userID)
                    response["status"] = "success"
                    response["code"] = 200
                    response["message"] = "Your password has been updated successfully."
                else:
                    response["status"] = "failed"
                    response["code"] = 400
                    response["message"] = "Password doesn't meet the requirements."
            else:
                response["status"] = "failed"
                response["code"] = 401
                response["message"] = "Invalid current password."
    else:
        response["status"] = "failed"
        response["code"] = 401
        response["message"] = "You are not logged in, please login and try again."

    return jsonify(response)






@app.route("/api/check_edit_url", methods=["POST"])
def check_edit_url():

    response = {"status":"", "code": 0, "message": "", "data": {}}

    userID = session["user_id"]
    apiKey = session["api_key"]
    print(userID, apiKey)
    if not userID or not apiKey:
        response["status"] = "failed"
        response["code"] = 401
        response["message"] = "You must be logged in to edit URL."
    else:

        # validate user id and api key
        userExist = db.execute("SELECT * FROM users WHERE id = ? AND api_key = ?", userID, apiKey)
        if len(userExist) > 0:
            urlID = request.form.get("url_id")
            if not urlID:
                response["status"] = "failed"
                response["code"] = 400
                response["message"] = "Please provide URL ID to edit."
            else:

                # check if url id is valid
                checkURL = db.execute("SELECT * FROM urls WHERE id = ? AND user_id = ?", urlID, userID)
                if len(checkURL) > 0:
                    response["status"] = "success"
                    response["code"] = 200
                    response["message"] = "You are allowed to edit this URL."
                else:
                    response["status"] = "failed"
                    response["code"] = 401
                    response["message"] = "You are not allowed to edit this URL."

        else:
            response["status"] = "failed"
            response["code"] = 401
            response["message"] = "You must be logged in to edit URL."


    return jsonify(response)
    


@login_required
@app.route("/api/edit_url", methods=["POST"])
def edit_url():
    response = {"status":"", "code": 0, "message": "", "data": {}}

    userID = session["user_id"]
    apiKey = session["api_key"]

    
    if not userID or not apiKey:
        response["status"] = "failed"
        response["code"] = 401
        response["message"] = "You must be logged in to edit this URL."

    else:

        userExist = db.execute("SELECT * FROM users WHERE id = ? AND api_key = ?", userID, apiKey)

        if len(userExist) > 0 :
            urlID = request.form.get("url_id")
            newURL = request.form.get("new_url")

            if not urlID or not newURL:
                response["status"] = "failed"
                response["code"] = 400
                response["message"] = "Please provide valid URL and URL ID."
            else:

                urlIDExist = db.execute("SELECT * FROM urls WHERE id = ? AND user_id = ?", urlID, userID)
                if len(urlIDExist) > 0:
                    checkNewURL = db.execute("SELECT * FROM urls WHERE short_id LIKE ?", newURL)
                    if len(checkNewURL)  ==  0:
                        changeURL = db.execute("UPDATE urls SET short_id = ? WHERE id = ?", newURL, urlID)
                        response["status"] = "success"
                        response["code"] = 200
                        response["message"] = "URL has been updated successfully."
                        response["data"]["url_id"] = urlID 
                        response["data"]["new_url"] = newURL 
                    else:
                        response["status"] = "failed"
                        response["code"] = 400
                        response["message"] = "URL already exists."
                else:
                    response["status"] = "failed"
                    response["code"] = 400
                    response["message"] = "Either you entered wrong URL ID or you don't have permissions to edit this URL."


        else:
            response["status"] = "failed"
            response["code"] = 401
            response["message"] = "You must be logged in to edit this URL."

    return jsonify(response)


@app.route('/<shortened_url>')
def url_redirect(shortened_url):

    urlExist = db.execute("SELECT * FROM urls WHERE short_id LIKE ?", shortened_url)
    if len(urlExist) == 0:
        return redirect("/")
    else:
        urlID = urlExist[0]['id']
        fullURL = urlExist[0]['full_url']
        if not (fullURL.startswith('http://') or fullURL.startswith('https://')):
            fullURL = 'https://' + fullURL
        visitNumber = int(urlExist[0]['visits'])
        db.execute("UPDATE urls SET visits = ? WHERE id = ?", visitNumber + 1 , urlID)
        return redirect(fullURL)



@login_required
@app.route("/api/delete_url", methods=["POST"])
def delete_url():
    response = {"status":"", "code": 0, "message": "", "data": {}}

    userID = session["user_id"]
    urlID = request.form.get("url_id")

    if not userID:
        response["status"] = "failed"
        response["code"] = 401
        response["message"] = "You must be logged in to delete this url."
    
    if not urlID:
        response["status"] = "failed"
        response["code"] = 400
        response["message"] = "Invalid url ID."


    isURLFound  = db.execute("SELECT * FROM urls WHERE id = ? AND user_id = ?", urlID, userID)

    if len(isURLFound) > 0:
        deleteURL = db.execute("DELETE FROM urls WHERE id = ? AND user_id = ?", urlID, userID)
        response["status"] = "success"
        response["code"] = 200
        response["message"] = "URL has been deleted successfully."


    else:
        response["status"] = "failed"
        response["code"] = 400
        response["message"] = "URL not found."


    return jsonify(response)