import pandas as pd

# 1. Carrega o CSV original
df = pd.read_csv("noticias_newsapi.csv")

# 2. Exibe os dados antes da limpeza
print("ANTES DA LIMPEZA:\n", df)

# 3. Converte a coluna de data para datetime padrão (AAAA-MM-DD, formato ISO 8601)
df["data_publicacao"] = pd.to_datetime(
    df["data_publicacao"], format="%Y-%m-%dT%H:%M:%SZ", errors="coerce"
)

# 4. Ordena as notícias da mais antiga para a mais recente
df = df.sort_values("data_publicacao")

# 5. Remove duplicatas exatas, mantendo a mais antiga, e reseta o índice
df = df.drop_duplicates(subset=["titulo", "fonte"], keep="first")
#df = df.reset_index(drop=True)
#df = df.sort_values("titulo")

# 5.1. Calcula o peso (quantidade de registros por título, após remoção de duplicatas exatas)
df["peso"] = df.groupby("titulo")["fonte"].transform("count")

# 6. Seleciona uma ocorrência por título, priorizando maior peso e mais antiga
df_unico = (
    df.sort_values(["peso", "data_publicacao"], ascending=[False, True])
      .drop_duplicates(subset="titulo", keep="first")
      .reset_index(drop=True)
)

# 7. Exibe relevância e resultado final
print("\nRELEVÂNCIA (Nº de fontes distintas por título):\n", df_unico[["titulo", "peso"]])
print("-" * 40)
print("\nDEPOIS DA LIMPEZA:\n", df_unico)

# 8. Salva o resultado em CSV compacto
# Inclui apenas as colunas que já estão no CSV de entrada + 'peso'
df_unico.to_csv(
    "noticias_limpo.csv",
    index=False,
    columns=["titulo", "descricao", "fonte", "data_publicacao", "regiao", "query_busca", "peso"]
)