from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_error

def modelar_arima_automatico(y_train, y_test):
    modelo = auto_arima(
        y_train,
        seasonal=False,
        stepwise=True,
        trace=True,
        error_action='ignore',
        suppress_warnings=True
    )

    # Previsão validação
    # previsao_val = modelo.predict(n_periods=len(y_val))
    # mae_val = mean_absolute_error(y_val, previsao_val)

    # # Atualiza com validação e prevê teste
    # modelo.update(y_val)
    
    previsao_test = modelo.predict(n_periods=len(y_test))
    mae_test = mean_absolute_error(y_test, previsao_test)

    return {
        'modelo': modelo,
        'melhor_ordem': modelo.order,
        # 'mae_val': mae_val,
        'mae_test': mae_test,
        # 'previsao_val': previsao_val,
        'previsao_test': previsao_test
    }
