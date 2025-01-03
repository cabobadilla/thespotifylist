import streamlit as st
import requests
import base64
from urllib.parse import urlencode

# Spotify API Credentials
CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = st.secrets.get("SPOTIFY_REDIRECT_URI", "http://localhost:8501/callback")  # Configurado como secreto

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

# Function to get access token using authorization code
def get_access_token(client_id, client_secret, code, redirect_uri):
    token_url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(token_url, headers=headers, data=data)
    return response.json()

# Function to create a new playlist
def create_playlist(token, user_id, name, description):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "name": name,
        "description": description,
        "public": False,  # False for private playlist
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to search for tracks on Spotify
def search_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": track_name,
        "type": "track",
        "limit": 1,
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Streamlit App
def main():
    st.title("🎵 Spotify Playlist Manager")
    
    # Step 1: Authorization
    st.subheader("1️⃣ Autenticación")
    if "access_token" not in st.session_state:
        auth_url = get_auth_url(CLIENT_ID, REDIRECT_URI, SCOPES)
        st.markdown(f"[Iniciar sesión en Spotify]({auth_url})", unsafe_allow_html=True)

        # Listen for the authorization code in the URL
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"]
            token_response = get_access_token(CLIENT_ID, CLIENT_SECRET, code, REDIRECT_URI)
            if "access_token" in token_response:
                st.session_state.access_token = token_response["access_token"]
                st.session_state.refresh_token = token_response.get("refresh_token")
                st.success("Autenticación completada.")
            else:
                st.error("No se pudo obtener el token de acceso. Verifica tus credenciales.")
    else:
        st.success("Ya estás autenticado.")

    # Step 2: Generate song list using ChatGPT
    if "access_token" in st.session_state:
        token = st.session_state.access_token
        st.subheader("🎶 Generar canciones basadas en tu estado de ánimo")
        mood = st.selectbox("Selecciona tu estado de ánimo deseado:", ["Concentración", "Mejorar el ánimo", "Relajación"])
        genres = st.multiselect("Selecciona los géneros musicales:", ["Rock", "Hip Hop", "Jazz", "Pop", "Clásica"])

        if st.button("Generar lista de canciones"):
            if mood and genres:
                # Call ChatGPT to generate a song list
                st.info("Generando lista de canciones...")
                prompt = f"Genera una lista de 10 canciones populares de los géneros {', '.join(genres)} que ayuden a {mood.lower()}."
                try:
                    # Replace with a call to OpenAI API if integrated
                    song_list = [
                        {"title": "Song 1", "artist": "Artist A"},
                        {"title": "Song 2", "artist": "Artist B"},
                        {"title": "Song 3", "artist": "Artist C"},
                    ]  # Replace with actual ChatGPT response
                    st.session_state.generated_songs = song_list
                    st.success("Lista generada exitosamente.")
                    for song in song_list:
                        st.write(f"🎵 **{song['title']}** - {song['artist']}")
                except Exception as e:
                    st.error("Hubo un problema al generar la lista de canciones.")
            else:
                st.warning("Selecciona un estado de ánimo y al menos un género.")

    # Step 3: Create a Playlist with generated songs
    if "generated_songs" in st.session_state and "access_token" in st.session_state:
        user_id = st.text_input("Introduce tu ID de usuario de Spotify:", value="", placeholder="Usuario de Spotify")
        if user_id:
            st.subheader("🎶 Crear una nueva lista de reproducción")
            new_playlist_name = st.text_input("Nombre de la nueva lista de reproducción", placeholder="Mi nueva playlist")
            new_playlist_description = st.text_area("Descripción de la lista", placeholder="Describe tu playlist")
            if st.button("Crear lista de reproducción"):
                if new_playlist_name:
                    # Create the playlist
                    creation_response = create_playlist(token, user_id, new_playlist_name, new_playlist_description)
                    if "id" in creation_response:
                        playlist_id = creation_response["id"]
                        st.success(f"Lista de reproducción '{new_playlist_name}' creada exitosamente.")
                        # Add songs to the playlist
                        st.info("Agregando canciones a la lista...")
                        track_uris = []
                        for song in st.session_state.generated_songs:
                            search_response = search_track(token, song["title"])
                            if search_response and "tracks" in search_response:
                                items = search_response["tracks"]["items"]
                                if items:
                                    track_uris.append(items[0]["uri"])
                        if track_uris:
                            add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                            add_tracks_headers = {"Authorization": f"Bearer {token}"}
                            add_tracks_response = requests.post(add_tracks_url, headers=add_tracks_headers, json={"uris": track_uris})
                            if add_tracks_response.status_code == 201:
                                st.success("Canciones agregadas exitosamente.")
                            else:
                                st.error("No se pudieron agregar las canciones.")
                    else:
                        st.error("No se pudo crear la lista. Verifica los permisos y vuelve a intentar.")
                else:
                    st.warning("El nombre de la lista no puede estar vacío.")

if __name__ == "__main__":
    main()
