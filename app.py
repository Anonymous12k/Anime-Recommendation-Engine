import streamlit as st
import pandas as pd
import ast

# ------------------- Load Data -------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_dataset.csv")
    df['genres'] = df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df['emotion_tags'] = df['emotion_tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

# ------------------- Main App -------------------
df = load_data()

# -------- Check if navigating to Detail Page --------
if 'selected_anime' not in st.session_state:
    st.session_state.selected_anime = None

if st.session_state.selected_anime is None:
    st.title("🎭 Anime Emotion Recommender")

    # -------- Show Favorites on Home Page --------
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    if st.session_state.favorites:
        st.subheader("❤️ Your Favorites")
        for fav_title in st.session_state.favorites:
            anime_row = df[df["title"] == fav_title].iloc[0]
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.image(anime_row["image_url"], width=80)
            with col2:
                st.markdown(f"**{anime_row['title']}**")
                st.caption(", ".join(anime_row["genres"]))
            with col3:
                if st.button("❌", key=f"remove_{fav_title}"):
                    st.session_state.favorites.remove(fav_title)
                    st.experimental_rerun()

        st.markdown("---")

    # -------- Emotion Filter Section --------
    selected_emotion = st.selectbox("Choose your emotion", sorted(set(tag for tags in df['emotion_tags'] for tag in tags)))

    filtered_df = df[df['emotion_tags'].apply(lambda tags: selected_emotion in tags)]

    for index, row in filtered_df.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(row['image_url'], width=120)
        with col2:
            st.subheader(row['title'])
            st.caption(", ".join(row['genres']))
            if st.button("View Details", key=f"details_{index}"):
                st.session_state.selected_anime = row.to_dict()
                st.experimental_rerun()

            if st.button("View Details", key=f"details_{index}"):
                st.session_state.selected_anime = row.to_dict()
                st.experimental_rerun()

else:
    anime = st.session_state.selected_anime

    # -------- Back Button (just an arrow) --------
    if st.button("⬅️"):
        st.session_state.selected_anime = None
        st.experimental_rerun()

    st.title(anime['title'])
    st.image(anime['image_url'], width=300)

    # -------- Genres, Score --------
    st.markdown(f"**Genres:** {', '.join(anime['genres'])}")
    st.markdown(f"**Score:** {anime.get('score', 'N/A')}")

    # -------- Synopsis --------
    st.markdown("### 📖 Synopsis")
    st.write(anime.get("synopsis", "No synopsis available."))

       # -------- Trailer --------
    trailer_url = anime.get("trailer_url", "").strip()

    st.markdown("### 🎬 Watch Trailer")
    if trailer_url and ("youtube.com" in trailer_url or "youtu.be" in trailer_url or trailer_url.endswith(".mp4")):
        st.video(trailer_url)
    else:
        st.info("Trailer not available or invalid link.")

    # -------- Watch on MAL --------
    if anime.get("watch_url"):
        st.markdown(f"[🎞️ Watch on MAL]({anime['watch_url']})", unsafe_allow_html=True)

    # -------- Add to Favorites --------
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    is_favorite = anime['title'] in st.session_state.favorites
    fav_button_label = "❤️" if is_favorite else "🤍"

    if st.button(fav_button_label + " Add to Favorites"):
        if is_favorite:
            st.session_state.favorites.remove(anime['title'])
        else:
            st.session_state.favorites.append(anime['title'])
        st.experimental_rerun()
