import streamlit as st
import google.generativeai as genai
import os
import pdfplumber

# Configuración básica
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("🎓 Profesor de Logística")

# Función que lee solo un pedacito para no saturar
@st.cache_data # Esto hace que solo lea los archivos UNA VEZ y no gaste cuota extra
def obtener_contexto():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos[:2]: # SOLO LEE LOS PRIMEROS 2 ARCHIVOS
        with pdfplumber.open(arc) as pdf:
            for page in pdf.pages[:5]: # SOLO LEE LAS PRIMERAS 5 PÁGINAS
                texto += page.extract_text() + "\n"
    return texto[:10000] # LÍMITE ESTRICTO DE 10,000 CARACTERES

contexto_educativo = obtener_contexto()

model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Enviamos el manual junto con la pregunta en un formato comprimido
        instruccion = f"Usa este manual: {contexto_educativo}. Pregunta: {prompt}"
        try:
            response = model.generate_content(instruccion)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Google sigue bloqueando la conexión. Por favor, crea una nueva API Key.")
