import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader # Librería para leer PDFs automáticamente

# 1. Configuración de API
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 2. Función para extraer texto del archivo adjunto en GitHub
def extraer_conocimiento(archivo_pdf):
    reader = PdfReader(archivo_pdf)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto

# Cargamos el archivo que subiste a GitHub
# (Asegúrate de que el nombre coincida exactamente)
import os

# Busca cualquier archivo que termine en .pdf en tu repositorio
archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]

if archivos_pdf:
    # Toma el primer PDF que encuentre
    contenido_logistica = extraer_conocimiento(archivos_pdf[0])
else:
    st.error("No encontré ningún archivo PDF en el repositorio. Por favor, sube uno a GitHub.")
    st.stop()

# 3. Instrucciones del Sistema (System Instruction)
SYSTEM_PROMPT = f"""
Eres un profesor experto en logística. 
Tu base de conocimiento es el siguiente texto extraído del manual oficial:
{contenido_logistica}

Responde siempre basándote en este contenido.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=SYSTEM_PROMPT
)

# --- Interfaz de Chat ---
st.title("🎓 Profesor de Logística 24/7")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Pregúntame sobre el manual"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
