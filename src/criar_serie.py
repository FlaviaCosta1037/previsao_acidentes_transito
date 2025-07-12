import unidecode
import pandas as pd
import unicodedata

def criar_serie(df, coluna_valor, coluna_data='data', colunas_agrupamento=None):

    df[coluna_data] = pd.to_datetime(df[coluna_data])
    
    # Cria a coluna de período mensal
    df['Periodo'] = df[coluna_data].dt.to_period('M').dt.to_timestamp()
    
    # Define colunas para agrupar
    if colunas_agrupamento is None:
        colunas_agrupamento = ['Periodo']
    else:
        colunas_agrupamento = ['Periodo'] + colunas_agrupamento
    
    # Agrupa somando os valores
    df_agrupado = df.groupby(colunas_agrupamento)[coluna_valor].sum().reset_index()
    
    print('Tamanho do agrupamento:', df_agrupado.shape)
    print(df_agrupado.head())
    
    return df_agrupado

def criar_serie_contagem(df, coluna_valor, coluna_data='data', colunas_agrupamento=None):
    df[coluna_data] = pd.to_datetime(df[coluna_data])
    df['Periodo'] = df[coluna_data].dt.to_period('M').dt.to_timestamp()

    if colunas_agrupamento is None:
        colunas_agrupamento = ['Periodo']
    else:
        colunas_agrupamento = ['Periodo'] + colunas_agrupamento

    # Se a coluna_valor já estiver nas colunas de agrupamento, use o index para contar
    if coluna_valor in colunas_agrupamento:
        df_agrupado = df.groupby(colunas_agrupamento).size().reset_index(name='total_ocorrencias')
    else:
        df_agrupado = df.groupby(colunas_agrupamento)[coluna_valor].count().reset_index(name='total_ocorrencias')

    print('Tamanho do agrupamento:', df_agrupado.shape)
    print(df_agrupado.head())

    return df_agrupado

