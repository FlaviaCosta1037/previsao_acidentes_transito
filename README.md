# 🚦 **PROJETO DE PREVISÃO DE ACIDENTES DE TRÂNSITO**

> **Versão Atual:** Carga de dados, tratamento, análise exploratória e previsão.

---

## 📝 **Sobre o Projeto**

Este projeto tem como objetivo **carregar, tratar, analisar e prever acidentes de trânsito** utilizando técnicas de **Ciência de Dados** e **Machine Learning**.  
A versão atual contempla as etapas de:  
- **Carga de dados**  
- **Tratamento e limpeza**  
- **Análise exploratória**  
- **Modelagem e previsão**  

---

## 📂 **Estrutura do Projeto**
├── csvs/ # Diretório com arquivos CSV  
│ └── ... # (Dados brutos e tratados)  
│
├── src/ # Código fonte  
│ ├── ajuste.py # Ajustes e pré-processamentos  
│ ├── carga_dados.py # Rotinas de carga de dados  
│ ├── dividir_modelagem.py # Divisão treino/teste e pipelines de modelagem  
│ ├── funcoes_eda.py # Funções para análise exploratória (EDA)  
│ ├── modelos_arima.py # Modelagem ARIMA  
│ ├── modelos_sarima.py # Modelagem SARIMA  
│ ├── modelos_prophet.py # Modelagem Prophet (Facebook)  
│ ├── modelos_sarima_r.py # Modelagem SARIMA com R  
│ └── modelos_svr.py # Modelagem com SVR  
│
├── compilar_base.py # Script para compilar e consolidar dados  
├── main.ipynb # Notebook principal de análise  
└── README.md # Este arquivo  


---

## ⚙️ **Funcionalidades**

### **1. Carga de Dados**  
- Importação e organização de dados históricos de acidentes.

### **2. Tratamento**  
- Limpeza, remoção de outliers e padronização.

### **3. Análise Exploratória (EDA)**  
- Gráficos de dispersão, histogramas, heatmaps e estatísticas descritivas.

### **4. Previsão**  
- Modelagem com **ARIMA, SARIMA, Prophet, SARIMA (R)** e **SVR**.  
- Avaliação com métricas como **MAE, RMSE**.

---

## 🛠 **Tecnologias Utilizadas**

- **Python 3.10+**
- **Bibliotecas principais**:
  - `pandas`
  - `numpy`
  - `matplotlib` / `seaborn`
  - `scikit-learn`
  - `statsmodels`
  - `prophet`
  - `flask` (para API)
  - `joblib`
  - `rpy2` (para integração com R)

---

## 🚀 **Como Executar**

### **1. Clone este repositório**  
```bash
git clone https://github.com/FlaviaCosta1037/previsao_acidentes_transito.git

