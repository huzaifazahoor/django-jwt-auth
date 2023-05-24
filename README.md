Django JWT Authentication
=========================

This is a Django application for JWT Authentication using Django Rest Framework and the `djangorestframework_simplejwt` package.

Table of Contents
-----------------

*   [Installation](#installation)
*   [Features](#features)
*   [Usage](#usage)
*   [Testing](#testing)
*   [Contributing](#contributing)

Installation
------------

1.  Install Django and Django Rest Framework:
    `pip install django djangorestframework`
    
2.  Install djangorestframework\_simplejwt:
    `pip install djangorestframework_simplejwt`
    
3.  Add the following apps to your `INSTALLED_APPS` in settings.py:
    ```INSTALLED_APPS = [     ...     'rest_framework', 'rest_framework_simplejwt',     'authentication',     ... ]```
    
4.  Migrate your models:
    `python manage.py makemigrations`
    `python manage.py migrate`
    
5.  Ensure to add the JWT authentication classes to your `REST_FRAMEWORK` settings:
	`REST_FRAMEWORK = {     'DEFAULT_AUTHENTICATION_CLASSES': (         'rest_framework_simplejwt.authentication.JWTAuthentication',     ) }`
    

Features
--------

The authentication application includes the following features:

*   User Registration (`/signup/`)
*   User Login (`/login/`)
*   Token Refresh (`/refresh/`)
*   Token Verification (`/verify/`)

Usage
-----

To use the JWT Authentication application:

1.  To create a new user, send a POST request to `/signup/` with the following data:
    `{     "username": "user",     "email": "user@example.com",     "first_name": "First",     "last_name": "Last",     "password": "yourpassword" }`
    
    This will return a JSON response with the user data and the access and refresh tokens.
    
2.  To log in, send a POST request to `/login/` with either the username or email and password:
    `{     "username": "user@example.com",     "password": "yourpassword" }`
    
    This will return a JSON response with the access and refresh tokens.
    
3.  To refresh a token, send a POST request to `/refresh/` with a valid refresh token:
    `{     "refresh": "<REFRESH_TOKEN>" }`
    
    This will return a new access token.
    
4.  To verify a token, send a POST request to `/verify/` with any valid token:
    `{     "token": "<TOKEN>" }`
    
    If the token is valid, this will return a 200 status code.
    

Testing
-------

The Django JWT Authentication application includes a set of tests to verify its functionality. To run the tests, execute the following command:
`python manage.py test authentication`

Contributing
------------

Contributions are welcome! Please submit a pull request or open an issue if you would like to propose changes or additions.