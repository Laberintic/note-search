from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import re
import logging

import streamlit as st


MAX_NOTES = 100

QUERIES_MIN = 5
QUERIES_MAX = 12

def get_obsidian_path():
    safeload_env()
    return os.environ.get("OBSIDIAN_PATH")

env_loaded = False


def safeload_env():
    global env_loaded
    if env_loaded: return
    load_dotenv()
    env_loaded = True


def generate_query(prompt: str) -> list:
    preprompt = f"""
    Necesito que, dada una pregunta, idea o termino de busqueda, generes
    entre {QUERIES_MIN} y {QUERIES_MAX} terminos de busqueda concretos relacionados con ese tema.
    No hagas terminos genericos. Cada termino deberia ser de una palabra de longitud
    pues se va a buscar cuantas veces aparece en distintos apuntes. Cada termino
    debe tener como maximo dos palabras de longitud.
    Si la palabra lleva tildes, ponlas.
    Devuelvelo en el siguiente formato "termino1,termino2,termino3...", sin 
    espacios entre las comas.
    Te doy un ejemplo. La pregunta del usuario es "¿Como vuelan los aviones?".
    Un par de terminos de busqueda serian:
    "principios aerodinámicos,alas,sustentación,motor avión,aerodinámica,forma ala,fuerzas vuelo"
    Ahora genera la respuesta a esta pregunta: 
    """

    safeload_env()

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=preprompt + prompt,
    )

    return response.text.split(",")


def search_notes(queries: list) -> list:
    """
    Searches through the notes given for appearances of each of the 
    queries passed in the queries list.

    Parameters:
    queries - a list of strings

    Returns:
    a list of tuples (filepath, query appearance)
    """
    notes_with_appearences = []
    

    for root, _, files in os.walk(get_obsidian_path()):
        for query in queries:
            pattern = r"\b" + re.escape(query) + r"\b"
            for file in files:
                if file.endswith(".md"):
                    with open(os.path.join(root, file), "r") as f:
                        contents = f.read()
                        count = len(re.findall(pattern, contents))

                        # honestly dont know how this regex works, but it does. Cool!

                        if count > 0:
                            notes_with_appearences.append((os.path.join(root, file), count, contents))

    sorted_results = sorted(notes_with_appearences, key=lambda x: x[1])

    return sorted_results


def search_until_finds(question: str, max_tries: int) -> str:
    """
    Centralizes the entire searching process
    """

    queries = generate_query(question)
    logging.info("Generated queries: %s", str(queries))
    notes = search_notes(queries)
    logging.info("Found a total of %d related notes", len(notes))

    # TODO: make it select the notes?
    prompt = f"Como asistente, es suficiente este contexto para responder a '{question}', es decir, menciona la idea o ideas? responde unicamente 'si' o 'no', pon un guion '-' y explica por que. CONTEXTO" + search_to_context_str(notes, MAX_NOTES) + "FIN DE CONTEXTO"

    prompt = f"""
    Como asistente que ha de responder a esta pregunta: '{question}', cuales de las notas pasadas son las mas
    utiles y por tanto deberian ser pasadas al encargado de respodner a la pregunta de la forma mas correcta
    posible? No tiene porque ser el tema concreto pues tal vez no existe nota para tal tema, pero temas similares
    o relacionados. Devuelvelos de una en una, con el nombre entero del path.
    Ejemplo:
    /path/to/notea.md
    /path/to/noteb.md
    Fin ejemplo. Ahora tu. Aqui tienes el contexto.
    INICIO CONTEXTO
    {search_to_context_str(notes, MAX_NOTES)}
    FIN CONTEXTO
    """

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )

    result = []
    for note in notes:
        if note[0] in response.text:
            result.append(note)

    if len(result) == 0:
        logging.info("No notes found.")
        return "NO NOTES FOUND. APOLOGIZE TO THE USER, OUR SYSTEM FAILED"

    logging.info(f"Selected the following notes: \n{"\n".join(f"{i+1}. {item[:-1]}" for i, item in enumerate(result))}")

    return search_to_context_str(result, MAX_NOTES)

    

    # past_queries = []
    # past_queries.append(queries)
    
    # for i in range(max_tries):
    #     logging.debug("Starting try %d.", i)
    #     if len(notes) > 0:
    #         logging.debug("Try sucessful.")
    #         return search_to_context_str(notes, 5)
    #     queries = generate_query(question + "- DO NOT INCLUDE: " + str(past_queries))
    #     notes = search_notes(queries)
    #     past_queries.append(queries)


