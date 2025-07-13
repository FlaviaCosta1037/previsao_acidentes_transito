import pandas as pd
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_error
from src.dividir_modelagem import dividir_modelagem  # ajuste se necessário

def preparar_modelo_arima(df):
    df_com_data = df[df['data_unificada'].notnull()].copy()
    df_com_data['data_unificada'] = pd.to_datetime(df_com_data['data_unificada'])

    serie = df_com_data.groupby('data_unificada').size()
    full_index = pd.date_range(start=serie.index.min(), end=serie.index.max(), freq='D')
    serie = serie.reindex(full_index).fillna(0)

    y_train, y_val, y_test = dividir_modelagem(serie)
    modelo = auto_arima(
        y_train,
        seasonal=True,
        stepwise=True,
        trace=True,
        error_action='ignore',
        suppress_warnings=True
    )

    previsao_val = modelo.predict(n_periods=len(y_val))
    mae_val = mean_absolute_error(y_val, previsao_val)

    modelo.update(y_val)
    previsao_test = modelo.predict(n_periods=len(y_test))
    mae_test = mean_absolute_error(y_test, previsao_test)

    return {
        'modelo': modelo,
        'melhor_ordem': modelo.order,
        'mae_val': mae_val,
        'mae_test': mae_test,
        'previsao_val': previsao_val,
        'previsao_test': previsao_test
    }
