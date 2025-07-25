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

# ------------------------ UI Styling (Japanese Anime Theme) ------------------------
st.set_page_config(page_title="Anime Recommender", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700&display=swap');

    html, body, .stApp {
        background-color: #1a1a2e;
        color: #f5f5f5;
        font-family: 'Noto Sans JP', sans-serif;
        animation: fadeIn 1s ease-in;
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
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------ Title ------------------------
st.title("🌸 アニメ感情レコメンダー (Anime Emotion Recommender)")
st.write("感情に基づいてアニメを探しましょう！ (Find anime based on how you feel!)")

# ------------------------ Sidebar Filters ------------------------
st.sidebar.header("🔍 フィルター (Filters)")

all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
selected_emotions = st.sidebar.multiselect("🎯 感情を選択 (Choose Emotions)", all_emotions)

all_genres = sorted({genre for sublist in df["genres"] for genre in sublist})
selected_genre = st.sidebar.selectbox("📚 ジャンルを選択 (Choose Genre)", ["Any"] + all_genres)

min_score = st.sidebar.slider("⭐ 最低スコア (Minimum Score)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)

# ------------------------ Recommendation Logic ------------------------
if st.sidebar.button("🎬 レコメンド (Recommend)"):
    results = df.copy()

    if selected_emotions:
        results = results[results["emotion_tags"].apply(lambda tags: any(em in tags for em in selected_emotions))]

    if selected_genre != "Any":
        results = results[results["genres"].apply(lambda genres: selected_genre in genres)]

    results = results[results["score"] >= min_score]
    results = results.sort_values(by="score", ascending=False).head(45)

    if results.empty:
        st.warning("😢 該当するアニメが見つかりませんでした (No matching anime found.)")
    else:
        st.markdown("## 🎥 レコメンデーション (Recommendations)")
        cols = st.columns(5)

        for idx, (i, row) in enumerate(results.iterrows()):
            with cols[idx % 5]:
                st.image(row.get("image_url", ""), width=150)
                st.markdown(f"**{row['title']}**")
                st.write(f"⭐ {row['score']}")
                st.write(f"🎭 {', '.join(row['emotion_tags'])}")
                st.write(f"📚 {', '.join(row['genres'])}")

                if row['title'] in st.session_state.favorites:
                    if st.button("❌ お気に入り削除 (Remove Favorite)", key=f"unfav_{row['title']}_{i}"):
                        st.session_state.favorites.remove(row['title'])
                        st.success(f"❎ '{row['title']}' をお気に入りから削除しました (Removed from favorites)")
                else:
                    if st.button("❤️ お気に入り (Favorite)", key=f"fav_{row['title']}_{i}"):
                        st.session_state.favorites.append(row['title'])
                        st.success(f"✅ '{row['title']}' をお気に入りに追加しました (Added to favorites)")

                if st.button("🔍 詳細を見る (View Details)", key=f"details_{row['title']}_{i}"):
                    st.markdown(f"### 📖 {row['title']}")
                    st.write(f"**あらすじ (Synopsis)**: {row.get('synopsis', 'No synopsis available.')}")
                    trailer_url = row.get("trailer_url", None)
                    if trailer_url:
                        st.video(trailer_url)
                    else:
                        st.write("🎞️ トレーラーは利用できません (Trailer not available).")

                    watch_url = row.get("watch_url", None)
                    if watch_url:
                        st.markdown(f"[▶️ 今すぐ見る (Watch Now)]({watch_url})")
                    else:
                        st.markdown(f"[🔗 ストリーミングを探す (Find Streaming)](https://anilist.co/search/anime?search={row['title'].replace(' ', '%20')})")

                st.markdown("---")

# ------------------------ Favorites Section ------------------------
if st.sidebar.button("❤️ お気に入りを見る (View Favorites)"):
    st.markdown("## ⭐ お気に入りのアニメ (Your Favorite Anime)")
    fav_df = df[df['title'].isin(st.session_state.favorites)]

    if fav_df.empty:
        st.info("まだお気に入りはありません (No favorites selected yet).")
    else:
        for i, row in fav_df.iterrows():
            st.markdown(f"**{row['title']}** - ⭐ {row['score']} - 🎭 {', '.join(row['emotion_tags'])}")
