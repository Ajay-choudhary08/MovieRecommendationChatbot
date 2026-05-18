# ============================================
# SECTION 1: IMPORT LIBRARIES
# Use:
# Flask -> backend API banane ke liye
# jsonify -> JSON response bhejne ke liye
# request -> frontend data receive karne ke liye
# flask_cors -> frontend/backend connect karne ke liye
# json -> JSON files read/write karne ke liye
# os -> file paths handle karne ke liye
# ============================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os


# ============================================
# SECTION 2: FLASK APP SETUP
# Use:
# Flask app create karta hai aur CORS enable karta hai
# Streamlit frontend ko Flask backend se connect karne ke liye
# ============================================

app = Flask(__name__)
CORS(app)


# ============================================
# SECTION 3: FILE PATH CONFIGURATION
# Use:
# Backend folder ke andar movies, watchlist aur users JSON files ke path set karta hai
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIES_FILE = os.path.join(BASE_DIR, "movies.json")
WATCHLIST_FILE = os.path.join(BASE_DIR, "watchlist.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")


# ============================================
# SECTION 3A: ADMIN LOGIN CONFIGURATION
# Use:
# Hidden admin panel ke liye fixed admin credentials
# Normal user ko ye frontend par kabhi show nahi hoga
# ============================================

ADMIN_EMAIL = "admin@cinemate.com"
ADMIN_PASSWORD = "admin123"

# ============================================
# SECTION 3B: ADMIN SECRET KEY
# Use:
# Secure admin registration ke liye
# Sirf jisko secret key pata hogi wahi admin bana payega
# ============================================

ADMIN_SECRET_KEY = "123@@@"


# ============================================
# SECTION 4: LOAD MOVIES
# Use:
# movies.json file se movie data load karta hai
# ============================================

def load_movies():

    with open(MOVIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================
# SECTION 5: SAVE MOVIES
# Use:
# Updated movie data ko movies.json file me save karta hai
# Admin side ke add/edit/delete features ke liye useful rahega
# ============================================

def save_movies(movies):

    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=4)


# ============================================
# SECTION 6: LOAD WATCHLIST
# Use:
# watchlist.json file se user ki saved movies load karta hai
# Agar file missing/empty/corrupt ho to empty list return karta hai
# ============================================

def load_watchlist():

    if not os.path.exists(WATCHLIST_FILE):
        return []

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:

            content = f.read().strip()

            if not content:
                return []

            return json.loads(content)

    except json.JSONDecodeError:
        return []


# ============================================
# SECTION 7: SAVE WATCHLIST
# Use:
# User ki saved/watchlist movies ko watchlist.json me save karta hai
# ============================================

def save_watchlist(watchlist):

    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, indent=4)


# ============================================
# SECTION 8: LOAD USERS
# Use:
# users.json file se registered users load karta hai
# Agar file missing/empty/corrupt ho to empty list return karta hai
# ============================================

def load_users():

    if not os.path.exists(USERS_FILE):
        return []

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:

            content = f.read().strip()

            if not content:
                return []

            return json.loads(content)

    except json.JSONDecodeError:
        return []


# ============================================
# SECTION 9: SAVE USERS
# Use:
# New registered users ko users.json file me save karta hai
# ============================================

def save_users(users):

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


# ============================================
# SECTION 10: HOME ROUTE
# Use:
# Backend running hai ya nahi check karne ke liye simple route
# ============================================

@app.route("/")
def home():

    return jsonify({
        "message": "CineMate AI Backend Running"
    })


# ============================================
# SECTION 11: USER REGISTER API
# Use:
# Normal user registration ke liye
# Admin option user side par nahi diya jayega
# ============================================

@app.route("/register", methods=["POST"])
def register_user():

    users = load_users()
    data = request.json

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    for user in users:
        if user["email"].lower() == email:
            return jsonify({
                "message": "User already registered"
            }), 409

    new_user = {
        "name": name,
        "email": email,
        "password": password,
        "role": "user"
    }

    users.append(new_user)
    save_users(users)

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "name": name,
            "email": email,
            "role": "user"
        }
    }), 201


# ============================================
# SECTION 12: USER LOGIN API
# Use:
# Registered user ko login karne ke liye
# Sirf normal user login return karega, admin UI visible nahi hoga
# ============================================

@app.route("/login", methods=["POST"])
def login_user():

    users = load_users()
    data = request.json

    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    for user in users:
        if user["email"].lower() == email and user["password"] == password:
            return jsonify({
                "message": "Login successful",
                "user": {
                    "name": user["name"],
                    "email": user["email"],
                    "role": user.get("role", "user")
                }
            }), 200

    return jsonify({
        "message": "Invalid email or password"
    }), 401


# ============================================
# SECTION 12A: ADMIN LOGIN API
# Use:
# Hidden admin panel ke liye admin login verify karta hai
# Fixed admin credentials aur registered admin users dono ko login allow karta hai
# ============================================

@app.route("/admin/login", methods=["POST"])
def admin_login():

    users = load_users()
    data = request.json

    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:

        return jsonify({
            "message": "Admin login successful",
            "admin": {
                "email": ADMIN_EMAIL,
                "role": "admin"
            }
        }), 200

    for user in users:

        if (
            user["email"].lower() == email
            and user["password"] == password
            and user.get("role") == "admin"
        ):

            return jsonify({
                "message": "Admin login successful",
                "admin": {
                    "name": user.get("name", "Admin"),
                    "email": user["email"],
                    "role": "admin"
                }
            }), 200

    return jsonify({
        "message": "Invalid admin credentials"
    }), 401

    # ============================================
