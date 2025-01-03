import streamlit as st
import openai

# Configuración de la API de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configuración de la página
st.title("🎵 Generador de Playlists por Estado de Ánimo 🎶")

# Selección del estado de ánimo y género musical
st.header("Configura tu playlist")

mood = st.selectbox(
    "Estado de ánimo a lograr:",
    ["Feliz", "Motivado", "Concentrado", "Meditación"]
)

genre = st.selectbox(
    "Tipo de género musical a considerar:",
    ["Rock", "Rock Progresivo", "Rock Alternativo", "Pop 80s", "Pop 90s"]
)

if st.button("Crear una Playlist"):
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

        # Mostrar las canciones en formato de lista
        st.subheader("🎧 Tu Playlist Generada:")
        st.markdown(songs_text)

    except Exception as e:
        st.error(f"Hubo un error al generar la playlist: {e}")
