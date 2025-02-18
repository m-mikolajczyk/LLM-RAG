from llama_cpp import Llama

# n_ctx to maksymalna długość kontekstu modelu, czyli liczba tokenów, które model może pamiętać w jednej interakcji
# verbose usuwa logi
llm = Llama(model_path="C:\M\Studia\SEM2\Projekt_badawczy\llama\llama.cpp\models\Llama-3.2-1B-Instruct-Q4_K_M.gguf", 
            n_gpu_layers = 35,
            n_ctx = 1024,
            verbose = False 
            ) 


response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "Can you tell me something about movie Substance"}]
)
print(response["choices"][0]["message"]["content"])

