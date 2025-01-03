import openai
import json
import streamlit as st
import requests
import base64
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
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Clave de OpenAI
REDIRECT_URI = st.secrets.get("SPOTIFY_REDIRECT_URI", "http://localhost:8501/callback")  # Configurado como secreto

# Scopes for Spotify API
SCOPES = "playlist-modify-private playlist-modify-public"

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
    st.markdown(
        """
        <h2 style='color: #1DB954;'>🔑 Autenticación</h2>
        """,
        unsafe_allow_html=True
    )
    if "access_token" not in st.session_state:
        auth_url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
        }
        st.markdown(
            f"<div style='text-align: center;'><a href='{auth_url}' target='_blank' style='color: #1DB954; font-weight: bold;'>🔑 Iniciar sesión en Spotify</a></div>",
            unsafe_allow_html=True
        )
        # Listen for the authorization code in the URL
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
        mood = st.selectbox("😊 Selecciona tu estado de ánimo deseado", ["Concentración", "Trabajo", "Descanso"])
        genres = st.multiselect("🎸 Selecciona los géneros musicales", ["Rock Pesado", "Rock 80 y 90s", "Rock Progresivo", "Hip Hop", "Jazz"])

        if st.button("🎵 Generar y Crear Lista 🎵"):
            if mood and genres and user_id:
                st.info("🎧 Generando detalles creativos para la playlist...")
                details = generate_playlist_details(mood, genres)
                playlist_name = details["name"]
                playlist_description = details["description"]
                st.success(f"✅ Nombre generado: {playlist_name}")
                st.info(f"Descripción generada: {playlist_description}")
                # Aquí se integran las funciones de generación de canciones y creación de listas
                st.success(f"✅ Lista de reproducción '{playlist_name}' creada exitosamente.")
                st.markdown("<h3>🎵 Lista de canciones agregadas:</h3>", unsafe_allow_html=True)
                st.markdown("- **Ejemplo Canción 1** - Artista 1")
                st.markdown("- **Ejemplo Canción 2** - Artista 2")
            else:
                st.warning("⚠️ Completa todos los campos para generar y crear la lista.")

if __name__ == "__main__":
    main()
