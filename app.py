import streamlit as st
import pandas as pd
import ast

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    return df

df = load_data()

# Initialize session state for favourites
if "favourites" not in st.session_state:
    st.session_state.favourites = []

# Title
st.title("🎭 Anime Recommendation Engine Based on Emotions")
st.write("Select your mood and discover anime tailored to your emotions and preferences.")

# Emotion Selection
all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
selected_emotion = st.selectbox("🎯 Choose an Emotion", all_emotions)

# Genre Selection
all_genres = sorted({g for tags in df["genres"] for g in tags})
selected_genres = st.multiselect("🎞️ Select Genre(s)", all_genres)

# Number of Recommendations
top_n = st.slider("📊 Number of Recommendations", 1, 20, 5)

# Recommend Button
if st.button("🎬 Recommend"):
    filtered_df = df.copy()

    # Filter by emotion
    filtered_df = filtered_df[filtered_df["emotion_tags"].apply(lambda tags: selected_emotion in tags)]

    # Filter by genre
    if selected_genres:
        filtered_df = filtered_df[filtered_df["genres"].apply(
            lambda g_list: any(g in g_list for g in selected_genres)
        )]

    # Sort by score
    filtered_df = filtered_df.sort_values(by="score", ascending=False).head(top_n)

    # Show Results
    if not filtered_df.empty:
        st.subheader("🔍 Recommended Anime")
        for _, row in filtered_df.iterrows():
            st.markdown(f"### {row['title']} ({row['score']})")
            st.image(row["image_url"], width=200)
            st.write(f"📌 **Genres:** {', '.join(row['genres'])}")
            st.write(f"🎭 **Emotions:** {', '.join(row['emotion_tags'])}")
            st.write(row['synopsis'])

            if pd.notnull(row['trailer_url']):
                st.video(row['trailer_url'])

            if pd.notnull(row['watch_link']):
                st.markdown(f"[🔗 Watch Now]({row['watch_link']})")

            if st.button(f"❤️ Save to Favourites", key=row["title"]):
                if row["title"] not in st.session_state.favourites:
                    st.session_state.favourites.append(row["title"])
                    st.success(f"'{row['title']}' added to favourites!")
            st.markdown("---")
    else:
        st.warning("No anime found matching your filters.")

# Show Favourites
st.subheader("⭐ Your Favourite Anime")
if st.session_state.favourites:
    for title in st.session_state.favourites:
        st.write(f"🔖 {title}")
    if st.button("🗑️ Clear Favourites"):
        st.session_state.favourites = []
        st.success("Favourites cleared!")
else:
    st.info("You haven't added any favourites yet.")
