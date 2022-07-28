from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import generateApikey, login_required, shorten_url
from os import path

RESPONSE = {"status":"", "code": 0, "message": "", "data": {}}



# check if user is already logged in user id and api key is valid
def check_user_authenication():
    try:
        # get user id and api key from current session
        userID = session["user_id"]
        apiKey = session["api_key"]

        # if session doesn't contain user id or api key
        if not userID or not apiKey:
            return False
        # check for user id and api matching with database
        userExist = getUserDetails(userID, apiKey)

        # if user exists in database
        if userExist:
            return True
        
        # if user not found in database
        else:
            return False
    except:
        return False


# get details of user given the user id or user id and api key
def getUserDetails(userID, apiKey=False):

    # if only user id is provided
    if userID and not apiKey:

        # get user details given the user id only
        userDetails = db.execute("SELECT * FROM users WHERE id = ?", userID)
    
    # if both user id and api key is provided
    else:

        # get the user details given user id and api key
        userDetails = db.execute("SELECT * FROM users WHERE id = ? AND api_key = ?", userID, apiKey)

    # if no user exists with this information
    if len(userDetails) == 0:
        userDetails = False

    # if user found
    else:
        userDetails = userDetails[0]

    # return user details
    return userDetails


# define flask application
app = Flask(__name__)


# add favicon to application
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'),'favicon.ico',mimetype='image/vnd.microsoft.icon')



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


# run before the template gets rendered and has the ability to inject new values into the context of template
@app.context_processor
def get_user_details():

    # if user is logged in
    if check_user_authenication():
        try:

            # get user details from database
            userDetails = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
        except:
            userDetails = False
    else:
        userDetails = False
    
    # return dictionary of user details
    return dict(userDetails=userDetails)



# index page ( home page)
@app.route("/")
def index():

    # render the home page
    return render_template('index.html')


# registeration page
@app.route("/register", methods=["GET","POST"])
def register():

    """ if user used GET method """
    
    if request.method == "GET":
        
        # if user already logged in
        if check_user_authenication():

            # redirect user to home page
            return redirect("/")

        # redirect user to registeration page
        return render_template('register.html')


    """ if user used POST method """

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
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 400
        RESPONSE["message"] = "Missing required fields."
    else:

        # check for username and email address in database
        userNameExist = db.execute("SELECT * FROM users WHERE username LIKE ?", userName)
        emailExist = db.execute("SELECT * FROM users WHERE email LIKE ?", emailAddress)

        # if username already exists in database
        if len(userNameExist) > 0 :
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 400
            RESPONSE["message"] = "Username already in use."
        
        # if email already exists in database
        elif len(emailExist ) > 0:
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 400
            RESPONSE["message"] = "Email adress already in use."

        else:
            # generate unique api key for the user
            while True:

                # generate api key
                apiKey = generateApikey()
                
                # check if generated api key already exists in database
                apiExist = db.execute("SELECT * FROM users WHERE api_key = ?", apiKey)
                
                # if generated api key not exist in database
                if (len(apiExist) == 0):
                    break

            # try to add the user details to dabase
            try:
                userID = db.execute("INSERT INTO users(first_name, last_name, email, username, password, api_key) VALUES(?,?,?,?,?,?)", firstName.lower().capitalize(), lastName.lower().capitalize(), emailAddress.lower(), userName.lower(), generate_password_hash(passWord), apiKey)
                RESPONSE["status"] = "success"
                RESPONSE["code"] = 200
                RESPONSE["message"] = "Account was created successfully."
                RESPONSE["data"] = {"user_id":f"{userID}", "api_key":f"{apiKey}", "firstName":f"{firstName}", "lastName":f"{lastName}", "userName":f"{userName}", "emailAddress":f"{emailAddress}", "passWord":f"{passWord}"}

                # log user in by adding session details
                session["user_id"] = userID
                session["api_key"] = apiKey

            # if error happends while adding user to database
            except Exception as databaseError:
                RESPONSE["status"] = "failed"
                RESPONSE["code"] = 400
                RESPONSE["message"] = str(databaseError)
    
    # return json response
    return jsonify(RESPONSE)



