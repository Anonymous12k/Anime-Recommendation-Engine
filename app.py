import streamlit as st
import pandas as pd
import ast
import random

# ------------------------ Page Config ------------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ------------------------ Load & Parse Data ------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_extended_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ------------------------ Session State Init ------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_anime" not in st.session_state:
    st.session_state.selected_anime = None

# ------------------------ Styling ------------------------
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
            font-family: 'Courier New', monospace;
        }
        .anime-card {
            background-color: #1e1e2f;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 0 10px #8e44ad;
            margin-bottom: 1rem;
        }
        .anime-title {
            font-size: 1.4rem;
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
            width: 75%;
            aspect-ratio: 4 / 3;
            border-radius: 0.5rem;
            margin: auto;
            box-shadow: 0 0 15px #9b59b6;
        }
        img.anime-img {
            border-radius: 0.5rem;
            width: 100%;
            height: auto;
        }
        .clickable-img {
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------ Header ------------------------
st.title("MoodFlix Anime Recommender")
st.markdown("Find anime based on how you feel! 🖤")

# ------------------------ Sidebar ------------------------
st.sidebar.header("🧠 Select Your Emotion")
emotion_options = ["any"] + sorted(set(e for sublist in df["emotion_tags"] for e in sublist))
selected_emotion = st.sidebar.selectbox("Choose an emotion:", emotion_options)

# ------------------------ Navigation ------------------------
def go_home():
    st.session_state.page = "home"

def open_anime_details(row):
    st.session_state.selected_anime = row.to_dict()
    st.session_state.page = "details"

# ------------------------ Anime Details Page ------------------------
if st.session_state.page == "details":
    anime = st.session_state.selected_anime
    st.markdown("""
        <div class='detail-box'>
            <h2 class='anime-title'>{}</h2>
            <p><strong>Genre:</strong> {}</p>
            <p><strong>Emotions:</strong> {}</p>
            <p><strong>Synopsis:</strong> {}</p>
    """.format(
        anime["title"],
        ", ".join(anime["genres"]),
        ", ".join(anime["emotion_tags"]),
        anime["synopsis"]
    ), unsafe_allow_html=True)

    if 'trailer_url' in anime and pd.notna(anime['trailer_url']):
        st.markdown(f"<a href='{anime['trailer_url']}' target='_blank'>🎬 Watch Trailer</a>", unsafe_allow_html=True)

    if anime["title"] in st.session_state.favorites:
        if st.button("❌ Remove Favorite", key=f"remove_{anime['title']}"):
            st.session_state.favorites.remove(anime["title"])
    else:
        if st.button("❤️ Add to Favorites", key=f"add_{anime['title']}"):
            st.session_state.favorites.append(anime["title"])

    if st.button("🔙 Back", key="back_btn"):
        go_home()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------ Home Page ------------------------
else:
    if selected_emotion == "any":
        filtered_df = df.sample(n=9)
    else:
        filtered_df = df[df["emotion_tags"].apply(lambda x: selected_emotion in x)]

    if not filtered_df.empty:
        st.subheader(f"🎬 Recommended Anime for Emotion: {selected_emotion}")
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                        <div class='anime-card'>
                            <span class='anime-title'>{row['title']}</span><br>
                            <strong>Genre:</strong> {', '.join(row['genres'])}<br>
                            <strong>Emotions:</strong> {', '.join(row['emotion_tags'])}<br>
                    """, unsafe_allow_html=True)

                    if 'image_url' in row and pd.notna(row['image_url']):
                        st.image(row['image_url'], use_container_width=True)
                        if st.button("📖 View Details", key=f"details_{row['title']}_{i}"):
                            open_anime_details(row)
                    else:
                        st.markdown("<em>No image available</em>", unsafe_allow_html=True)

                    if row["title"] in st.session_state.favorites:
                        if st.button("❌ Remove Favorite", key=f"remove_{row['title']}_{i}"):
                            st.session_state.favorites.remove(row["title"])
                    else:
                        if st.button("❤️ Add to Favorites", key=f"add_{row['title']}_{i}"):
                            st.session_state.favorites.append(row["title"])

                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("😢 No anime found for that emotion.")

    # ------------------------ Favorites ------------------------
    st.markdown("""
        <h3 style='color:#f39c12;'>⭐ Your Favorite Anime</h3>
        <div class='scrollbox'>
    """, unsafe_allow_html=True)
    if st.session_state.favorites:
        fav_df = df[df['title'].isin(st.session_state.favorites)]
        fav_cols = st.columns(3)
        for i, (_, row) in enumerate(fav_df.iterrows()):
            with fav_cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                        <div class='anime-card'>
                            <span class='anime-title'>{row['title']}</span><br>
                            <strong>Genre:</strong> {', '.join(row['genres'])}<br>
                    """, unsafe_allow_html=True)
                    if pd.notna(row['image_url']):
                        st.image(row['image_url'], use_container_width=True)
                    else:
                        st.markdown("<em>No image available</em>", unsafe_allow_html=True)

                    if st.button("📖 View Details", key=f"fav_details_{row['title']}"):
                        open_anime_details(row)
                    if st.button("❌ Remove Favorite", key=f"fav_remove_{row['title']}"):
                        st.session_state.favorites.remove(row["title"])

                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No favorites selected yet.")
    st.markdown("</div>", unsafe_allow_html=True)
