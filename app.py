import streamlit as st
import pandas as pd
import ast
import random

# ---------------------- Config ----------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ---------------------- Safe Rerun ----------------------
def safe_rerun():
    try:
        st.experimental_rerun()
    except RuntimeError:
        pass  # Prevent rerun error from double click

# ---------------------- Load Data ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_extended_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ---------------------- Initialize State ----------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_anime" not in st.session_state:
    st.session_state.selected_anime = None

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
        .scrollbox {
            overflow-y: auto;
            max-height: 400px;
            padding-right: 10px;
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
        .fav-btn {
            position: fixed;
            top: 20px;
            right: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar Emotion ----------------------
st.sidebar.header("🧠 Select Your Emotion")
emotion_options = ["Any"] + sorted(set(e for tags in df["emotion_tags"] for e in tags))
selected_emotion = st.sidebar.selectbox("Choose an emotion:", emotion_options)

# ---------------------- Navigation Button (Favorites) ----------------------
if st.session_state.page != "favorites":
    if st.sidebar.button("⭐ View Favorites"):
        st.session_state.page = "favorites"

# ---------------------- Detail View ----------------------
if st.session_state.page == "details":
    anime = st.session_state.selected_anime
    st.markdown(f"""
        <div class='detail-box'>
            <h2 class='anime-title'>{anime['title']}</h2>
            <p><strong>Genres:</strong> {', '.join(anime['genres'])}</p>
            <p><strong>Emotions:</strong> {', '.join(anime['emotion_tags'])}</p>
            <p><strong>Synopsis:</strong> {anime.get('synopsis', 'No synopsis available.')}</p>
    """, unsafe_allow_html=True)

    if pd.notna(anime.get("trailer_url", None)):
        st.markdown(f"<a href='{anime['trailer_url']}' target='_blank'>🎬 Watch Trailer</a>", unsafe_allow_html=True)

    if anime["title"] in st.session_state.favorites:
        if st.button("❌ Remove from Favorites"):
            st.session_state.favorites.remove(anime["title"])
            safe_rerun()
    else:
        if st.button("❤️ Add to Favorites"):
            if anime["title"] not in st.session_state.favorites:
                st.session_state.favorites.append(anime["title"])
            safe_rerun()

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        safe_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Favorites Page ----------------------
elif st.session_state.page == "favorites":
    st.subheader("⭐ Your Favorite Anime")
    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        safe_rerun()

    if st.session_state.favorites:
        fav_df = df[df["title"].isin(st.session_state.favorites)]
        fav_cols = st.columns(3)
        for i, (_, row) in enumerate(fav_df.iterrows()):
            with fav_cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                        <div class='anime-card'>
                            <span class='anime-title'>{row['title']}</span><br>
                            <strong>Genres:</strong> {', '.join(row['genres'])}<br>
                    """, unsafe_allow_html=True)

                    if pd.notna(row['image_url']):
                        st.image(row['image_url'], use_container_width=True)

                    if st.button("📖 View Details", key=f"fav_view_{i}"):
                        st.session_state.selected_anime = row.to_dict()
                        st.session_state.page = "details"
                        safe_rerun()

                    if st.button("❌ Remove", key=f"fav_remove_{i}"):
                        if row["title"] in st.session_state.favorites:
                            st.session_state.favorites.remove(row["title"])
                            safe_rerun()

                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No favorites yet.")

# ---------------------- Home Page ----------------------
else:
    st.title("MoodFlix Anime Recommender")
    st.markdown("Find anime based on how you feel 🎭")

    if selected_emotion.lower() == "any" or selected_emotion == "":
        filtered_df = df.sample(n=min(9, len(df)))
    else:
        filtered_df = df[df["emotion_tags"].apply(lambda tags: selected_emotion in tags)]

    if filtered_df.empty:
        st.warning("No anime found for this emotion.")
    else:
        st.subheader(f"🎬 Recommendations for '{selected_emotion}'")
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                        <div class='anime-card'>
                            <span class='anime-title'>{row['title']}</span><br>
                            <strong>Genres:</strong> {', '.join(row['genres'])}<br>
                            <strong>Emotions:</strong> {', '.join(row['emotion_tags'])}<br>
                    """, unsafe_allow_html=True)

                    if pd.notna(row['image_url']):
                        st.image(row['image_url'], use_container_width=True)

                    if st.button("📖 View Details", key=f"home_details_{i}"):
                        st.session_state.selected_anime = row.to_dict()
                        st.session_state.page = "details"
                        safe_rerun()

                    if row["title"] in st.session_state.favorites:
                        if st.button("❌ Remove", key=f"home_remove_{i}"):
                            st.session_state.favorites.remove(row["title"])
                            safe_rerun()
                    else:
                        if st.button("❤️ Add", key=f"home_add_{i}"):
                            if row["title"] not in st.session_state.favorites:
                                st.session_state.favorites.append(row["title"])
                            safe_rerun()

                    st.markdown("</div>", unsafe_allow_html=True)
