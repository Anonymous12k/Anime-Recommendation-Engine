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

if "view_detail" not in st.session_state:
    st.session_state.view_detail = None

# ------------------------ Sidebar Navigation ------------------------
page = st.sidebar.radio("Navigate", ["Home", "Favorites"])

# ------------------------ View Detail Modal ------------------------
def show_detail(anime):
    with st.container():
        st.markdown("---")
        st.subheader(f"📘 {anime['title']}")
        st.image(anime["image_url"], width=300)
        st.write(f"**Genre:** {', '.join(anime['genres'])}")
        st.write(f"**Score:** {anime['score']}")
        st.write(f"**Synopsis:** {anime['synopsis']}")

        # Watch Now Button (Muse Asia YouTube redirect)
        search_query = f"https://www.youtube.com/results?search_query={anime['title'].replace(' ', '+')}+Muse+Asia"
        st.markdown(f"[▶️ Watch Now on YouTube]({search_query})", unsafe_allow_html=True)
        st.markdown("---")

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

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("❤️ Favorite", key=f"fav_{row['title']}"):
                        if row['title'] not in [a['title'] for a in st.session_state.favorites]:
                            st.session_state.favorites.append(row)

                with col2:
                    if st.button("ℹ️ View Details", key=f"view_{row['title']}"):
                        st.session_state.view_detail = row
                        st.experimental_rerun()

        if st.session_state.view_detail:
            show_detail(st.session_state.view_detail)
            st.session_state.view_detail = None

# ------------------------ Favorites Page ------------------------
elif page == "Favorites":
    st.header("💖 Your Favorite Anime")

    if not st.session_state.favorites:
        st.info("You haven't added any favorites yet.")
    else:
        fav_cols = st.columns(3)
        for i, row in enumerate(st.session_state.favorites):
            with fav_cols[i % 3]:
                st.image(row["image_url"], use_container_width=True)
                st.markdown(f"### {row['title']}")
                st.markdown(f"**Genre:** {', '.join(row['genres'][:2])}")
                st.markdown(f"**Score:** {row['score']}")

                search_query = f"https://www.youtube.com/results?search_query={row['title'].replace(' ', '+')}+Muse+Asia"
                st.markdown(f"[▶️ Watch Now on YouTube]({search_query})", unsafe_allow_html=True)

                if st.button("ℹ️ View Details", key=f"view_fav_{row['title']}"):
                    st.session_state.view_detail = row
                    st.experimental_rerun()

        if st.session_state.view_detail:
            show_detail(st.session_state.view_detail)
            st.session_state.view_detail = None
