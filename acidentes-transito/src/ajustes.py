import pandas as pd

def padronizar_tipo_acidente(df, coluna='tipo'):
    """
    Renomeia e padroniza os valores da coluna de tipo de acidente.
    
    Parâmetros:
    - df: DataFrame pandas contendo os dados
    - coluna: nome da coluna a ser padronizada (padrão: 'tipo_acidente')
    
    Retorna:
    - DataFrame com a coluna padronizada
    """
    mapeamento = {
        'SEM VATIMA': 'Sem Vítima',
        'COM VATIMA': 'Com Vítima',
        'VATIMA FATAL': 'Vítima Fatal',
        'ENTRADA E SAADA': 'Entrada e Saída',
        'APOIO': 'Apoio',
        'OUTROS': 'Outros'
    }

    df[coluna] = df[coluna].replace(mapeamento)
    df[coluna] = df[coluna].fillna('Não Informado')
    return df

def padronizar_tipo_evento(df, coluna='natureza_acidente'):
    """
    Padroniza e limpa os valores da coluna com os tipos de eventos/acidentes.
    
    Parâmetros:
    - df: DataFrame pandas contendo os dados
    - coluna: nome da coluna a ser padronizada
    
    Retorna:
    - DataFrame com a coluna padronizada
    """
    mapeamento = {
        'COLISAO': 'Colisão',
        'CHOQUE': 'Choque',
        'ATROPELAMENTO ANIMAL': 'Atropelamento de Animal',
        'QUEDA DE ARVORE': 'Queda de Árvore',
        'ATROPELAMENTO': 'Atropelamento',
        'CAPOTAMENTO': 'Capotamento',
        'COLISAO COM CICLISTA': 'Colisão com Ciclista',
        'ENGAVETAMENTO': 'Engavetamento',
        'TOMBAMENTO': 'Tombamento',
        'ACID. DE PERCURSO': 'Acidente de Percurso',
        'FISCALIZAAAO': 'Fiscalização',
        'COM VATIMA': 'Outro',
        'SEM VATIMA': 'Outro',
        'VATIMA FATAL': 'Outro',
        'MMMMMMMMMMMMNNNNNNNNNNNNNNC': 'Categoria Inválida'
    }

    df[coluna] = df[coluna].replace(mapeamento)
    df[coluna] = df[coluna].fillna('Não Informado')
    return df

