import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Profesor de Logística 24/7", layout="centered")
st.title("🎓 LogiPro: Tu Profesor de Logística")

# 1. Configurar la API Key (la pondremos de forma segura en Streamlit más adelante)
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 2. Definir las instrucciones del profesor
SYSTEM_PROMPT = """
Eres un profesor experto en Logística y Supply Chain. 
Tu objetivo es guiar al usuario basándote en los manuales proporcionados.
Responde de forma didáctica, usa ejemplos y asegúrate de que el alumno aprenda.
Si no sabes algo basado en la info suministrada, admítelo con profesionalismo.
"""

# Inicializar el modelo
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=SYSTEM_PROMPT
)

# Historial de chat para la sesión actual
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("¿Qué duda logística tienes hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del profesor
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
