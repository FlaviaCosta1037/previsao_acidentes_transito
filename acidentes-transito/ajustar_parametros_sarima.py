# ajustar_parametros_sarima.py
from src.carga_dados import carregar_dados
from src.dividir_modelagem import dividir_modelagem
from src.preparar_modelo import buscar_melhor_ordem_sarima
import pandas as pd
from src.utils import extrair_hora, limpar_descricao

df = carregar_dados()
# Aplica limpeza extra no texto e hora
df['descricao_limpa'] = df['descricao'].fillna('').apply(limpar_descricao)
df['hora_limpa'] = df['hora'].apply(extrair_hora)

df['data_unificada'] = pd.to_datetime(df['data_unificada'])
serie = df.groupby('data_unificada').size()
serie = serie.reindex(pd.date_range(serie.index.min(), serie.index.max(), freq='D')).fillna(0)

melhores_param, melhor_mape = buscar_melhor_ordem_sarima(serie)
print("Melhor combinação:", melhores_param)
print("Melhor MAPE:", melhor_mape)
