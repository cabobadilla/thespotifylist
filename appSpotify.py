import streamlit as st
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configuración de las APIs
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configuración de Spotify
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = "https://thespotifylist.streamlit.app/"

scope = "playlist-modify-public"

# Autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))

# Configuración de la página
st.title("🎵 Generador de Playlists por Estado de Ánimo 🎶")

# Selección del estado de ánimo y género musical
st.header("Configura tu playlist")

mood = st.selectbox(
    "Estado de ánimo a lograr:",
    ["Feliz", "Motivado", "Concentrado", "Meditación"]
)

genre = st.selectbox(
    "Tipo de género musical a considerar:",
    ["Rock", "Rock Progresivo", "Rock Alternativo", "Pop 80s", "Pop 90s"]
)

if st.button("Crear una Playlist"):
    # Generar lista de canciones usando ChatGPT
    prompt = (
        f"Genera una lista de 30 canciones que sean apropiadas para lograr un estado de ánimo '{mood}' "
        f"con música del género '{genre}'. Devuelve los resultados como una lista en formato: "
        f"- [Grupo] - [Canción] (Año de la canción)."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente que genera listas de canciones basadas en estados de ánimo y géneros musicales."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        # Procesar la respuesta de OpenAI
        songs_text = response['choices'][0]['message']['content'].strip()
        st.subheader("🎧 Tu Playlist Generada:")
        st.markdown(songs_text)

        # Preguntar si se desea crear la playlist en Spotify
        if st.button("Crear en Spotify"):
            try:
                # Crear la playlist en Spotify
                user_id = sp.current_user()["id"]
                playlist = sp.user_playlist_create(
                    user=user_id,
                    name=f"Playlist {mood} 🎧",
                    public=True,
                    description=f"Lista generada para estado de ánimo {mood} y género {genre}."
                )

                # Extraer los títulos de las canciones
                tracks = [line.split("-")[1].strip().split("(")[0] for line in songs_text.split("\n") if "-" in line]
                results = sp.search(q=tracks[0], type="track", limit=1)
                track_uris = [item["uri"] for track in results["tracks"]["items"]]

                # Agregar canciones a la playlist
                sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
                st.success(f"¡Playlist creada exitosamente en Spotify! [Abrir en Spotify]({playlist['external_urls']['spotify']})")

            except Exception as e:
                st.error(f"Error al crear la playlist en Spotify: {e}")

    except Exception as e:
        st.error(f"Hubo un error al generar la playlist: {e}")
