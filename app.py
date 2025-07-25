import streamlit as st
import pandas as pd
import ast
import random

# ---------------------- Config ----------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ---------------------- Load Data ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_dataset.csv")  # Updated to new dataset with watch_url
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ---------------------- Initialize State ----------------------
for key in ["favorites", "page", "selected_anime", "trigger_rerun"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "favorites" else "home" if key == "page" else None if key == "selected_anime" else False

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
st.sidebar.header("\U0001F9E0 Select Your Emotion")
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

    if pd.notna(anime.get("watch_url", None)):
        st.markdown(f"<a href='{anime['watch_url']}' target='_blank'>▶️ Watch Now</a>", unsafe_allow_html=True)

    if anime["title"] in st.session_state.favorites:
        if st.button("❌ Remove from Favorites", key="remove_detail"):
            st.session_state.favorites.remove(anime["title"])
            st.session_state.trigger_rerun = True
    else:
        if st.button("❤ Add to Favorites", key="add_detail"):
            st.session_state.favorites.append(anime["title"])
            st.session_state.trigger_rerun = True

    if st.button("🔙 Back to Home", key="back_detail"):
        st.session_state.page = "home"
        st.session_state.trigger_rerun = True

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Favorites Page ----------------------
elif st.session_state.page == "favorites":
    st.subheader("⭐ Your Favorite Anime")
    if st.button("🔙 Back to Home", key="back_favs"):
        st.session_state.page = "home"
        st.session_state.trigger_rerun = True

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

                    if st.button("📖 View Details", key=f"fav_view_{row['title']}_{i}"):
                        st.session_state.selected_anime = row.to_dict()
                        st.session_state.page = "details"
                        st.session_state.trigger_rerun = True

                    if st.button("❌ Remove", key=f"fav_remove_{row['title']}_{i}"):
                        st.session_state.favorites.remove(row["title"])
                        st.session_state.trigger_rerun = True

                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No favorites yet.")

# ---------------------- Home Page ----------------------
else:
    st.title("MoodFlix Anime Recommender")
    st.markdown("Find anime based on how you feel 🎭")

    filtered_df = df if selected_emotion.lower() == "any" else df[df["emotion_tags"].apply(lambda tags: selected_emotion in tags)]
    filtered_df = filtered_df.sample(n=min(9, len(filtered_df)))

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

                    if st.button("📖 View Details", key=f"home_details_{row['title']}_{i}"):
                        st.session_state.selected_anime = row.to_dict()
                        st.session_state.page = "details"
                        st.session_state.trigger_rerun = True

                    if row["title"] in st.session_state.favorites:
                        if st.button("❌ Remove", key=f"home_remove_{row['title']}_{i}"):
                            st.session_state.favorites.remove(row["title"])
                            st.session_state.trigger_rerun = True
                    else:
                        if st.button("❤ Add", key=f"home_add_{row['title']}_{i}"):
                            st.session_state.favorites.append(row["title"])
                            st.session_state.trigger_rerun = True

                    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Trigger Rerun if Needed ----------------------
if st.session_state.trigger_rerun:
    st.session_state.trigger_rerun = False
    st.experimental_rerun()
