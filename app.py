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

# ------------------------ UI Styling ------------------------
st.set_page_config(page_title="Anime Recommender", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #0e0e10;
        color: white;
    }
    .stApp {
        background-color: #111;
        color: #eee;
    }
    h1, h2, h3, h4 {
        color: #f92672;
    }
    .stButton>button {
        background-color: #2c2f33;
        color: #ffffff;
        border-radius: 8px;
        border: 1px solid #f92672;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------ Title ------------------------
st.title("🦇 Anime Emotion Recommender (Goth UI)")
st.write("Find anime based on how you feel. Pick your emotion and explore!")

# ------------------------ Sidebar Filters ------------------------
st.sidebar.header("🔍 Filters")

# 🎭 Emotion Filter
all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
selected_emotions = st.sidebar.multiselect("🎯 Choose Emotions", all_emotions)

# 🎬 Genre Filter
all_genres = sorted({genre for sublist in df["genres"] for genre in sublist})
selected_genre = st.sidebar.selectbox("📚 Choose Genre (optional)", ["Any"] + all_genres)

# ⭐ Score Filter
min_score = st.sidebar.slider("⭐ Minimum Score", min_value=0.0, max_value=10.0, value=7.0, step=0.1)

# ------------------------ Recommend Button ------------------------
if st.sidebar.button("🎬 Recommend"):
    results = df.copy()

    # Filter by emotion
    if selected_emotions:
        results = results[results["emotion_tags"].apply(lambda tags: any(em in tags for em in selected_emotions))]

    # Filter by genre
    if selected_genre != "Any":
        results = results[results["genres"].apply(lambda genres: selected_genre in genres)]

    # Filter by score
    results = results[results["score"] >= min_score]

    # Sort and limit
    results = results.sort_values(by="score", ascending=False).head(45)

    if results.empty:
        st.warning("😢 No matching anime found.")
    else:
        st.markdown("## 🎥 Recommendations")

        cols = st.columns(5)  # 5 anime per row

        for idx, (i, row) in enumerate(results.iterrows()):
            with cols[idx % 5]:
                st.image(row.get("image_url", ""), width=150)
                st.markdown(f"**{row['title']}**")
                st.write(f"⭐ {row['score']}")
                st.write(f"🎭 {', '.join(row['emotion_tags'])}")
                st.write(f"📚 {', '.join(row['genres'])}")
                
                # Unique button key using index
                if st.button("❤️ Favorite", key=f"{row['title']}_{i}"):
                    st.success(f"✅ Added '{row['title']}' to favorites!")

                st.markdown("---")
