import requests
import time
import json
import itertools

API_KEY = "1f91d301"  # Podmień na swój klucz API
BASE_URL = "https://www.omdbapi.com/"

# Funkcja do pobierania filmów dla danego wzorca w tytule
def search_movies_by_pattern(pattern):
    url = f"{BASE_URL}?apikey={API_KEY}&s={pattern}&type=movie&y=2024"
    response = requests.get(url)
    data = response.json()
    print(f"Zapytanie: {url}")  # Debugowanie
    
    if data.get("Response") == "True":
        return data.get("Search", [])
    return []

# Pobieranie szczegółowych informacji o filmie
def get_movie_details(imdb_id):
    url = f"{BASE_URL}?apikey={API_KEY}&i={imdb_id}&plot=full"
    response = requests.get(url)
    return response.json()

# Pobieranie filmów z różnymi wzorcami
def get_all_movies_2024():
    all_movies = []
    seen_ids = set()
    request_count = 0

    # Tworzymy listę wzorców od "a", "b", ..., "z", "aa", "ab", ..., "zz"
    patterns = list("abcdefghijklmnopqrstuvwxyz") + [''.join(p) for p in itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=2)]
    
    for pattern in patterns:
        if request_count >= 1000:
            break  # Limit dzienny osiągnięty
        
        movies = search_movies_by_pattern(pattern)
        request_count += 1
        time.sleep(1)  # Uniknięcie blokady API
        
        for movie in movies:
            imdb_id = movie["imdbID"]
            if imdb_id not in seen_ids:
                seen_ids.add(imdb_id)

                if request_count >= 1000:
                    break  # Osiągnięto limit zapytań

                details = get_movie_details(imdb_id)
                request_count += 1
                time.sleep(1)
                
                if details.get("Response") == "True":
                    all_movies.append(details)

    return all_movies

# Pobranie wszystkich filmów
movies_2024 = get_all_movies_2024()

# Zapisanie wyników do pliku JSON
with open("movies_2024.json", "w", encoding="utf-8") as f:
    json.dump(movies_2024, f, indent=4, ensure_ascii=False)

print(f"Pobrano {len(movies_2024)} filmów z 2024 roku.")