# login page
@app.route("/login", methods=["GET","POST"])
def login():

    """ if user used get method """
    if request.method == "GET":

        # if user already logged in
        if check_user_authenication():

            # redirect user to home page
            return redirect("/")

        # render the login page
        return render_template("login.html")
    

    """ if user request is post """

    # get user inputs
    identifier = request.form.get("identifier")
    passWord = request.form.get("passWord")

    # if any input is empty
    if not identifier or not passWord:
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 400
        RESPONSE["message"] = "Please fill all fields."
    else:

        # check if username exists in database
        isUserFound = db.execute("SELECT * FROM users WHERE (username LIKE ? OR email LIKE ?)", identifier, identifier)
        
        # if username exists in database
        if len(isUserFound) > 0:

            # get user details from database
            userDetails = isUserFound[0]

            # get user password from database
            hashPassword = userDetails["password"]

            # check for password validation
            if check_password_hash(hashPassword, passWord):

                # get user id and api key from database
                userID = userDetails["id"]
                apiKey = userDetails["api_key"]
                RESPONSE["status"] = "success"
                RESPONSE["message"] = "Logged in successfully."
                RESPONSE["code"] = 200
                for eachKey in userDetails:
                    RESPONSE["data"][eachKey] = userDetails[eachKey]
                RESPONSE["data"]["destination"] = '/'

                # add user details to session to log user in
                session["user_id"] = userID
                session["api_key"] = apiKey

            # if password user entered doesn't match the password found in database
            else:
                RESPONSE["status"] = "failed"
                RESPONSE["code"] = 401
                RESPONSE["message"] = "Wrong Email/Username or Password."

        # if username not exist in database
        else:
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 401
            RESPONSE["message"] = "Wrong Email/Username or Password."

    # return the json response
    return jsonify(RESPONSE)


# shorten given url
@app.route("/api/shorten", methods=["POST"])
def shorten():


    # get url that will be shortened
    url = request.form.get("url")

    # if no url provided
    if not url:
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 400
        RESPONSE["message"] = "Please fill the URL field."
    else:

        # shorten the url
        while True:
            shortenURL = shorten_url()

            # check if shorten url already exists
            isExist = db.execute("SELECT * FROM urls WHERE short_id LIKE ?", shortenURL)

            # if generated url is unique
            if len(isExist) == 0:
                break

        # update the response
        RESPONSE["status"] = "success"
        RESPONSE["code"] = 200
        RESPONSE["message"] = "URL shortened successfully."
        RESPONSE["data"]["full_url"] = url
        RESPONSE["data"]["shortened_url_id"] = shortenURL
        
        # if user is logged in
        if check_user_authenication():

            # get user id from session
            userID = session["user_id"]

            # add url to user dashboard
            addURL = db.execute("INSERT INTO urls (full_url, short_id, user_id) VALUES (?,?,?)", url, shortenURL, userID)
            RESPONSE["data"]["url_id"] = addURL
        
        # if no logged in user
        else:

            # add url to database to the admin id ( first id)
            addURL = db.execute("INSERT INTO urls (full_url, short_id, user_id) VALUES (?,?,?)", url, shortenURL,1)
            RESPONSE["data"]["url_id"] = addURL


    # return json response
    return jsonify(RESPONSE)


# logout user
@login_required
@app.route("/logout")
def logout():

    # clear session values by setting them to none
    session["user_id"] = None
    session["api_key"] = None

    # redirect user to homepage
    return redirect("/")


# user setting page
@login_required 
@app.route("/settings", methods=["GET", "POST"])
def settings():
    
    """ user profile and settings"""

    # if user used get method
    if request.method == "GET":

        # render the setting page
        return render_template("settings.html")

# user dashboard page
@login_required
@app.route("/dashboard")
def dashboard():

    # if user not logged in
    if not check_user_authenication():
        
        # redirect user to login page
        return redirect("/login")

    # if user is logged in
    else:

        # get user id from session
        userID = session["user_id"]
        
        # get user urls from database 
        userURLS = db.execute("SELECT * FROM urls WHERE user_id = ?", userID)

        # render the dashboard and pass the user urls data to the template
        return render_template("dashboard.html", userURLS=userURLS)


