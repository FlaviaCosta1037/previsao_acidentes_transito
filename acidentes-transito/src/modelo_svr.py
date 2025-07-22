import numpy as np
import pandas as pd
from sklearn.svm import SVR 
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

def modelar_svr(serie_data):
    
    serie_data = serie_data.fillna(0)

        # --- validação inicial da série ---
    if np.isnan(serie_data.values).any():
        raise ValueError("A série original contém valores NaN. Limpe os dados antes de rodar o modelo.")

    # parâmetros
    trainSplit = 0.6
    validSplit = 0.2

    dataset = serie_data.values
    print(f"Tamanho do dataset original: {len(dataset)}")

    trainSize = int(np.floor(trainSplit * len(dataset)))
    validSize = int(np.floor(validSplit * len(dataset)))

    maxData = np.max(dataset)
    minData = np.min(dataset)

    ndataset = (dataset - minData) / (maxData - minData)
    datasetSeries = pd.Series(ndataset)

    dimension = 6
    stepahead = 6         # <-- aqui você define quantos passos quer prever
    stepahead_max = 12    # <-- fixo para manter coerência nas previsões

    # Criação do dataset deslocado com base em stepahead_max
    datasetShifted = pd.concat([datasetSeries.shift(i) for i in range(dimension + stepahead_max)], axis=1)
    print(f"Tamanho do datasetShifted (antes de dropar NaNs): {datasetShifted.shape}")
    print(datasetShifted.head(25))

    # Entrada (lags)
    Input = datasetShifted.iloc[dimension + (stepahead_max - 1):, -dimension:]
    print(f"Tamanho do Input (após slice): {Input.shape}")

    # listas para armazenar
    previsoes = []
    reais = []

    for i in range(stepahead):
        # Target deslocado i passos à frente (baseado em stepahead_max)
        Target = datasetShifted.iloc[dimension + (stepahead_max - 1):, -(dimension + i + 1)]

        # concatena Input + Target e remove NaNs apenas nessa fatia
        df_temp = pd.concat([Input, Target], axis=1).dropna()
        if df_temp.empty:
            raise ValueError(f"Após remover NaNs, não restaram dados suficientes para o passo {i+1}.")

        X = df_temp.iloc[:, :-1]
        y = df_temp.iloc[:, -1]

        mySVR = SVR(C=1000.0, epsilon=0.001, gamma=3.2)
        mySVR.fit(X, y)

        # prevê usando a última linha **original** de Input
        last_instance = Input.iloc[-1, :].values.reshape(1, -1)
        previsao_norm = mySVR.predict(last_instance)[0]

        # dessinaliza
        previsao_real = previsao_norm * (maxData - minData) + minData
        valor_real = y.iloc[-1] * (maxData - minData) + minData

        print(f"Previsão passo {i+1}: {int(round(previsao_real))}")

        previsoes.append(previsao_real)
        reais.append(valor_real)

    # métricas
    mae = mean_absolute_error(reais, previsoes)
    mse_ = mean_squared_error(reais, previsoes)
    rmse = np.sqrt(mse_)

    def safe_mape(y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        mask = y_true != 0
        if not mask.any():
            return np.nan
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

    mape = safe_mape(reais, previsoes)

    return {
        'mae': mae,
        'mse': mse_,
        'rmse': rmse,
        'mape': mape,
        'previsao': previsoes
    }
