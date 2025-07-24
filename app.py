import streamlit as st
import pandas as pd
import ast

# Load data and fix if needed
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    return df

df = load_data()

# Initialize session state for favorites
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

# Title
st.title("🎭 Anime Emotion Recommender")
st.write("Select an emotion to discover anime that matches your mood.")

# Extract all unique emotions
all_emotions = sorted({emotion for row in df["emotion_tags"] for emotion in row})
selected = st.selectbox("🎯 Choose an Emotion", all_emotions)

# Recommend button
if st.button("🎬 Recommend"):
    filtered = df[df["emotion_tags"].apply(lambda tags: selected in tags)]
    top_anime = filtered.sort_values(by="score", ascending=False).head(10)

    if top_anime.empty:
        st.warning("No anime found for the selected emotion.")
    else:
        for _, row in top_anime.iterrows():
            st.subheader(row['title'])
            st.write(f"⭐ Score: {row['score']}")
            st.write(f"📌 Genres: {', '.join(row['genres'])}")
            st.write(f"🎭 Emotion Tags: {', '.join(row['emotion_tags'])}")
            if pd.notnull(row.get("watch_url", "")):
                st.markdown(f"[🔗 Watch Here]({row['watch_url']})")
            if pd.notnull(row.get("image_url", "")):
                st.image(row['image_url'], use_column_width=True)

            # Add to favorites
            if st.button(f"❤️ Add to Favorites: {row['title']}"):
                if row['title'] not in st.session_state["favorites"]:
                    st.session_state["favorites"].append(row['title'])
                    st.success(f"Added {row['title']} to favorites!")

            st.markdown("---")

# Show favorites section
st.sidebar.header("📚 Your Favorites")
if st.session_state["favorites"]:
    for fav in st.session_state["favorites"]:
        st.sidebar.write(f"✅ {fav}")
else:
    st.sidebar.write("No favorites yet. Start adding!")
