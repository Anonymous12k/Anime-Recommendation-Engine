# anime_app.py (Main Page)
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

# ------------------------ Session State ------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "selected_anime" not in st.session_state:
    st.session_state.selected_anime = None

# ------------------------ Page Config ------------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ------------------------ Emotion Emoji Mapping ------------------------
emoji_emotions = {
    "💔 Heartbroken": "heartbroken",
    "😤 Rage": "rage",
    "😂 Joy": "joy",
    "😭 Sad": "sad",
    "😨 Fear": "fear",
    "😐 Neutral": "neutral",
    "😳 Surprise": "surprise",
    "😍 Love": "love",
    "😎 Cool": "cool"
}

# ------------------------ Filters ------------------------
st.sidebar.header("🔍 Filters")
selected_emojis = st.sidebar.multiselect("🎯 Select your emotion", list(emoji_emotions.keys()))
selected_emotions = [emoji_emotions[e] for e in selected_emojis]

all_genres = sorted({genre for sublist in df["genres"] for genre in sublist})
selected_genre = st.sidebar.selectbox("📚 Choose Genre", ["Any"] + all_genres)

search_query = st.sidebar.text_input("🔎 Search Anime by Name")

# ------------------------ Recommend Button ------------------------
if st.sidebar.button("🎬 Recommend"):
    results = df.copy()

    if selected_emotions:
        results = results[results["emotion_tags"].apply(lambda tags: any(em in tags for em in selected_emotions))]

    if selected_genre != "Any":
        results = results[results["genres"].apply(lambda genres: selected_genre in genres)]

    if search_query:
        results = results[results['title'].str.contains(search_query, case=False)]

    results = results.sort_values(by="score", ascending=False).head(45)

    if results.empty:
        st.warning("😢 No matching anime found.")
    else:
        st.markdown("## 🎥 Recommendations")
        cols = st.columns(5)

        for idx, (i, row) in enumerate(results.iterrows()):
            with cols[idx % 5]:
                st.image(row.get("image_url", ""), width=150)
                if st.button(row['title'], key=f"title_btn_{row['title']}"):
                    st.session_state.selected_anime = row['title']
                    st.experimental_rerun()
                st.write(f"⭐ {row['score']}")

# ------------------------ Anime Detail Page ------------------------
if st.session_state.selected_anime:
    selected_row = df[df['title'] == st.session_state.selected_anime].iloc[0]

    st.markdown("""
    <div style='background: rgba(0,0,0,0.6); padding: 30px; border-radius: 8px;'>
        <h2>{}</h2>
        <p><strong>Genres:</strong> {}</p>
        <p><strong>Emotion Tags:</strong> {}</p>
        <div style="aspect-ratio: 4 / 3; border: 2px solid #ccc; padding: 10px; overflow-y: auto;">
            <p><strong>Synopsis:</strong><br>{}</p>
        </div>
    </div>
    """.format(
        selected_row['title'],
        ', '.join(selected_row['genres']),
        ', '.join(selected_row['emotion_tags']),
        selected_row.get('synopsis', 'No synopsis available.')
    ), unsafe_allow_html=True)

    if selected_row['title'] in st.session_state.favorites:
        if st.button("💔 Remove from Favorites"):
            st.session_state.favorites.remove(selected_row['title'])
            st.success("Removed from favorites")
    else:
        if st.button("❤️ Add to Favorites"):
            st.session_state.favorites.append(selected_row['title'])
            st.success("Added to favorites")

    if st.button("🔙 Back to Recommendations"):
        st.session_state.selected_anime = None
        st.experimental_rerun()

# ------------------------ Favorites ------------------------
if st.sidebar.button("❤️ View Favorites"):
    fav_df = df[df['title'].isin(st.session_state.favorites)]
    st.markdown("## ⭐ Your Favorite Anime")
    if fav_df.empty:
        st.info("No favorites selected yet.")
    else:
        for i, row in fav_df.iterrows():
            st.markdown(f"""
            <div style='background: rgba(40, 40, 40, 0.8); padding: 10px; margin: 10px 0; border-radius: 8px;'>
                <h4 style='margin-bottom: 5px;'>{row['title']}</h4>
                <p>⭐ {row['score']}<br>🎭 {', '.join(row['emotion_tags'])}<br>📚 {', '.join(row['genres'])}</p>
            </div>
            """, unsafe_allow_html=True)
