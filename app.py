# ============================================
# SECTION 1: IMPORT LIBRARIES
# Use:
# ollama -> AI chatbot response ke liye
# streamlit -> frontend UI
# pandas -> movie data handle karne ke liye
# os -> CSS file load karne ke liye
# requests -> backend APIs aur OMDb API call karne ke liye
# ============================================

#import ollama
from groq import Groq
import streamlit as st
import pandas as pd
import os
import requests


# ============================================
# SECTION 2: PAGE CONFIGURATION
# Use:
# Streamlit app ka title, icon aur layout set karta hai
# ============================================

st.set_page_config(
    page_title="CineMate AI",
    page_icon="🎬",
    layout="wide"
)


# ============================================
# SECTION 3: BACKEND API URLS
# Use:
# Flask backend APIs connect karne ke liye
# ============================================

API_URL = "https://movierecommendationchatbot.onrender.com/movies"
WATCHLIST_URL = "https://movierecommendationchatbot.onrender.com/watchlist"

LOGIN_URL = "https://movierecommendationchatbot.onrender.com/login"
REGISTER_URL = "https://movierecommendationchatbot.onrender.com/register"

# ============================================
# SECTION 3A: ADMIN API URL
# Use:
# Hidden admin login API connect karne ke liye
# Normal user ko admin option show nahi hoga
# ============================================

ADMIN_LOGIN_URL = "https://movierecommendationchatbot.onrender.com/admin/login"
ADMIN_REGISTER_URL = "https://movierecommendationchatbot.onrender.com/admin/register"
MOVIES_URL = "https://movierecommendationchatbot.onrender.com/movies"

# ============================================
# SECTION 4: OMDb API KEY
# Use:
# Movie posters aur details fetch karne ke liye
# ============================================

OMDB_API_KEY = "87eb1b2f"


# ============================================
# SECTION 5: LOAD EXTERNAL CSS
# Use:
# style.css apply karne ke liye
# ============================================

if os.path.exists("style.css"):
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================
# SECTION 6: USER SESSION STATE
# Use:
# User login state track karne ke liye
# ============================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

    # ============================================
# SECTION 6A: ADMIN SESSION STATE
# Use:
# Hidden admin login state track karne ke liye
# ============================================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "admin" not in st.session_state:
    st.session_state.admin = None


# ============================================
# SECTION 7: OMDb MOVIE DETAILS FUNCTION
# Use:
# OMDb API se extra movie details fetch karta hai
# ============================================

@st.cache_data(show_spinner=False)
def get_omdb_details(movie_title, movie_year=None):

    try:

        response = requests.get(
            "https://www.omdbapi.com/",
            params={
                "t": str(movie_title).strip(),
                "y": str(movie_year),
                "apikey": OMDB_API_KEY
            },
            timeout=10
        )

        data = response.json()

        if data.get("Response") == "True":

            return {
                "poster": data.get("Poster", "N/A"),
                "imdb_rating": data.get("imdbRating", "N/A"),
                "genre": data.get("Genre", "N/A"),
                "plot": data.get("Plot", "N/A"),
                "actors": data.get("Actors", "N/A"),
                "runtime": data.get("Runtime", "N/A")
            }

    except Exception:
        pass

    return {
        "poster": "N/A",
        "imdb_rating": "N/A",
        "genre": "N/A",
        "plot": "N/A",
        "actors": "N/A",
        "runtime": "N/A"
    }
# ============================================
# SECTION 7A: HIDDEN ADMIN ACCESS CHECK
# Use:
# URL me ?admin=true hone par hidden admin login open hota hai
# Normal user ko app me admin ka koi button/link nahi dikhaya jayega
# ============================================

admin_mode = st.query_params.get("admin") == "true"


# ============================================
# SECTION 7B: HIDDEN ADMIN LOGIN SCREEN
# Use:
# Admin ko separate login screen deta hai
# Ye normal user login/register se completely hidden hai
# ============================================

