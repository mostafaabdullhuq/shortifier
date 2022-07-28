<<<<<<< HEAD
# **Shortifier**

## Video Demo:  

    https://youtu.be/39VxUcMhrZA


## Description:

    Shortifier is a free tool to convert long complex URLs to small
    rememberable ones (URL Shortener).


## Features:

    - Generates Random URL ID for easy remembering.
    - User registeration and login support.
    - User dashboard to to view, track, delete and edit all of your saved URLs.
    - Easy to implement API support.
    - Javascript & Flask inputs validation.
    - securly stores user password by converting them to a hash string.


## Used Technologies:

    - HTML
    - CSS
    - Javascript
    - Python Flask
    - jQuery
    - Bootstrap
    - SweetAlert2
    - SQLite3
    - Ajax


## Project Structure:

![Project Structure](https://i.imgur.com/8nTZ8ZC.png)

- **/flask_session :** stores the users sessions.
- **/static/img :** contains all images that used in the templates.
- **/static/jquery3.6.0.min.js :** contains jQuery script that allows the application to use jQuery.
- **/static/script.js :** contains pure javascript code that controls the web application dynamic behaviors, ajax requests and inputs validations.
- **/static/style.css :** contains all of the CSS styling of the application's templates.
- **/templates/dashboard.html :** contains the template HTML of the user dashboard interface.
- **/templates/index.html :** contains the template HTML of the application's homepage.
- **/templates/layout.html :** contains the base layout of the application's HTML that is used across all pages of the application.
- **/templates/login.html :** contains the template HTML of the login page.
- **/templates/register.html :** contains the template HTML of the registeration page.
- **/templates/settings.html :** contains the template HTML of the user update profile page.
- **app.py :** contains the main flask application configurations, declarations of application routes, database queries and inputs validation.
- **helpers.py :** contains helper functions that generates random api key, validate user login and generate random url id.
- **project.db :** contains the project database
- **requirements.txt :** contains the required packages to run the project.


## Database Structure:

- **users table:**

    stores all user information

> CREATE TABLE IF NOT EXISTS "users" (
  "id" integer PRIMARY KEY,
  "first_name" text NOT NULL,
  "last_name" text NOT NULL,
  "email" text UNIQUE NOT NULL,
  "username" text UNIQUE NOT NULL,
  "password" text NOT NULL,
  "api_key" text UNIQUE NOT NULL
); 

- **urls table:**

    stores all urls information

> CREATE TABLE IF NOT EXISTS "urls" (
  "id" integer PRIMARY KEY,
  "full_url" text NOT NULL,
  "short_id" text UNIQUE NOT NULL,
  "user_id" integer DEFAULT(0),
  "visits" integer DEFAULT(0),
  FOREIGN KEY (user_id) REFERENCES "users" (id)
);
=======
# shortifier
A simple URL shortener app using python flask, sqlite3, html, javascript, css, bootstrap, sweetalert and jQuery
>>>>>>> e4e459bc09ccba71295f564b8713439542094d35
