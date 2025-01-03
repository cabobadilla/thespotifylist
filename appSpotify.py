import streamlit as st
import pandas as pd
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

if st.button("Crear una Playlist en Spotify"):
    # Generar lista de canciones usando ChatGPT
    prompt = (
        f"Genera una lista de 30 canciones que sean apropiadas para lograr un estado de ánimo '{mood}' "
        f"con música del género '{genre}'. Devuelve los resultados en formato tabular con columnas: "
        f"Grupo, Canción, Año de la canción, Tipo de música o género."
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

        # Convertir texto a tabla
        data = []
        for line in songs_text.split("\n")[1:]:  # Omitimos el encabezado
            if line.strip():  # Ignorar líneas vacías
                parts = [part.strip() for part in line.split("|")]
                if len(parts) == 4:  # Asegurar que cada línea tenga 4 columnas
                    data.append(parts)

        # Crear DataFrame
        columns = ["Grupo", "Canción", "Año de la canción", "Tipo de música o género"]
        df = pd.DataFrame(data, columns=columns)

        # Mostrar la tabla
        st.subheader("🎧 Tu Playlist Generada:")
        st.dataframe(df)

    except Exception as e:
        st.error(f"Hubo un error al generar la playlist: {e}")