# change the api key
@login_required
@app.route("/api/change_key", methods=["GET"])
def change_key():

    # if user not logged in
    if not check_user_authenication():
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 401
        RESPONSE["message"] = "You are not logged in, please login and try again."

    else:

        # if user is logged in generate a new api key
        newApiKey = generateApikey()

        # update the api key value in database
        db.execute("UPDATE users SET api_key = ? WHERE id = ? AND api_key = ?", newApiKey, session["user_id"], session["api_key"])
        RESPONSE["status"] = "success"
        RESPONSE["code"] = 200
        RESPONSE["message"] = "Api Key Changed Successfully."
        RESPONSE["data"]["api_key"] = newApiKey

        # change session api key
        session["api_key"] = newApiKey

    # return json response
    return jsonify(RESPONSE)


# edit user profile data
@login_required
@app.route("/api/update_profile", methods=["POST"])
def update_profile():

    # if user not logged in
    if not check_user_authenication():
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 401
        RESPONSE["message"] = "You are not logged in, please login and try again."
    
    # if user is logged in
    else:

        # get user id from session
        userID = session["user_id"]

        # initialize new variables to track any changes in profile data
        firstNameChanged = lastNameChanged = userNameChanged = emailChanged = False
        
        # extract user inputs
        newFirstName = request.form.get("first_name")
        newLastName = request.form.get("last_name")
        newUserName = request.form.get("username")
        newEmail = request.form.get("email_address")

        # if any input is blank
        if not newFirstName or not newLastName or not newEmail or not newUserName:
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 400
            RESPONSE["message"] = "Please fill all fields."

        else:

            # get current user details from database
            userDetails = getUserDetails(userID)
            oldFirstName = userDetails["first_name"]
            oldLastName = userDetails["last_name"]
            oldUserName = userDetails["username"]
            oldEmail = userDetails["email"]

            # if user changed first name
            if (oldFirstName.lower().strip() != newFirstName.lower().strip()):
                firstNameChanged = True

            # if user changed last name
            if (oldLastName.lower().strip() != newLastName.lower().strip()):
                lastNameChanged = True

            # if user changed username
            if (oldUserName.lower().strip() != newUserName.lower().strip()):
                userNameChanged = True

            # if user changed email address
            if (oldEmail.lower().strip() != newEmail.lower().strip()):
                emailChanged = True

            # if user made any changes
            if userNameChanged or emailChanged or firstNameChanged or lastNameChanged:
                
                # if user changed username
                if userNameChanged:

                    # check for new username dupplication
                    userNameExist = db.execute("SELECT * FROM users where username LIKE ?", newUserName)

                    # if new username already exists in database
                    if len(userNameExist) > 0:
                        RESPONSE["status"] = "failed"
                        RESPONSE["code"] = 400
                        RESPONSE["message"] = "username already exists."

                        # keep the current username as the old one
                        newUserName = oldUserName
                        userNameChanged = False
                    
                    # check for email dupplication
                    emailExist = db.execute("SELECT * FROM users WHERE email LIKE ?", newEmail)

                    # if email already exists in database
                    if len(emailExist) > 0:
                        RESPONSE["status"] = "failed"
                        RESPONSE["code"] = 400
                        RESPONSE["message"] = "email already exists."

                        # keep the current email address as the old one
                        newEmail = oldEmail
                        emailChanged = False
                    

                # if user changed any profile detail
                if userNameChanged or emailChanged or firstNameChanged or lastNameChanged:
                    
                    # update the user details in database
                    db.execute("UPDATE users SET first_name = ? , last_name = ?, email = ?, username = ? WHERE id = ?", newFirstName, newLastName, newEmail, newUserName, userID)

                    # get new user details from database
                    userDetails = getUserDetails(userID)
                    RESPONSE["status"] = "success"
                    RESPONSE["code"] = 200
                    RESPONSE["message"] = "Your Details Changed Successfully."
                    for eachKey in userDetails:
                        RESPONSE["data"][eachKey] = userDetails[eachKey]
            else:
                RESPONSE["status"] = "failed"
                RESPONSE["code"] = 400
                RESPONSE["message"] = "No edits to change."

    return jsonify(RESPONSE)



