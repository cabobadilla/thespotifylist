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

# Apply Spotify colors (green and black) to the app
st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        .stButton>button {
            background-color: #1DB954;
            color: white;
            border: None;
            font-size: 16px;
            padding: 8px 16px;
            border-radius: 25px;
        }
        .stButton>button:hover {
            background-color: #1ED760;
        }
        h1, h2, h3 {
            color: #1DB954;
        }
        .stTextInput>div>input {
            background-color: #2C2C2C;
            color: white;
            border: 1px solid #1DB954;
            border-radius: 10px;
        }
        .stTextArea>div>textarea {
            background-color: #2C2C2C;
            color: white;
            border: 1px solid #1DB954;
            border-radius: 10px;
        }
        .stSelectbox>div>div>div {
            background-color: #2C2C2C;
            color: white;
            border: 1px solid #1DB954;
            border-radius: 10px;
        }
        .stMultiSelect>div>div>div {
            background-color: #2C2C2C;
            color: white;
            border: 1px solid #1DB954;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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

# Streamlit App
def main():
    st.markdown("<h1 style='text-align: center;'>🎵 Spotify Playlist Manager 🎵</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Crea listas de reproducción personalizadas según tu estado de ánimo y género favorito.</h3>", unsafe_allow_html=True)
    
    # Step 1: Authorization
    st.markdown("<h2>1️⃣ Autenticación</h2>", unsafe_allow_html=True)
    if "access_token" not in st.session_state:
        auth_url = get_auth_url(CLIENT_ID, REDIRECT_URI, SCOPES)
        st.markdown(f"<div style='text-align: center;'><a href='{auth_url}' target='_blank' style='color: #1DB954; font-weight: bold;'>🔑 Iniciar sesión en Spotify</a></div>", unsafe_allow_html=True)

        # Listen for the authorization code in the URL
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"]
            token_response = get_access_token(CLIENT_ID, CLIENT_SECRET, code, REDIRECT_URI)
            if "access_token" in token_response:
                st.session_state.access_token = token_response["access_token"]
                st.session_state.refresh_token = token_response.get("refresh_token")
                st.success("✅ Autenticación completada.")
            else:
                st.error("❌ No se pudo obtener el token de acceso. Verifica tus credenciales.")
    else:
        st.success("✅ Ya estás autenticado.")

    # Step 2: Generate songs and create playlist
    if "access_token" in st.session_state:
        token = st.session_state.access_token
        st.markdown("<h2>🎶 Generar y Crear Lista de Reproducción</h2>", unsafe_allow_html=True)
        user_id = st.text_input("🎤 Introduce tu ID de usuario de Spotify", placeholder="Usuario de Spotify")
        mood = st.selectbox("😊 Selecciona tu estado de ánimo deseado", ["Subir el ánimo", "Trabajo", "Concentración", "Fiesta"])
        genres = st.multiselect("🎸 Selecciona los géneros musicales", ["Rock 80s", "Rock 90s", "Pop 80s", "Rock Progresivo", "Rock Pesado"])
        playlist_name = st.text_input("📜 Nombre de la nueva lista de reproducción", placeholder="Mi nueva playlist")
        playlist_description = st.text_area("📝 Descripción de la lista", placeholder="Describe tu playlist")

        if st.button("🎵 Generar y Crear Lista 🎵"):
            if mood and genres and playlist_name and user_id:
                st.info("🎧 Generando canciones y creando lista...")
                # Aquí se integran las funciones de generación de canciones y creación de listas
                st.success(f"✅ Lista de reproducción '{playlist_name}' creada exitosamente.")
                st.markdown("<h3>🎵 Lista de canciones agregadas:</h3>", unsafe_allow_html=True)
                st.markdown("- **Ejemplo Canción 1** - Artista 1")
                st.markdown("- **Ejemplo Canción 2** - Artista 2")
            else:
                st.warning("⚠️ Completa todos los campos para generar y crear la lista.")

if __name__ == "__main__":
    main()
