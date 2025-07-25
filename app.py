import streamlit as st
import pandas as pd
import ast
import random

# ---------------------- Config ----------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ---------------------- Helper ----------------------
def safe_get(key, default):
    return st.session_state.get(key, default)

# ---------------------- Load Data ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_extended_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ---------------------- Initialize State ----------------------
st.session_state.setdefault("favorites", [])
st.session_state.setdefault("page", "home")
st.session_state.setdefault("selected_anime", None)

# ---------------------- Sidebar ----------------------
st.sidebar.header("🎭 Choose Your Emotion")
emotions = ["Any"] + sorted({emotion for sublist in df["emotion_tags"] for emotion in sublist})
selected_emotion = st.sidebar.selectbox("Emotion", emotions)

if st.session_state.page != "favorites":
    if st.sidebar.button("⭐ View Favorites"):
        st.session_state.page = "favorites"

# ---------------------- Detail Page ----------------------
if st.session_state.page == "details" and st.session_state.selected_anime:
    anime = st.session_state.selected_anime

    st.markdown(f"""
        <div class='detail-box'>
            <h2 style='color:#e91e63'>{anime['title']}</h2>
            <p><strong>Genres:</strong> {', '.join(anime['genres'])}</p>
            <p><strong>Emotions:</strong> {', '.join(anime['emotion_tags'])}</p>
            <p><strong>Synopsis:</strong> {anime.get('synopsis', 'No synopsis available.')}</p>
    """, unsafe_allow_html=True)

    if pd.notna(anime.get("trailer_url", None)):
        st.markdown(f"<a href='{anime['trailer_url']}' target='_blank'>🎬 Watch Trailer</a>", unsafe_allow_html=True)

    if anime["title"] in st.session_state.favorites:
        if st.button("❌ Remove from Favorites"):
            st.session_state.favorites.remove(anime["title"])
    else:
        if st.button("❤️ Add to Favorites"):
            st.session_state.favorites.append(anime["title"])

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.session_state.selected_anime = None

# ---------------------- Favorites Page ----------------------
elif st.session_state.page == "favorites":
    st.subheader("⭐ Your Favorite Anime")

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"

    if st.session_state.favorites:
        fav_df = df[df["title"].isin(st.session_state.favorites)]
        cols = st.columns(3)

        for i, (_, row) in enumerate(fav_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style='background:#1e1e2f;padding:1rem;border-radius:1rem;box-shadow:0 0 10px #8e44ad;margin-bottom:1rem'>
                        <h4 style='color:#e91e63'>{row['title']}</h4>
                        <p><strong>Genres:</strong> {', '.join(row['genres'])}</p>
                """, unsafe_allow_html=True)

                if pd.notna(row["image_url"]):
                    st.image(row["image_url"], use_container_width=True)

                if st.button("📖 View Details", key=f"fav_view_{i}"):
                    st.session_state.selected_anime = row.to_dict()
                    st.session_state.page = "details"

                if st.button("❌ Remove", key=f"fav_remove_{i}"):
                    st.session_state.favorites.remove(row["title"])
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No favorites added yet.")

# ---------------------- Home Page ----------------------
else:
    st.title("🎬 MoodFlix: Emotion-Based Anime Recommender")
    st.markdown("Discover anime that matches your mood!")

    if selected_emotion.lower() == "any":
        filtered_df = df.sample(n=min(9, len(df)))
    else:
        filtered_df = df[df["emotion_tags"].apply(lambda tags: selected_emotion in tags)]

    if filtered_df.empty:
        st.warning("No anime found for this emotion.")
    else:
        st.subheader(f"🎭 Recommendations for '{selected_emotion}'")
        cols = st.columns(3)

        for i, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class='anime-card' style='background:#1e1e2f;padding:1rem;border-radius:1rem;box-shadow:0 0 10px #8e44ad;margin-bottom:1rem'>
                        <h4 style='color:#e91e63'>{row['title']}</h4>
                        <p><strong>Genres:</strong> {', '.join(row['genres'])}</p>
                        <p><strong>Emotions:</strong> {', '.join(row['emotion_tags'])}</p>
                """, unsafe_allow_html=True)

                if pd.notna(row["image_url"]):
                    st.image(row["image_url"], use_container_width=True)

                if st.button("📖 View Details", key=f"home_detail_{i}"):
                    st.session_state.selected_anime = row.to_dict()
                    st.session_state.page = "details"

                if row["title"] in st.session_state.favorites:
                    if st.button("❌ Remove", key=f"home_remove_{i}"):
                        st.session_state.favorites.remove(row["title"])
                        st.rerun()
                else:
                    if st.button("❤️ Add", key=f"home_add_{i}"):
                        st.session_state.favorites.append(row["title"])
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
