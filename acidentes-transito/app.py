from flask import Flask, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS
from src.carga_dados import carregar_dados
from src.modelo_arima import preparar_modelo_arima
from src.dados_grafico import preparar_dados_graficos
from src.utils import limpar_descricao, extrair_hora

app = Flask(__name__)
CORS(app)

# Carrega dados e prepara tudo só uma vez na inicialização
df, dados_graficos = carregar_dados()

# Aplica limpeza extra no texto e hora
df['descricao_limpa'] = df['descricao'].fillna('').apply(limpar_descricao)
df['hora_limpa'] = df['hora'].apply(extrair_hora)

# Atualiza dados dos gráficos com dados já tratados
dados_graficos = preparar_dados_graficos(df)

# Treina o modelo ARIMA e guarda para usar depois
resultados_arima = preparar_modelo_arima(df)
modelo_arima = resultados_arima['modelo']

# Função auxiliar para garantir que numpy int64 viram int normais para jsonify
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
    try:
        # Previsão para o próximo dia (1 período à frente)
        pred = modelo_arima.predict(n_periods=1)[0]
        pred_float = round(float(pred), 2)
        return jsonify({'previsao_proximo_dia': pred_float})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graficos')
def graficos():
    # Garante que todos os tipos numpy serão convertidos antes do jsonify
    dados_limpos = convert_np(dados_graficos)
    return jsonify(dados_limpos)

@app.route('/')
def home():
    return '<h1>API Acidentes - Previsão e Dados</h1>'

if __name__ == '__main__':
    app.run(debug=True)
