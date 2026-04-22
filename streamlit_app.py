import streamlit as st
import google.generativeai as genai
import os
import pdfplumber

# 1. Configuración de API y Seguridad
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.set_page_config(page_title="Profesor de Logística Actualizado", page_icon="📚")
st.title("🎓 Profesor de Logística (Lectura Total)")

# 2. Función de procesamiento dinámico
@st.cache_data(show_spinner=False)
def cargar_todo_el_conocimiento(lista_archivos):
    texto_combinado = ""
    
    if not lista_archivos:
        return "No hay documentos cargados en el repositorio."

    for nombre_archivo in lista_archivos:
        try:
            with pdfplumber.open(nombre_archivo) as pdf:
                total_paginas = len(pdf.pages)
                # Leemos hasta 100 páginas por documento
                limite_paginas = min(total_paginas, 100)
                
                texto_combinado += f"\n--- DOCUMENTO DETECTADO: {nombre_archivo} ---\n"
                
                for i in range(limite_paginas):
                    contenido = pdf.pages[i].extract_text()
                    if contenido:
                        texto_combinado += f"[Archivo: {nombre_archivo} - Pág {i+1}]: {contenido}\n"
        except Exception:
            continue 
            
    # Límite de seguridad para evitar errores de saturación en la API
    # Aquí estaba el error anterior, ya está corregido a 'texto_combinado'
    return texto_combinado[:120000]

# --- Lógica de Actualización Automática ---
# Listamos los archivos fuera para que Streamlit detecte cambios en GitHub
archivos_en_repositorio = sorted([f for f in os.listdir('.') if f.endswith('.pdf')])

# Si la lista de archivos cambia, la caché se invalida automáticamente
contexto_profesor = cargar_todo_el_conocimiento(archivos_en_repositorio)

# 3. Interfaz de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Haz una pregunta sobre cualquier manual cargado..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
            
            nombres_archivos = ", ".join(archivos_en_repositorio)
            
            instruccion = (
                f"Eres un profesor experto en logística. Tienes acceso a estos archivos: {nombres_archivos}.\n\n"
                f"Contenido de los manuales:\n{contexto_profesor}\n\n"
                f"Pregunta del alumno: {prompt}\n\n"
                "Responde usando la información de todos los archivos disponibles."
            )
            
            response = model.generate_content(instruccion)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error de Google: {e}")