def search_to_context_str(search: list, n: int) -> str:
    """
    Will return the first n results as a big concatenated string
    """
    # TODO: limit size

    result = ""
    for (note, count, context) in search:
        result += f"""AQUI TIENES LA SIGUIENTE NOTA RELEVANTE; APOTAYE EN ELLA PARA RESPONDER:
        (Nombre de la nota: {note}). CONTENIDOS:
        """
        result += context
        result += f"FIN DE LA NOTA {note}"

    return result


class Chat():
    chat_history = []

    system_prompt = """Eres un asistente servicial. Te proporcionaré información contextual sobre algunos temas que quiero discutir. Intenta responder a mis preguntas lo más exactamente posible según la información que te proporcione en el contexto. Hazlo de manera concisa y clara, y trata de explicar lo mejor que puedas.
    """

    context_preprompt = """
Aquí tienes mis notas sobre algunos temas que quiero discutir. Ten en cuenta todas las ideas mencionadas.
Trata de responder a mi pregunta de la forma mas correcta aunque no encuentres el tema concreto, casi siempre
habra textos con ideas similares o relacionadas. Si realmente no encuentras nada, disculpate y explica por que.
Siempre trata de mencionar de donde sacas las ideas. Prefiere una respuesta mas superficial y basada en notas
a una mas compleja que no este en notas.
El texto entre dobles corchetes representa enlaces a otras notas (por ejemplo, [[bola]] enlaza a la nota “bola”).
El texto entre signos de dólar y dobles signos de dólar debe leerse como ecuaciones en LaTeX. Aquí tienes:
    """

    context_response = """¡Perfecto! Estaré encantado de responder a tus preguntas. ¿Sobre qué te gustaría saber?
"""

    def __init__(self, context):
        safeload_env()

        self.client = genai.Client()
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt
            ),
            history=[types.Content(role="user", parts=[types.Part(text=self.context_preprompt + context)]),
                        types.Content(role="model", parts=[types.Part(text=self.context_response)]),]
        )

    def get_response(self, client_message):
        logging.debug("Waiting for API response.")
        return self.chat.send_message_stream(client_message)

    def get_history(self):
        return self.chat.get_history()

    def print_entire_chat(self):
        for message in self.chat.get_history():
            print(f'role - {message.role}',end=": ")
            print(message.parts[0].text)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

        # --- PAGE SETUP ---
    st.set_page_config(page_title="AI Chatbot", layout="wide")

    # --- SESSION STATE INIT ---
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None

    # --- HELPER FUNCTIONS ---
    def new_chat():
        """Create a new empty chat session."""
        chat_id = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[chat_id] = {"messages": [], "chat_instance": None}
        st.session_state.current_chat = chat_id

    def delete_chat(chat_id):
        """Safely delete a chat and switch to another if available."""
        if chat_id in st.session_state.chats:
            del st.session_state.chats[chat_id]
        if st.session_state.chats:
            # Pick the most recent remaining chat as current
            st.session_state.current_chat = list(st.session_state.chats.keys())[-1]
        else:
            new_chat()

    # --- INITIAL STATE ---
    if not st.session_state.chats:
        new_chat()

    # --- SIDEBAR ---
    st.sidebar.title("💬 Chats")

    # New chat button
    if st.sidebar.button("➕ New Chat", use_container_width=True):
        new_chat()
        st.rerun()

    # Chat list
    for chat_id in list(st.session_state.chats.keys()):
        is_selected = chat_id == st.session_state.current_chat
        cols = st.sidebar.columns([0.8, 0.2])
        if cols[0].button(chat_id, use_container_width=True):
            st.session_state.current_chat = chat_id
            st.rerun()
        if cols[1].button("🗑️", key=f"del_{chat_id}"):
            delete_chat(chat_id)
            st.rerun()

    # --- MAIN CHAT UI ---
    chat_data = st.session_state.chats[st.session_state.current_chat]
    st.title("🤖 AI Chatbot")

    # Display messages
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Display user message
        st.chat_message("user").markdown(user_input)
        chat_data["messages"].append({"role": "user", "content": user_input})

        # Create a new chat on first run
        if chat_data["chat_instance"] is None:
            context = search_until_finds(user_input, 3)
            chat_data["chat_instance"] = Chat(context)

        # Stream the AI response inside the assistant message container
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            ai_response = chat_data["chat_instance"].get_response(user_input)
            for chunk in ai_response:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")

            # Final clean message (no cursor)
        response_placeholder.markdown(full_response)

        # Save to history
        chat_data["messages"].append({"role": "assistant", "content": full_response})