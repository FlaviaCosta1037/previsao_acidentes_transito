import firebase_admin
from firebase_admin import credentials, firestore

# Caminho para o arquivo de credenciais
cred = credentials.Certificate("firebase-credenciais.json")
firebase_admin.initialize_app(cred)

# Inicializa o Firestore
db = firestore.client()

