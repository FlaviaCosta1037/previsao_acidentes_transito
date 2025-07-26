import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    if not np.any(mask):
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def testar_estacionariedade(y):
    resultado_adf = adfuller(y.dropna())
    estatistica = resultado_adf[0]
    p_valor = resultado_adf[1]
    print(f"ADF Statistic: {estatistica:.4f}")
    print(f"p-valor: {p_valor:.4f}")
    return p_valor < 0.05

def modelar_sarima_automatico(y_train, y_val, y_test, m):
    # Normalização
    scaler = MinMaxScaler()
    y_train_scaled = scaler.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    y_val_scaled = scaler.transform(y_val.values.reshape(-1, 1)).flatten()
    y_test_scaled = scaler.transform(y_test.values.reshape(-1, 1)).flatten()

    # ADF
    print("Teste ADF em y_train:")
    if not testar_estacionariedade(pd.Series(y_train_scaled, index=y_train.index)):
        print("⚠️ Série não estacionária. O auto_arima tentará identificar d e D automaticamente.")

    modelo = auto_arima(
        y_train_scaled,
        seasonal=True,
        m=m,
        stepwise=True,
        trace=True,
        error_action='ignore',
        suppress_warnings=True,
        max_p=3, max_q=3,
        max_P=2, max_Q=2,
        max_order=10,
        d=None, D=None
    )

    # Previsão para validação
    previsao_val_scaled = modelo.predict(n_periods=len(y_val_scaled))
    previsao_val = scaler.inverse_transform(previsao_val_scaled.reshape(-1, 1)).flatten()
    mae_val = mean_absolute_error(y_val, previsao_val)
    rmse_val = mean_squared_error(y_val, previsao_val, squared=False)
    mape_val = mean_absolute_percentage_error(y_val, previsao_val)

    # Atualiza com y_val e prevê teste
    modelo.update(y_val_scaled)
    previsao_test_scaled = modelo.predict(n_periods=len(y_test_scaled))
    previsao_test = scaler.inverse_transform(previsao_test_scaled.reshape(-1, 1)).flatten()
    mae_test = mean_absolute_error(y_test, previsao_test)
    rmse_test = mean_squared_error(y_test, previsao_test, squared=False)
    mape_test = mean_absolute_percentage_error(y_test, previsao_test)

    # PLOTS
    plt.figure(figsize=(12, 4))
    plt.plot(y_val.index, y_val, label='Real')
    plt.plot(y_val.index, previsao_val, label='Previsão', color='orange')
    plt.title('Validação - Real vs Previsão')
    plt.xlabel('Data')
    plt.ylabel('Valor')
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 4))
    plt.plot(y_test.index, y_test, label='Real')
    plt.plot(y_test.index, previsao_test, label='Previsão', color='orange')
    plt.title('Teste - Real vs Previsão')
    plt.xlabel('Data')
    plt.ylabel('Valor')
    plt.legend()
    plt.tight_layout()
    plt.show()

    residuos = pd.Series(y_test.values - previsao_test, index=y_test.index)

    plt.figure(figsize=(12, 4))
    plt.plot(residuos.index, residuos)
    plt.title('Resíduos no Teste')
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel('Data')
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(6, 4))
    sns.histplot(residuos, kde=True, bins=30)
    plt.title('Distribuição dos Resíduos')
    plt.tight_layout()
    plt.show()

    sm.qqplot(residuos, line='s')
    plt.title('QQ-Plot dos Resíduos')
    plt.tight_layout()
    plt.show()

    return {
        'modelo': modelo,
        'melhor_ordem': modelo.order,
        'melhor_ordem_sazonal': modelo.seasonal_order,
        'aic': modelo.aic(),
        'mae_val': mae_val,
        'rmse_val': rmse_val,
        'mape_val': mape_val,
        'mae_test': mae_test,
        'rmse_test': rmse_test,
        'mape_test': mape_test,
        'previsao_val': previsao_val,
        'previsao_test': previsao_test
    }

def modelar_sarima_manual(y_train, y_val, y_test, order, seasonal_order):
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    # Normalização
    scaler = MinMaxScaler()
    y_train_scaled = scaler.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    y_val_scaled = scaler.transform(y_val.values.reshape(-1, 1)).flatten()
    y_test_scaled = scaler.transform(y_test.values.reshape(-1, 1)).flatten()

    # Ajustar modelo SARIMA manualmente
    modelo = SARIMAX(y_train_scaled, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
    resultado = modelo.fit(disp=False)

    # Previsão na validação
    previsao_val_scaled = resultado.get_forecast(steps=len(y_val)).predicted_mean
    previsao_val = scaler.inverse_transform(previsao_val_scaled.reshape(-1, 1)).flatten()
    mae_val = mean_absolute_error(y_val, previsao_val)
    rmse_val = mean_squared_error(y_val, previsao_val, squared=False)
    mape_val = mean_absolute_percentage_error(y_val, previsao_val)

    # Reajustar com validação + treino
    full_train_scaled = np.concatenate([y_train_scaled, y_val_scaled])
    modelo = SARIMAX(full_train_scaled, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
    resultado_full = modelo.fit(disp=False)
    
    previsao_test_scaled = resultado_full.get_forecast(steps=len(y_test)).predicted_mean
    previsao_test = scaler.inverse_transform(previsao_test_scaled.reshape(-1, 1)).flatten()
    mae_test = mean_absolute_error(y_test, previsao_test)
    rmse_test = mean_squared_error(y_test, previsao_test, squared=False)
    mape_test = mean_absolute_percentage_error(y_test, previsao_test)

    # PLOTS
    plt.figure(figsize=(12, 4))
    plt.plot(y_val.index, y_val, label='Real')
    plt.plot(y_val.index, previsao_val, label='Previsão', color='orange')
    plt.title('Validação - Real vs Previsão (Manual)')
    plt.xlabel('Data')
    plt.ylabel('Valor')
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 4))
    plt.plot(y_test.index, y_test, label='Real')
    plt.plot(y_test.index, previsao_test, label='Previsão', color='orange')
    plt.title('Teste - Real vs Previsão (Manual)')
    plt.xlabel('Data')
    plt.ylabel('Valor')
    plt.legend()
    plt.tight_layout()
    plt.show()

    residuos = pd.Series(y_test.values - previsao_test, index=y_test.index)

    plt.figure(figsize=(12, 4))
    plt.plot(residuos.index, residuos)
    plt.title('Resíduos no Teste (Manual)')
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel('Data')
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(6, 4))
    sns.histplot(residuos, kde=True, bins=30)
    plt.title('Distribuição dos Resíduos (Manual)')
    plt.tight_layout()
    plt.show()

    sm.qqplot(residuos, line='s')
    plt.title('QQ-Plot dos Resíduos (Manual)')
    plt.tight_layout()
    plt.show()

    return {
        'modelo': resultado_full,
        'mae_val': mae_val,
        'rmse_val': rmse_val,
        'mape_val': mape_val,
        'mae_test': mae_test,
        'rmse_test': rmse_test,
        'mape_test': mape_test,
        'previsao_val': previsao_val,
        'previsao_test': previsao_test
    }
