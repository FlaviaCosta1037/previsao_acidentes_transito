from prophet import Prophet
from sklearn.metrics import mean_absolute_error
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Função de erro percentual médio absoluto (MAPE)
def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    if np.sum(mask) == 0:
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

# Função principal com melhorias
def modelar_prophet(serie, horizonte=1, reamostragem='W', remover_negativos=True):
    # Reamostragem semanal para suavizar a série, se necessário
    df = pd.DataFrame({'ds': serie.index, 'y': serie.values})
    df = df.resample(reamostragem, on='ds').mean().reset_index()

    # Divisão 60% treino, 20% validação, 20% teste
    n = len(df)
    n_train = int(n * 0.6)
    n_val = int(n * 0.2)
    n_test = n - n_train - n_val

    df_train = df.iloc[:n_train]
    df_val = df.iloc[n_train:n_train + n_val]
    df_test = df.iloc[n_train + n_val:]

    # Modelo para validação
    modelo_val = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        seasonality_mode='additive'
    )
    modelo_val.fit(df_train)

    # Previsão para validação
    datas_val = modelo_val.make_future_dataframe(periods=n_val, freq=reamostragem)
    previsao_val = modelo_val.predict(datas_val)
    previsoes_val = previsao_val[['ds', 'yhat']].set_index('ds').loc[df_val['ds']]

    # Suavização por média móvel
    previsoes_val['yhat'] = previsoes_val['yhat'].rolling(3, center=True).mean()

    # Remoção de negativos, se solicitado
    if remover_negativos:
        previsoes_val['yhat'] = previsoes_val['yhat'].clip(lower=0)

    # Remoção de NaNs após suavização
    previsoes_val = previsoes_val.dropna()
    df_val_filtrado = df_val.set_index('ds').loc[previsoes_val.index]

    # Avaliação
    mae_val = mean_absolute_error(df_val_filtrado['y'], previsoes_val['yhat'])
    mape_val = mape(df_val_filtrado['y'], previsoes_val['yhat'])

    print(f"Validação - MAE: {mae_val:.2f}, MAPE: {mape_val:.2f}%")

    # Modelo final (treino + validação)
    df_treino_completo = pd.concat([df_train, df_val])
    modelo_final = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        seasonality_mode='additive'
    )
    modelo_final.fit(df_treino_completo)

    # Previsão para teste + horizonte
    datas_teste = modelo_final.make_future_dataframe(periods=n_test + horizonte, freq=reamostragem)
    previsao_teste = modelo_final.predict(datas_teste)
    previsoes_teste = previsao_teste[['ds', 'yhat']].set_index('ds').loc[df_test['ds']]

    # Suavização
    previsoes_teste['yhat'] = previsoes_teste['yhat'].rolling(3, center=True).mean()
    if remover_negativos:
        previsoes_teste['yhat'] = previsoes_teste['yhat'].clip(lower=0)

    previsoes_teste = previsoes_teste.dropna()
    df_test_filtrado = df_test.set_index('ds').loc[previsoes_teste.index]

    mae_teste = mean_absolute_error(df_test_filtrado['y'], previsoes_teste['yhat'])
    mape_teste = mape(df_test_filtrado['y'], previsoes_teste['yhat'])

    print(f"Teste - MAE: {mae_teste:.2f}, MAPE: {mape_teste:.2f}%")

    # Previsão do próximo ponto
    horizon_date = previsao_teste['ds'].iloc[-1]
    horizon_pred = previsao_teste['yhat'].iloc[-1]
    print(f"Previsão para o próximo período ({horizon_date.date()}): {horizon_pred:.2f}")

    # Plotagem
    plt.figure(figsize=(14, 6))
    plt.plot(df_train['ds'], df_train['y'], label='Treino', color='blue', alpha=0.7)
    plt.plot(df_val['ds'], df_val['y'], label='Validação Real', color='green', alpha=0.7)
    plt.plot(previsoes_val.index, previsoes_val['yhat'], '--', label='Validação Prevista', color='lime', alpha=0.8)
    plt.plot(df_test['ds'], df_test['y'], label='Teste Real', color='red', alpha=0.7)
    plt.plot(previsoes_teste.index, previsoes_teste['yhat'], '--', label='Teste Previsto', color='orange', alpha=0.8)

    plt.axvline(df_val['ds'].iloc[0], color='black', linestyle='--', label='Início Validação')
    plt.axvline(df_test['ds'].iloc[0], color='gray', linestyle='--', label='Início Teste')

    plt.title('Prophet - Previsão com Treino, Validação e Teste (Suavizado)')
    plt.xlabel('Data')
    plt.ylabel('Valor')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return {
        'previsao_val': previsoes_val['yhat'].values,
        'real_val': df_val['y'].values,
        'previsao_test': previsoes_teste['yhat'].values,
        'real_test': df_test['y'].values,
        'horizon': horizon_pred,
        'data_horizon': horizon_date
    }
