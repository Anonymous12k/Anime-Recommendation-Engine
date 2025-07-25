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

# ------------------------ UI Styling (Night Sky Theme with Overlay) ------------------------
st.set_page_config(page_title="Anime Recommender", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700&display=swap');

    html, body, .stApp {
        background-image: url('https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=1350&q=80');
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        color: #f5f5f5;
        font-family: 'Noto Sans JP', sans-serif;
        animation: fadeIn 1s ease-in;
    }

    .main-block {
        background: rgba(0, 0, 0, 0.6);
        padding: 20px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }

    h1, h2, h3, h4 {
        color: #f67280;
    }

    .stButton>button {
        background-color: #355c7d;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #6c5b7b;
    }

    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------ Title ------------------------
st.markdown("<div class='main-block'>", unsafe_allow_html=True)
st.title("MoodFlix Anime Recommender")
st.write("Find anime based on how you feel!")

# ------------------------ Sidebar Filters ------------------------
st.sidebar.header("🔍 Filters")

all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
selected_emotions = st.sidebar.multiselect("🎯 Select how you feel today", all_emotions)

all_genres = sorted({genre for sublist in df["genres"] for genre in sublist})
selected_genre = st.sidebar.selectbox("📚 Choose Genre", ["Any"] + all_genres)

search_query = st.sidebar.text_input("🔎 Search Anime by Name")

# ------------------------ Recommendation Logic ------------------------
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
                st.markdown(f"**{row['title']}**")
                st.write(f"⭐ {row['score']}")
                st.write(f"🎭 {', '.join(row['emotion_tags'])}")
                st.write(f"📚 {', '.join(row['genres'])}")

                if row['title'] in st.session_state.favorites:
                    if st.button("❌ Remove Favorite", key=f"unfav_{row['title']}_{i}"):
                        st.session_state.favorites.remove(row['title'])
                        st.success(f"❎ Removed '{row['title']}' from favorites")
                else:
                    if st.button("❤️ Favorite", key=f"fav_{row['title']}_{i}"):
                        st.session_state.favorites.append(row['title'])
                        st.success(f"✅ Added '{row['title']}' to favorites")

                if st.button("🔍 View Details", key=f"details_{row['title']}_{i}"):
                    st.markdown(f"### 📖 {row['title']}")
                    st.write(f"**Synopsis**: {row.get('synopsis', 'No synopsis available.')}")
                    trailer_url = row.get("trailer_url", None)
                    if trailer_url:
                        st.video(trailer_url)
                    else:
                        st.write("🎞️ Trailer not available.")

                    watch_url = row.get("watch_url", None)
                    if watch_url:
                        st.markdown(f"[▶️ Watch Now]({watch_url})")
                    else:
                        st.markdown(f"[🔗 Find Streaming](https://anilist.co/search/anime?search={row['title'].replace(' ', '%20')})")

                st.markdown("---")

# ------------------------ Favorites Section ------------------------
if st.sidebar.button("❤️ View Favorites"):
    st.markdown("## ⭐ Your Favorite Anime")
    fav_df = df[df['title'].isin(st.session_state.favorites)]

    if fav_df.empty:
        st.info("No favorites selected yet.")
    else:
        for i, row in fav_df.iterrows():
            st.markdown(f"**{row['title']}** - ⭐ {row['score']} - 🎭 {', '.join(row['emotion_tags'])}")

st.markdown("</div>", unsafe_allow_html=True)
