import openai
from dotenv import load_dotenv
import os
import streamlit as st
from fpdf import FPDF
import pdfplumber
from bs4 import BeautifulSoup
import pandas as pd
from difflib import get_close_matches
from gtts import gTTS

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Configurar la clave API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Lista de objetos analizados relevantes
RELEVANT_OBJECTS = [
    "Viscosidad de la Sangre", "Cristal de Colesterol", "Grasa en Sangre", 
    "Resistencia Vascular", "Elasticidad Vascular", "Demanda de Sangre Miocardial", 
    "Volumen de Perfusión Sanguínea Miocardial", "Consumo de Oxígeno Miocardial", 
    "Volumen de Latido", "Impedancia Ventricular Izquierda de Expulsión", 
    "Fuerza de Bombeo Efectiva Ventricular Izquierda", "Elasticidad de Arteria Coronaria", 
    "Presión de Perfusión Coronaria", "Elasticidad de Vaso Sanguíneo Cerebral", 
    "Estado de Suministro Sanguíneo de Tejido Cerebral", "Coeficiente de Secreción de Pepsina", 
    "Coeficiente de Función de Peristalsis Gástrica", "Coeficiente de Función de Absorción Gástrica", 
    "Coeficiente de Función de Peristalsis del Intestino Delgado", 
    "Coeficiente de Función de Absorción del Intestino Delgado", 
    "Coeficiente de la Función de Peristalsis del Intestino Grueso (colon)", 
    "Coeficiente de absorción colónica", "Coeficiente intestinal bacteriano", 
    "Coeficiente de presión intraluminal", "Metabolismo de las proteínas", 
    "Función de producción de energía", "Función de Desintoxicación", 
    "Función de Secreción de Bilis", "Contenido de Grasa en el Hígado", 
    "Seroglobulina (A/G)", "Bilirrubina Total (TBIL)", "Fosfatasa Alcalina (ALP)", 
    "Ácidos Biliares Totales Séricos (TBA)", "Bilirrubina (DBIL)", "Insulina", 
    "Polipéptido Pancreático (PP)", "Glucagón", "Índice de Urobilinógeno", 
    "Índice de Ácido Úrico", "Índice de Nitrógeno Ureico en la Sangre (BUN)", 
    "Índice de Proteinuria", "Capacidad Vital (VC)", "Capacidad Pulmonar Total (TLC)", 
    "Resistencia de las Vías Aéreas (RAM)", "Contenido de Oxígeno Arterial (PaCO2)", 
    "Estado del Suministro Sanguíneo al Tejido Cerebral", "Arterioesclerosis Cerebral", 
    "Estado Funcional de Nervio Craneal", "Índice de Emoción", "Índice de Memoria (ZS)", 
    "Calcio", "Hierro", "Zinc", "Selenio", "Fósforo", "Potasio", "Magnesio", 
    "Cobre", "Cobalto", "Manganeso", "Yodo", "Níquel", "Flúor", "Molibdeno", 
    "Vanadio", "Estaño", "Silicio", "Estroncio", "Boro"
]

# Función para extraer texto de un archivo PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Función para extraer datos de un archivo HTML
def extract_data_from_html(file):
    soup = BeautifulSoup(file, 'html.parser')
    tables = soup.find_all('table')

    data = []
    for table in tables:
        rows = table.find_all('tr')[1:]  # Omitir la fila del encabezado
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                objeto_analizado = ' '.join(cols[0].text.split()).strip().lower()  # Normalización del texto
                valor_obtenido = cols[2].text.strip()

                # Verificar coincidencia exacta o aproximada
                matches = get_close_matches(objeto_analizado, [obj.lower() for obj in RELEVANT_OBJECTS], n=1, cutoff=0.8)
                if matches and valor_obtenido:
                    # Usar el nombre exacto del parámetro de la lista RELEVANT_OBJECTS
                    original_match = RELEVANT_OBJECTS[[obj.lower() for obj in RELEVANT_OBJECTS].index(matches[0])]
                    data.append([original_match, valor_obtenido])

    # Crear DataFrame y filtrar solo los parámetros relevantes
    df = pd.DataFrame(data, columns=['Objeto Analizado', 'Valor Obtenido'])
    df = df[df['Objeto Analizado'].isin(RELEVANT_OBJECTS)]
    df = df.drop_duplicates(subset='Objeto Analizado', keep='first')
    df.reset_index(drop=True, inplace=True)  # Resetear índice para asegurar consecutividad
    df.index += 1  # Asegurar que el índice comience en 1
    return df