@login_required
@app.route("/api/change_password", methods=["POST"])
def change_password():

    # get user id from the session
    userID = session["user_id"]

    # check if user is correct
    userExist = getUserDetails(userID)

    # if id is correct and user is logged in
    if userExist:

        # get user inputs
        currentPassword = request.form.get("current_password")
        newPassword = request.form.get("new_password")
        newPasswordConfirmation = request.form.get("new_password_confirmation")

        # if any input is empty
        if not currentPassword or not newPassword or not newPasswordConfirmation:
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 400
            RESPONSE["message"] = "Please fill all fields."
        else:

            # get current password
            currentHashPassword = userExist['password']

            # check if current password is correct
            if check_password_hash(currentHashPassword, currentPassword):

                # check if password confirmation is the same as new password
                if newPassword == newPasswordConfirmation:

                    # convert password to hash and update password in database
                    changePassword = db.execute("UPDATE users SET password = ? WHERE id = ?",generate_password_hash(newPassword), userID)
                    RESPONSE["status"] = "success"
                    RESPONSE["code"] = 200
                    RESPONSE["message"] = "Your password has been updated successfully."

                # if new password doesn't meet the requirements
                else:
                    RESPONSE["status"] = "failed"
                    RESPONSE["code"] = 400
                    RESPONSE["message"] = "Password doesn't meet the requirements."
            
            # if user provided wrong current password
            else:
                RESPONSE["status"] = "failed"
                RESPONSE["code"] = 401
                RESPONSE["message"] = "Invalid current password."

    # if user not found in database
    else:
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 401
        RESPONSE["message"] = "You are not logged in, please login and try again."

    # return json response
    return jsonify(RESPONSE)





# check url if it is able to be edited
@app.route("/api/check_edit_url", methods=["POST"])
def check_edit_url():

    # if user is not logged in
    if not check_user_authenication():
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 401
        RESPONSE["message"] = "You must be logged in to edit URL."

    # if user is logged in
    else:

        # get user id and api key
        userID = session["user_id"]
        apiKey = session["api_key"]

        # get user details from database
        userExist = getUserDetails(userID, apiKey)

        # if user exists
        if userExist:

            # get url id from post data
            urlID = request.form.get("url_id")

            # if no url id found in post data
            if not urlID:
                RESPONSE["status"] = "failed"
                RESPONSE["code"] = 400
                RESPONSE["message"] = "Please provide URL ID to edit."
            else:

                # check if url id is valid and belongs to the current user
                checkURL = db.execute("SELECT * FROM urls WHERE id = ? AND user_id = ?", urlID, userID)

                # if url found and belongs to user
                if len(checkURL) > 0:
                    RESPONSE["status"] = "success"
                    RESPONSE["code"] = 200
                    RESPONSE["message"] = "You are allowed to edit this URL."

                # if the url not belongs to the current user
                else:
                    RESPONSE["status"] = "failed"
                    RESPONSE["code"] = 401
                    RESPONSE["message"] = "You are not allowed to edit this URL."

        # if no user found with the given id and api key
        else:
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 401
            RESPONSE["message"] = "You must be logged in to edit URL."

    # return json response
    return jsonify(RESPONSE)



