import streamlit as st
import openai
import requests
from datetime import datetime

# Configuración de las APIs
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Estado de la sesión
if "spotify_access_token" not in st.session_state:
    st.session_state.spotify_access_token = None

# Pantalla de la App
st.title("🎵 Generador y Creador de Playlists por Estado de Ánimo 🎶")

# Solicitar token de Spotify si no está configurado
if not st.session_state.spotify_access_token:
    st.markdown("Para continuar, genera tu token de acceso a Spotify siguiendo los pasos a continuación.")
    st.markdown("1. Usa el comando de `curl` en tu terminal (ver instrucciones más abajo).")
    st.markdown("2. Copia y pega el token generado aquí.")
    token_input = st.text_input("Pega aquí tu token de acceso de Spotify:")
    if st.button("Guardar Token"):
        if token_input:
            st.session_state.spotify_access_token = token_input
            st.success("¡Token guardado correctamente! Ahora puedes generar y crear playlists.")
        else:
            st.error("El token no puede estar vacío.")
else:
    # Solicitar estado de ánimo y tipo de música
    st.header("Configura tu playlist")

    mood = st.selectbox(
        "Estado de ánimo a lograr:",
        ["Feliz", "Motivado", "Concentrado", "Meditación"]
    )

    genre = st.selectbox(
        "Tipo de género musical a considerar:",
        ["Rock", "Rock Progresivo", "Rock Alternativo", "Pop 80s", "Pop 90s"]
    )

    if st.button("Generar y Crear Playlist en Spotify"):
        # Generar lista de canciones usando ChatGPT
        prompt = (
            f"Genera una lista de 30 canciones que sean apropiadas para lograr un estado de ánimo '{mood}' "
            f"con música del género '{genre}'. Devuelve los resultados como una lista en formato: "
            f"- [Grupo] - [Canción] (Año de la canción)."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente que genera listas de canciones basadas en estados de ánimo y géneros musicales."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
            )

            # Procesar la respuesta de OpenAI
            songs_text = response['choices'][0]['message']['content'].strip()

            # Mostrar las canciones generadas
            st.subheader("🎧 Tu Playlist Generada:")
            st.markdown(songs_text)

            # Crear la playlist en Spotify
            try:
                current_date = datetime.now().strftime("%d%m%y")
                playlist_name = f"{current_date} - {mood} - {genre}"

                # Crear la playlist
                headers = {
                    "Authorization": f"Bearer {st.session_state.spotify_access_token}",
                    "Content-Type": "application/json"
                }
                user_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
                if user_response.status_code == 200:
                    user_id = user_response.json()["id"]
                    playlist_response = requests.post(
                        f"https://api.spotify.com/v1/users/{user_id}/playlists",
                        headers=headers,
                        json={
                            "name": playlist_name,
                            "description": f"Playlist generada para estado de ánimo '{mood}' y género '{genre}'.",
                            "public": True
                        }
                    )
                    if playlist_response.status_code == 201:
                        playlist = playlist_response.json()
                        st.success(f"¡Playlist creada exitosamente! [Abrir en Spotify]({playlist['external_urls']['spotify']})")
                    else:
                        st.error(f"Error al crear la playlist: {playlist_response.json()}")
                else:
                    st.error(f"Error al obtener la información del usuario: {user_response.json()}")

            except Exception as e:
                st.error(f"Error al crear la playlist en Spotify: {e}")

        except Exception as e:
            st.error(f"Hubo un error al generar la playlist: {e}")
