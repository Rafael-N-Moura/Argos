### **Plano de Ação Técnico: Construção do MVP**

Projeto: Plataforma de Inteligência Política (Nome Provisório: Argos)

Versão: 1.0 (MVP)

Objetivo: Construir um produto mínimo viável funcional para validar a proposta de valor central: transformar dados de mídia e redes sociais em inteligência geográfica e de sentimento para campanhas políticas regionais.

### **Visão Geral do Fluxo de Trabalho**

O MVP será construído em um pipeline de 5 fases sequenciais. Cada fase utiliza ferramentas específicas para transformar dados brutos em um dashboard de inteligência interativo.

### **Fase 1: Configuração do Ambiente (A Fundação)**

**Objetivo:** Preparar todo o ambiente de desenvolvimento e obter as credenciais de acesso necessárias.

- **Atividade 1.1: Configurar Ambiente Python**
- **Ferramentas:** Python (versão 3.9 ou superior), um gerenciador de pacotes (pip) e um ambiente virtual (venv).
- **Passo a Passo:**
1. Instalar o Python no computador de desenvolvimento.
2. Criar uma pasta para o projeto.
3. Dentro da pasta, criar um ambiente virtual com o comando: python -m venv venv.
4. Ativar o ambiente virtual.
5. Instalar as bibliotecas iniciais com pip: pip install requests beautifulsoup4 pandas tweepy spacy scikit-learn transformers torch sqlite3.
- **Atividade 1.2: Obter Chaves de API**
- **Ferramentas:** Contas de desenvolvedor na NewsAPI e na plataforma X.
- **Passo a Passo:**
1. **NewsAPI:** Registrar-se no site newsapi.org para obter uma chave de API do plano gratuito ("Developer").
2. **X (Twitter):** Aplicar para uma conta de desenvolvedor no portal developer.twitter.com e assinar o plano "Free" para obter as chaves de API necessárias (API Key, API Secret, Bearer Token).
3. Armazenar essas chaves de forma segura (ex: em variáveis de ambiente) para que o script Python possa acessá-las.
- **Atividade 1.3: Preparar a Plataforma de Visualização**
- **Ferramentas:** Conta Google.
- **Passo a Passo:**
1. Criar uma nova **Planilha Google** que servirá como a ponte entre nosso script e o dashboard.
2. Acessar o **Google Looker Studio** (lookerstudio.google.com) com a mesma conta.

### **Fase 2: Coleta de Dados Automatizada (Os Coletores)**

**Objetivo:** Desenvolver os scripts Python que buscarão os dados brutos de notícias e tweets.

- **Atividade 2.1: Desenvolver o Scraper Hiperlocal**
- **Ferramentas:** Python, Requests, Beautiful Soup 4.
- **Passo a Passo:**
1. **Curadoria Manual:** Criar um arquivo de configuração (ex: um JSON ou CSV) mapeando fontes de mídia hiperlocais às suas respectivas regiões (ex: {"blog_do_mario_flavio": "Agreste", "g1_caruaru": "Agreste"}).
2. Script de Scraping: Escrever uma função em Python que:
    
    a. Lê a lista de sites do arquivo de configuração.
    
    b. Para cada site, usa requests.get() para baixar o HTML.
    
    c. Usa BeautifulSoup() para analisar o HTML e extrair as manchetes, links e datas, seguindo as regras específicas de cada site.
    
    d. Armazena os resultados em uma lista de dicionários Python, já com a etiqueta da região.
    
- **Atividade 2.2: Desenvolver o Coletor da NewsAPI**
- **Ferramentas:** Python, Requests.
- **Passo a Passo:**
1. Escrever uma função que monta uma URL de requisição para a NewsAPI, incluindo a chave de API e a query de busca (ex: "Roberto Neves" AND "Pernambuco").
2. Usa requests.get() para fazer a chamada à API.
3. Processa a resposta (que vem em formato JSON) e extrai as manchetes, fontes e datas.
- **Atividade 2.3: Desenvolver o Coletor do X (Twitter)**
- **Ferramentas:** Python, Tweepy.
- **Passo a Passo:**
1. Escrever uma função que se autentica na API do X usando as chaves obtidas e a biblioteca Tweepy.
2. Realiza uma busca por tweets recentes que mencionem o nome do candidato (ex: "Roberto Neves" -is:retweet).
3. Coleta o texto de cada tweet, o nome do usuário, e métricas de engajamento (curtidas, retweets).

