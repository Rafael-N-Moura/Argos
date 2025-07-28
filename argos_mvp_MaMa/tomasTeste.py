import requests
import pandas as pd
from datetime import datetime

### 1. Chave da NewsAPI (adicione a sua aqui)
API_KEY = "050b9ea04ae549bdb25f223d9964c1c9"

### 2. Parâmetros de busca
QUERY = '"Lula" AND Brasil'
LANGUAGE = "pt"
FROM_DATE = "2025-07-01"
TO_DATE = "2025-07-27"
PAGE_SIZE = 100
MAX_PAGES = 1

### 3. Lista para armazenar as notícias
noticias = []

### 4. Loop de coleta
for page in range(1, MAX_PAGES + 1):
    url = (
        f"https://newsapi.org/v2/everything?q={QUERY}&language={LANGUAGE}"
        f"&from={FROM_DATE}&to={TO_DATE}&pageSize={PAGE_SIZE}&page={page}&apiKey={API_KEY}"
    )
    resposta = requests.get(url)
    dados = resposta.json()

    if "articles" not in dados:
        print("Erro na requisição ou limite da API atingido:", dados)
        break

    for artigo in dados["articles"]:
        noticias.append({
            "titulo": artigo.get("title", ""),
            "descricao": artigo.get("description", ""),
            "fonte": artigo.get("source", {}).get("name", ""),
            "data_publicacao": artigo.get("publishedAt", ""),
            "regiao": "Pernambuco",
            "query_busca": QUERY
        })

### 5. Salvar CSV
df = pd.DataFrame(noticias)
df.to_csv("noticias_newsapi2.csv", index=False)

print("Coleta finalizada. Total de notícias coletadas:",len(df))