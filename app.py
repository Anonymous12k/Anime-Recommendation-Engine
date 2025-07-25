import streamlit as st
import pandas as pd
import ast

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
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "home"
if "selected_anime" not in st.session_state:
    st.session_state.selected_anime = None

# ------------------------ Goth Style ------------------------
st.markdown("""
    <style>
        body, .stApp {
            background-color: #0e0e0e;
            color: #ffffff;
            font-family: 'Yu Gothic', 'Noto Sans JP', sans-serif;
        }
        .anime-card {
            background: rgba(30, 30, 30, 0.7);
            padding: 1.5em;
            margin: 1em 0;
            border-radius: 1em;
            backdrop-filter: blur(4px);
            border: 1px solid #2c2c2c;
        }
        .detail-box {
            width: 100%;
            aspect-ratio: 4 / 3;
            background-color: #1a1a1a;
            padding: 1.5em;
            border: 1px solid #444;
            overflow-y: auto;
            border-radius: 0.5em;
        }
        .block-container {
            padding-top: 2rem;
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------ Emoji Mood Presets ------------------------
emoji_emotions = {
    "😊 Happy": "happy",
    "😢 Sad": "sad",
    "😡 Angry": "angry",
    "😱 Fearful": "fear",
    "😌 Relaxed": "relaxed",
    "🤩 Excited": "excited",
    "😤 Rage": "rage",
    "💔 Heartbroken": "heartbroken",
    "🥺 Emotional": "emotional",
    "😎 Cool": "cool"
}

# ------------------------ Navigation ------------------------
def go_home():
    st.session_state.selected_page = "home"
    st.session_state.selected_anime = None

# ------------------------ Anime Detail Page ------------------------
def anime_detail_page(anime_title):
    anime = df[df['title'] == anime_title].iloc[0]
    st.title(anime['title'])
    with st.container():
        st.markdown(f"""
        <div class='detail-box'>
            <strong>🎭 Genres:</strong> {', '.join(anime['genres'])}<br>
            <strong>💫 Emotions:</strong> {', '.join(anime['emotion_tags'])}<br><br>
            <strong>📖 Synopsis:</strong><br>
            {anime['synopsis']}
        </div>
        """, unsafe_allow_html=True)

    is_fav = anime['title'] in st.session_state.favorites
    if is_fav:
        if st.button("❎ Remove from Favorites"):
            st.session_state.favorites.remove(anime['title'])
            st.toast(f"❌ Removed '{anime['title']}' from favorites")
    else:
        if st.button("❤️ Add to Favorites"):
            st.session_state.favorites.append(anime['title'])
            st.toast(f"✅ Added '{anime['title']}' to favorites")

    if st.button("🔙 Back"):
        go_home()

# ------------------------ Home Page ------------------------
def home_page():
    st.title("MoodFlix Anime Recommender")
    st.subheader("Find anime based on how you feel!")

    # Mood selection
    mood_label = st.sidebar.selectbox("🎭 Choose Your Mood", list(emoji_emotions.keys()))
    selected_emotion = emoji_emotions[mood_label]

    if st.button("🎬 Recommend"):
        st.session_state.recommend_triggered = True

    if st.session_state.get("recommend_triggered", False):
        results = df[df["emotion_tags"].apply(lambda x: selected_emotion in x)]

        if results.empty:
            st.warning("😢 No anime found for that emotion.")
        else:
            for i, (_, row) in enumerate(results.iterrows()):
                with st.container():
                    st.markdown(f"""
                    <div class='anime-card'>
                        <h3 style='cursor:pointer;'>{row['title']}</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(row['title'], key=f"title_btn_{row['title']}_{i}"):
                        st.session_state.selected_anime = row['title']
                        st.session_state.selected_page = "detail"

                    is_fav = row['title'] in st.session_state.favorites
                    fav_key = f"fav_btn_{i}"
                    if is_fav:
                        if st.button("❎ Remove Favorite", key=fav_key):
                            st.session_state.favorites.remove(row['title'])
                            st.toast(f"❌ Removed '{row['title']}' from favorites")
                    else:
                        if st.button("❤️ Add to Favorites", key=fav_key):
                            st.session_state.favorites.append(row['title'])
                            st.toast(f"✅ Added '{row['title']}' to favorites")

# ------------------------ Router ------------------------
if st.session_state.selected_page == "home":
    home_page()
elif st.session_state.selected_page == "detail":
    anime_detail_page(st.session_state.selected_anime)
