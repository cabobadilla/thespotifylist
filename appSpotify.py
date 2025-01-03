import streamlit as st
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import time

# Configuración de las APIs
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configuración de Spotify
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = st.secrets["SPOTIFY_REDIRECT_URI"]

scope = "playlist-modify-public"

# Estado de la sesión
if "spotify_connected" not in st.session_state:
    st.session_state.spotify_connected = False

if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# Pantalla 1: Conexión con Spotify
def connect_to_spotify():
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            open_browser=True
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        user_info = sp.current_user()
        st.session_state.spotify_connected = True
        st.session_state.user_info = user_info
    except Exception as e:
        st.error(f"Error al conectar con Spotify: {e}")
        time.sleep(10)  # Esperar 10 segundos en caso de error
        st.stop()

# Pantalla 2: Generar y Crear Playlist
def create_playlist():
    st.title("🎵 Generador y Creador de Playlists por Estado de Ánimo 🎶")

    # Mostrar datos del usuario conectado
    st.subheader("Información del Usuario:")
    user_info = st.session_state.user_info
    st.write(f"**Nombre del Usuario:** {user_info.get('display_name', 'N/A')}")
    st.write(f"**ID de Usuario:** {user_info.get('id', 'N/A')}")

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

    if st.button("Generar y Crear Playlist en Spotify"):
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

            # Mostrar las canciones generadas
            st.subheader("🎧 Tu Playlist Generada:")
            st.markdown(songs_text)

            # Crear la playlist en Spotify
            try:
                current_date = datetime.now().strftime("%d%m%y")
                playlist_name = f"{current_date} - {mood} - {genre}"

                # Crear la playlist
                auth_manager = SpotifyOAuth(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=SPOTIFY_REDIRECT_URI,
                    scope=scope,
                    open_browser=False
                )
                sp = spotipy.Spotify(auth_manager=auth_manager)
                user_id = st.session_state.user_info["id"]
                playlist = sp.user_playlist_create(
                    user=user_id,
                    name=playlist_name,
                    public=True,
                    description=f"Playlist generada para estado de ánimo '{mood}' y género '{genre}'."
                )

                # Buscar canciones y agregar a la playlist
                tracks = [line.split("-")[1].strip().split("(")[0] for line in songs_text.split("\n") if "-" in line]
                track_uris = []
                for track in tracks[:20]:  # Limitar a las primeras 20 canciones
                    results = sp.search(q=track, type="track", limit=1)
                    if results["tracks"]["items"]:
                        track_uris.append(results["tracks"]["items"][0]["uri"])

                if track_uris:
                    sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
                    st.success(f"¡Playlist creada exitosamente! [Abrir en Spotify]({playlist['external_urls']['spotify']})")
                else:
                    st.warning("No se encontraron canciones en Spotify para agregar a la playlist.")

            except Exception as e:
                st.error(f"Error al crear la playlist en Spotify: {e}")

        except Exception as e:
            st.error(f"Hubo un error al generar la playlist: {e}")

# Lógica de la App
if not st.session_state.spotify_connected:
    st.title("🎵 Conexión con Spotify")
    st.markdown("Haz clic en el botón para autenticarte con Spotify.")
    if st.button("Conectar con Spotify"):
        connect_to_spotify()
else:
    create_playlist()
