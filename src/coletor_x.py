import tweepy
import json
from typing import List, Dict
import os

# Carregar as chaves da API do X (Twitter) de variáveis de ambiente
API_KEY = '1948827962846961664-Eq9Cjda8nroferSmXYlp6RdCVusqAM'
API_SECRET = 'kiJE0rVRVO8kbm1rAy9RcWZ8f2AFOpMFerFpUtb1u0EFS'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAABH73AEAAAAA5ErKxzBIQC1gduV0TLcmhrLTuOQ%3DFLJWq3n3BeFS9rUkh27HnrcR8oT9bby3pzAleTfh0rrAEw0gTW'

# Parâmetros de busca
QUERY = 'João Campos -is:retweet'  # Exemplo de busca
MAX_RESULTS = 50  # Número máximo de tweets a coletar


def autenticar() -> tweepy.Client:
    """
    Autentica na API do X usando o Bearer Token.
    """
    if not BEARER_TOKEN:
        raise ValueError('Bearer Token não encontrado nas variáveis de ambiente.')
    return tweepy.Client(bearer_token=BEARER_TOKEN)


def buscar_tweets(client: tweepy.Client, query: str, max_results: int = 50) -> List[Dict]:
    """
    Busca tweets recentes usando a API v2 do X (Twitter).
    """
    tweets = []
    response = client.search_recent_tweets(
        query=query,
        tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
        expansions=['author_id'],
        max_results=max_results
    )
    users = {u['id']: u for u in response.includes['users']} if response.includes and 'users' in response.includes else {}
    for tweet in response.data or []:
        user = users.get(tweet.author_id, {})
        tweets.append({
            'id': tweet.id,
            'texto': tweet.text,
            'usuario': user.get('username', tweet.author_id),
            'data': tweet.created_at.isoformat() if tweet.created_at else None,
            'curtidas': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
            'retweets': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
            'lang': tweet.lang
        })
    return tweets


def main():
    client = autenticar()
    print(f'Buscando tweets para a query: {QUERY}')
    tweets = buscar_tweets(client, QUERY, MAX_RESULTS)
    print(f'Total de tweets coletados: {len(tweets)}')
    # Salvar resultados
    with open('data/tweets_x.json', 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main() 