import streamlit as st
import google.generativeai as genai
import os
import pdfplumber

# 1. Configuración de API
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Configuración visual de la aplicación
st.set_page_config(page_title="Profesor de Logística Pro", page_icon="📚")
st.title("🎓 Profesor de Logística (Modo Lectura Profunda)")

# 2. Lógica de procesamiento de gran volumen
@st.cache_data
def cargar_manuales_extensos():
    texto_combinado = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not archivos:
        return "No hay documentos cargados en el repositorio."

    for nombre_archivo in archivos:
        try:
            with pdfplumber.open(nombre_archivo) as pdf:
                # Leemos hasta 100 páginas del documento
                paginas_objetivo = pdf.pages[:100] 
                
                texto_combinado += f"\n--- INICIO DEL DOCUMENTO: {nombre_archivo} ---\n"
                
                for i, page in enumerate(paginas_objetivo):
                    contenido = page.extract_text()
                    if contenido:
                        texto_combinado += f"[Pág. {i+1}] {contenido}\n"
                
                texto_combinado += f"--- FIN DEL DOCUMENTO: {nombre_archivo} ---\n"
        except Exception as e:
            # Si falla un archivo, continúa con el siguiente
            continue
            
    # Límite de 100,000 caracteres. 
    # Esto equivale aproximadamente a 150-200 páginas de texto puro.
    return texto_combinado[:100000]

# El profesor procesa la información en segundo plano
with st.spinner("El profesor está leyendo los manuales... esto puede tardar un momento."):
    contexto_profesor = cargar_manuales_extensos()

# 3. Interfaz de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de preguntas
if prompt := st.chat_input("Haz una pregunta técnica sobre los manuales..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Usamos Gemini 3 Flash Preview por su gran ventana de contexto
            model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
            
            # Instrucción robusta
            instruccion = (
                f"Eres un profesor experto en transporte terrestre y normativa logística. "
                f"Analiza los siguientes documentos (hasta 100 páginas por archivo):\n\n"
                f"{contexto_profesor}\n\n"
                f"Instrucciones: Responde de forma detallada. Si mencionas un dato específico, "
                f"indica de qué archivo proviene si es posible.\n\n"
                f"Pregunta del alumno: {prompt}"
            )
            
            response = model.generate_content(instruccion)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                st.error("Los documentos son muy extensos para la cuota gratuita actual. Espera 1 minuto o reduce la cantidad de PDFs en GitHub.")
            else:
                st.error(f"Error: {e}")
