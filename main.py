from google import genai
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

if __name__ == "__main__":
    queries = generate_query("Que es una bola en topologia?")
    print("Queries: " + str(queries))
    print(search_notes(queries))
