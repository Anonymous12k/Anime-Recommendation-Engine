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

# ------------------------ Session State for Favorites ------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ------------------------ Page Config & Styling ------------------------
st.set_page_config(page_title="Anime Recommender", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');

    html, body, .stApp {
        background-image: url('https://i.imgur.com/4NJlNeE.jpg');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        font-family: 'Noto Sans JP', sans-serif;
        color: #f5f5f5;
        animation: fadeIn 1s ease-in-out;
    }

    h1, h2, h3 {
        color: #ffc9e3;
    }

    .stButton > button {
        background-color: #663399;
        color: white;
        border-radius: 10px;
        padding: 0.4rem 1rem;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }

    .stButton > button:hover {
        background-color: #ff69b4;
    }

    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------ Title ------------------------
st.title("🌸 Anime Emotion Recommender")
st.write("Find anime based on your emotions — powered by a Japanese-themed vibe!")

# ------------------------ Sidebar Filters ------------------------
st.sidebar.header("🔍 Filters")

all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
selected_emotions = st.sidebar.multiselect("🎯 Choose Emotions", all_emotions)

all_genres = sorted({genre for sublist in df["genres"] for genre in sublist})
selected_genre = st.sidebar.selectbox("📚 Choose Genre", ["Any"] + all_genres)

min_score = st.sidebar.slider("⭐ Minimum Score", 0.0, 10.0, 7.0, 0.1)

# ------------------------ Recommendation Logic ------------------------
if st.sidebar.button("🎬 Recommend"):
    results = df.copy()

    if selected_emotions:
        results = results[results["emotion_tags"].apply(lambda tags: any(em in tags for em in selected_emotions))]

    if selected_genre != "Any":
        results = results[results["genres"].apply(lambda genres: selected_genre in genres)]

    results = results[results["score"] >= min_score]
    results = results.sort_values(by="score", ascending=False).head(45)

    if results.empty:
        st.warning("😢 No matching anime found.")
    else:
        st.markdown("## 🎥 Recommendations")
        cols = st.columns(5)

        for idx, (i, row) in enumerate(results.iterrows()):
            with cols[idx % 5]:
                st.image(row.get("image_url", ""), width=150)
                st.markdown(f"**{row['title']}**")
                st.write(f"⭐ {row['score']}")
                st.write(f"🎭 {', '.join(row['emotion_tags'])}")
                st.write(f"📚 {', '.join(row['genres'])}")

                if row['title'] in st.session_state.favorites:
                    if st.button("❌ Remove Favorite", key=f"unfav_{row['title']}_{i}"):
                        st.session_state.favorites.remove(row['title'])
                        st.success(f"❎ Removed '{row['title']}' from favorites.")
                else:
                    if st.button("❤️ Favorite", key=f"fav_{row['title']}_{i}"):
                        st.session_state.favorites.append(row['title'])
                        st.success(f"✅ Added '{row['title']}' to favorites.")

                if st.button("🔍 View Details", key=f"details_{row['title']}_{i}"):
                    st.markdown(f"### 📖 {row['title']}")
                    st.write(f"**Synopsis:** {row.get('synopsis', 'No synopsis available.')}")
                    
                    trailer_url = row.get("trailer_url", None)
                    if trailer_url:
                        st.video(trailer_url)
                    else:
                        st.write("🎞️ Trailer not available.")
                    
                    watch_url = row.get("watch_url", None)
                    if watch_url:
                        st.markdown(f"[▶️ Watch Now]({watch_url})")
                    else:
                        st.markdown(f"[🔗 Find on Anilist](https://anilist.co/search/anime?search={row['title'].replace(' ', '%20')})")

                st.markdown("---")

# ------------------------ Favorites Section ------------------------
if st.sidebar.button("❤️ View Favorites"):
    st.markdown("## ⭐ Your Favorite Anime")
    fav_df = df[df['title'].isin(st.session_state.favorites)]

    if fav_df.empty:
        st.info("You haven't added any favorites yet.")
    else:
        for i, row in fav_df.iterrows():
            st.markdown(f"**{row['title']}** - ⭐ {row['score']} - 🎭 {', '.join(row['emotion_tags'])}")
