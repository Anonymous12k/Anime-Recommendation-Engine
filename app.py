import streamlit as st
import pandas as pd
import ast
import os

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    return df

df = load_data()

# Unique emotions
unique_emotions = sorted({e.strip().capitalize() for tags in df["emotion_tags"] for e in tags})

# Sidebar Favorites
st.sidebar.header("⭐ Your Favorites")
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

for fav in st.session_state["favorites"]:
    st.sidebar.write(f"• {fav}")

# Main Title
st.title("🎭 Anime Recommendation Engine Based on Emotions")
st.markdown("Select your emotion and genre to discover matching anime!")

# Emotion & Genre Selection
selected_emotions = st.multiselect("🎯 Choose Emotion(s)", unique_emotions)
all_genres = sorted({g for tags in df["genres"] for g in tags})
selected_genres = st.multiselect("📚 Choose Genre(s)", all_genres)

match_all = st.checkbox("🔍 Match all selected emotions", value=False)
min_score = st.slider("⭐ Minimum Rating", 0.0, 10.0, 7.0, 0.1)
top_n = st.slider("🎯 Number of Recommendations", 1, 20, 5)

# Filter Function
def recommend_anime(emotions=[], genres=[], top_n=10, match_all=False, min_score=0.0):
    df_filtered = df.copy()
    df_filtered = df_filtered[df_filtered["score"] >= min_score]

    if genres:
        df_filtered = df_filtered[df_filtered["genres"].apply(
            lambda g_list: any(g.lower() in [x.lower() for x in g_list] for g in genres)
        )]

    if emotions:
        if match_all:
            df_filtered = df_filtered[df_filtered["emotion_tags"].apply(
                lambda tags: all(e.lower() in [t.lower() for t in tags] for e in emotions)
            )]
        else:
            df_filtered = df_filtered[df_filtered["emotion_tags"].apply(
                lambda tags: any(e.lower() in [t.lower() for t in tags] for e in emotions)
            )]

    return df_filtered.sort_values(by="score", ascending=False).head(top_n)

# Recommend Button
if st.button("🎬 Recommend Anime"):
    if selected_emotions:
        results = recommend_anime(selected_emotions, selected_genres, top_n, match_all, min_score)
        if not results.empty:
            for _, row in results.iterrows():
                st.markdown(f"### {row['title']}  ⭐ {row['score']}")
                st.image(row['image_url'], width=250)
                st.write(f"📚 **Genres:** {', '.join(row['genres'])}")
                st.write(f"🎭 **Emotions:** {', '.join(row['emotion_tags'])}")
                st.write(f"📝 {row['synopsis'][:300]}...")

                if pd.notnull(row['trailer_url']):
                    st.video(row['trailer_url'])

                if pd.notnull(row['watch_link']):
                    st.markdown(f"[🔗 Watch on MyAnimeList]({row['watch_link']})")

                if st.button(f"❤️ Add to Favorites: {row['title']}", key=row['title']):
                    if row['title'] not in st.session_state["favorites"]:
                        st.session_state["favorites"].append(row['title'])

                st.markdown("---")
        else:
            st.warning("😕 No anime found matching your selection.")
    else:
        st.error("⚠️ Please select at least one emotion.")
