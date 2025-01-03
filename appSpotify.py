import streamlit as st
import requests
import base64

# Spotify API Credentials
CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# Function to get Spotify token
def get_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

# Function to fetch playlists
def get_user_playlists(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# Streamlit App
def main():
    st.title("🎵 Mis Listas de Spotify")
    st.markdown(
        "Una app sencilla para explorar tus listas de reproducción de Spotify. Asegúrate de que tienes tus credenciales de la API configuradas correctamente."
    )
    
    user_id = st.text_input("Introduce tu ID de usuario de Spotify:", value="", placeholder="Usuario de Spotify")
    
    if user_id:
        token = get_token(CLIENT_ID, CLIENT_SECRET)
        if token:
            playlists = get_user_playlists(token, user_id)
            if playlists and "items" in playlists:
                st.subheader("🎧 Listas de Reproducción")
                for playlist in playlists["items"]:
                    st.write(f"**{playlist['name']}** ({playlist['tracks']['total']} canciones)")
                    st.markdown(f"[Abrir en Spotify]({playlist['external_urls']['spotify']})")
            else:
                st.error("No se pudieron recuperar tus listas. Verifica tu ID o permisos.")
        else:
            st.error("Error al obtener el token de acceso. Verifica tus credenciales.")

if __name__ == "__main__":
    main()
