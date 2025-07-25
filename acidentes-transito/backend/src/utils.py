import re
import numpy as np
import pandas as pd
from src.funcoes_eda import classificar_turno
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
    df.columns = [unidecode.unidecode(col).strip().replace(' ', '_') for col in df.columns]
    
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].apply(lambda x: unidecode.unidecode(x).strip() if isinstance(x, str) else x)

    return df


def extrair_hora(valor):
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, str):
        valor = valor.strip()
        match = re.match(r'^(\d{1,2})', str(valor))  
        if match:
            h = int(match.group(1))
            return h if 0 <= h <= 23 else np.nan
    return np.nan

def limpar_descricao(texto):

    texto = texto.lower()
    texto = re.sub(r'[^a-zA-ZáéíóúãõâêôçÀ-ÿ\s]', '', texto)
    
    tokens = word_tokenize(texto)
    
    stop_words = set(stopwords.words('portuguese'))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
    
    return ' '.join(tokens)     

def tratar_dados(df):
    df['data_dt'] = pd.to_datetime(df['data'], errors='coerce', dayfirst=True)
    mask = df['data_dt'].isna() & df['data'].notna()
    df.loc[mask, 'data_dt'] = pd.to_datetime(df.loc[mask, 'data'], errors='coerce', dayfirst=False)

    df['DATA_dt'] = pd.to_datetime(df['DATA'], errors='coerce', dayfirst=True)
    mask2 = df['DATA_dt'].isna() & df['DATA'].notna()
    df.loc[mask2, 'DATA_dt'] = pd.to_datetime(df.loc[mask2, 'DATA'], errors='coerce', dayfirst=False)

    df['data_unificada'] = df['data_dt']
    mask3 = df['data_unificada'].isna()
    df.loc[mask3, 'data_unificada'] = df.loc[mask3, 'DATA_dt']

    df['ano'] = df['data_unificada'].dt.year.astype('Int64')  
    df['mes'] = df['data_unificada'].dt.month.astype('Int64')
    df['dia_semana'] = df['data_unificada'].dt.dayofweek.astype('Int64')

    df['dia_nome'] = df['dia_semana'].map({0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sáb', 6: 'Dom'})
    df['turno'] = df['hora'].apply(classificar_turno) 
    df['hora_limpa'] = df['hora'].apply(extrair_hora)  

    df['descricao'] = df['descricao'].fillna('')
    df['descricao_limpa'] = df['descricao'].apply(limpar_descricao)

    tipo_veiculos = ['auto', 'moto', 'ciclom', 'ciclista', 'pedestre', 'onibus', 'caminhao', 'viatura', 'outros']
    for col in tipo_veiculos + ['vitimas', 'vitimasfatais']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

