import openai
import json
import streamlit as st
import requests
import base64
from urllib.parse import urlencode

# Spotify API Credentials
CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Clave de OpenAI
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

# Function to clean and validate ChatGPT's response
def clean_and_validate_response(response_text):
    try:
        # Eliminar cualquier texto antes o después del JSON
        start_index = response_text.find("[")
        end_index = response_text.rfind("]") + 1
        if start_index == -1 or end_index == -1:
            raise ValueError("No se encontró un JSON válido en la respuesta.")
        json_content = response_text[start_index:end_index]
        # Convertir a JSON
        song_list = json.loads(json_content)
        # Validar estructura
        if isinstance(song_list, list) and all("title" in song and "artist" in song for song in song_list):
            return song_list
        else:
            raise ValueError("El JSON no tiene la estructura esperada.")
    except Exception as e:
        raise ValueError(f"Error al procesar la respuesta: {e}")

# Function to generate songs using ChatGPT (gpt-3.5-turbo)
def generate_song_list(mood, genres):
    openai.api_key = OPENAI_API_KEY
    messages = [
        {
            "role": "system",
            "content": (
                "You are a music expert that generates song recommendations. "
                "When asked, you provide a JSON list of 10 songs, each with the 'title' and 'artist' keys."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Generate a list of 10 songs based on the mood '{mood}' and the genres {', '.join(genres)}. "
                f"Provide the response in JSON format as a list of objects, each with 'title' and 'artist'."
            ),
        },
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        songs = response.choices[0].message.content.strip()
        # Limpiar y validar el JSON
        return clean_and_validate_response(songs)
    except ValueError as ve:
        st.error(f"Error al procesar la respuesta de ChatGPT: {ve}")
        return []
    except Exception as e:
        st.error(f"Error al generar la lista de canciones: {e}")
        return []

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
                st.info("Generando lista de canciones...")
                songs = generate_song_list(mood, genres)
                if songs:
                    st.session_state.generated_songs = songs
                    st.success("Lista generada exitosamente.")
                    for song in songs:
                        st.write(f"🎵 **{song['title']}** - {song['artist']}")
            else:
                st.warning("Selecciona un estado de ánimo y al menos un género.")

if __name__ == "__main__":
    main()
