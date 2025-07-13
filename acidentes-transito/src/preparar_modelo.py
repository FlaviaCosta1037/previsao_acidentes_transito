from src.dividir_modelagem import dividir_modelagem
from src.modelo_arima import modelar_arima_automatico
import pandas as pd


def preparar_modelo_arima(df):
    df_com_data = df[df['data_unificada'].notnull()].copy()
    df_com_data['data_unificada'] = pd.to_datetime(df_com_data['data_unificada'])

    serie = df_com_data.groupby('data_unificada').size()
    full_index = pd.date_range(start=serie.index.min(), end=serie.index.max(), freq='D')
    serie = serie.reindex(full_index).fillna(0)

    y_train, y_val, y_test = dividir_modelagem(serie)
    resultados_auto = modelar_arima_automatico(y_train, y_val, y_test)
    return resultados_auto

resultados_arima = preparar_modelo_arima(df)
modelo_arima = resultados_arima['modelo']