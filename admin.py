# ============================================
# SECTION 1: IMPORT LIBRARIES
# Use:
# streamlit -> admin dashboard UI banane ke liye
# requests -> Flask backend APIs call karne ke liye
# pandas -> movie data ko table format me handle karne ke liye
# os -> admin.css file load karne ke liye
# ============================================

import streamlit as st
import requests
import pandas as pd
import os


# ============================================
# SECTION 2: PAGE CONFIGURATION
# Use:
# Admin panel ka title, icon aur layout set karne ke liye
# ============================================

st.set_page_config(
    page_title="CineMate Admin",
    page_icon="🛠️",
    layout="wide"
)


# ============================================
# SECTION 3: BACKEND API URLS
# Use:
# Admin login aur movie management ke liye backend APIs connect karne ke liye
# ============================================

ADMIN_LOGIN_URL = "http://127.0.0.1:5000/admin/login"
MOVIES_URL = "http://127.0.0.1:5000/movies"

# ============================================
# SECTION 3A: ADMIN REGISTER API URL
# Use:
# Hidden admin registration ko Flask backend se connect karne ke liye
# ============================================

ADMIN_REGISTER_URL = "http://127.0.0.1:5000/admin/register"


# ============================================
# SECTION 4: LOAD ADMIN CSS
# Use:
# admin.css file ko load karke admin panel par styling apply karne ke liye
# ============================================

if os.path.exists("admin.css"):
    with open("admin.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================
# SECTION 5: ADMIN SESSION STATE
# Use:
# Admin login state ko track karne ke liye
# ============================================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "admin_data" not in st.session_state:
    st.session_state.admin_data = None


# ============================================
# SECTION 6: ADMIN LOGIN / REGISTER SCREEN
# Use:
# Admin login aur hidden admin register screen show karta hai
# Admin panel normal user app se completely separate rahega
# ============================================

if not st.session_state.admin_logged_in:

    admin_auth_tab = st.radio(
        "Admin Access",
        ["Login", "Register"],
        horizontal=True
    )

    # ============================================
    # SECTION 6A: ADMIN LOGIN FORM
    # Use:
    # Existing admin ko dashboard me login karne ke liye
    # ============================================

    if admin_auth_tab == "Login":

        st.markdown('<div class="admin-login-card">', unsafe_allow_html=True)

        st.title("🛠️ CineMate Admin")
        st.subheader("Secure Admin Login")

        email = st.text_input("Admin Email")
        password = st.text_input("Admin Password", type="password")

        if st.button("Login as Admin"):

            try:
                response = requests.post(
                    ADMIN_LOGIN_URL,
                    json={
                        "email": email,
                        "password": password
                    }
                )

                data = response.json()

                if response.status_code == 200:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_data = data["admin"]
                    st.success("Admin login successful ✅")
                    st.rerun()
                else:
                    st.error(data.get("message", "Invalid admin credentials"))

            except Exception as e:
                st.error("Backend not connected. Make sure Flask backend is running.")
                st.code(str(e))

        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================
    # SECTION 6B: HIDDEN ADMIN REGISTER FORM
    # Use:
    # Secret key ke through new admin account create karne ke liye
    # Iska access sirf admin.py me hoga, normal user app me nahi
    # ============================================

    else:

        st.markdown('<div class="admin-register-card">', unsafe_allow_html=True)

        st.title("🔐 Register Admin")
        st.subheader("Create new admin account using secret key")

        name = st.text_input("Admin Name")
        email = st.text_input("Admin Email")
        password = st.text_input("Admin Password", type="password")
        secret_key = st.text_input("Admin Secret Key", type="password")

        if st.button("Register Admin"):

            try:
                response = requests.post(
                    ADMIN_REGISTER_URL,
                    json={
                        "name": name,
                        "email": email,
                        "password": password,
                        "secret_key": secret_key
                    }
                )

                data = response.json()

                if response.status_code == 201:
                    st.success("Admin registered successfully ✅ Now login.")
                else:
                    st.error(data.get("message", "Admin registration failed"))

            except Exception as e:
                st.error("Admin Register API Error")
                st.code(str(e))

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# ============================================
# SECTION 7: LOAD MOVIES FUNCTION
# Use:
# Backend se latest movie list fetch karne ke liye
# ============================================

def load_movies():

    try:
        response = requests.get(MOVIES_URL)

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


# ============================================
# SECTION 8: ADMIN DASHBOARD HEADER
# Use:
# Admin dashboard ka title, logout aur welcome section show karne ke liye
# ============================================

st.sidebar.title("🛠️ Admin Panel")
st.sidebar.success("Logged in as Admin")

if st.sidebar.button("🚪 Admin Logout"):
    st.session_state.admin_logged_in = False
    st.session_state.admin_data = None
    st.rerun()

st.title("🎬 CineMate Admin Dashboard")
st.write("Manage movies, update content, and keep the platform fresh.")


# ============================================
# SECTION 9: FETCH MOVIES DATA
# Use:
# Dashboard stats aur movie management ke liye movies load karne ke liye
# ============================================

movies = load_movies()


# ============================================
# SECTION 10: DASHBOARD STATS CARDS
# Use:
# Admin ko total movies, genres aur average rating ka quick overview dene ke liye
# ============================================

total_movies = len(movies)

genres = set()
ratings = []

for movie in movies:
    if movie.get("genre"):
        genres.add(movie.get("genre"))

    try:
        ratings.append(float(movie.get("rating", 0)))
    except Exception:
        pass

avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <h2>{total_movies}</h2>
        <p>Total Movies</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <h2>{len(genres)}</h2>
        <p>Total Genres</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <h2>{avg_rating}</h2>
        <p>Average Rating</p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")


# ============================================
# SECTION 11: ADMIN NAVIGATION
# Use:
# Admin dashboard ke pages switch karne ke liye
# ============================================

admin_page = st.radio(
    "Admin Menu",
    [
        "➕ Add Movie",
        "🎬 Manage Movies",
        "📊 Movie Data"
    ],
    horizontal=True
)


# ============================================
# SECTION 12: ADD MOVIE PAGE
# Use:
# Admin new movie add kar sakta hai
# ============================================

if admin_page == "➕ Add Movie":

    st.subheader("➕ Add New Movie")

    with st.form("add_movie_form"):

        title = st.text_input("Movie Title")
        genre = st.text_input("Genre")
        rating = st.number_input(
            "Rating",
            min_value=0.0,
            max_value=10.0,
            step=0.1
        )
        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=2100,
            step=1
        )
        description = st.text_area("Description")

        add_button = st.form_submit_button("Add Movie")

        if add_button:

            if not title or not genre or not description:
                st.warning("Please fill all required fields.")

            else:
                try:
                    response = requests.post(
                        MOVIES_URL,
                        json={
                            "title": title,
                            "genre": genre,
                            "rating": rating,
                            "year": year,
                            "description": description
                        }
                    )

                    if response.status_code == 201:
                        st.success("Movie added successfully ✅")
                        st.rerun()
                    else:
                        st.error("Movie add failed")

                except Exception as e:
                    st.error("Backend Error")
                    st.code(str(e))