### **Fase 3: Processamento e Análise de IA (O Cérebro)**

**Objetivo:** Transformar os dados brutos coletados em dados estruturados e enriquecidos com insights.

- **Atividade 3.1: Limpeza e Estruturação com Pandas**
- **Ferramentas:** Python, Pandas.
- **Passo a Passo:**
1. Carregar todos os dados coletados (scraping, NewsAPI, X) em DataFrames do Pandas.
2. Unificar os dados de notícias em um único DataFrame, removendo duplicatas.
3. Padronizar formatos (especialmente datas).
- **Atividade 3.2: Análise de Pautas da Mídia (Topic Modeling)**
- **Ferramentas:** Python, spaCy, Scikit-learn.
- **Passo a Passo:**
1. Para cada manchete no DataFrame de notícias, usar o spaCy para limpar e lematizar o texto.
2. Alimentar a lista de manchetes limpas no modelo LatentDirichletAllocation (LDA) do Scikit-learn para agrupar as notícias em tópicos.
3. Mapear os tópicos gerados (que são apenas números e listas de palavras) para nomes legíveis (ex: Tópico 1 -> "Saúde Pública").
4. Adicionar uma nova coluna id_topico ao DataFrame de notícias, associando cada notícia ao seu tema.
- **Atividade 3.3: Análise de Sentimento dos Tweets**
- **Ferramentas:** Python, Transformers.
- **Passo a Passo:**
1. Carregar um modelo de análise de sentimento pré-treinado para português da biblioteca Transformers (Hugging Face).
2. Para cada tweet no DataFrame do X, passar o texto pelo modelo.
3. O modelo retornará uma classificação ("Positivo", "Neutro", "Negativo").
4. Adicionar uma nova coluna sentimento ao DataFrame de tweets com essa classificação.

### **Fase 4: Armazenamento dos Dados Processados (A Memória)**

**Objetivo:** Salvar os dados enriquecidos de forma persistente e organizada.

- **Atividade 4.1: Persistência dos Dados**
- **Ferramentas:** Python, sqlite3 (ou gspread para Planilhas Google).
- **Passo a Passo:**
1. **Opção SQLite:** Usar a biblioteca sqlite3 para criar um arquivo de banco de dados (radar_politico.db). Criar duas tabelas: noticias e tweets. Usar o método .to_sql() do Pandas para salvar os DataFrames processados diretamente nessas tabelas.
2. **Opção Planilhas Google (Recomendada para o MVP):** Usar a biblioteca gspread para se autenticar na API do Google Sheets. Criar duas abas na planilha ("Notícias" e "Tweets"). Usar uma função para converter os DataFrames e popular essas abas.

### **Fase 5: Visualização e Interatividade (A Interface)**

**Objetivo:** Apresentar os insights de forma clara e interativa para o usuário final.

- **Atividade 5.1: Construção do Dashboard**
- **Ferramentas:** Google Looker Studio.
- **Passo a Passo:**
1. **Conectar Fonte de Dados:** No Looker Studio, criar uma nova fonte de dados conectada à Planilha Google criada na Fase 4.
2. **Criar o Layout:** Arrastar e soltar os componentes visuais na tela.
3. **Configurar Gráficos:**
- **Mapa de Calor:** Configurar para usar a coluna estado como dimensão de localização e a contagem de notícias como métrica de cor.
- **Termômetro de Sentimento:** Usar um gráfico de pizza ou barras empilhadas com a coluna sentimento como dimensão.
- **Gráfico de Pautas:** Usar um gráfico de barras com a coluna id_topico como dimensão e a contagem de notícias como métrica.
- **Tabelas:** Configurar as tabelas para exibir as colunas relevantes de manchetes e tweets.
1. **Ativar Interatividade:** Garantir que a opção "Aplicar filtro" esteja ativa nos gráficos principais (mapa e gráfico de pautas) para que eles controlem os outros elementos do dashboard.
2. **Finalizar o Design:** Adicionar títulos, textos explicativos e ajustar as cores para criar uma experiência de usuário profissional.
