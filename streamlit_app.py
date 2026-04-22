import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. Configuración de API
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 2. Función mejorada para leer MÚLTIPLES archivos
def cargar_toda_la_informacion():
    texto_total = ""
    # Listamos todos los archivos en el repositorio
    archivos = os.listdir('.')
    archivos_pdf = [f for f in archivos if f.endswith('.pdf')]
    
    if not archivos_pdf:
        st.error("No se encontraron archivos PDF en el repositorio.")
        st.stop()
    
    for archivo in archivos_pdf:
        try:
            reader = PdfReader(archivo)
            for page in reader.pages:
                texto_total += page.extract_text() + "\n"
        except Exception as e:
            st.warning(f"No pude leer el archivo {archivo}: {e}")
            
    return texto_total

# Cargamos el conocimiento de todos los PDFs subidos
conocimiento_logistica = cargar_toda_la_informacion()

# 3. Instrucciones del Sistema
SYSTEM_PROMPT = f"""
Eres un profesor experto en logística. 
Tu base de conocimiento se compone de varios manuales y documentos que te han sido suministrados.
Aquí tienes el contenido total de esos documentos:

{conocimiento_logistica}

Instrucciones:
- Responde siempre basándote en esta información.
- Si la respuesta varía entre documentos, intenta dar una respuesta integrada.
- Si algo no figura en ninguno de los archivos, indícalo claramente.
"""

# Actualiza esta línea con el nombre exacto que viste:
model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview", 
    system_instruction=SYSTEM_PROMPT
)

# --- Interfaz de Chat ---
st.title("🎓 Profesor de Logística Multi-Manual")
st.info(f"📚 El profesor ha leído la información de todos tus PDFs disponibles.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Haz una pregunta sobre los manuales..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