# ============================================
# SECTION 13: MANAGE MOVIES PAGE
# Use:
# Admin existing movies ko edit aur delete kar sakta hai
# ============================================

elif admin_page == "🎬 Manage Movies":

    st.subheader("🎬 Manage Existing Movies")

    if len(movies) == 0:
        st.info("No movies available.")

    else:
        for index, movie in enumerate(movies):

            with st.expander(f"{index + 1}. {movie.get('title', 'No Title')}"):

                edit_title = st.text_input(
                    "Title",
                    value=movie.get("title", ""),
                    key=f"title_{index}"
                )

                edit_genre = st.text_input(
                    "Genre",
                    value=movie.get("genre", ""),
                    key=f"genre_{index}"
                )

                edit_rating = st.number_input(
                    "Rating",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(movie.get("rating", 0)),
                    step=0.1,
                    key=f"rating_{index}"
                )

                edit_year = st.number_input(
                    "Year",
                    min_value=1900,
                    max_value=2100,
                    value=int(movie.get("year", 2000)),
                    step=1,
                    key=f"year_{index}"
                )

                edit_description = st.text_area(
                    "Description",
                    value=movie.get("description", ""),
                    key=f"description_{index}"
                )

                col_update, col_delete = st.columns(2)

                with col_update:
                    if st.button("✏️ Update Movie", key=f"update_{index}"):

                        try:
                            response = requests.put(
                                f"{MOVIES_URL}/{index}",
                                json={
                                    "title": edit_title,
                                    "genre": edit_genre,
                                    "rating": edit_rating,
                                    "year": edit_year,
                                    "description": edit_description
                                }
                            )

                            if response.status_code == 200:
                                st.success("Movie updated successfully ✅")
                                st.rerun()
                            else:
                                st.error("Update failed")

                        except Exception as e:
                            st.error("Backend Error")
                            st.code(str(e))

                with col_delete:
                    if st.button("🗑 Delete Movie", key=f"delete_{index}"):

                        try:
                            response = requests.delete(
                                f"{MOVIES_URL}/{index}"
                            )

                            if response.status_code == 200:
                                st.success("Movie deleted successfully ✅")
                                st.rerun()
                            else:
                                st.error("Delete failed")

                        except Exception as e:
                            st.error("Backend Error")
                            st.code(str(e))


# ============================================
# SECTION 14: MOVIE DATA PAGE
# Use:
# Admin ko movies ka table overview dikhane ke liye
# ============================================

elif admin_page == "📊 Movie Data":

    st.subheader("📊 Movie Data Overview")

    if len(movies) == 0:
        st.info("No movie data available.")

    else:
        df = pd.DataFrame(movies)
        st.dataframe(df, use_container_width=True)