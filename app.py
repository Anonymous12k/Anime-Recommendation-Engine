import streamlit as st
import pandas as pd
import ast

# ✅ Load and parse data
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ✅ UI: Title and instructions
st.title("🎭 Anime Emotion Recommender")
st.write("Select an emotion to discover anime that matches your mood.")

# ✅ Extract unique emotions (cleaned)
all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})

# ✅ Select emotion from dropdown
if all_emotions:
    selected = st.selectbox("🎯 Choose an Emotion", all_emotions)
else:
    st.error("⚠️ No emotions found in dataset.")

# ✅ Recommend button
if st.button("🎬 Recommend") and all_emotions:
    results = df[df["emotion_tags"].apply(lambda tags: selected in tags)]
    results = results.sort_values(by="score", ascending=False).head(10)

    if results.empty:
        st.warning("No anime found with that emotion.")
    else:
        for _, row in results.iterrows():
            st.subheader(row["title"])
            st.write(f"⭐ Score: {row['score']}")
            st.write(f"📌 Genres: {', '.join(row['genres'])}")
            st.write(f"🎭 Emotions: {', '.join(row['emotion_tags'])}")
            if pd.notnull(row.get("image_url", "")):
                st.image(row["image_url"], width=300)
            st.markdown("---")
