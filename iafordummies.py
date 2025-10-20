import streamlit as st
import requests

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente AI Multifunción", page_icon="💡", layout="wide")

# --- ESTILO CSS (Opcional) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body { font-family: 'Roboto', sans-serif; }
    h1 { text-align: center; color: #8A2BE2; } /* Azul Violeta */
    .stButton>button { background-color: #8A2BE2; color: white; border-radius: 5px; }
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div { 
        border: 1px solid #ccc; border-radius: 5px; 
    }
    #output_result textarea { /* Estilo específico para el resultado */
        font-family: 'Roboto', sans-serif; /* Usar fuente normal para resultados */
        font-size: 1.1em;
        border: 2px solid #8A2BE2;
        height: 350px !important; /* Más alto para resultados más largos */
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE LA API ---
def execute_ai_task(api_key, task_type, **kwargs):
    """Construye el prompt adecuado según la tarea y llama a la API."""
    
    prompt = ""
    model = "openai/gpt-3.5-turbo" # Modelo por defecto
    temperature = 0.7 # Temperatura estándar

    # Construir el prompt basado en la tarea
    if task_type == "Traducir":
        prompt = f"""
        Eres un traductor experto. Traduce el siguiente texto al idioma '{kwargs.get('idioma_destino', 'Inglés')}'.
        Identifica automáticamente el idioma original.
        Devuelve ÚNICAMENTE el texto traducido.

        Texto: "{kwargs.get('texto', '')}"
        """
        temperature = 0.3
    
    elif task_type == "Resumir":
        prompt = f"""
        Eres un experto en síntesis de información. Resume el siguiente texto de forma concisa, capturando las ideas principales.
        El resumen debe ser significativamente más corto que el original.
        Devuelve ÚNICAMENTE el texto resumido.

        Texto: "{kwargs.get('texto', '')}"
        """
        temperature = 0.5

    elif task_type == "Generar Ideas":
        prompt = f"""
        Eres un generador de ideas creativo. Realiza una lluvia de ideas sobre el siguiente tema y proporciona una lista de 5 a 7 ideas originales y variadas.
        Formato: Lista numerada.
        Devuelve ÚNICAMENTE la lista de ideas.

        Tema: "{kwargs.get('tema', '')}"
        """
        temperature = 0.8 # Más creatividad

    elif task_type == "Explicar Concepto":
        prompt = f"""
        Eres un profesor experto y paciente. Explica el siguiente concepto de forma clara y sencilla, adaptada para '{kwargs.get('audiencia', 'un principiante')}'.
        Utiliza analogías si es posible. Evita jerga técnica excesiva.
        Devuelve ÚNICAMENTE la explicación.

        Concepto: "{kwargs.get('concepto', '')}"
        """
        temperature = 0.6
        
    elif task_type == "Corregir Gramática":
        prompt = f"""
        Eres un asistente de escritura meticuloso. Revisa el siguiente texto en busca de errores gramaticales y ortográficos y devuelve el texto corregido.
        Realiza solo las correcciones necesarias. No cambies el significado ni el estilo.
        Devuelve ÚNICAMENTE el texto corregido.

        Texto: "{kwargs.get('texto', '')}"
        """
        temperature = 0.2


    else:
        return "Error: Tipo de tarea no reconocida."

    if not prompt:
         return "Error: No se pudo construir el prompt."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1500, "temperature": temperature}

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=90)
        if response.status_code != 200: return f"Error HTTP {response.status_code}: {response.text}"
        data = response.json()
        if "error" in data: return f"Error de OpenRouter: {data['error'].get('message', 'Sin mensaje')}"
        ai_response = data["choices"][0]["message"]["content"]
        return ai_response.strip()
    except Exception as e:
        return f"Error interno de la aplicación: {str(e)}"

# --- INTERFAZ DE USUARIO ---
st.title("💡 Asistente AI Multifunción")
st.write("Selecciona una tarea, completa los campos y deja que la IA haga el trabajo.")

# 1. Selector de Tarea Principal
task_options = ["Traducir", "Resumir", "Generar Ideas", "Explicar Concepto", "Corregir Gramática"]
selected_task = st.selectbox("Elige la tarea que quieres realizar:", task_options)

st.markdown("---")

# 2. Campos de Entrada Condicionales
input_args = {} # Diccionario para guardar los argumentos específicos de la tarea

if selected_task == "Traducir":
    st.subheader("Parámetros para Traducir:")
    col1, col2 = st.columns(2)
    with col1:
        input_args['texto'] = st.text_area("Texto a Traducir:", height=200)
    with col2:
        input_args['idioma_destino'] = st.selectbox(
            "Idioma de Destino:",
            ("Inglés", "Francés", "Alemán", "Italiano", "Portugués", "Chino (Simplificado)", "Japonés", "Ruso", "Árabe", "Español")
        )

elif selected_task == "Resumir":
    st.subheader("Parámetros para Resumir:")
    input_args['texto'] = st.text_area("Texto a Resumir:", height=250)

elif selected_task == "Generar Ideas":
    st.subheader("Parámetros para Generar Ideas:")
    input_args['tema'] = st.text_input("Tema sobre el que generar ideas:", placeholder="Ej: Marketing para pequeñas empresas")

elif selected_task == "Explicar Concepto":
    st.subheader("Parámetros para Explicar Concepto:")
    col1, col2 = st.columns(2)
    with col1:
        input_args['concepto'] = st.text_input("Concepto a Explicar:", placeholder="Ej: Agujero negro")
    with col2:
        input_args['audiencia'] = st.selectbox("Nivel de la Audiencia:", ("Principiante", "Intermedio", "Experto", "Niño"))

elif selected_task == "Corregir Gramática":
     st.subheader("Parámetros para Corregir Gramática:")
     input_args['texto'] = st.text_area("Texto a Corregir:", height=250)


# 3. Botón para Ejecutar
st.markdown("---")
if st.button(f"Ejecutar Tarea: {selected_task}", use_container_width=True):
    # Validación básica
    is_valid = True
    if 'texto' in input_args and not input_args['texto']: is_valid = False
    if 'tema' in input_args and not input_args['tema']: is_valid = False
    if 'concepto' in input_args and not input_args['concepto']: is_valid = False
    
    if not is_valid:
        st.warning("Por favor, completa los campos requeridos para esta tarea.")
    elif "OPENROUTER_API_KEY" not in st.secrets:
        st.error("Error: La clave API no está configurada en los 'Secrets' de la aplicación.")
    else:
        api_key = st.secrets["OPENROUTER_API_KEY"]
        with st.spinner(f"Procesando tu petición de '{selected_task}'..."):
            # Pasamos el diccionario de argumentos desempaquetado a la función
            ai_result = execute_ai_task(api_key, selected_task, **input_args) 
            st.session_state.result = ai_result # Guardar en estado

# 4. Mostrar Resultado
if 'result' in st.session_state and st.session_state.result:
    st.markdown("---")
    st.subheader("Resultado de la IA:")
    # Usamos text_area para resultados que pueden ser largos y multilínea
    st.text_area("Respuesta:", value=st.session_state.result, height=350, key="output_result", disabled=True, label_visibility="collapsed")
    
    # Simple lógica para limpiar resultado si cambias de tarea (opcional)
    if selected_task != st.session_state.get('last_task', ''):
        del st.session_state.result
    st.session_state.last_task = selected_task

