from turtle import pd
import numpy as np

from src.dividir_modelagem import dividir_modelagem
from statsmodels.tsa.statespace.sarimax import SARIMAX 


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Evita divisão por zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def modelo_sarima(df):
    df_com_data = df[df['data_unificada'].notnull()].copy()
    df_com_data['data_unificada'] = pd.to_datetime(df_com_data['data_unificada'])

    serie = df_com_data.groupby('data_unificada').size()
    full_index = pd.date_range(start=serie.index.min(), end=serie.index.max(), freq='D')
    serie = serie.reindex(full_index).fillna(0)

    y_train, y_val, y_test = dividir_modelagem(serie)
    
    # Ajuste manual - Exemplo SARIMA(1,1,1)(1,1,1,7) para sazonalidade semanal
    modelo = SARIMAX(y_train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
    resultado = modelo.fit(disp=False)

    previsao_val = modelo.forecast(n_periods=len(y_val))
    mape_val = mean_absolute_percentage_error(y_val, previsao_val)

    modelo.update(y_val)
    previsao_test = modelo.forecast(n_periods=len(y_test))
    mape_test = mean_absolute_percentage_error(y_test, previsao_test)

    return {
        'modelo': modelo,
        'melhor_ordem': modelo.order,
        'mape_val': mape_val,
        'mape_test': mape_test,
        'previsao_val': previsao_val,
        'previsao_test': previsao_test
    }