import streamlit as st
import pandas as pd
import ast
import random

st.set_page_config(page_title="MoodFlix Anime Recommender", layout="wide")
st.title("🎭 MoodFlix Anime Recommender")
st.markdown("_Find anime based on how you feel!_")

# ------------------------ Load Data ------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("anime_with_extended_emotions.csv")
    df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["emotion_tags"] = df["emotion_tags"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df

data = load_data()

# ------------------------ Session State ------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "selected_anime" not in st.session_state:
    st.session_state.selected_anime = None

# ------------------------ Show Anime Details ------------------------
def show_detail(anime):
    st.markdown("---")
    st.subheader(f"📘 {anime['title']}")
    st.image(anime["image_url"], width=300)
    st.write(f"**Genre:** {', '.join(anime['genres'])}")
    st.write(f"**Score:** {anime['score']}")
    st.write(f"**Synopsis:** {anime['synopsis']}")
    
    trailer_url = anime.get("trailer_url")
    if trailer_url:
        st.markdown(f"[🎬 Watch Trailer]({trailer_url})", unsafe_allow_html=True)

    # Watch Now on YouTube via Muse Asia or search query
    search_query = f"https://www.youtube.com/results?search_query={anime['title'].replace(' ', '+')}+Muse+Asia"
    st.markdown(f"[▶️ Watch Now on YouTube]({search_query})", unsafe_allow_html=True)
    st.markdown("---")

# ------------------------ Sidebar Navigation ------------------------
page = st.sidebar.radio("Navigate", ["Home", "Favorites"])

# ------------------------ Home Page ------------------------
if page == "Home":
    selected_emotion = st.selectbox("Select your mood:", ["Any"] + sorted({tag for tags in data.emotion_tags for tag in tags}))

    if selected_emotion == "Any":
        filtered = data.sample(12)
    else:
        filtered = data[data["emotion_tags"].apply(lambda x: selected_emotion in x)]

    if filtered.empty:
        st.warning("😢 No anime found for that emotion.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                st.image(row["image_url"], use_container_width=True)
                st.markdown(f"### {row['title']}")
                st.markdown(f"**Genre:** {', '.join(row['genres'][:2])}")
                st.markdown(f"**Score:** {row['score']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❤️ Favorite", key=f"fav_{i}"):
                        if all(row["title"] != fav["title"] for fav in st.session_state.favorites):
                            st.session_state.favorites.append(row.to_dict())

                with col2:
                    if st.button("ℹ️ View Details", key=f"view_{i}"):
                        st.session_state.selected_anime = row.to_dict()

    if st.session_state.selected_anime:
        show_detail(st.session_state.selected_anime)

# ------------------------ Favorites Page ------------------------
elif page == "Favorites":
    st.header("💖 Your Favorite Anime")

    if not st.session_state.favorites:
        st.info("You haven't added any favorites yet.")
    else:
        fav_cols = st.columns(3)
        for i, fav in enumerate(st.session_state.favorites):
            with fav_cols[i % 3]:
                st.image(fav["image_url"], use_container_width=True)
                st.markdown(f"### {fav['title']}")
                st.markdown(f"**Genre:** {', '.join(fav['genres'][:2])}")
                st.markdown(f"**Score:** {fav['score']}")

                col1, col2 = st.columns(2)
                with col1:
                    search_query = f"https://www.youtube.com/results?search_query={fav['title'].replace(' ', '+')}+Muse+Asia"
                    st.markdown(f"[▶️ Watch Now]({search_query})", unsafe_allow_html=True)

                with col2:
                    if st.button("ℹ️ View Details", key=f"fav_detail_{i}"):
                        st.session_state.selected_anime = fav

    if st.session_state.selected_anime:
        show_detail(st.session_state.selected_anime)