if admin_mode and not st.session_state.admin_logged_in:

    st.title("🔐 CineMate Admin Login")
    st.subheader("Hidden Admin Access")

    admin_email = st.text_input("Admin Email")
    admin_password = st.text_input("Admin Password", type="password")

    if st.button("Admin Login"):

        try:
            response = requests.post(
                ADMIN_LOGIN_URL,
                json={
                    "email": admin_email,
                    "password": admin_password
                }
            )

            data = response.json()

            if response.status_code == 200:
                st.session_state.admin_logged_in = True
                st.session_state.admin = data["admin"]
                st.success("Admin login successful ✅")
                st.rerun()
            else:
                st.error(data.get("message", "Admin login failed"))

        except Exception as e:
            st.error("Admin Login API Error")
            st.code(str(e))

    st.stop()


# ============================================
# SECTION 7C: HIDDEN ADMIN DASHBOARD
# Use:
# Admin login ke baad Add/Edit/Delete movies manage karne ke liye
# Normal user yaha kabhi access nahi karega
# ============================================

if admin_mode and st.session_state.admin_logged_in:

    st.title("🛠 CineMate Admin Dashboard")
    st.subheader("Manage Movies")

    if st.button("🚪 Admin Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.admin = None
        st.rerun()

    st.markdown("---")

    # ============================================
    # SECTION 7D: ADMIN ADD MOVIE FORM
    # Use:
    # Admin new movie add kar sakta hai
    # ============================================

    st.subheader("➕ Add New Movie")

    with st.form("admin_add_movie_form"):

        title = st.text_input("Movie Title")
        genre = st.text_input("Genre")
        rating = st.number_input("Rating", min_value=0.0, max_value=10.0, step=0.1)
        year = st.number_input("Year", min_value=1900, max_value=2100, step=1)
        description = st.text_area("Description")

        add_btn = st.form_submit_button("Add Movie")

        if add_btn:

            try:
                response = requests.post(
                    API_URL,
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

    st.markdown("---")

    # ============================================
    # SECTION 7E: ADMIN MOVIE LIST
    # Use:
    # Admin existing movies ko view, edit aur delete kar sakta hai
    # ============================================

    st.subheader("🎬 Manage Existing Movies")

    try:
        movie_response = requests.get(API_URL)
        admin_movies = movie_response.json()

        for index, movie in enumerate(admin_movies):

            with st.expander(f"{index + 1}. {movie.get('title', 'No Title')}"):

                edit_title = st.text_input(
                    "Title",
                    value=movie.get("title", ""),
                    key=f"admin_title_{index}"
                )

                edit_genre = st.text_input(
                    "Genre",
                    value=movie.get("genre", ""),
                    key=f"admin_genre_{index}"
                )

                edit_rating = st.number_input(
                    "Rating",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(movie.get("rating", 0)),
                    step=0.1,
                    key=f"admin_rating_{index}"
                )

                edit_year = st.number_input(
                    "Year",
                    min_value=1900,
                    max_value=2100,
                    value=int(movie.get("year", 2000)),
                    step=1,
                    key=f"admin_year_{index}"
                )

                edit_description = st.text_area(
                    "Description",
                    value=movie.get("description", ""),
                    key=f"admin_desc_{index}"
                )

                col_update, col_delete = st.columns(2)

                with col_update:

                    if st.button("✏️ Update Movie", key=f"admin_update_{index}"):

                        update_response = requests.put(
                            f"{API_URL}/{index}",
                            json={
                                "title": edit_title,
                                "genre": edit_genre,
                                "rating": edit_rating,
                                "year": edit_year,
                                "description": edit_description
                            }
                        )

                        if update_response.status_code == 200:
                            st.success("Movie updated successfully ✅")
                            st.rerun()
                        else:
                            st.error("Update failed")

                with col_delete:

                    if st.button("🗑 Delete Movie", key=f"admin_delete_{index}"):

                        delete_response = requests.delete(
                            f"{API_URL}/{index}"
                        )

                        if delete_response.status_code == 200:
                            st.success("Movie deleted successfully ✅")
                            st.rerun()
                        else:
                            st.error("Delete failed")

    except Exception as e:
        st.error("Admin movie list load failed")
        st.code(str(e))

    st.stop()


# ============================================
# SECTION 8: LOGIN / REGISTER SCREEN
# Use:
# Premium Netflix-style login/register landing page dikhane ke liye
# User yaha se login ya register kar sakta hai
# Admin option yaha bilkul show nahi hota
# ============================================

if not st.session_state.logged_in:

    # Hero Section
    st.markdown("""
    <div class="auth-hero">
        <div class="auth-overlay">
            <div class="auth-left">
                <span class="auth-badge">AI Movie Recommendation Platform</span>
                <h1>Find your next favorite movie.</h1>
                <p>
                    Search movies, save your watchlist and ask CineMate AI
                    what to watch next — all in one place.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature Cards
    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        st.markdown("""
        <div class="auth-feature-card">
            <h3>🍿 Smart Suggestions</h3>
            <p>Get movie ideas according to your mood and interest.</p>
        </div>
        """, unsafe_allow_html=True)

    with feature_col2:
        st.markdown("""
        <div class="auth-feature-card">
            <h3>⭐ Personal Watchlist</h3>
            <p>Save your favorite movies and watch them later.</p>
        </div>
        """, unsafe_allow_html=True)

    with feature_col3:
        st.markdown("""
        <div class="auth-feature-card">
            <h3>🤖 AI Movie Guide</h3>
            <p>Ask AI for story, cast, genre and similar movies.</p>
        </div>
        """, unsafe_allow_html=True)

    # Login/Register Card
    st.markdown('<div class="auth-form-card">', unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-form-title">
        <h2>🎬 CineMate AI</h2>
        <p>Login or create your account</p>
    </div>
    """, unsafe_allow_html=True)

    auth_tab = st.radio(
        "Choose Option",
        ["Login", "Register"],
        horizontal=True
    )

    # Login Form
    if auth_tab == "Login":

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            try:
                response = requests.post(
                    LOGIN_URL,
                    json={
                        "email": email,
                        "password": password
                    }
                )

                data = response.json()

                if response.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.user = data["user"]
                    st.success("Login successful ✅")
                    st.rerun()
                else:
                    st.error(data.get("message", "Login failed"))

            except Exception as e:
                st.error("Login API Error")
                st.code(str(e))

    # Register Form
    else:

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):

            try:
                response = requests.post(
                    REGISTER_URL,
                    json={
                        "name": name,
                        "email": email,
                        "password": password
                    }
                )

                data = response.json()

                if response.status_code == 201:
                    st.success("Registration successful ✅ Now login.")
                else:
                    st.error(data.get("message", "Registration failed"))

            except Exception as e:
                st.error("Register API Error")
                st.code(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()
    # ============================================
    # SECTION 8A: LOGIN FORM
    # ============================================

    if auth_tab == "Login":

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            try:

                response = requests.post(
                    LOGIN_URL,
                    json={
                        "email": email,
                        "password": password
                    }
                )

                data = response.json()

                if response.status_code == 200:

                    st.session_state.logged_in = True
                    st.session_state.user = data["user"]

                    st.success("Login successful ✅")
                    st.rerun()

                else:
                    st.error(data.get("message", "Login failed"))

            except Exception as e:
                st.error("Login API Error")
                st.code(str(e))

    # ============================================
    # SECTION 8B: REGISTER FORM
    # ============================================

    else:

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):

            try:

                response = requests.post(
                    REGISTER_URL,
                    json={
                        "name": name,
                        "email": email,
                        "password": password
                    }
                )

                data = response.json()

                if response.status_code == 201:
                    st.success("Registration successful ✅")
                else:
                    st.error(data.get("message", "Registration failed"))

            except Exception as e:
                st.error("Register API Error")
                st.code(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

        # ============================================
    # SECTION 8C: LOGIN PAGE HERO TEXT
    # Use:
    # Login/Register page ko attractive welcome screen look dene ke liye
    # ============================================

    st.markdown("""
    <div class="user-login-hero">
        <h1>🎬 CineMate AI</h1>
        <h3>Unlimited Movies. Smart Recommendations.</h3>
        <p>Login or create your account to explore movies, build your watchlist and chat with AI.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# SECTION 9: LOAD MOVIES FROM BACKEND
# Use:
# Backend se movie data fetch karta hai
# ============================================

try:

    response = requests.get(API_URL)
    response.raise_for_status()

    data = response.json()

    movies = pd.DataFrame(data)

except Exception as e:

    st.error("Backend API not connected")
    st.code(str(e))
    st.stop()


# ============================================
# SECTION 10: APP NAVIGATION
# Use:
# Netflix-style top navigation system
# Main features top par show honge
# Sidebar me sirf watchlist, user info aur logout rahega
# ============================================

st.sidebar.title("🎬 CineMate AI")

st.sidebar.success(
    f"Welcome {st.session_state.user['name']}"
)

# ============================================
# SECTION 10A: SIDEBAR OPTIONS
# Use:
# Sidebar ko clean rakhne ke liye sirf watchlist aur logout
# ============================================

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Name: {st.session_state.user['name']}")
st.sidebar.write(f"📧 Email: {st.session_state.user['email']}")
st.sidebar.markdown("---")

show_watchlist = st.sidebar.button("⭐ My Watchlist")

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.user = None

    st.rerun()


# ============================================
# SECTION 10B: TOP NAVIGATION MENU
# Use:
# Main pages ko Netflix-style top navigation me show karta hai
# ============================================

top_menu = st.radio(
    "",
    [
        "🏠 Home",
        "🔍 Search Movies",
        "🤖 AI Chatbot"
    ],
    horizontal=True
)


# ============================================
# SECTION 10C: ACTIVE PAGE CONTROL
# Use:
# Sidebar aur top menu navigation ko control karta hai
# ============================================

if show_watchlist:
    page = "⭐ My Watchlist"
else:
    page = top_menu


# ============================================
# SECTION 11: HOME PAGE
# Use:
# Login ke baad user ko Netflix-style attractive home screen dikhata hai
# Isme project intro, features aur navigation guidance show hoti hai
# Admin option yaha bilkul show nahi hota
# ============================================

if page == "🏠 Home":

    st.title("🎬 CineMate AI")
    st.subheader("Your Personal AI Movie Recommendation Platform")

    st.markdown("""
    <div class="home-hero">
        <h1>Unlimited Movies, Smart Recommendations 🍿</h1>
        <p>
            CineMate AI helps you discover movies, search by genre, save your favorite movies
            in watchlist, and ask an AI chatbot for personalized movie suggestions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="home-card">
            <h3>🔍 Search Movies</h3>
            <p>Find movies by name and genre with posters, ratings, actors and plot.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="home-card">
            <h3>⭐ My Watchlist</h3>
            <p>Save your favorite movies and manage your personal movie list anytime.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="home-card">
            <h3>🤖 AI Chatbot</h3>
            <p>Ask for movie suggestions, similar movies, story details and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("🔥 Why CineMate AI?")

    st.markdown("""
    - Discover movies according to your mood  
    - Save your favorite movies in your personal watchlist  
    - Get smart movie suggestions instantly  
    - Explore movie story, cast, rating and details easily  
    - Simple, clean and Netflix-style experience  
    - Perfect place to find what to watch next  
    """)

    st.success("Start exploring movies from the sidebar and build your own watchlist.")
# ============================================
# SECTION 12: SEARCH MOVIES PAGE
# Use:
# User movie browse/search kar sakta hai
# Genre filter aur search box se movies filter hoti hain
# Movie cards Netflix-style layout me show hote hain
# ============================================

elif page == "🔍 Search Movies":

    st.title("🔍 Search Movies")
    st.write("Find your next favorite movie and save it to your watchlist.")

    col_filter, col_search = st.columns([1, 2])

    with col_filter:
        genre = st.selectbox(
            "Select Genre",
            ["All"] + sorted(movies["genre"].dropna().unique().tolist())
        )

    with col_search:
        search_query = st.text_input(
            "Search Movie",
            placeholder="Enter movie name..."
        )

    if genre == "All":
        filtered_movies = movies
    else:
        filtered_movies = movies[movies["genre"] == genre]

    if search_query:
        filtered_movies = filtered_movies[
            filtered_movies["title"].str.contains(
                search_query,
                case=False,
                na=False
            )
        ]

    st.subheader("🍿 Recommended Movies")

    if filtered_movies.empty:
        st.warning("No movies found. Try another name or genre.")

    else:
        for i, row in enumerate(filtered_movies.itertuples(index=False)):

            omdb = get_omdb_details(row.title, row.year)

            # ============================================
            # SECTION 12A: MOVIE CARD CONTAINER
            # Use:
            # Har movie ko poster aur details ke sath card-style layout me dikhata hai
            # ============================================

            st.markdown('<div class="search-movie-card">', unsafe_allow_html=True)

            col_img, col_info = st.columns([1, 3])

            with col_img:
                if omdb["poster"] != "N/A":
                    st.image(omdb["poster"], use_container_width=True)
                else:
                    st.info("No Poster")

            with col_info:
                st.subheader(row.title)

                st.markdown(
                    f"""
                    <p class="movie-meta">
                        ⭐ App Rating: {row.rating} &nbsp; | &nbsp;
                        IMDb: {omdb['imdb_rating']} &nbsp; | &nbsp;
                        📅 {row.year}
                    </p>
                    """,
                    unsafe_allow_html=True
                )

                st.write(f"🎭 Genre: {omdb['genre']}")
                st.write(f"🎬 Actors: {omdb['actors']}")
                st.write(f"⏱️ Runtime: {omdb['runtime']}")
                st.write(omdb["plot"])

                # ============================================
                # SECTION 12B: ADD TO WATCHLIST BUTTON
                # Use:
                # User selected movie ko personal watchlist me save kar sakta hai
                # ============================================

                if st.button(
                    "⭐ Add to Watchlist",
                    key=f"watch_{i}_{row.title}"
                ):

                    movie_data = {
                        "title": row.title,
                        "genre": omdb["genre"] if omdb["genre"] != "N/A" else row.genre,
                        "rating": row.rating,
                        "year": row.year,
                        "description": omdb["plot"] if omdb["plot"] != "N/A" else row.description,
                        "poster": omdb["poster"],
                        "imdb_rating": omdb["imdb_rating"],
                        "actors": omdb["actors"],
                        "runtime": omdb["runtime"]
                    }

                    try:
                        response = requests.post(
                            WATCHLIST_URL,
                            json=movie_data
                        )

                        if response.status_code == 201:
                            st.success("Added to watchlist ✅")

                        elif response.status_code == 409:
                            st.warning("Already in watchlist")

                        else:
                            st.error("Watchlist add failed")

                    except Exception as e:
                        st.error("Backend Error")
                        st.code(str(e))

            st.markdown("</div>", unsafe_allow_html=True)
            st.divider()


# ============================================
# SECTION 13: WATCHLIST PAGE
# Use:
# User ki saved movies ko premium card layout me show karta hai
# User apni watchlist se movie remove kar sakta hai
# Ye movie database delete nahi karta
# ============================================

elif page == "⭐ My Watchlist":

    st.title("⭐ My Watchlist")
    st.write("Your saved movies are here. Watch later, remove anytime.")

    try:
        response = requests.get(WATCHLIST_URL)
        watchlist = response.json()

        if len(watchlist) == 0:

            st.markdown("""
            <div class="empty-watchlist">
                <h2>🍿 Your watchlist is empty</h2>
                <p>Go to Search Movies and add your favorite movies here.</p>
            </div>
            """, unsafe_allow_html=True)

        else:

            st.subheader(f"Saved Movies: {len(watchlist)}")

            for j, movie in enumerate(watchlist):

                # ============================================
                # SECTION 13A: WATCHLIST MOVIE CARD
                # Use:
                # Saved movie ko poster aur details ke sath card-style me show karta hai
                # ============================================

                st.markdown('<div class="watchlist-card">', unsafe_allow_html=True)

                col_img, col_info = st.columns([1, 3])

                with col_img:

                    poster = movie.get("poster", "N/A")

                    if poster != "N/A":
                        st.image(
                            poster,
                            use_container_width=True
                        )
                    else:
                        st.info("No Poster")

                with col_info:

                    st.subheader(movie.get("title", "No Title"))

                    st.markdown(
                        f"""
                        <p class="movie-meta">
                            ⭐ App Rating: {movie.get('rating', 'N/A')} &nbsp; | &nbsp;
                            IMDb: {movie.get('imdb_rating', 'N/A')} &nbsp; | &nbsp;
                            📅 {movie.get('year', 'N/A')}
                        </p>
                        """,
                        unsafe_allow_html=True
                    )

                    st.write(f"🎭 Genre: {movie.get('genre', 'N/A')}")
                    st.write(f"🎬 Actors: {movie.get('actors', 'N/A')}")
                    st.write(f"⏱️ Runtime: {movie.get('runtime', 'N/A')}")
                    st.write(movie.get("description", "No description"))

                    # ============================================
                    # SECTION 13B: REMOVE FROM WATCHLIST BUTTON
                    # Use:
                    # Movie ko sirf user ki watchlist se remove karta hai
                    # Main movies database par koi effect nahi padta
                    # ============================================

                    if st.button(
                        "🗑 Remove from Watchlist",
                        key=f"remove_{j}_{movie.get('title', '')}"
                    ):

                        delete_response = requests.delete(
                            f"{WATCHLIST_URL}/{movie.get('title')}"
                        )

                        if delete_response.status_code == 200:
                            st.success("Removed from watchlist ✅")
                            st.rerun()
                        else:
                            st.error("Failed to remove movie from watchlist")

                st.markdown("</div>", unsafe_allow_html=True)
                st.divider()

    except Exception as e:

        st.error("Watchlist API Error")
        st.code(str(e))

# ============================================
# SECTION 14: AI CHATBOT PAGE
# Use:
# User movie-related AI questions pooch sakta hai
# Cloud deployment par Ollama unavailable hone par fallback message show hota hai
# ============================================

elif page == "🤖 AI Chatbot":

    st.title("🤖 CineMate AI Chatbot")

    st.markdown("""
    <div class="chatbot-hero">
        <h2>Ask CineMate AI anything about movies 🎬</h2>
        <p>
            Get movie suggestions, story details, cast information,
            similar movie ideas and watch recommendations instantly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Movie Context
    movie_context = movies[
        ["title", "genre", "rating", "year", "description"]
    ].head(30).to_string(index=False)

    # Suggested Questions
    st.subheader("💡 Try asking:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Suggest me a thriller movie")

    with col2:
        st.info("Best movie for weekend night?")

    with col3:
        st.info("Tell me similar movies like Inception")

    # Clear Chat Button
    if st.button("🧹 Clear Chat"):

        st.session_state.chat_history = []
        st.rerun()

    # Display Old Chat Messages
    for msg in st.session_state.chat_history:

        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input
    user_prompt = st.chat_input(
        "Ask me about movies, actors, story or recommendations..."
    )

    if user_prompt:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):

            with st.spinner("CineMate AI is thinking..."):

                ai_reply = """
# ============================================
# SECTION 14F: GROQ AI RESPONSE
# Use:
# Groq cloud AI API se chatbot response generate karta hai
# ============================================

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "system",
            "content": f"""
You are CineMate AI, a friendly movie recommendation assistant.

Available Movies:
{movie_context}

Reply in Hinglish if user asks in Hinglish.
"""
        },
        *st.session_state.chat_history
    ]
)

ai_reply = response.choices[0].message.content

st.write(ai_reply)

st.session_state.chat_history.append({
    "role": "assistant",
    "content": ai_reply
})