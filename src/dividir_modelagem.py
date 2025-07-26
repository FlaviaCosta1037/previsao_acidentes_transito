def dividir_modelagem(serie, proporcao_treino=0.6, proporcao_val=0.2):
    """
    Divide uma série temporal em treino, validação e teste.
    
    Parâmetros:
    - serie: pandas Series com índice temporal (DatetimeIndex).
    - proporcao_treino: proporção para treino (padrão 0.6).
    - proporcao_val: proporção para validação (padrão 0.2).

    Retorna:
    - y_train, y_val, y_test
    """
    n = len(serie)
    train_size = int(n * proporcao_treino)
    val_size = int(n * proporcao_val)

    y_train = serie.iloc[:train_size].copy()
    y_val = serie.iloc[train_size:train_size + val_size].copy()
    y_test = serie.iloc[train_size + val_size:].copy()

    print(f"Tamanho Treino: {len(y_train)}, Validação: {len(y_val)}, Teste: {len(y_test)}")

    return y_train, y_val, y_test

def dividir_modelagem_2(serie, proporcao_treino=0.7):
    n = len(serie)
    train_size = int(n * proporcao_treino)

    y_train = serie.iloc[:train_size].copy()
    y_test = serie.iloc[train_size:].copy()

    print(f"Tamanho Treino: {len(y_train)}, Teste: {len(y_test)}")

    return y_train, y_test