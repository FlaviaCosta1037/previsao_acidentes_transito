import pandas as pd
import re


def classificar_turno(hora):
    try:
        if pd.isna(hora):
            return 'Indefinido'
        h = int(str(hora).split(':')[0])
        if 0 <= h < 6:
            return 'Madrugada'
        elif 6 <= h < 12:
            return 'Manhã'
        elif 12 <= h < 18:
            return 'Tarde'
        elif 18 <= h <= 23:
            return 'Noite'
        else:
            return 'Indefinido'
    except:
        return 'Indefinido'

def extrair_hora(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, str):
        valor = valor.strip()
        match = re.match(r'^(\d{1,2})', valor)
        if match:
            return int(match.group(1))
        else:
            return None
    elif isinstance(valor, (int, float)):
        return int(valor)
    return None

def classificar_turno(hora):
    if pd.isna(hora): return 'Indefinido'
    hora = int(hora)
    if 5 <= hora < 12: return 'Manhã'
    elif 12 <= hora < 17: return 'Tarde'
    elif 17 <= hora < 21: return 'Noite'
    else: return 'Madrugada'

def preparar_dados_graficos(df):
    import re

    # Aplica extração da hora
    df['hora_limpa'] = df['hora'].apply(extrair_hora)

    # Aplica classificação de turno
    df['turno'] = df['hora_limpa'].apply(classificar_turno)

    dados = {}

    # Acidentes por ano
    acidentes_ano = df['ano'].value_counts().sort_index()
    dados['acidentes_ano'] = {
        'anos': acidentes_ano.index.tolist(),
        'valores': acidentes_ano.values.tolist()
    }

    # Acidentes por dia da semana
    acidentes_dia = df['dia_nome'].value_counts().reindex(
        ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']
    ).fillna(0)
    dados['acidentes_dia'] = {
        'dias': acidentes_dia.index.tolist(),
        'valores': acidentes_dia.values.tolist()
    }

    # Top 10 bairros
    top_bairros = df['bairro'].value_counts().head(10)
    dados['top_bairros'] = {
        'bairros': top_bairros.index.tolist(),
        'valores': top_bairros.values.tolist()
    }

    # Natureza dos acidentes
    natureza = df['natureza_acidente'].value_counts()
    dados['natureza'] = {
        'naturezas': natureza.index.tolist(),
        'valores': natureza.values.tolist()
    }

    # Tipos de acidentes
    tipo = df['tipo'].value_counts().head(20)
    dados['tipo'] = {
        'tipos': tipo.index.tolist(),
        'valores': tipo.values.tolist()
    }

    # Heatmap (Dia da semana x Turno)
    tabela = pd.crosstab(
        df['dia_nome'],
        df['turno']
    ).reindex(
        index=['Seg','Ter','Qua','Qui','Sex','Sáb','Dom'],
        columns=['Madrugada','Manhã','Tarde','Noite','Indefinido'],
        fill_value=0
    )

    dados['heatmap_turno'] = tabela.values.tolist()
    dados['heatmap_turno_dias'] = tabela.index.tolist()
    dados['heatmap_turno_turnos'] = tabela.columns.tolist()

    # Veículos
    tipo_veiculos = ['auto', 'moto', 'ciclom', 'ciclista', 'pedestre', 'onibus', 'caminhao', 'viatura', 'outros']
    soma_veiculos = df[tipo_veiculos].sum().astype(int)
    dados['veiculos'] = {
        'tipos': soma_veiculos.index.tolist(),
        'valores': soma_veiculos.values.tolist()
    }

    # Vítimas
    tipo_vitima = ['vitimas', 'vitimasfatais']
    soma_vitimas = df[tipo_vitima].sum().astype(int)
    dados['vitimas'] = {
        'tipos': soma_vitimas.index.tolist(),
        'valores': soma_vitimas.values.tolist()
    }

    # Acidentes por hora do dia
    hist = df['hora_limpa'].value_counts().sort_index()
    dados['hora_dia'] = {
        'horas': hist.index.tolist(),
        'valores': hist.values.tolist()
    }

    return dados
