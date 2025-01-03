import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
import spotipy

# Configuración de la API de Spotify
CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8501"  # URL de redirección para OAuth

scope = "playlist-modify-public user-top-read"

st.title("🎵 Generador de Playlists por Estado de Ánimo")

# Autenticación del usuario con Spotify
@st.cache_resource
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope
    ))

sp = get_spotify_client()

# Selección del estado de ánimo
st.header("¿Cómo te sientes hoy?")
mood = st.selectbox(
    "Selecciona tu estado de ánimo:",
    ["Feliz", "Triste", "Relajado", "Energético"]
)

# Consulta de géneros y preferencias
st.header("Preferencias musicales")
genres = sp.recommendation_genre_seeds()['genres']
selected_genres = st.multiselect("Elige tus géneros favoritos:", genres)

if st.button("Crear Playlist"):
    if not selected_genres:
        st.warning("Por favor selecciona al menos un género.")
    else:
        # Obtén recomendaciones basadas en estado de ánimo y géneros
        recommendations = sp.recommendations(
            seed_genres=selected_genres,
            limit=20
        )
        
        track_uris = [track['uri'] for track in recommendations['tracks']]
        
        # Crear la playlist en Spotify
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(
            user=user_id,
            name=f"Playlist {mood} 🎧",
            public=True,
            description=f"Lista generada para estado de ánimo {mood}."
        )
        
        # Agregar canciones a la playlist
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
        
        st.success(f"¡Playlist creada exitosamente! [Escúchala en Spotify]({playlist['external_urls']['spotify']})")

# Instrucciones para el usuario
st.write("👆 Autentícate con tu cuenta de Spotify para generar playlists personalizadas.")
