import streamlit as st
import openai
import requests
from urllib.parse import urlencode
from datetime import datetime

# Configuración de las APIs
openai.api_key = st.secrets["OPENAI_API_KEY"]
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = st.secrets["SPOTIFY_REDIRECT_URI"]

scope = "playlist-modify-public user-read-private"

# Estado de la sesión
if "spotify_access_token" not in st.session_state:
    st.session_state.spotify_access_token = None

if "spotify_refresh_token" not in st.session_state:
    st.session_state.spotify_refresh_token = None

# Funciones para la autenticación
def get_auth_url():
    """Genera la URL de autenticación de Spotify."""
    params = {
        "response_type": "code",
        "client_id": SPOTIFY_CLIENT_ID,
        "scope": scope,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
    }
    return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

def get_access_token(code):
    """Intercambia el código de autorización por un token de acceso."""
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al obtener el token: {response.json()}")
        return None

def refresh_access_token(refresh_token):
    """Refresca el token de acceso usando el refresh token."""
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al refrescar el token: {response.json()}")
        return None

# Pantalla principal
st.title("🎵 Generador y Creador de Playlists en tu Cuenta de Spotify 🎶")

if not st.session_state.spotify_access_token:
    # Mostrar URL para autenticación
    st.markdown("### Paso 1: Autenticación en Spotify")
    auth_url = get_auth_url()
    st.markdown(f"[Haz clic aquí para autenticarte en Spotify]({auth_url})")
    st.markdown("### Paso 2: Pega el código de autorización aquí:")
    code = st.text_input("Código de autorización:")

    if st.button("Autenticar"):
        if code:
            token_info = get_access_token(code)
            if token_info:
                st.session_state.spotify_access_token = token_info["access_token"]
                st.session_state.spotify_refresh_token = token_info.get("refresh_token")
                st.success("¡Autenticación exitosa! Ahora puedes crear playlists.")
        else:
            st.error("El código de autorización no puede estar vacío.")
else:
    # Configurar estado de ánimo y tipo de música
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
                headers = {
                    "Authorization": f"Bearer {st.session_state.spotify_access_token}",
                    "Content-Type": "application/json"
                }
                user_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
                if user_response.status_code == 200:
                    user_id = user_response.json()["id"]
                    playlist_response = requests.post(
                        f"https://api.spotify.com/v1/users/{user_id}/playlists",
                        headers=headers,
                        json={
                            "name": playlist_name,
                            "description": f"Playlist generada para estado de ánimo '{mood}' y género '{genre}'.",
                            "public": True
                        }
                    )
                    if playlist_response.status_code == 201:
                        playlist = playlist_response.json()
                        st.success(f"¡Playlist creada exitosamente! [Abrir en Spotify]({playlist['external_urls']['spotify']})")
                    else:
                        st.error(f"Error al crear la playlist: {playlist_response.json()}")
                else:
                    st.error(f"Error al obtener la información del usuario: {user_response.json()}")

            except Exception as e:
                st.error(f"Error al crear la playlist en Spotify: {e}")

        except Exception as e:
            st.error(f"Hubo un error al generar la playlist: {e}")
