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

    # Step 2: Create a Playlist
    if "access_token" in st.session_state:
        token = st.session_state.access_token
        user_id = st.text_input("Introduce tu ID de usuario de Spotify:", value="", placeholder="Usuario de Spotify")
        if user_id:
            st.subheader("🎶 Crear una nueva lista de reproducción")
            new_playlist_name = st.text_input("Nombre de la nueva lista de reproducción", placeholder="Mi nueva playlist")
            new_playlist_description = st.text_area("Descripción de la lista", placeholder="Describe tu playlist")
            if st.button("Crear lista de reproducción"):
                if new_playlist_name:
                    creation_response = create_playlist(token, user_id, new_playlist_name, new_playlist_description)
                    if "id" in creation_response:
                        st.success(f"Lista de reproducción '{new_playlist_name}' creada exitosamente.")
                    else:
                        st.error("No se pudo crear la lista. Verifica los permisos y vuelve a intentar.")
                else:
                    st.warning("El nombre de la lista no puede estar vacío.")

if __name__ == "__main__":
    main()
