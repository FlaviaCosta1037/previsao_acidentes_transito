import pandas as pd

def classificar_turno(hora):
    if pd.isna(hora): return 'Indefinido'
    if 5 <= hora < 12: return 'Manhã'
    elif 12 <= hora < 17: return 'Tarde'
    elif 17 <= hora < 21: return 'Noite'
    else: return 'Madrugada'