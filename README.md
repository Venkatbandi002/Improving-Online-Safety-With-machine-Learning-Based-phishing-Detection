# Improving-Online-Safety-With-machine-Learning-Based-phishing-Detection

This is a web application that detects phishing websites using a machine learning model. 
Users can register, log in, check URLs, and share experiences.

----------------------------------------------
REQUIREMENTS
----------------------------------------------
Make sure you have Python installed (preferably Python 3.7 or above).

Install dependencies:
> pip install -r requirements.txt

(If no requirements.txt file, manually install using:)
> pip install flask

> pip install flask_sqlalchemy

> pip install werkzeug

> pip install joblib

> pip install pandas

> pip install tldextract

> pip install requests

----------------------------------------------
FILES STRUCTURE
----------------------------------------------
- app.py                : Main application file
- phishing_detector.pkl : Trained ML model (required for predictions)
- templates/
    - index.html        : Home page
    - login.html        : Login page
    - register.html     : Registration page
    - chat.html         : Forum/chat page
- static/               : (optional for CSS, JS if used)
- posts.db              : SQLite database (will be created automatically)

----------------------------------------------
HOW TO RUN
----------------------------------------------
1. Make sure all dependencies are installed.
2. Place your trained ML model file named `phishing_detector.pkl` in the project folder.
3. Run the app:
> python app.py

4. Open your browser and go to:
http://127.0.0.1:5000

----------------------------------------------
FEATURES
----------------------------------------------
- Check if a website exists and detect phishing.
- User registration and login.
- Forum-style chat to share experiences.
- Like system (1 like per user).
- Post deletion (only by the author).
- Password hashing and validation.
- Email validation during registration.
- Secure login/logout system.

----------------------------------------------
NOTES
----------------------------------------------
- Make sure the database schema matches your models. If you've added new columns (like email), delete the old posts.db and let Flask create a new one:
> Delete posts.db

> Then run app.py to auto-create the DB again.

----------------------------------------------
