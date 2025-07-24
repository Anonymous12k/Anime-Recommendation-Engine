import streamlit as st
import pandas as pd
import ast

# Page config
st.set_page_config(page_title="Anime Emotion Recommender 🎭", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    return df

df = load_data()

# Initialize session state
if "favourites" not in st.session_state:
    st.session_state.favourites = []

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filter Your Search")
    all_emotions = sorted({e.lower() for tags in df["emotion_tags"] for e in tags})
    all_genres = sorted({g.lower() for tags in df["genres"] for g in tags})
    selected_emotion = st.selectbox("🎭 Choose Emotion", all_emotions)
    selected_genre = st.selectbox("🎬 Choose Genre (Optional)", ["All"] + all_genres)
    top_n = st.slider("📊 Number of Recommendations", 1, 20, 10)
    rating_threshold = st.slider("⭐ Minimum Rating", 0.0, 10.0, 7.0, 0.1)
    show_explanations = st.checkbox("💡 Show Why These Were Recommended", value=True)

st.title("🎭 Anime Recommendation Engine Based on Emotions")

# Recommendation Logic
if st.button("🎬 Recommend"):
    filtered_df = df.copy()

    filtered_df = filtered_df[filtered_df["emotion_tags"].apply(lambda tags: selected_emotion in [e.lower() for e in tags])]

    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df["genres"].apply(lambda genres: selected_genre in [g.lower() for g in genres])]

    filtered_df = filtered_df[filtered_df["score"] >= rating_threshold]
    filtered_df = filtered_df.sort_values(by="score", ascending=False).head(top_n)

    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            st.markdown(f"### 🎥 {row['title']}")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(row["image_url"], width=150)
            with col2:
                st.markdown(f"⭐ **Rating**: {row['score']} / 10")
                st.markdown(f"🎭 **Emotions**: {', '.join(row['emotion_tags'])}")
                st.markdown(f"📌 **Genres**: {', '.join(row['genres'])}")
                if pd.notnull(row.get("synopsis")):
                    st.write("📝 " + row["synopsis"][:300] + "...")
                if pd.notnull(row.get("trailer_url")):
                    st.video(row["trailer_url"])
                if pd.notnull(row.get("watch_url")):
                    st.markdown(f"[▶️ Watch Now]({row['watch_url']})")

                if show_explanations:
                    st.success(f"🎯 **Matched for '{selected_emotion}' emotion**")

                # Save to favourites button
                if st.button(f"❤️ Save to Favourites", key=row["title"]):
                    if row["title"] not in [anime["title"] for anime in st.session_state.favourites]:
                        st.session_state.favourites.append({
                            "title": row["title"],
                            "image_url": row["image_url"],
                            "score": row["score"],
                            "genres": row["genres"],
                            "emotion_tags": row["emotion_tags"],
                            "watch_url": row.get("watch_url", ""),
                            "trailer_url": row.get("trailer_url", "")
                        })
                        st.success("✅ Saved to favourites!")
                    else:
                        st.info("Already in favourites ❤️")

            st.markdown("---")
    else:
        st.warning("😞 No anime matched your filters. Try adjusting them.")

# View Favourites Section
st.markdown("## ⭐ Your Favourite Anime List")

if st.session_state.favourites:
    for fav in st.session_state.favourites:
        st.markdown(f"### 🎥 {fav['title']}")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(fav["image_url"], width=150)
        with col2:
            st.markdown(f"⭐ **Rating**: {fav['score']} / 10")
            st.markdown(f"🎭 **Emotions**: {', '.join(fav['emotion_tags'])}")
            st.markdown(f"📌 **Genres**: {', '.join(fav['genres'])}")
            if fav.get("trailer_url"):
                st.video(fav["trailer_url"])
            if fav.get("watch_url"):
                st.markdown(f"[▶️ Watch Now]({fav['watch_url']})")
        st.markdown("---")
else:
    st.info("📭 You haven't saved any favourites yet. Start exploring!")