# edit url
@login_required
@app.route("/api/edit_url", methods=["POST"])
def edit_url():


    # if user not logged in
    if not check_user_authenication():
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 401
        RESPONSE["message"] = "You must be logged in to edit this URL."

    # if user is logged in
    else:

        # get user id and api key
        userID = session["user_id"]
        apiKey = session["api_key"]

        # check if user exists in database
        userExist = getUserDetails(userID, apiKey)

        # if user exists in database
        if userExist:

            # get the url that needs to be edited from the post data
            urlID = request.form.get("url_id")

            # get new url from post data
            newURL = request.form.get("new_url")

            # if any input not provided in post data
            if not urlID or not newURL:
                RESPONSE["status"] = "failed"
                RESPONSE["code"] = 400
                RESPONSE["message"] = "Please provide valid URL and URL ID."
            
            # if user provided all inputs required
            else:

                # check if url belongs to the current user
                urlIDExist = db.execute("SELECT * FROM urls WHERE id = ? AND user_id = ?", urlID, userID)

                # if user owns the current url
                if len(urlIDExist) > 0:

                    # check if the new url already exists in the database
                    checkNewURL = db.execute("SELECT * FROM urls WHERE short_id LIKE ?", newURL)

                    # if no dupplication found in the database
                    if len(checkNewURL)  ==  0:

                        # update the url id to the new one
                        db.execute("UPDATE urls SET short_id = ? WHERE id = ?", newURL, urlID)
                        RESPONSE["status"] = "success"
                        RESPONSE["code"] = 200
                        RESPONSE["message"] = "URL has been updated successfully."
                        RESPONSE["data"]["url_id"] = urlID 
                        RESPONSE["data"]["new_url"] = newURL 

                    # if new url already exists in the database
                    else:
                        RESPONSE["status"] = "failed"
                        RESPONSE["code"] = 400
                        RESPONSE["message"] = "URL already exists."

                # if user don't have permissions to edit the url
                else:
                    RESPONSE["status"] = "failed"
                    RESPONSE["code"] = 400
                    RESPONSE["message"] = "Either you entered wrong URL ID or you don't have permissions to edit this URL."

        # if user not logged in
        else:
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 401
            RESPONSE["message"] = "You must be logged in to edit this URL."

    # return json response
    return jsonify(RESPONSE)


# redirect the shortened url to the original url
@app.route('/<shortened_url>')
def url_redirect(shortened_url):

    # check if the url provided already exists in the database
    urlExist = db.execute("SELECT * FROM urls WHERE short_id LIKE ?", shortened_url)

    # if url not found in the database
    if len(urlExist) == 0:

        # redirect to the homepage
        return redirect("/")

    # if url found in database
    else:

        # get the id of the url from the database
        urlID = urlExist[0]['id']

        # get the original url from the database
        fullURL = urlExist[0]['full_url']

        # if the full url doesn't start with http:// or https://
        if not (fullURL.startswith('http://') or fullURL.startswith('https://')):

            # add https:// to the url
            fullURL = 'https://' + fullURL
        
        # get the current visit number from the database
        visitNumber = int(urlExist[0]['visits'])

        # increment the number of visits of the current url
        db.execute("UPDATE urls SET visits = ? WHERE id = ?", visitNumber + 1 , urlID)

        # redirect the user to the original url
        return redirect(fullURL)



# delete given url from the database
@login_required
@app.route("/api/delete_url", methods=["POST"])
def delete_url():


    # if user not logged in
    if not check_user_authenication():
        RESPONSE["status"] = "failed"
        RESPONSE["code"] = 401
        RESPONSE["message"] = "You must be logged in to delete this url."

    # if user is logged in
    else:

        # get the user id and url id
        userID = session["user_id"]
        urlID = request.form.get("url_id")

        # if no url id provided
        if not urlID:
            RESPONSE["status"] = "failed"
            RESPONSE["code"] = 400
            RESPONSE["message"] = "Invalid url ID."

        # if url id provided
        else:

            # check if the url id already exists in database
            isURLFound  = db.execute("SELECT * FROM urls WHERE id = ? AND user_id = ?", urlID, userID)

            # if url found in database
            if len(isURLFound) > 0:

                # delete the url from the database
                db.execute("DELETE FROM urls WHERE id = ? AND user_id = ?", urlID, userID)
                RESPONSE["status"] = "success"
                RESPONSE["code"] = 200
                RESPONSE["message"] = "URL has been deleted successfully."

            # if url not found in the database
            else:
                RESPONSE["status"] = "failed"
                RESPONSE["code"] = 400
                RESPONSE["message"] = "URL not found."


    return jsonify(RESPONSE)


