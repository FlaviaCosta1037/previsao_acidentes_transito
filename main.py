import pandas as pd
import warnings

from src.utils import tratamento
warnings.filterwarnings('ignore')

base = 'dataset/base.csv'
df = pd.read_csv(base, encoding='latin1')
print(df.shape)
print(df.columns)
tratamento(df)
print(df.columns)

print(df.info())

df['vitimas'] = pd.to_numeric(df['vitimas'], errors='coerce').astype('Int64')
df['vitimasfatais'] = pd.to_numeric(df['vitimasfatais'], errors='coerce').astype('Int64')

verificar_nulos_vf = df['vitimasfatais'].isnull().sum()
verificar_nulos_vnf = df['vitimas'].isnull().sum()
soma_vitimas_fatais = df['vitimasfatais'].sum()
soma_vitimas_nf = df['vitimas'].sum()

print("Quantidade de nulos em vitimas vatais: ", verificar_nulos_vf)
print("Quantidade de nulos em vitimas não fatais", verificar_nulos_vnf)
print('Total de vitimas fatais: ', soma_vitimas_fatais)
print("Total de vitimas não fatais: ", soma_vitimas_nf)