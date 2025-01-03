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

# Function to fetch tracks from a playlist
def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
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
        "public": False  # False for private playlist
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Streamlit App
def main():
    st.title("🎵 Mis Listas de Spotify")
    st.markdown(
        "Una app sencilla para explorar tus listas de reproducción y canciones de Spotify. Asegúrate de que tienes tus credenciales de la API configuradas correctamente."
    )
    
    user_id = st.text_input("Introduce tu ID de usuario de Spotify:", value="", placeholder="Usuario de Spotify")
    
    if user_id:
        token = get_token(CLIENT_ID, CLIENT_SECRET)
        if token:
            playlists = get_user_playlists(token, user_id)
            if playlists and "items" in playlists:
                st.subheader("🎧 Listas de Reproducción")
                for playlist in playlists["items"]:
                    with st.expander(f"{playlist['name']} ({playlist['tracks']['total']} canciones)"):
                        tracks = get_playlist_tracks(token, playlist["id"])
                        if tracks and "items" in tracks:
                            for item in tracks["items"]:
                                track = item["track"]
                                st.write(f"**{track['name']}** - {', '.join([artist['name'] for artist in track['artists']])}")
                        else:
                            st.warning("No se pudieron recuperar las canciones de esta lista.")
            else:
                st.error("No se pudieron recuperar tus listas. Verifica tu ID o permisos.")
            
            # Section to create a new playlist
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
        else:
            st.error("Error al obtener el token de acceso. Verifica tus credenciales.")

if __name__ == "__main__":
    main()
