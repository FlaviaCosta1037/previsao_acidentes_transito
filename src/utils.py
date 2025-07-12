import re
import pandas as pd
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import unidecode
nltk.download('punkt')
nltk.download('stopwords')

def tratamento(df):
    """
    Limpa e padroniza nomes de colunas e campos textuais sem alterar o case:
    - Remove acentos e espaços dos nomes de colunas
    - Limpa colunas texto (remove acentos, espaços extras)
    """

    # Padronizar nomes de colunas (sem lower)
    df.columns = [unidecode.unidecode(col).strip().replace(' ', '_') for col in df.columns]

    # Limpar valores texto sem afetar NaN ou tipos
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].apply(lambda x: unidecode.unidecode(x).strip() if isinstance(x, str) else x)

    return df


def extrair_hora(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, str):
        valor = valor.strip()
        match = re.match(r'^(\d{1,2})', valor)  # pega os 1 ou 2 primeiros dígitos
        if match:
            return int(match.group(1))
        else:
            return None
    elif isinstance(valor, (int, float)):
        return int(valor)
    return None



def limpar_descricao(texto):
    # Converte para minúsculo
    texto = texto.lower()
    
    # Remove caracteres especiais e números
    texto = re.sub(r'[^a-zA-ZáéíóúãõâêôçÀ-ÿ\s]', '', texto)
    
    # Tokeniza
    tokens = word_tokenize(texto)
    
    # Remove stopwords
    stop_words = set(stopwords.words('portuguese'))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
    
    return ' '.join(tokens)     


