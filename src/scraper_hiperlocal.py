
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse
import warnings
warnings.filterwarnings('ignore')

class ScraperHiperlocal:
    def __init__(self, config_path="../config/config_fontes_hiperlocalais.json"):
        """
        Inicializa o scraper com configurações das fontes hiperlocais
        """
        self.config_path = config_path
        self.fontes = self.carregar_configuracao()
        self.noticias_coletadas = []
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def carregar_configuracao(self):
        """
        Carrega o arquivo de configuração JSON com as fontes hiperlocais
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Arquivo de configuração {self.config_path} não encontrado")
            return {}

    def fazer_requisicao(self, url, timeout=10):
        """
        Faz requisição HTTP 
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            return None

    def extrair_texto_limpo(self, elemento):
        """
        Extrai texto limpo de um BeautifulSoup
        """
        if elemento:
            texto = elemento.get_text(strip=True)
            texto = re.sub(r'\s+', ' ', texto)
            return texto
        return ""

    def normalizar_data(self, data_str):
        """
        Tenta normalizar diferentes formatos de data para ISO 8601
        """
        if not data_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        padroes = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/AAAA
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # AAAA-MM-DD
            r'(\d{1,2}) de (\w+) de (\d{4})', # DD de mês de AAAA
        ]
        
        meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
            'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
            'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }
        
        for padrao in padroes:
            match = re.search(padrao, data_str)
            if match:
                if 'de' in padrao:  # Por extenso
                    dia, mes_nome, ano = match.groups()
                    mes = meses.get(mes_nome.lower(), '01')
                    return f"{ano}-{mes}-{dia.zfill(2)} 00:00:00"
                elif '/' in padrao:  # DD/MM/AAAA
                    dia, mes, ano = match.groups()
                    return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)} 00:00:00"
                else:  # AAAA-MM-DD
                    ano, mes, dia = match.groups()
                    return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)} 00:00:00"
        
        # Se não conseguir parsear, retorna data atual
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def scraping_fonte(self, fonte_config):
        """
        Realiza scraping de uma fonte específica
        """
        nome = fonte_config['nome']
        url = fonte_config['url']
        regiao = fonte_config['regiao']
        
        # Pula fontes que precisam de JavaScript
        if fonte_config.get('javascript_required', False):
            print(f"Pulando {nome} ({regiao}) - Precisa de JavaScript")
            return []
        
        # Verifica se tem seletores
        if 'selectors' not in fonte_config:
            print(f"Pulando {nome} ({regiao}) - Sem seletores definidos")
            return []
            
        selectors = fonte_config['selectors']
        
        print(f"Coletando de {nome} ({regiao})...")
        
        # Faz requisição
        response = self.fazer_requisicao(url)
        if not response:
            return []
        
        # Parse do HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        noticias_fonte = []
        
        try:
            manchetes_elements = []
            for selector in selectors['manchetes'].split(', '):
                manchetes_elements.extend(soup.select(selector.strip()))
            
            links_elements = []
            for selector in selectors['links'].split(', '):
                links_elements.extend(soup.select(selector.strip()))
            
            datas_elements = []
            for selector in selectors['datas'].split(', '):
                datas_elements.extend(soup.select(selector.strip()))
            
            for i, manchete_elem in enumerate(manchetes_elements[:30]):  # Limita a 30 por fonte
                manchete = self.extrair_texto_limpo(manchete_elem)
                
                # Obter link
                if i < len(links_elements):
                    link_elem = links_elements[i]
                    link = link_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = urljoin(url, link)
                else:
                    link = url
                
                # Obter data
                data_publicacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if i < len(datas_elements):
                    data_elem = datas_elements[i]
                    data_str = self.extrair_texto_limpo(data_elem)
                    data_publicacao = self.normalizar_data(data_str)
                
                # Adicionar notícia se tiver conteúdo válido
                if manchete and len(manchete) > 10:  # Filtrar títulos muito curtos
                    noticia = {
                        'titulo': manchete,
                        'link': link,
                        'fonte': nome,
                        'data_publicacao': data_publicacao,
                        'regiao': regiao,
                        'metodo_coleta': 'scraping_hiperlocal'
                    }
                    noticias_fonte.append(noticia)
            
            print(f"{nome}: {len(noticias_fonte)} notícias coletadas")
            
        except Exception as e:
            print(f"Erro ao processar {nome}: {e}")
        
        return noticias_fonte

    def coletar_todas_fontes(self):
        """
        Realiza coleta de todas as fontes configuradas
        """
        print("Iniciando coleta hiperlocal...")
        self.noticias_coletadas = []
        
        for regiao, fontes_regiao in self.fontes.get('fontes_hiperlocais', {}).items():
            print(f"\nColetando região: {regiao}")
            
            for fonte_config in fontes_regiao:
                noticias_fonte = self.scraping_fonte(fonte_config)
                self.noticias_coletadas.extend(noticias_fonte)

                # Pausa entre requisições
                time.sleep(2)
        
        print(f"\nColeta finalizada! Total: {len(self.noticias_coletadas)} notícias")

    def salvar_resultados(self, nome_arquivo="noticias_hiperlocais.csv"):
        """
        Salva os resultados em CSV
        """
        if not self.noticias_coletadas:
            print("Nenhuma notícia coletada para salvar")
            return
        
        df = pd.DataFrame(self.noticias_coletadas)
        
        # Remover duplicatas por título
        df_limpo = df.drop_duplicates(subset=['titulo'], keep='first')
        
        # Salvar CSV
        df_limpo.to_csv(nome_arquivo, index=False, encoding='utf-8')
        print(f"Resultados salvos em {nome_arquivo}")
        print(f"Total de notícias únicas: {len(df_limpo)}")
        
        # Mostrar estatísticas por região
        print("\nEstatísticas por região:")
        stats = df_limpo['regiao'].value_counts()
        for regiao, count in stats.items():
            print(f"  • {regiao}: {count} notícias")

    def executar_coleta_completa(self, nome_arquivo="noticias_hiperlocais.csv"):
        """
        Método principal que executa todo o processo de coleta
        """
        
        # Verificar configuração
        if not self.fontes:
            print("Configuração de fontes não encontrada")
            return
        
        # Executar coleta
        self.coletar_todas_fontes()
        
        # Salvar resultados
        self.salvar_resultados(nome_arquivo)
        
        return self.noticias_coletadas


def main():
    scraper = ScraperHiperlocal()
    noticias = scraper.executar_coleta_completa()
    
    if noticias:
        print("\nAmostra das notícias coletadas:")
        df = pd.DataFrame(noticias)
        print(df[['titulo', 'fonte', 'regiao']].head())


if __name__ == "__main__":
    main()
