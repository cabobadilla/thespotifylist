import streamlit as st
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

# Configuración de las APIs
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configuración de Spotify
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = st.secrets["SPOTIFY_REDIRECT_URI"]  # Configurable como un secreto

scope = "playlist-modify-public"

# Verificar conexión con Spotify
spotify_connection_status = ""
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=scope
    ))
    # Intentar obtener información del usuario para validar la conexión
    user_info = sp.current_user()
    spotify_connection_status = f"Conexión exitosa con Spotify. Usuario autenticado: {user_info['display_name']}"
except Exception as e:
    spotify_connection_status = f"Error en la conexión con Spotify: {e}"

# Mostrar estado de conexión con Spotify antes de proceder
st.title("🎵 Generador y Creador de Playlists por Estado de Ánimo 🎶")
st.markdown(f"**Estado de la conexión con Spotify:** {spotify_connection_status}")

# Detener la ejecución si no hay conexión con Spotify
if "Error" in spotify_connection_status:
    st.error("No se puede continuar sin conexión a Spotify. Verifica tus credenciales.")
    st.stop()

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
            # Nombre de la playlist
            current_date = datetime.now().strftime("%d%m%y")
            playlist_name = f"{current_date} - {mood} - {genre}"

            # Crear la playlist en Spotify
            user_id = sp.current_user()["id"]
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
