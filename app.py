import streamlit as st
import pandas as pd
import ast

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    return df

df = load_data()

# UI Title
st.title("🎭 Anime Recommendation Engine Based on Emotions")

# Emotion & Genre Selections
all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
selected_emotions = st.multiselect("Select Emotion(s)", all_emotions)

all_genres = sorted({g for tags in df["genres"] for g in tags})
selected_genres = st.multiselect("Select Genre(s)", all_genres)

match_all = st.checkbox("Match all selected emotions", value=False)
top_n = st.slider("Number of recommendations", 1, 20, 5)

# Recommend Logic
def recommend_anime(emotions=[], genres=[], top_n=10, match_all=False):
    df_filtered = df.copy()

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

    df_filtered = df_filtered.sort_values(by="score", ascending=False)
    return df_filtered.head(top_n)

# Trigger button only once
if st.button("🎬 Recommend"):
    if selected_emotions:
        results = recommend_anime(selected_emotions, selected_genres, top_n, match_all)

        if not results.empty:
            for _, row in results.iterrows():
                st.markdown(f"### {row['title']} ({row['score']})")
                st.image(row['image_url'], width=200)
                st.write(f"**Genres:** {', '.join(row['genres'])}")
                st.write(f"**Emotions:** {', '.join(row['emotion_tags'])}")
                st.write(row['synopsis'])

                if pd.notnull(row['trailer_url']):
                    st.video(row['trailer_url'])
                if pd.notnull(row['watch_link']):
                    st.markdown(f"[🔗 Watch on MyAnimeList]({row['watch_link']})")

                st.markdown("---")
        else:
            st.warning("No anime found for the selected filters.")
    else:
        st.error("⚠️ Please select at least one emotion.")
