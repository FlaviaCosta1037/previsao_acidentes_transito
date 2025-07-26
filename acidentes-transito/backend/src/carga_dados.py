import pandas as pd
import os
from src.utils import tratar_dados

def carregar_dados():
    dados = {}

    # Caminho absoluto para a pasta csvs
    base_dir = os.path.dirname(os.path.abspath(__file__))  # backend/src
    pasta = os.path.join(base_dir, '..', 'csvs')
    pasta = os.path.abspath(pasta)

    print(f"Lendo CSVs da pasta: {pasta}")

    # Lista de arquivos CSV
    arquivos_csv = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.csv')]

    dfs = []
    for arquivo in arquivos_csv:
        try:
            df_temp = pd.read_csv(arquivo, encoding='latin1', sep=';')
            dfs.append(df_temp)
            print(f'Lido: {arquivo}')
        except Exception as e:
            print(f'Erro ao ler {arquivo}: {e}')

    # Junta todos os dataframes válidos
    df = pd.concat(dfs, ignore_index=True)
    print(f'\nTotal de arquivos lidos com sucesso: {len(dfs)}')
    print(f'Total de registros: {df.shape[0]}')

    # TRATA O DATAFRAME
    df = tratar_dados(df)

    # ======================================
    #    GERAÇÃO DOS DADOS PARA OS GRÁFICOS
    # ======================================
    acidentes_ano = df['ano'].value_counts().sort_index()
    dados['acidentes_ano'] = {'anos': acidentes_ano.index.tolist(), 'valores': acidentes_ano.values.tolist()}

    acidentes_dia = df['dia_nome'].value_counts().reindex(['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']).fillna(0)
    dados['acidentes_dia'] = {'dias': acidentes_dia.index.tolist(), 'valores': acidentes_dia.values.tolist()}

    top_bairros = df['bairro'].value_counts().head(10)
    dados['top_bairros'] = {'bairros': top_bairros.index.tolist(), 'valores': top_bairros.values.tolist()}

    natureza = df['natureza_acidente'].value_counts()
    dados['natureza'] = {'naturezas': natureza.index.tolist(), 'valores': natureza.values.tolist()}

    tipo = df['tipo'].value_counts().head(20)
    dados['tipo'] = {'tipos': tipo.index.tolist(), 'valores': tipo.values.tolist()}

    tabela = pd.crosstab(df['dia_nome'], df['turno']).reindex(
        index=['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
        columns=['Madrugada', 'Manhã', 'Tarde', 'Noite', 'Indefinido'],
        fill_value=0
    )
    dados['heatmap_turno'] = tabela.values.tolist()
    dados['heatmap_turno_dias'] = tabela.index.tolist()
    dados['heatmap_turno_turnos'] = tabela.columns.tolist()

    tipo_veiculos = ['auto', 'moto', 'ciclom', 'ciclista', 'pedestre', 'onibus', 'caminhao', 'viatura', 'outros']
    soma_veiculos = df[tipo_veiculos].sum().astype(int)
    dados['veiculos'] = {'tipos': soma_veiculos.index.tolist(), 'valores': soma_veiculos.values.tolist()}

    tipo_vitima = ['vitimas', 'vitimasfatais']
    soma_vitimas = df[tipo_vitima].sum().astype(int)
    dados['vitimas'] = {'tipos': soma_vitimas.index.tolist(), 'valores': soma_vitimas.values.tolist()}

    hist = df['hora_limpa'].value_counts().sort_index()
    dados['hora_dia'] = {'horas': hist.index.tolist(), 'valores': hist.values.tolist()}

    return df, dados
