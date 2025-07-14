import numpy as np
from src.dividir_modelagem import dividir_modelagem
import itertools
import warnings
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Evita divisão por zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def buscar_melhor_ordem_sarima(serie, 
                               p_values=[0,1,2,3], d_values=[0,1], q_values=[0,1,2,3],
                               P_values=[0,1], D_values=[0,1], Q_values=[0,1],
                               m=7):
    """
    Busca a melhor combinação de parâmetros SARIMA (p,d,q)(P,D,Q,m) baseado em MAPE no conjunto de validação.
    """
    y_train, y_val, y_test = dividir_modelagem(serie)
    
    melhores_param = None
    melhor_mape = float('inf')
    
    warnings.filterwarnings("ignore")
    
    for p, d, q in itertools.product(p_values, d_values, q_values):
        for P, D, Q in itertools.product(P_values, D_values, Q_values):
            try:
                modelo = SARIMAX(y_train, order=(p,d,q), seasonal_order=(P,D,Q,m))
                resultado = modelo.fit(disp=False)
                
                previsao_val = resultado.forecast(steps=len(y_val))
                mape_val = mean_absolute_percentage_error(y_val, previsao_val)
                
                if mape_val < melhor_mape:
                    melhor_mape = mape_val
                    melhores_param = (p,d,q,P,D,Q)
                    
                print(f"Testando SARIMA{(p,d,q)}x{(P,D,Q,m)} - MAPE: {mape_val:.3f}")
                
            except Exception as e:
                print(f"Erro SARIMA{(p,d,q)}x{(P,D,Q,m)}: {e}")
                continue
    
    print(f"Melhor ordem SARIMA encontrada: SARIMA{melhores_param[:3]}x{melhores_param[3:]}, MAPE validação: {melhor_mape:.3f}")
    return melhores_param, melhor_mape

def preparar_modelo_arima(df):
    df_com_data = df[df['data_unificada'].notnull()].copy()
    df_com_data['data_unificada'] = pd.to_datetime(df_com_data['data_unificada'])

    serie = df_com_data.groupby('data_unificada').size()
    full_index = pd.date_range(start=serie.index.min(), end=serie.index.max(), freq='D')
    serie = serie.reindex(full_index).fillna(0)

    y_train, y_val, y_test = dividir_modelagem(serie)
    resultados_auto = modelar_arima_automatico(y_train, y_val, y_test)
    return resultados_auto

def preparar_modelo_sarima(df):
    df_com_data = df[df['data_unificada'].notnull()].copy()
    df_com_data['data_unificada'] = pd.to_datetime(df_com_data['data_unificada'])

    serie = df_com_data.groupby('data_unificada').size()
    full_index = pd.date_range(start=serie.index.min(), end=serie.index.max(), freq='D')
    serie = serie.reindex(full_index).fillna(0)
    
    y_train, y_val, y_test = dividir_modelagem(serie)

    order = (2, 0, 0)
    seasonal_order = (1, 1, 0, 7)
    
    # Treinando modelo SARIMA
    modelo = SARIMAX(y_train, order=order, seasonal_order=seasonal_order)
    resultado = modelo.fit(disp=False)

    previsao_val = resultado.forecast(steps=len(y_val))
    mape_val = mean_absolute_percentage_error(y_val, previsao_val)

    previsao_test = resultado.forecast(steps=len(y_test))
    mape_test = mean_absolute_percentage_error(y_test, previsao_test)

    return {
        'modelo': resultado,
        'mape_val': mape_val,
        'mape_test': mape_test,
        'previsao_val': previsao_val,
        'previsao_test': previsao_test
    }

