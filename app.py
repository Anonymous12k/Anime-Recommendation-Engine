import streamlit as st
import pandas as pd
import ast
import requests
import urllib.parse

# ---------------------- Config ----------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ---------------------- Load Data ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_dataset.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ---------------------- MAL Helper ----------------------
@st.cache_data(show_spinner=False)
def get_mal_url(title):
    try:
        query = urllib.parse.quote(title)
        response = requests.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
        if response.status_code == 200:
            results = response.json().get("data", [])
            if results:
                return results[0].get("url")
    except:
        pass
    return ""

# ---------------------- Initialize State ----------------------
def init_state():
    default_states = {
        "favorites": [],
        "page": "home",
        "selected_anime": None,
        "search": "",
        "selected_genre": "All",
    }
    for key, val in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# ---------------------- Style ----------------------
st.markdown("""
    <style>
        .anime-card {
            background-color: #1e1e2f;
            padding: 1rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 0 10px #8e44ad;
        }
        .anime-title {
            font-size: 1.2rem;
            color: #e91e63;
        }
        .detail-box {
            background-color: #2c2c3e;
            padding: 2rem;
            width: 80%;
            aspect-ratio: 4 / 3;
            border-radius: 0.5rem;
            margin: auto;
            box-shadow: 0 0 15px #9b59b6;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar ----------------------
st.sidebar.header("🧠 Filter Options")
emotion_options = ["Any"] + sorted(set(e for tags in df["emotion_tags"] for e in tags))
genre_options = ["All"] + sorted(set(g for genres in df["genres"] for g in genres))

selected_emotion = st.sidebar.selectbox("Choose an emotion:", emotion_options)
st.session_state.selected_genre = st.sidebar.selectbox("Choose a genre:", genre_options)

if st.sidebar.button("⭐ View Favorites"):
    st.session_state.page = "favorites"
    st.experimental_rerun()

# ---------------------- Search ----------------------
st.session_state.search = st.text_input("🔍 Search Anime:", st.session_state.search)

# ---------------------- Details Page ----------------------
if st.session_state.page == "details":
    anime = st.session_state.selected_anime
    title = anime.get("title", "Unknown Title")
    genres = anime.get("genres", [])
    emotions = anime.get("emotion_tags", [])
    synopsis = anime.get("synopsis", "No synopsis available.")
    image_url = anime.get("image_url", "")

    st.markdown(f"<div class='detail-box'>", unsafe_allow_html=True)
    st.markdown(f"### 🎬 {title}")
    st.markdown(f"**Genres:** {', '.join(genres)}")
    st.markdown(f"**Emotions:** {', '.join(emotions)}")
    st.markdown(f"**Synopsis:** {synopsis}")

    if image_url:
        st.image(image_url, width=300)

    mal_url = get_mal_url(title)
    if mal_url:
        st.markdown(f"<a href='{mal_url}' target='_blank'><button style='background-color:#e91e63;color:white;padding:10px;border:none;border-radius:5px;'>▶️ Watch on MAL</button></a>", unsafe_allow_html=True)

    if title in st.session_state.favorites:
        if st.button("❌ Remove from Favorites"):
            st.session_state.favorites.remove(title)
            st.experimental_rerun()
    else:
        if st.button("❤ Add to Favorites"):
            st.session_state.favorites.append(title)
            st.experimental_rerun()

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Favorites Page ----------------------
elif st.session_state.page == "favorites":
    st.subheader("⭐ Your Favorite Anime")
    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.experimental_rerun()

    fav_df = df[df["title"].isin(st.session_state.favorites)]
    if not fav_df.empty:
        for i, (_, row) in enumerate(fav_df.iterrows()):
            st.markdown(f"<div class='anime-card'>", unsafe_allow_html=True)
            st.markdown(f"**{row['title']}**")
            st.markdown(f"_Genres:_ {', '.join(row['genres'])}")
            if row["image_url"]:
                st.image(row["image_url"], use_container_width=True)
            if st.button("📖 View Details", key=f"fav_detail_{i}"):
                st.session_state.selected_anime = row.to_dict()
                st.session_state.page = "details"
                st.experimental_rerun()
            if st.button("❌ Remove", key=f"fav_remove_{i}"):
                st.session_state.favorites.remove(row["title"])
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No favorites yet.")

# ---------------------- Home Page ----------------------
else:
    st.title("MoodFlix Anime Recommender 🎭")

    filtered_df = df.copy()
    if selected_emotion != "Any":
        filtered_df = filtered_df[filtered_df["emotion_tags"].apply(lambda x: selected_emotion in x)]
    if st.session_state.selected_genre != "All":
        filtered_df = filtered_df[filtered_df["genres"].apply(lambda x: st.session_state.selected_genre in x)]
    if st.session_state.search:
        filtered_df = filtered_df[filtered_df["title"].str.contains(st.session_state.search, case=False, na=False)]

    if filtered_df.empty:
        st.warning("No anime found for selected filters.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"<div class='anime-card'>", unsafe_allow_html=True)
                st.markdown(f"**{row['title']}**")
                st.markdown(f"_Genres:_ {', '.join(row['genres'])}")
                st.markdown(f"_Emotions:_ {', '.join(row['emotion_tags'])}")
                if row["image_url"]:
                    st.image(row["image_url"], use_container_width=True)
                if st.button("📖 View Details", key=f"view_{i}"):
                    st.session_state.selected_anime = row.to_dict()
                    st.session_state.page = "details"
                    st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
