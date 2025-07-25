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

# ------------------------ Page Configuration ------------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ------------------------ Gothic + Japanese Theme Styling ------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500&family=Cinzel:wght@500&display=swap');

    html, body, .stApp {
        background-image: url('https://images.unsplash.com/photo-1600051857820-d3f93e4f3bd4?auto=format&fit=crop&w=1350&q=80');
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        font-family: 'Noto Sans JP', sans-serif;
        color: #e0e0e0;
        text-shadow: 1px 1px 2px #000;
    }

    .main-block {
        background: rgba(0, 0, 0, 0.7);
        padding: 30px;
        border-radius: 12px;
        backdrop-filter: blur(8px);
        animation: fadeIn 1.2s ease-in-out;
    }

    h1, h2, h3, h4 {
        font-family: 'Cinzel', serif;
        color: #dcd6f7;
        text-shadow: 2px 2px 4px #000;
    }

    .stButton>button {
        background-color: #2e1a47;
        color: #fff;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #6c5b7b;
        transform: scale(1.05);
    }

    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.2);
    }
    ::-webkit-scrollbar-thumb {
        background: #6c5b7b;
        border-radius: 10px;
    }

    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------ Title Block ------------------------
st.markdown("<div class='main-block' style='text-align: center;'>", unsafe_allow_html=True)
st.markdown("<h1>🖤 MoodFlix</h1>", unsafe_allow_html=True)
st.markdown("<h3>感情に合わせてアニメを探す - Discover anime based on your emotions</h3>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------ Sidebar Filters ------------------------
st.sidebar.header("🔍 Filters")

all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
selected_emotions = st.sidebar.multiselect("🎯 Select how you feel today", all_emotions)

all_genres = sorted({genre for sublist in df["genres"] for genre in sublist})
selected_genre = st.sidebar.selectbox("📚 Choose Genre", ["Any"] + all_genres)

search_query = st.sidebar.text_input("🔎 Search Anime by Name")

# ------------------------ Recommendations ------------------------
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
                st.markdown(f"<h4>{row['title']}</h4>", unsafe_allow_html=True)
                st.write(f"⭐ {row['score']}")
                st.write(f"🎭 {', '.join(row['emotion_tags'])}")
                st.write(f"📚 {', '.join(row['genres'])}")

                # Favorite toggle
                is_fav = row['title'] in st.session_state.favorites
                fav_toggle = st.checkbox("❤️ Favorite", value=is_fav, key=f"fav_toggle_{row['title']}_{i}")
                if fav_toggle and not is_fav:
                    st.session_state.favorites.append(row['title'])
                    st.toast(f"✅ Added '{row['title']}' to favorites")
                elif not fav_toggle and is_fav:
                    st.session_state.favorites.remove(row['title'])
                    st.toast(f"❎ Removed '{row['title']}' from favorites")

                # View Details Expander
                with st.expander("🔍 View Details"):
                    st.markdown(f"**Synopsis:** {row.get('synopsis', 'No synopsis available.')}")
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
            st.markdown(f"""
            <div style='background: rgba(40, 40, 40, 0.8); padding: 10px; margin: 10px 0; border-radius: 8px;'>
                <h4 style='margin-bottom: 5px;'>{row['title']}</h4>
                <p>⭐ {row['score']}<br>🎭 {', '.join(row['emotion_tags'])}<br>📚 {', '.join(row['genres'])}</p>
            </div>
            """, unsafe_allow_html=True)

# ------------------------ Footer ------------------------
st.markdown("""
<hr style="border-top: 1px solid #999;">
<div style='text-align: center; font-size: 14px; opacity: 0.7;'>
    Made with 🖤 by Kishore | 感情に響くアニメ体験
</div>
""", unsafe_allow_html=True)
