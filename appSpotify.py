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
    """
    Constructs the Spotify authorization URL.
    """
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
        # Generar la URL de autorización
        auth_url = get_auth_url(CLIENT_ID, REDIRECT_URI, SCOPES)
        st.markdown(
            f"<div style='text-align: center;'><a href='{auth_url}' target='_blank' style='color: #1DB954; font-weight: bold;'>🔑 Iniciar sesión en Spotify</a></div>",
            unsafe_allow_html=True
        )
        # Verificar si se recibió el código de autorización
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
        generate_details = st.checkbox("🪄 Generar nombre y descripción automáticamente")

        playlist_name = st.text_input("📜 Nombre de la lista de reproducción", placeholder="Mi nueva playlist")
        playlist_description = st.text_area("📝 Descripción de la lista", placeholder="Describe tu playlist")

        if generate_details and mood and genres:
            st.info("🎧 Generando detalles creativos para la playlist...")
            try:
                openai.api_key = OPENAI_API_KEY
                messages = [
                    {
                        "role": "system",
                        "content": "You are a creative assistant that generates names and descriptions for playlists."
                    },
                    {
                        "role": "user",
                        "content": f"Create a playlist name and description for the mood '{mood}' and genres {', '.join(genres)}."
                    },
                ]
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=100,
                )
                result = response.choices[0].message.content.strip()
                playlist_name, playlist_description = result.split("\n", 1)
                st.success(f"✅ Nombre generado: {playlist_name}")
                st.info(f"Descripción generada: {playlist_description}")
            except Exception as e:
                st.error(f"❌ Error al generar los detalles: {e}")

        if st.button("🎵 Crear Lista 🎵"):
            if playlist_name and playlist_description and user_id:
                st.success(f"✅ Lista de reproducción '{playlist_name}' creada exitosamente.")
                st.markdown("<h3>🎵 Lista de canciones agregadas:</h3>", unsafe_allow_html=True)
                st.markdown("- **Ejemplo Canción 1** - Artista 1")
                st.markdown("- **Ejemplo Canción 2** - Artista 2")
            else:
                st.warning("⚠️ Completa todos los campos para crear la lista.")

if __name__ == "__main__":
    main()
