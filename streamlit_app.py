import streamlit as st
import google.generativeai as genai
import os
import pdfplumber

# 1. Configuración
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("🎓 Profesor de Logística")

# 2. Leer todos los PDFs disponibles (Optimizado)
@st.cache_data
def cargar_manuales_dinamicos():
    texto_combinado = ""
    # Busca todos los archivos que terminen en .pdf
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not archivos:
        return "No hay documentos PDF cargados en el repositorio."

    for nombre_archivo in archivos:
        try:
            with pdfplumber.open(nombre_archivo) as pdf:
                # Extrae las primeras 2 páginas de cada archivo para no saturar
                for page in pdf.pages[:2]:
                    contenido = page.extract_text()
                    if contenido:
                        texto_combinado += f"--- Fuente: {nombre_archivo} ---\n"
                        texto_combinado += contenido + "\n\n"
        except Exception as e:
            print(f"Error leyendo {nombre_archivo}: {e}")
            
    # Mantenemos un límite de 10,000 caracteres para proteger la cuota gratuita
    return texto_combinado[:10000]

# Llamamos a la función que ahora busca múltiples archivos
contexto = cargar_manuales_dinamicos()

# Mostrar qué archivos está leyendo el profesor (Opcional, para confirmar)
with st.expander("Ver documentos detectados"):
    archivos_detectados = [f for f in os.listdir('.') if f.endswith('.pdf')]
    st.write(archivos_detectados)

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
            # Usamos el modelo que confirmamos que tienes activo
            model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
            
            # Instrucción al modelo
            instruccion = f"Eres un experto en transporte. Basado en este contexto: {contexto}, responde: {prompt}"
            
            response = model.generate_content(instruccion)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error de Google: {e}")
