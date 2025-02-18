import requests
import chromadb
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import logging

# #Ukrywanie loggingu ChromaDB (Add of existing embedding ID: ...)
# logging.getLogger("chromadb").setLevel(logging.CRITICAL)

#OMDb API
OMDB_API_KEY = "1f91d301"
OMDB_URL = "http://www.omdbapi.com/"

#Inicjalizacja modelu do embeddingów
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

#Inicjalizacja bazy wektorowej
chroma_client = chromadb.PersistentClient(path="./chroma_db")

#Czyszczenie kolekcji filmów -> (usunięcie i utworzenie nowej)
chroma_client.delete_collection("movies")  
collection = chroma_client.get_or_create_collection(name="movies")  

#Pobieranie danych o filmie i zapisywanie w bazie 
def add_movie_to_db(title):
    params = {"t": title, "apikey": OMDB_API_KEY}
    response = requests.get(OMDB_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            movie_id = data.get("Title")

            #SPRAWDZANIE, CZY FILM JUŻ ISTNIEJE W BAZIE
            existing = collection.get(ids=[movie_id])
            if existing and existing["ids"]:  
                return f"Film '{title}' już istnieje w bazie."

            # Pobranie konkretnych pól
            movie_info = f"Tytuł: {data.get('Title')}\nRok: {data.get('Year')}\nGatunek: {data.get('Genre')}\nReżyser: {data.get('Director')}\nObsada: {data.get('Actors')}\nOpis: {data.get('Plot')}"
            embedding = embedding_model.encode(movie_info).tolist()
            
            print("\n\n")
            print(movie_info)
            print("\n\n")

            collection.add(documents=[movie_info], embeddings=[embedding], ids=[movie_id])
            return f"Dodano do bazy: {title}"
        else:
            return f"Nie znaleziono filmu: {title}"
    return "Błąd w zapytaniu do OMDb API."

#Dodawanie filmów do bazy
print(add_movie_to_db("Substance"))
print(add_movie_to_db("Gladiator II"))
print(add_movie_to_db("A Different Man"))
print("\n")

#Pobieranie informacji na podstawie zapytania użytkownika
def retrieve_info(query):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=1)

    if results["documents"]:
        return results["documents"][0][0]  
    return "Nie znaleziono pasujących informacji."

#InicjalizacjaLLaMA
llm = Llama(model_path="C:\\M\\Studia\\SEM2\\Projekt_badawczy\\llama\\llama.cpp\\models\\Llama-3.2-1B-Instruct-Q4_K_M.gguf", 
            n_gpu_layers=35,
            n_ctx=8192,  
            verbose=False
)

#Zadawanie pytań modelowi
user_query = "Kto gra główną rolę w filmie Substance wyprodukowanym w 2024?"
retrieved_info = retrieve_info(user_query)

print("\n\n")
print(retrieved_info)
print("\n\n")

prompt = f"Oto informacje znalezione w bazie:\n\n{retrieved_info}\n\n{user_query}"

response = llm.create_chat_completion(
    messages=[{"role": "user", "content": prompt}]
)

print("\n\n")
print(response["choices"][0]["message"]["content"])
print("\n\n")

#Zwolnienie pamięci
del llm
import gc
gc.collect()
