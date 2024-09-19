import os
from gtts import gTTS
import streamlit as st

# Función para convertir texto a audio y guardar el archivo
def text_to_speech(text):
    tts = gTTS(text=text, lang='es')  # 'es' para español
    audio_file = "speech_output.mp3"
    tts.save(audio_file)
    return audio_file

# Configuración de la página de Streamlit
st.set_page_config(page_title="Conversor de Texto a Audio", page_icon="🎤")

# Título y descripción
st.title("🎤 Conversor de Texto a Audio")
st.write("Introduce el texto que deseas convertir a audio y presiona el botón para escuchar la respuesta.")

# Inicializar el estado de la sesión si no está ya inicializado
if 'audio_bytes' not in st.session_state:
    st.session_state['audio_bytes'] = None

# Campo de texto para ingresar el texto
text_input = st.text_area("Escribe el texto aquí", height=150)

# Botón para convertir a audio
if st.button("Convertir a Audio"):
    if text_input.strip():
        audio_path = text_to_speech(text_input)
        st.success("✅ El audio ha sido generado. Puedes reproducirlo o descargarlo a continuación.")
        
        # Reproducir el archivo de audio generado y guardarlo en la sesión
        with open(audio_path, "rb") as audio_file:
            st.session_state['audio_bytes'] = audio_file.read()  # Guardar en el estado de sesión
            st.audio(st.session_state['audio_bytes'], format="audio/mp3")

# Si hay un archivo de audio en el estado de sesión, mostrarlo y permitir la descarga
if st.session_state['audio_bytes']:
    st.audio(st.session_state['audio_bytes'], format="audio/mp3")
    
    # Botón para descargar el archivo de audio
    st.download_button(
        label="Descargar Audio",
        data=st.session_state['audio_bytes'],
        file_name="speech_output.mp3",  # Asegura que la extensión sea .mp3
        mime="audio/mp3"
    )

# Información adicional
st.write("Este conversor usa la tecnología de Google Text-to-Speech (gTTS).")


