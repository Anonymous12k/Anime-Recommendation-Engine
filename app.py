import streamlit as st
import pandas as pd
import ast
import urllib.parse
import random

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

# ---------------------- Initialize State ----------------------
default_states = {
    "favorites": [],
    "page": "home",
    "selected_anime": None,
}
for key, val in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------- Style ----------------------
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
        }
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
        a button {
            margin-right: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar ----------------------
st.sidebar.header("🧠 Filter Your Mood")
emotion_options = ["Any"] + sorted(set(e for tags in df["emotion_tags"] for e in tags))
selected_emotion = st.sidebar.selectbox("Choose an emotion:", emotion_options)

genre_options = ["Any"] + sorted(set(g for tags in df["genres"] for g in tags))
selected_genre = st.sidebar.selectbox("Choose a genre:", genre_options)

if st.session_state.page != "favorites":
    if st.sidebar.button("⭐ View Favorites"):
        st.session_state.page = "favorites"
        st.experimental_rerun()

# ---------------------- Details Page ----------------------
if st.session_state.page == "details":
    anime = st.session_state.selected_anime
    st.markdown(f"<div class='detail-box'>", unsafe_allow_html=True)

    title = anime.get("title", "Unknown Title")
    genres = anime.get("genres", [])
    emotions = anime.get("emotion_tags", [])
    synopsis = anime.get("synopsis", "No synopsis available.")
    image_url = anime.get("image_url", "")

    st.markdown(f"### 🎬 {title}")
    st.markdown(f"**Genres:** {', '.join(genres)}")
    st.markdown(f"**Emotions:** {', '.join(emotions)}")
    st.markdown(f"**Synopsis:** {synopsis}")

    if image_url:
        st.image(image_url, width=300)

    buttons_html = ""
    trailer_url = anime.get("trailer_url", "")
    watch_url = f"https://myanimelist.net/anime?q={urllib.parse.quote(title)}"

    if trailer_url:
        buttons_html += f"<a href='{trailer_url}' target='_blank'><button style='background-color:#8e44ad;color:white;padding:10px;border:none;border-radius:5px;'>🎞️ Watch Trailer</button></a>"
    buttons_html += f"<a href='{watch_url}' target='_blank'><button style='background-color:#e91e63;color:white;padding:10px;border:none;border-radius:5px;'>▶️ Watch Anime</button></a>"

    st.markdown(buttons_html, unsafe_allow_html=True)

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
        fav_cols = st.columns(3)
        for i, (_, row) in enumerate(fav_df.iterrows()):
            with fav_cols[i % 3]:
                st.markdown(f"<div class='anime-card'>", unsafe_allow_html=True)
                st.markdown(f"**{row['title']}**")
                st.markdown(f"_Genres:_ {', '.join(row['genres'])}")
                if row["image_url"]:
                    st.image(row["image_url"], use_container_width=True)

                if st.button("📖 View Details", key=f"view_fav_{i}"):
                    st.session_state.selected_anime = row.to_dict()
                    st.session_state.page = "details"
                    st.experimental_rerun()

                if st.button("❌ Remove", key=f"remove_fav_{i}"):
                    st.session_state.favorites.remove(row["title"])
                    st.experimental_rerun()

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No favorites yet.")

# ---------------------- Home Page ----------------------
else:
    st.title("MoodFlix Anime Recommender")
    st.markdown("Find anime based on how you feel 🎭")

    # Search
    search_query = st.text_input("🔍 Search Anime by Title")
    filtered_df = df

    if search_query:
        filtered_df = filtered_df[filtered_df["title"].str.contains(search_query, case=False, na=False)]

    if selected_emotion != "Any":
        filtered_df = filtered_df[filtered_df["emotion_tags"].apply(lambda tags: selected_emotion in tags)]

    if selected_genre != "Any":
        filtered_df = filtered_df[filtered_df["genres"].apply(lambda genres: selected_genre in genres)]

    if filtered_df.empty:
        st.warning("No anime found for this filter.")
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

