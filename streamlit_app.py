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
# No usamos ttl para que se actualice cada vez que detecte cambios en los archivos de la carpeta
@st.cache_data(show_spinner=False)
def cargar_todo_el_conocimiento(lista_archivos):
    texto_combinado = ""
    
    if not lista_archivos:
        return "No hay documentos cargados en el repositorio."

    for nombre_archivo in lista_archivos:
        try:
            with pdfplumber.open(nombre_archivo) as pdf:
                total_paginas = len(pdf.pages)
                # Determinamos cuántas páginas leer (hasta 100, pero con un máximo de seguridad)
                limite_paginas = min(total_paginas, 100)
                
                texto_combinado += f"\n--- DOCUMENTO DETECTADO: {nombre_archivo} ---\n"
                
                for i in range(limite_paginas):
                    contenido = pdf.pages[i].extract_text()
                    if contenido:
                        texto_combinado += f"[Archivo: {nombre_archivo} - Pág {i+1}]: {contenido}\n"
        except Exception:
            continue # Salta archivos corruptos o bloqueados
            
    # Límite de seguridad para evitar errores de saturación en la API (aprox 120,000 caracteres)
    return texto_combined[:120000]

# --- Lógica de Actualización Automática ---
# Listamos los archivos fuera de la función cacheada para detectar cambios reales
archivos_en_repositorio = sorted([f for f in os.listdir('.') if f.endswith('.pdf')])

# Si cambias archivos en GitHub, esta línea detectará que la lista es distinta y recargará
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
            # Gemini 3 Flash soporta contextos masivos
            model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
            
            # Construimos la instrucción enviando la lista de archivos detectados para que la IA sepa qué tiene
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
            st.error(f"Error: {e}")
            st.info("Si acabas de subir archivos, espera 1 minuto a que GitHub sincronice y refresca la página.")
