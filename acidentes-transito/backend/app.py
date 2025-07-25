from flask import Flask, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS
from src.carga_dados import carregar_dados
from src.modelo_svr import modelar_svr
from src.dados_grafico import preparar_dados_graficos
from src.utils import limpar_descricao, extrair_hora

app = Flask(__name__)
CORS(app)

# Carrega dados e prepara tudo na inicialização
df, dados_graficos = carregar_dados()

# Limpeza
df['descricao_limpa'] = df['descricao'].fillna('').apply(limpar_descricao)
df['hora_limpa'] = df['hora'].apply(extrair_hora)
df.rename(columns={'ï»¿data': 'i_data'}, inplace=True)
def parse_date_column(col):
    # Tenta com dayfirst=True
    dt = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
    # Onde deu NaT, tenta com dayfirst=False
    mask = dt.isna() & df[col].notna()
    dt.loc[mask] = pd.to_datetime(df.loc[mask, col], errors='coerce', dayfirst=False)
    return dt

# Faz o parse das 3 colunas
df['data_dt'] = parse_date_column('data')
df['DATA_dt'] = parse_date_column('DATA')
df['i_data_dt'] = parse_date_column('i_data')

# Agora, unifica: prioridade para data_dt, se nulo tenta DATA_dt, se nulo tenta i_data_dt
df['data_unificada'] = df['data_dt']
mask = df['data_unificada'].isna()
df.loc[mask, 'data_unificada'] = df.loc[mask, 'DATA_dt']
mask = df['data_unificada'].isna()
df.loc[mask, 'data_unificada'] = df.loc[mask, 'i_data_dt']

print("Valores válidos em data_unificada:", df['data_unificada'].notna().sum())

data_final_serie = '2024-12-31'
df_com_data = df[df['data_unificada'].notnull()].copy()
df_com_data['data_unificada'] = pd.to_datetime(df_com_data['data_unificada'])
serie = df_com_data.groupby('data_unificada').size()
serie = serie.asfreq('D')  # define frequência diária
serie = serie.loc[:data_final_serie]
serie = serie[serie.index >= '2021-01-01']

# Prepara gráficos
dados_graficos = preparar_dados_graficos(df)

# Treina o modelo uma vez ao iniciar
print("Treinando modelo SVR uma única vez na inicialização...")
try:
    cached_result = modelar_svr(serie)
    print("Modelo treinado e resultado armazenado no cache.")
except Exception as e:
    print(f"Erro ao treinar o modelo na inicialização: {e}")
    cached_result = None

# Conversão para tipos compatíveis com JSON
def convert_np(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_np(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_np(i) for i in obj]
    return obj

@app.route('/api/previsao')
def previsao():
    if cached_result is None:
        return jsonify({'error': 'Modelo ainda não foi carregado.'}), 500
    previsoes = cached_result['previsao']
    return jsonify({'previsoes': [round(p, 2) for p in previsoes]})

@app.route('/api/avaliacao')
def avaliacao():
    if cached_result is None:
        return jsonify({'error': 'Modelo ainda não foi carregado.'}), 500
    
    return jsonify({
        'MAE': round(cached_result['mae'], 4),
        'MSE': round(cached_result['mse'], 4),
        'RMSE': round(cached_result['rmse'], 4),
        'MAPE (%)': round(cached_result['mape'], 2)
    })

@app.route('/api/graficos')
def graficos():
    dados_limpos = convert_np(dados_graficos)
    return jsonify(dados_limpos)

@app.route('/')
def home():
    return '<h1>API Acidentes - Previsão e Dados</h1>'

if __name__ == '__main__':
    app.run(debug=True)
