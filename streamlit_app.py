import streamlit as st
import google.generativeai as genai
import os
import pdfplumber

# 1. Configuración
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("🎓 Profesor de Logística")

# 2. Leer solo lo básico (Solo el primer PDF, solo las primeras 3 páginas)
@st.cache_data
def cargar_manual_corto():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if archivos:
        with pdfplumber.open(archivos[0]) as pdf:
            for page in pdf.pages[:3]: # Solo 3 páginas para no saturar
                texto += page.extract_text() + "\n"
    return texto[:5000]

contexto = cargar_manual_corto()

# 3. Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Escribe tu duda aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Prueba con esta dirección exacta que es la que corresponde a lo que viste
            model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
            # Enviamos una instrucción muy corta
            response = model.generate_content(f"Contexto: {contexto}. Pregunta: {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            # Si falla, mostramos el error real de Google para saber qué pasa
            st.error(f"Error de Google: {e}")
