import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def classificar_turno(hora):
    try:
        hora = int(hora)
        if 0 <= hora < 6:
            return 'Madrugada'
        elif 6 <= hora < 12:
            return 'Manhã'
        elif 12 <= hora < 18:
            return 'Tarde'
        elif 18 <= hora < 24:
            return 'Noite'
        else:
            return 'Indefinido'
    except:
        return 'Indefinido'

def limpar_descricao(texto):
    texto = texto.lower()
    texto = re.sub(r'[^a-záàâãéèêíïóôõöúçñ\s]', '', texto)
    palavras = word_tokenize(texto, language='portuguese')
    stop_words = set(stopwords.words('portuguese'))
    palavras_filtradas = [p for p in palavras if p not in stop_words]
    return ' '.join(palavras_filtradas)

def extrair_hora(valor):
    try:
        if isinstance(valor, str) and ':' in valor:
            return int(valor.split(':')[0])
        return int(valor)
    except:
        return None
