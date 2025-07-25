import streamlit as st
import pandas as pd
import ast

# ✅ Load and cache data
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ✅ Unique options
all_emotions = sorted({e for tags in df["emotion_tags"] for e in tags})
all_genres = sorted({g for genre in df["genres"] for g in genre})
all_titles = df["title"].dropna().unique()

# 🎯 UI layout
st.title("🎭 Anime Emotion Recommender")

with st.sidebar:
    st.header("🔍 Filter Options")

    selected_emotions = st.multiselect("😊 Select Emotion(s)", all_emotions)
    selected_genres = st.multiselect("🎬 Select Genre(s) (optional)", all_genres)
    search_title = st.text_input("🔎 Search by Anime Name")
    top_n = st.slider("📈 Number of Results", 1, 20, 5)
    match_all = st.checkbox("✅ Match all selected emotions", value=False)

# 📌 Filtering function
def filter_anime(df, emotions, genres, name_query, match_all):
    filtered = df.copy()

    if emotions:
        if match_all:
            filtered = filtered[filtered["emotion_tags"].apply(lambda tags: all(e in tags for e in emotions))]
        else:
            filtered = filtered[filtered["emotion_tags"].apply(lambda tags: any(e in tags for e in emotions))]

    if genres:
        filtered = filtered[filtered["genres"].apply(lambda g_list: any(g in g_list for g in genres))]

    if name_query:
        filtered = filtered[filtered["title"].str.contains(name_query, case=False, na=False)]

    return filtered.sort_values(by="score", ascending=False)

# ✅ Show recommendations
if st.button("🎬 Recommend Anime"):
    filtered_df = filter_anime(df, selected_emotions, selected_genres, search_title, match_all)

    if filtered_df.empty:
        st.warning("No anime found for the selected filters.")
    else:
        favorites = st.session_state.setdefault("favorites", [])

        for _, row in filtered_df.head(top_n).iterrows():
            st.markdown(f"### {row['title']} (⭐ {row['score']})")
            st.image(row.get("image_url", ""), width=250)
            st.write(f"📌 **Genres**: {', '.join(row['genres'])}")
            st.write(f"🎭 **Emotions**: {', '.join(row['emotion_tags'])}")

            if st.button(f"❤️ Save to Favorites", key=row["title"]):
                if row["title"] not in favorites:
                    favorites.append(row["title"])
                    st.success(f"'{row['title']}' added to favorites!")

            st.markdown("---")

# ❤️ Show Favorites
if st.sidebar.button("📁 Show Favorites"):
    favorites = st.session_state.get("favorites", [])
    st.sidebar.markdown("### ❤️ Your Favorite Anime")
    if favorites:
        for fav in favorites:
            st.sidebar.markdown(f"- {fav}")
    else:
        st.sidebar.info("No favorites saved yet.")
