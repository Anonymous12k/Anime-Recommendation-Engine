import streamlit as st
import pandas as pd
import ast
import random

# ---------------------- Config ----------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ---------------------- Load Data ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_dataset.csv")  # Includes 'watch_url'
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ---------------------- Initialize State ----------------------
default_states = {
    "favorites": [],
    "page": "home",
    "selected_anime": None,
    "action": None,
    "action_payload": None
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
    </style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar ----------------------
st.sidebar.header("🧠 Select Your Emotion")
emotion_options = ["Any"] + sorted(set(e for tags in df["emotion_tags"] for e in tags))
selected_emotion = st.sidebar.selectbox("Choose an emotion:", emotion_options)

if st.session_state.page != "favorites":
    if st.sidebar.button("⭐ View Favorites"):
        st.session_state.page = "favorites"

# ---------------------- Details Page ----------------------
if st.session_state.page == "details":
    anime = st.session_state.selected_anime
    st.markdown(f"<div class='detail-box'>", unsafe_allow_html=True)
    st.markdown(f"### 🎬 {anime['title']}")
    st.markdown(f"**Genres:** {', '.join(anime['genres'])}")
    st.markdown(f"**Emotions:** {', '.join(anime['emotion_tags'])}")
    st.markdown(f"**Synopsis:** {anime.get('synopsis', 'No synopsis available.')}")

    if pd.notna(anime.get("watch_url", None)) and "youtube.com" in anime["watch_url"]:
        st.markdown(f"[▶️ Watch Trailer]({anime['watch_url']})", unsafe_allow_html=True)

    if anime["title"] in st.session_state.favorites:
        if st.button("❌ Remove from Favorites"):
            st.session_state.favorites.remove(anime["title"])
            st.experimental_rerun()
    else:
        if st.button("❤ Add to Favorites"):
            st.session_state.favorites.append(anime["title"])
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

                if pd.notna(row["image_url"]):
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

    filtered_df = (
        df.sample(n=min(9, len(df))) if selected_emotion.lower() == "any"
        else df[df["emotion_tags"].apply(lambda tags: selected_emotion in tags)]
    )

    if filtered_df.empty:
        st.warning("No anime found for this emotion.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"<div class='anime-card'>", unsafe_allow_html=True)
                st.markdown(f"**{row['title']}**")
                st.markdown(f"_Genres:_ {', '.join(row['genres'])}")
                st.markdown(f"_Emotions:_ {', '.join(row['emotion_tags'])}")

                if pd.notna(row["image_url"]):
                    st.image(row["image_url"], use_container_width=True)

                if st.button("📖 View Details", key=f"view_{i}"):
                    st.session_state.selected_anime = row.to_dict()
                    st.session_state.page = "details"
                    st.experimental_rerun()

                if row["title"] in st.session_state.favorites:
                    if st.button("❌ Remove", key=f"remove_{i}"):
                        st.session_state.favorites.remove(row["title"])
                        st.experimental_rerun()
                else:
                    if st.button("❤ Add", key=f"add_{i}"):
                        st.session_state.favorites.append(row["title"])
                        st.experimental_rerun()

                st.markdown("</div>", unsafe_allow_html=True)
