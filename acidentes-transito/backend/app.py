from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta
import pandas as pd
import numpy as np

from src.carga_dados import carregar_dados
from src.modelo_svr import modelar_svr
from src.dados_grafico import preparar_dados_graficos
from src.utils import limpar_descricao, extrair_hora
from firebase_config import db  # Importa conexão com Firebase

app = Flask(__name__)
CORS(app)

# ========================================================
# Carregamento inicial de dados
# ========================================================
df, dados_graficos = carregar_dados()

# Limpeza e padronização
df['descricao_limpa'] = df['descricao'].fillna('').apply(limpar_descricao)
df['hora_limpa'] = df['hora'].apply(extrair_hora)
df.rename(columns={'ï»¿data': 'i_data'}, inplace=True)


def parse_date_column(col):
    dt = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
    mask = dt.isna() & df[col].notna()
    dt.loc[mask] = pd.to_datetime(df.loc[mask, col], errors='coerce', dayfirst=False)
    return dt


df['data_dt'] = parse_date_column('data')
df['DATA_dt'] = parse_date_column('DATA')
df['i_data_dt'] = parse_date_column('i_data')

df['data_unificada'] = df['data_dt']
mask = df['data_unificada'].isna()
df.loc[mask, 'data_unificada'] = df.loc[mask, 'DATA_dt']
mask = df['data_unificada'].isna()
df.loc[mask, 'data_unificada'] = df.loc[mask, 'i_data_dt']

# Série até 31/12/2024
df_com_data = df[df['data_unificada'].notnull()].copy()
df_com_data['data_unificada'] = pd.to_datetime(df_com_data['data_unificada'])
serie = df_com_data.groupby('data_unificada').size()
serie = serie.asfreq('D')
serie = serie.loc[:'2024-12-31']
serie = serie[serie.index >= '2021-01-01']

dados_graficos = preparar_dados_graficos(df)

# ========================================================
# Treinamento inicial de modelos
# ========================================================
print("Treinando modelo SVR (série até 31/12/2024)...")
try:
    cached_result = modelar_svr(serie)
    print("Modelo (treino/teste) armazenado em cache.")
except Exception as e:
    print(f"Erro ao treinar modelo: {e}")
    cached_result = None

# ========================================================
# Função para salvar no Firebase
# ========================================================
def salvar_previsoes_no_firebase():
    if cached_result:
        yhat = cached_result["previsao"]
        start_date = pd.to_datetime(serie.index[-1]) + pd.Timedelta(days=1)
        datas = [(start_date + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(len(yhat))]

        previsoes = [{"data": d, "valor": int(round(v))} for d, v in zip(datas, yhat)]
        erros = {
            "MAE": round(cached_result['mae'], 4),
            "MSE": round(cached_result['mse'], 4),
            "RMSE": round(cached_result['rmse'], 4),
            "MAPE (%)": round(cached_result['mape'], 2),
        }

        db.collection("previsoes").document("ultimo_modelo").set({
            "previsoes": previsoes,
            "erros": erros
        })

        print("✅ Previsões e erros salvos no Firebase.")
    else:
        print("⚠ Nenhum resultado para salvar no Firebase.")


# Salva automaticamente ao iniciar
salvar_previsoes_no_firebase()

# ========================================================
# Funções auxiliares
# ========================================================
def convert_np(obj):
    if isinstance(obj, np.integer): return int(obj)
    if isinstance(obj, np.floating): return float(obj)
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, dict): return {k: convert_np(v) for k, v in obj.items()}
    if isinstance(obj, list): return [convert_np(i) for i in obj]
    return obj

# ========================================================
# Rotas
# ========================================================
@app.route("/api/previsao", methods=["GET"])
def previsao():
    if cached_result is None:
        return jsonify({'error': 'Modelo não disponível'}), 500

    yhat = cached_result["previsao"]
    start_date = pd.to_datetime(serie.index[-1]) + pd.Timedelta(days=1)
    datas = [(start_date + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(len(yhat))]

    return jsonify({
        "previsao_proximo_dia": int(round(yhat[0])),
        "previsoes_proximos_6_dias": [
            {"data": d, "valor": int(round(v))} for d, v in zip(datas, yhat)
        ]
    })


@app.route('/api/avaliacao')
def avaliacao():
    if cached_result is None:
        return jsonify({'error': 'Modelo não disponível'}), 500
    return jsonify({
        'MAE': round(cached_result['mae'], 4),
        'MSE': round(cached_result['mse'], 4),
        'RMSE': round(cached_result['rmse'], 4),
        'MAPE (%)': round(cached_result['mape'], 2)
    })


@app.route('/api/graficos')
def graficos():
    return jsonify(convert_np(dados_graficos))

@app.route('/api/retrain', methods=['POST'])
def retrain():
    global cached_result
    try:
        df, _ = carregar_dados()
        serie = df.groupby('data_unificada').size().asfreq('D')
        cached_result = modelar_svr(serie)
        salvar_previsoes_no_firebase()
        return jsonify({'message': 'Modelo re-treinado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def home():
    return '<h1>API Acidentes - Previsão e Dados</h1>'


# ========================================================
if __name__ == '__main__':
    app.run(debug=True)
