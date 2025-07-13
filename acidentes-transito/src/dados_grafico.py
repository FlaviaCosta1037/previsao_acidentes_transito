import pandas as pd

def preparar_dados_graficos(df):
    dados = {}

    # Acidentes por ano
    acidentes_ano = df['ano'].value_counts().sort_index()
    dados['acidentes_ano'] = {'anos': acidentes_ano.index.tolist(), 'valores': acidentes_ano.values.tolist()}

    # Acidentes por dia da semana
    acidentes_dia = df['dia_nome'].value_counts().reindex(['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']).fillna(0)
    dados['acidentes_dia'] = {'dias': acidentes_dia.index.tolist(), 'valores': acidentes_dia.values.tolist()}

    # Top 10 bairros
    top_bairros = df['bairro'].value_counts().head(10)
    dados['top_bairros'] = {'bairros': top_bairros.index.tolist(), 'valores': top_bairros.values.tolist()}

    # Natureza dos acidentes
    natureza = df['natureza_acidente'].value_counts()
    dados['natureza'] = {'naturezas': natureza.index.tolist(), 'valores': natureza.values.tolist()}

    # Tipos de acidentes
    tipo = df['tipo'].value_counts().head(20)
    dados['tipo'] = {'tipos': tipo.index.tolist(), 'valores': tipo.values.tolist()}

    # Turno x Dia (matriz para heatmap)
    tabela = pd.crosstab(df['dia_nome'], df['turno']).reindex(index=['Seg','Ter','Qua','Qui','Sex','Sáb','Dom'], columns=['Madrugada','Manhã','Tarde','Noite','Indefinido'], fill_value=0)
    dados['heatmap_turno'] = tabela.values.tolist()
    dados['heatmap_turno_dias'] = tabela.index.tolist()
    dados['heatmap_turno_turnos'] = tabela.columns.tolist()

    # Veículos
    tipo_veiculos = ['auto', 'moto', 'ciclom', 'ciclista', 'pedestre', 'onibus', 'caminhao', 'viatura', 'outros']
    soma_veiculos = df[tipo_veiculos].sum().astype(int)
    dados['veiculos'] = {'tipos': soma_veiculos.index.tolist(), 'valores': soma_veiculos.values.tolist()}

    # Vítimas
    tipo_vitima = ['vitimas', 'vitimasfatais']
    soma_vitimas = df[tipo_vitima].sum().astype(int)
    dados['vitimas'] = {'tipos': soma_vitimas.index.tolist(), 'valores': soma_vitimas.values.tolist()}

    # Acidentes por hora do dia (distribuição)
    hist = df['hora_limpa'].value_counts().sort_index()
    dados['hora_dia'] = {'horas': hist.index.tolist(), 'valores': hist.values.tolist()}

    return dados