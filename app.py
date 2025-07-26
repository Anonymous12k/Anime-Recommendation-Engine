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
    if anime.get("trailer_url"):
        st.markdown("### 🎬 Watch Trailer")
        st.video(anime["trailer_url"])

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