# SECTION 12B: ADMIN REGISTER API
# Use:
# Hidden admin registration ke liye
# Secret key verify karke hi admin create karega
# ============================================

@app.route("/admin/register", methods=["POST"])
def admin_register():

    users = load_users()
    data = request.json

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    secret_key = data.get("secret_key", "").strip()

    if secret_key != ADMIN_SECRET_KEY:

        return jsonify({
            "message": "Invalid admin secret key"
        }), 401

    for user in users:

        if user["email"].lower() == email:

            return jsonify({
                "message": "Admin already exists"
            }), 409

    new_admin = {
        "name": name,
        "email": email,
        "password": password,
        "role": "admin"
    }

    users.append(new_admin)

    save_users(users)

    return jsonify({
        "message": "Admin registered successfully"
    }), 201


# ============================================
# SECTION 13: GET ALL MOVIES
# Use:
# Frontend user side par movies display karne ke liye
# ============================================

@app.route("/movies", methods=["GET"])
def get_movies():

    movies = load_movies()

    return jsonify(movies)


# ============================================
# SECTION 14: GET MOVIES BY GENRE
# Use:
# Genre ke basis par movies filter karne ke liye
# ============================================

@app.route("/movies/<genre>", methods=["GET"])
def get_movies_by_genre(genre):

    movies = load_movies()

    filtered = [
        movie for movie in movies
        if movie["genre"].lower() == genre.lower()
    ]

    return jsonify(filtered)


# ============================================
# SECTION 15: ADD MOVIE
# Use:
# Admin side ke liye movie add feature
# Normal user app.py me iska button/link show nahi kiya jayega
# ============================================

@app.route("/movies", methods=["POST"])
def add_movie():

    movies = load_movies()
    data = request.json

    new_movie = {
        "title": data.get("title"),
        "genre": data.get("genre"),
        "rating": float(data.get("rating")),
        "year": int(data.get("year")),
        "description": data.get("description")
    }

    movies.append(new_movie)
    save_movies(movies)

    return jsonify({
        "message": "Movie added successfully",
        "movie": new_movie
    }), 201


# ============================================
# SECTION 16: DELETE MOVIE
# Use:
# Admin side ke liye movie delete feature
# Normal user app.py me delete option remove/hide kiya gaya hai
# ============================================

@app.route("/movies/<int:index>", methods=["DELETE"])
def delete_movie(index):

    movies = load_movies()

    if index < 0 or index >= len(movies):
        return jsonify({
            "message": "Movie not found"
        }), 404

    deleted_movie = movies.pop(index)
    save_movies(movies)

    return jsonify({
        "message": "Movie deleted successfully",
        "movie": deleted_movie
    }), 200


# ============================================
# SECTION 17: UPDATE MOVIE
# Use:
# Admin side ke liye movie edit/update feature
# Normal user app.py me edit option remove/hide kiya gaya hai
# ============================================

@app.route("/movies/<int:index>", methods=["PUT"])
def update_movie(index):

    movies = load_movies()

    if index < 0 or index >= len(movies):
        return jsonify({
            "message": "Movie not found"
        }), 404

    data = request.json

    movies[index] = {
        "title": data.get("title"),
        "genre": data.get("genre"),
        "rating": float(data.get("rating")),
        "year": int(data.get("year")),
        "description": data.get("description")
    }

    save_movies(movies)

    return jsonify({
        "message": "Movie updated successfully",
        "movie": movies[index]
    }), 200


# ============================================
# SECTION 18: GET WATCHLIST
# Use:
# User ki saved/watchlist movies show karne ke liye
# ============================================

@app.route("/watchlist", methods=["GET"])
def get_watchlist():

    return jsonify(load_watchlist())


# ============================================
# SECTION 19: ADD TO WATCHLIST
# Use:
# User movie ko apni watchlist me add kar sakta hai
# Ye normal user feature hai, Netflix ke "My List" jaisa
# ============================================

@app.route("/watchlist", methods=["POST"])
def add_to_watchlist():

    watchlist = load_watchlist()
    data = request.json

    if not data.get("title"):
        return jsonify({
            "message": "Movie title required"
        }), 400

    for movie in watchlist:
        if movie["title"].lower() == data["title"].lower():
            return jsonify({
                "message": "Movie already in watchlist"
            }), 409

    watchlist.append(data)
    save_watchlist(watchlist)

    return jsonify({
        "message": "Movie added to watchlist",
        "movie": data
    }), 201


# ============================================
# SECTION 20: REMOVE FROM WATCHLIST
# Use:
# User apni watchlist se movie remove kar sakta hai
# Ye movie database delete nahi karta
# ============================================

@app.route("/watchlist/<title>", methods=["DELETE"])
def remove_from_watchlist(title):

    watchlist = load_watchlist()

    updated_watchlist = [
        movie for movie in watchlist
        if movie["title"].lower() != title.lower()
    ]

    save_watchlist(updated_watchlist)

    return jsonify({
        "message": "Movie removed from watchlist"
    }), 200


# ============================================
# SECTION 21: RUN FLASK SERVER
# Use:
# Flask backend ko local aur Render deployment dono par run karne ke liye
# Render par PORT environment variable use hota hai
# Local system par default port 5000 use hota hai
# ============================================

if __name__ == "__main__":

    print("CineMate AI Backend Starting...")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )