import pandas as pd
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# 1) Carrega o CSV já limpo da 3.1
df = pd.read_csv("noticias_limpo.csv")

# 2) Carrega o modelo de NLP do spaCy para PT
nlp = spacy.load("pt_core_news_sm")
#    - 'nlp' é o objeto que faz tokenização, reconhecimento de stopwords,
#      POS-tagging e lematização em português.

# 3) Função de pré-processamento
def preprocess(text):
    doc = nlp(text.lower())
    #    - .lower(): tudo em minúsculas para uniformizar.

    lemmas = []
    for token in doc:
        # token.is_alpha  → só palavras (sem números, pontuação, URLs)
        # not token.is_stop → retira “de”, “que”, “o”, etc.
        if token.is_alpha and not token.is_stop:
            lemmas.append(token.lemma_)
            # lemma_: forma base da palavra (“hospitalizações”→“hospitalização”)
    return " ".join(lemmas)

# 4) Monta o corpus de texto
df["corpus"] = (
    df["titulo"].fillna("") + " " +
    df["descricao"].fillna("")
).apply(preprocess)
#    - concatena título + descrição
#    - .fillna("") evita erros se algum for nulo
#    - .apply(preprocess) gera a coluna processada

# 5) Vetorização Bag-of-Words com uni-grams e bi-grams
vectorizer = CountVectorizer(
    ngram_range=(1, 2),   # inclui também pares de palavras
    max_df=0.95,           # descarta termos em >95% dos documentos
    min_df=1               # mantém termos que ocorrem em pelo menos 1 doc
)
X = vectorizer.fit_transform(df["corpus"])
#    - X é uma matriz (n_docs × n_palavras), com contagem de cada palavra

# 6) Configuração e treino do LDA !!!!
n_topics = 5
lda = LatentDirichletAllocation(
    n_components=n_topics,
    random_state=42  # fixa aleatoriedade para resultados reprodutíveis
)
lda.fit(X)
#    - o LDA aprende 5 “tópicos” como distribuições de palavras

# 7) Mostrar as top-10 palavras de cada tópico
palavras = vectorizer.get_feature_names_out()
for i, comp in enumerate(lda.components_):
    top_indices = comp.argsort()[-10:]
    top_palavras = [palavras[j] for j in top_indices]
    print(f"Tópico {i}: {', '.join(top_palavras)}")
#    - lda.components_[i] é um array com peso de cada palavra para o tópico i

# 8) Atribuir o tópico dominante a cada notícia
distribuicoes = lda.transform(X)
#    - transforma cada documento em um vetor de probabilidades (tamanho n_topics)
df["id_topico"] = distribuicoes.argmax(axis=1)
#    - .argmax(axis=1) retorna o índice do tópico com maior probabilidade

# 9) Mapear para nomes legíveis
nomes = {
    0: "Eleições Presidenciais",
    1: "Disputa Senado/PL",
    2: "Pesquisa e Intenção de Voto",
    3: "Casos e Investigações Locais",
    4: "Alianças Partidárias"
}

df["nome_topico"] = df["id_topico"].map(nomes)
#    - você ajusta esses nomes após ver as palavras de cada tópico no passo 7

# 10) Salvar o DataFrame final
df.to_csv("noticias_com_topicos.csv", index=False)
#    - gera o CSV com as colunas antigas + id_topico + nome_topico