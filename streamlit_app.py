import streamlit as st
import google.generativeai as genai
import os
import pdfplumber  # Usamos solo esta que es más robusta

# 1. Configuración de API
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 2. Función para leer múltiples PDFs (Optimizado)
def cargar_toda_la_informacion():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not archivos_pdf:
        return "No hay manuales cargados."
    
    for archivo in archivos_pdf:
        try:
            with pdfplumber.open(archivo) as pdf:
                for page in pdf.pages:
                    texto_total += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")
            
    # IMPORTANTE: Recortamos a 100,000 caracteres para que no agote la cuota gratuita
    # Esto es suficiente para unas 50-80 páginas de puro texto.
    return texto_total[:100000]

# Cargamos el texto una sola vez
conocimiento_logistica = cargar_toda_la_informacion()

# 3. Configuración del Modelo (Usamos Flash para evitar ResourceExhausted)
SYSTEM_PROMPT = f"""
Eres un profesor experto en logística y transporte terrestre. 
Responde dudas basado en este contenido:
{conocimiento_logistica}

Si la respuesta no está en el texto, admítelo con amabilidad.
"""

# Usamos gemini-1.5-flash porque es el que más capacidad gratuita tiene
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    system_instruction=SYSTEM_PROMPT
)

# --- Interfaz de Chat ---
st.title("🎓 Profesor de Logística")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Qué duda tienes sobre el manual?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Se agotó la cuota gratuita por un momento. Espera 60 segundos y vuelve a preguntar.")
