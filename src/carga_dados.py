import pandas as pd
import os

def carregar_dados():
    pasta = 'csvs/'
    arquivos_csv = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.csv')]

    dfs = []
    for arquivo in arquivos_csv:
        try:
            df_temp = pd.read_csv(arquivo, encoding='latin1',sep=';')
            dfs.append(df_temp)
            print(f'✅ Lido: {arquivo}')
        except Exception as e:
            print(f'❌ Erro ao ler {arquivo}: {e}')

    # Junta todos os dataframes válidos
    df = pd.concat(dfs, ignore_index=True)
    print(f'\nTotal de arquivos lidos com sucesso: {len(dfs)}')
    print(f'Total de registros: {df.shape[0]}')
    
    return df