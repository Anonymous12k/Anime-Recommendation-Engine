import streamlit as st
import pandas as pd

# Load the dataset
df = pd.read_csv("anime_with_emotions.csv")

# Title and instructions
st.title("🎭 Anime Emotion Recommender")
st.write("Select an emotion to discover anime that matches your mood.")

# Emotion selection
emotions = ['joy', 'sadness', 'anger', 'love', 'fear', 'surprise']
selected = st.selectbox("Choose an emotion", emotions)

# Recommend button
if st.button("Recommend"):
    filtered = df[df['emotion_tags'].str.contains(selected, case=False, na=False)]
    top_anime = filtered.sort_values(by='score', ascending=False).head(10)

    # Display results
    for _, row in top_anime.iterrows():
        st.subheader(row['title'])
        st.write(f"⭐ Score: {row['score']}")
        st.write(f"📌 Genres: {row['genres']}")
        st.write(f"🎭 Emotion Tags: {row['emotion_tags']}")
        st.write(f"[🔗 Watch Here]({row['watch_url']})")
        st.image(row['image_url'])
        st.markdown("---")


