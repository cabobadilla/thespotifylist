import openai
import json
import streamlit as st
import requests
from urllib.parse import urlencode

# Estilo de Spotify (colores verde y negro)
st.markdown(
    '''
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        h1, h2, h3 {
            color: #1DB954;
            font-weight: bold;
            text-align: center;
        }
        .stButton>button {
            background-color: #1DB954;
            color: white;
            font-size: 16px;
            border-radius: 25px;
            padding: 10px 20px;
        }
        .stButton>button:hover {
            background-color: #1ED760;
        }
        .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div, .stMultiSelect>div>div>div {
            background-color: #2C2C2C;
            color: white;
            border: 1px solid #1DB954;
            border-radius: 10px;
        }
    </style>
    ''',
    unsafe_allow_html=True
)

# Spotify API Credentials
CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
REDIRECT_URI = st.secrets.get("SPOTIFY_REDIRECT_URI", "http://localhost:8501/callback")

# Scopes for Spotify API
SCOPES = "playlist-modify-private playlist-modify-public"

# Function to get authorization URL
def get_auth_url(client_id, redirect_uri, scopes):
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scopes,
    }
    return f"{auth_url}?{urlencode(params)}"

# Function to generate songs, playlist name, and description using ChatGPT
def generate_playlist_details(mood, genres):
    """
    Generate a list of 20 songs, a playlist name (max 4 words), and a description (max 20 words) 
    based on the mood and genres provided.
    """
    openai.api_key = OPENAI_API_KEY
    messages = [
        {
            "role": "system",
            "content": (
                "You are a music expert and creative assistant. Generate a playlist name (max 4 words), "
                "a description (max 20 words), and 20 songs based on the mood and genres provided. "
                "Respond in JSON format with 'name', 'description', and 'songs' keys. "
                "The 'songs' key should contain an array of song objects, each with 'title' and 'artist'."
            ),
        },
        {
            "role": "user",
            "content": f"Generate a playlist for the mood '{mood}' and the genres {', '.join(genres)}."
        },
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=750,
            temperature=0.7,
        )
        playlist_response = response.choices[0].message.content.strip()

        # Validar y limpiar el JSON
        try:
            playlist_data = json.loads(playlist_response)  # Convertir la respuesta a JSON
            if (
                "name" in playlist_data and "description" in playlist_data and "songs" in playlist_data and 
                isinstance(playlist_data["songs"], list)
            ):
                name = playlist_data["name"]
                description = playlist_data["description"]
                songs = playlist_data["songs"]
                # Validar que las canciones tengan 'title' y 'artist'
                if all("title" in song and "artist" in song for song in songs):
                    return name, description, songs
                else:
                    raise ValueError("Las canciones no contienen los campos 'title' y 'artist'.")
            else:
                raise ValueError("El JSON no contiene las claves esperadas ('name', 'description', 'songs').")
        except json.JSONDecodeError:
            st.error("❌ La respuesta de ChatGPT no es un JSON válido.")
            return None, None, []
    except Exception as e:
        st.error(f"❌ Error al generar la playlist: {e}")
        return None, None, []

# Function to create a playlist on Spotify
def create_playlist(token, user_id, name, description):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"name": name, "description": description, "public": False}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Function to search for songs on Spotify
def search_tracks(token, query):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 1}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Function to add songs to a playlist on Spotify
def add_tracks_to_playlist(token, playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"uris": track_uris}
    response = requests.post(url, headers=headers, json=payload)
    return response

# Streamlit App
def main():
    st.markdown(
        """
        <h1 style='text-align: center;'>🎵 Spotify Playlist Creator 🎵</h1>
        <h3 style='text-align: center;'>Crea listas de reproducción personalizadas según tu estado de ánimo y género favorito.</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Step 1: Authorization
    st.markdown("<h2 style='color: #1DB954;'>🔑 Autenticación</h2>", unsafe_allow_html=True)
    if "access_token" not in st.session_state:
        auth_url = get_auth_url(CLIENT_ID, REDIRECT_URI, SCOPES)
        st.markdown(
            f"<div style='text-align: center;'><a href='{auth_url}' target='_blank' style='color: #1DB954; font-weight: bold;'>🔑 Iniciar sesión en Spotify</a></div>",
            unsafe_allow_html=True
        )
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"]
            token_response = requests.post(
                "https://accounts.spotify.com/api/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
            ).json()
            if "access_token" in token_response:
                st.session_state.access_token = token_response["access_token"]
                st.success("✅ Autenticación completada.")
            else:
                st.error("❌ Error en la autenticación.")
    else:
        st.success("✅ Ya estás autenticado.")

    # Step 2: Select mood, genres, and generate playlist
    if "access_token" in st.session_state:
        token = st.session_state.access_token
        st.markdown("<h2>🎶 Generar y Crear Lista de Reproducción</h2>", unsafe_allow_html=True)
        user_id = st.text_input("🎤 Introduce tu ID de usuario de Spotify", placeholder="Usuario de Spotify")
        mood = st.selectbox("😊 Selecciona tu estado de ánimo deseado", ["Max Focus", "Productive Work", "Sport Full Gas", "Relax"])
        genres = st.multiselect("🎸 Selecciona los géneros musicales", ["Hard Rock", "Rock 80 & 90s", "Modern Rock", "Pop", "Progresive Rock", "Hip Hop", "Rap"])

        if st.button("🎵 Generar y Crear Lista 🎵"):
            if user_id and mood and genres:
                st.info("🎧 Generando canciones, nombre y descripción...")
                name, description, songs = generate_playlist_details(mood, genres)

                if name and description and songs:
                    st.success(f"✅ Nombre generado: {name}")
                    st.info(f"📜 Descripción generada: {description}")
                    st.success(f"🎵 Canciones generadas:")
                    track_uris = []
                    for song in songs:
                        query = f"{song['title']} {song['artist']}"
                        search_response = search_tracks(token, query)
                        if "tracks" in search_response and search_response["tracks"]["items"]:
                            track_uris.append(search_response["tracks"]["items"][0]["uri"])
                            st.write(f"- **{song['title']}** - {song['artist']}")

                    if track_uris:
                        playlist_response = create_playlist(token, user_id, name, description)
                        if "id" in playlist_response:
                            playlist_id = playlist_response["id"]
                            add_tracks_to_playlist(token, playlist_id, track_uris)
                            st.success(f"✅ Lista '{name}' creada exitosamente en Spotify.")
                        else:
                            st.error("❌ No se pudo crear la playlist en Spotify.")
                else:
                    st.error("❌ No se pudo generar la playlist.")
            else:
                st.warning("⚠️ Completa todos los campos para crear la lista.")

if __name__ == "__main__":
    main()