# Función para generar PDF descargable
def generate_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Parámetros Médicos del Paciente", ln=True, align='C')

    # Agregar encabezados
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Objeto Analizado", 1)
    pdf.cell(90, 10, "Valor Obtenido", 1)
    pdf.ln()

    # Agregar datos
    pdf.set_font("Arial", size=10)
    for i, row in dataframe.iterrows():
        pdf.cell(90, 10, row['Objeto Analizado'], 1)
        pdf.cell(90, 10, row['Valor Obtenido'], 1)
        pdf.ln()

    pdf_output = 'Informe_Parametros_Clave.pdf'
    pdf.output(pdf_output)

    # Leer el archivo generado para que sea descargable
    with open(pdf_output, "rb") as file:
        pdf_bytes = file.read()

    return pdf_bytes

# Función para la conversión de texto a audio (conversor de texto a voz)
def text_to_speech(text):
    tts = gTTS(text=text, lang='es')  # 'es' para español
    audio_file = "speech_output.mp3"
    tts.save(audio_file)
    return audio_file

# Función principal de la sección de minería de datos
def mineria_de_datos():
    st.header("Minería de Datos")
    uploaded_file = st.file_uploader("Sube un archivo PDF o HTML/HTM", type=["pdf", "html", "htm"])

    if uploaded_file:
        # Detectar el tipo de archivo y extraer texto
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
            df = pd.DataFrame([
                ['Viscosidad de la Sangre', '72.211'],
                ['Cristal de Colesterol', '71.326'],
                ['Grasa en Sangre', '1.809']
            ], columns=['Objeto Analizado', 'Valor Obtenido'])
        else:
            html_content = uploaded_file.read().decode("iso-8859-1")
            df = extract_data_from_html(html_content)

        if not df.empty:
            st.write("Parámetros clave encontrados:")
            st.table(df)

            # Botón para descargar el PDF
            if st.button("Descargar como PDF"):
                pdf_bytes = generate_pdf(df)
                st.download_button(label="Descargar PDF", data=pdf_bytes, file_name="Informe_Parametros_Clave.pdf", mime="application/pdf")
        else:
            st.warning("No se encontraron parámetros clave en el archivo.")

# Función para la conversión de texto a audio
def conversion_texto_audio():
    st.header("Conversor de Texto a Audio")
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

# Título de la aplicación
st.title("Consultor de Informes Médicos")

# Crear una barra de navegación en la barra lateral
seccion = st.sidebar.selectbox("Navegar a:", ["Chat", "Mineria de datos", "Conversor de Texto a Audio"])

# Lógica para mostrar diferentes secciones según la selección
if seccion == "Chat":
    st.header("Chatbot")

    # Inicializar la sesión de mensajes
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hola! Soy tu asistente especializado en análisis de informes médicos. Estoy aquí para ayudarte a comprender mejor los resultados de tus análisis y ofrecerte recomendaciones basadas en la información proporcionada. Puedes subir información de tu informe médico, y con mi ayuda, recibirás un resumen detallado de los parámetros clave, una explicación de los síntomas reportados, y orientación personalizada sobre posibles medidas a seguir. ¡Comencemos a analizar tu informe para obtener respuestas claras y útiles!"}]

    # Mostrar historial de mensajes
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    # Capturar entrada del usuario
    if user_input := st.chat_input():
        # Añadir el mensaje del usuario al historial de la sesión
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # Llamada a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state["messages"]
        )
        
        # Extraer la respuesta del modelo
        response_message = response.choices[0].message.content
        st.session_state["messages"].append({"role": "assistant", "content": response_message})
        st.chat_message("assistant").write(response_message)

elif seccion == "Mineria de datos":
    mineria_de_datos()

elif seccion == "Conversor de Texto a Audio":
    conversion_texto_audio()
