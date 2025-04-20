from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import tldextract
import pandas as pd
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Load trained model
model = joblib.load("phishing_detector_stacked.pkl")

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    experience = db.Column(db.Text, nullable=False)
    is_phishing = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Feature extraction logic
def extract_features(url):
    features = {
        'url_length': len(url),
        'num_dots': url.count('.'),
        'num_hyphens': url.count('-'),
        'num_slashes': url.count('/'),
        'num_digits': sum(c.isdigit() for c in url)
    }
    domain_info = tldextract.extract(url)
    features['subdomain_length'] = len(domain_info.subdomain)
    features['domain_length'] = len(domain_info.domain)

    phishing_keywords = ['secure', 'login', 'bank', 'confirm', 'account', 'update']
    features['contains_phishing_keyword'] = int(any(keyword in url.lower() for keyword in phishing_keywords))

    return pd.DataFrame([features])

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        url = request.form["url"]
        features_df = extract_features(url)
        result = model.predict(features_df)[0]
        prediction = "🔴 Phishing Website" if result == 1 else "🟢 Legitimate Website"
    return render_template("index.html", prediction=prediction)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful, please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("User does not exist", "danger")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, password):
            flash("Incorrect password", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["username"] = user.username
        flash("Logged in successfully.", "success")
        return redirect(url_for("community"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

@app.route("/community", methods=["GET", "POST"])
def community():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        url = request.form["url"]
        experience = request.form["experience"]
        is_phishing = "phishing" in request.form

        new_post = Post(
            url=url,
            experience=experience,
            is_phishing=is_phishing,
            user_id=session["user_id"]
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("community"))

    posts = Post.query.all()
    return render_template("community.html", posts=posts, user_id=session["user_id"])

@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post and post.user_id == session.get("user_id"):
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for("community"))

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    results = Post.query.filter(Post.url.contains(query)).all()
    return render_template("community.html", posts=results, search_query=query, user_id=session.get("user_id"))

@app.route("/like_post/<int:post_id>", methods=["POST"])
def like_post(post_id):
    post = Post.query.get(post_id)
    if post:
        post.likes += 1
        db.session.commit()
    return redirect(url_for("community"))

# Run
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)