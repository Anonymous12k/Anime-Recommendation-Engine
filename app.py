import streamlit as st
import pandas as pd
import urllib.parse
import ast
import random

# ---------------------- Config ----------------------
st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")

# ---------------------- Load Data ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_dataset.csv")  # Includes 'watch_url' and 'trailer_url'
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

df = load_data()

# ---------------------- Initialize State ----------------------
default_states = {
    "favorites": [],
    "page": "home",
    "selected_anime": None,
}
for key, val in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------- Style ----------------------
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        .anime-card {
            background-color: #1e1e2f;
            padding: 1rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 0 10px #8e44ad;
        }
        .anime-title {
            font-size: 1.2rem;
            color: #e91e63;
        }
        .detail-box {
            background-color: #2c2c3e;
            padding: 2rem;
            width: 80%;
            aspect-ratio: 4 / 3;
            border-radius: 0.5rem;
            margin: auto;
            box-shadow: 0 0 15px #9b59b6;
        }
        a button {
            margin-right: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar ----------------------
st.sidebar.header("🧠 Select Your Emotion")
emotion_options = ["Any"] + sorted(set(e for tags in df["emotion_tags"] for e in tags))
selected_emotion = st.sidebar.selectbox("Choose an emotion:", emotion_options)

if st.session_state.page != "favorites":
    if st.sidebar.button("⭐ View Favorites"):
        st.session_state.page = "favorites"
        st.experimental_rerun()

# ---------------------- Details Page ----------------------
if st.session_state.page == "details":
    anime = st.session_state.selected_anime
    st.markdown(f"<div class='detail-box'>", unsafe_allow_html=True)

    # Ensure proper type and fallback
    title = anime.get("title", "Unknown Title")
    genres = anime.get("genres", [])
    emotions = anime.get("emotion_tags", [])
    synopsis = anime.get("synopsis", "No synopsis available.")
    image_url = anime.get("image_url", "")

    st.markdown(f"### 🎬 {title}")
    st.markdown(f"**Genres:** {', '.join(genres)}")
    st.markdown(f"**Emotions:** {', '.join(emotions)}")
    st.markdown(f"**Synopsis:** {synopsis}")

    # Show Poster if valid
    if isinstance(image_url, str) and image_url.strip() != "":
        st.image(image_url, width=300)
    else:
        st.warning("No poster available.")

    # Trailer & Watch buttons
    buttons_html = ""
    trailer_url = anime.get("trailer_url", "")
    watch_url = anime.get("watch_url", "")

    if isinstance(trailer_url, str) and trailer_url.strip() != "":
        buttons_html += f"<a href='{trailer_url}' target='_blank'><button style='background-color:#8e44ad;color:white;padding:10px;border:none;border-radius:5px;'>🎞️ Watch Trailer</button></a>"
    if isinstance(watch_url, str) and watch_url.strip() != "":
        buttons_html += f"<a href='{watch_url}' target='_blank'><button style='background-color:#e91e63;color:white;padding:10px;border:none;border-radius:5px;'>▶️ Watch Anime</button></a>"

    st.markdown(buttons_html, unsafe_allow_html=True)

    # Favorites button
    if title in st.session_state.favorites:
        if st.button("❌ Remove from Favorites"):
            st.session_state.favorites.remove(title)
            st.experimental_rerun()
    else:
        if st.button("❤ Add to Favorites"):
            st.session_state.favorites.append(title)
            st.experimental_rerun()

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Favorites Page ----------------------
elif st.session_state.page == "favorites":
    st.subheader("⭐ Your Favorite Anime")
    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.experimental_rerun()

    fav_df = df[df["title"].isin(st.session_state.favorites)]
    if not fav_df.empty:
        fav_cols = st.columns(3)
        for i, (_, row) in enumerate(fav_df.iterrows()):
            with fav_cols[i % 3]:
                st.markdown(f"<div class='anime-card'>", unsafe_allow_html=True)
                st.markdown(f"**{row['title']}**")
                st.markdown(f"_Genres:_ {', '.join(row['genres'])}")
                if isinstance(row["image_url"], str) and row["image_url"].strip() != "":
                    st.image(row["image_url"], use_container_width=True)

                if st.button("📖 View Details", key=f"view_fav_{i}"):
                    st.session_state.selected_anime = row.to_dict()
                    st.session_state.page = "details"
                    st.experimental_rerun()

                if st.button("❌ Remove", key=f"remove_fav_{i}"):
                    st.session_state.favorites.remove(row["title"])
                    st.experimental_rerun()

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No favorites yet.")

# ---------------------- Home Page ----------------------
else:
    st.title("MoodFlix Anime Recommender")
    st.markdown("Find anime based on how you feel 🎭")

    # ---------- Search Bar ----------
    all_titles = df["title"].dropna().unique()
    search_query = st.selectbox("🔍 Search for an Anime (or use filters below):", [""] + list(all_titles))

    if search_query:
        selected_row = df[df["title"] == search_query].iloc[0].to_dict()
        mal_url = selected_row.get("watch_url", f"https://myanimelist.net/anime.php?q={urllib.parse.quote(search_query)}")
        st.markdown(f"🎯 Found **{search_query}**! [Open on MyAnimeList 🚀]({mal_url})", unsafe_allow_html=True)

    # ---------- Genre Filter ----------
    all_genres = sorted(set(g for genre_list in df["genres"] for g in genre_list))
    selected_genre = st.sidebar.selectbox("🎞️ Choose a Genre (Optional):", ["Any"] + all_genres)

    # ---------- Filter Data ----------
    filtered_df = df.copy()
    if selected_emotion.lower() != "any":
        filtered_df = filtered_df[filtered_df["emotion_tags"].apply(lambda tags: selected_emotion in tags)]
    if selected_genre.lower() != "any":
        filtered_df = filtered_df[filtered_df["genres"].apply(lambda genres: selected_genre in genres)]

    if filtered_df.empty:
        st.warning("😢 No anime found matching your filters.")
    else:
        sample_df = filtered_df.sample(n=min(9, len(filtered_df)))
        cols = st.columns(3)

        for i, (_, row) in enumerate(sample_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"<div class='anime-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='anime-title'>{row['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"_Genres:_ {', '.join(row['genres'])}")
                st.markdown(f"_Emotions:_ {', '.join(row['emotion_tags'])}")

                if isinstance(row["image_url"], str) and row["image_url"].strip():
                    st.image(row["image_url"], use_container_width=True)

                # Redirect to MAL (watch_url)
                watch_url = row.get("watch_url", "")
                if isinstance(watch_url, str) and watch_url.strip() != "":
                    st.markdown(
                        f"<a href='{watch_url}' target='_blank'><button style='background-color:#e91e63;color:white;padding:10px;border:none;border-radius:5px;width:100%;'>▶️ Watch on MAL</button></a>",
                        unsafe_allow_html=True
                    )

                if st.button("📖 View Details", key=f"view_{i}"):
                    st.session_state.selected_anime = row.to_dict()
                    st.session_state.page = "details"
                    st.experimental_rerun()

                st.markdown("</div>", unsafe_allow_html=True)

