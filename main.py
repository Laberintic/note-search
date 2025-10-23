from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import re


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
    preprompt = """
    Necesito que, dada una pregunta, idea o termino de busqueda, generes
    entre 5 y 7 terminos de busqueda concretos relacionados con ese tema.
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
                            notes_with_appearences.append((os.path.join(root, file), count))

    sorted_results = sorted(notes_with_appearences, key=lambda x: x[1])

    return sorted_results


def search_to_context_str(search: list, n: int) -> str:
    """
    Will return the first n results as a big concatenated string
    """

    result = ""
    for (note, count) in search[:n]:
        result += note

    return result


class Chat():
    chat_history = []

    system_prompt = """You are a helful assistant. I will pass you some context information about some topics i want to
    discuss. Try to answer my questions as acuratelly as possible given the information i pass in the context. Do it in 
    concise and clear manner, and try to explain as good as you can.
    """

    context_preprompt = """Here you have my notes on some topics i want to discuss. Take into account all of the ideas
    mentioned. text between double square brackets represents links to other notes (example [[bola]] links to 'bola' note)
    text between dollar signs and double dollar signs shall be read as latex ecuations. Here you go:
    """

    context_response = """Perfect! I will be glad to respond to your questions. What do you want to know about?"""

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
        return self.chat.send_message(client_message).text

    def get_history(self):
        return self.chat.get_history()

    def print_entire_chat(self):
        for message in self.chat.get_history():
            print(f'role - {message.role}',end=": ")
            print(message.parts[0].text)





if __name__ == "__main__":
    question = input("Question: ")

    queries = generate_query(question)

    print("DEBUG: queries:" + str(queries))

    notes_list = search_notes(queries)

    print("DEBUG: notes: " + str(notes_list))

    context = search_to_context_str(notes_list, 5)

    mychat = Chat(context)

    print(mychat.get_response(question))
    print("-------------------------------------")

    follow_up = input("Follow up: ")

    print(mychat.get_response(follow_up))