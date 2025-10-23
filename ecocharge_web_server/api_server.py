# File: api_server.py - Server API REST (Punto 3)

import os
import hashlib
from flask import Flask, jsonify, request
from flask_cors import CORS 
import mysql.connector 
from dotenv import load_dotenv 

# Carica le variabili d'ambiente dal file .env (necessario per testare le credenziali DB in sviluppo)
load_dotenv()

# *****************************************************************
# CONFIGURAZIONE FLASK
# *****************************************************************

app = Flask(__name__)
# Abilita CORS per permettere al Web Server (che gira su una porta diversa, 5000)
# di effettuare chiamate a questa API (porta 5001).
CORS(app) 

# *****************************************************************
# FUNZIONE DI CONNESSIONE AIVEN/MYSQL (Struttura)
# *****************************************************************

def get_db_connection():
    """
    Stabilisce e restituisce una connessione al database MySQL ospitato su Aiven.
    I parametri sono letti dalle variabili d'ambiente.
    """
    try:
        # Recupero delle credenziali dalle variabili d'ambiente (Codespaces Secrets o .env)
        conn = mysql.connector.connect(
            host=os.environ.get('mysql-30ced52f-iisgalvanimi-cbb0.g.aivencloud.com'),  # Host Aiven
            port=os.environ.get(14409),      # Porta Aiven 
            user=os.environ.get('avnadmin'),            # Utente fornito da Aiven
            password=os.environ.get('AVNS_ROZR4I-u_7cKxsHOkgF'),    # Password fornita da Aiven
            database=os.environ.get('EcoChargeDB'),        # Nome del database
            
            # Necessario per connessioni sicure (Aiven)
            ssl_ca=os.environ.get('AIVEN_SSL_CA_PATH') 
        )
        return conn
    except mysql.connector.Error as err:
        # Questo errore apparirà finché non collegherai Aiven
        print(f"❌ Errore di connessione al database Aiven: {err}")
        return None

# *****************************************************************
# DATABASE SIMULATO (MOCK DATA)
# Queste variabili saranno usate finché non implementeremo le query SQL reali.
# *****************************************************************

# Simulazione di utenti: usiamo gli hash SHA256 per simulare la sicurezza
ADMIN_PASSWORD_HASH = hashlib.sha256('admin123'.encode()).hexdigest()
USER_PASSWORD_HASH = hashlib.sha256('user123'.encode()).hexdigest()

MOCK_USERS = [
    {'user_id': 1, 'email': 'admin@ecocharge.it', 'password_hash': ADMIN_PASSWORD_HASH, 'nome': 'Amministratore', 'ruolo': 'admin'},
    {'user_id': 2, 'email': 'utente@ecocharge.it', 'password_hash': USER_PASSWORD_HASH, 'nome': 'Mario Rossi', 'ruolo': 'user'}
]

# Simulazione delle colonnine (struttura definita nel Modello Logico)
MOCK_STATIONS = [
    {'colonnina_id': 1, 'indirizzo': "Via Roma 1", 'latitudine': 45.4678, 'longitudine': 9.1901, 'potenza_kw': 22, 'nil_quartiere': "NIL 1", 'stato': 'libera'},
    {'colonnina_id': 2, 'indirizzo': "Piazza Duomo 10", 'latitudine': 45.4645, 'longitudine': 9.1895, 'potenza_kw': 50, 'nil_quartiere': "NIL 1", 'stato': 'occupata'},
    {'colonnina_id': 3, 'indirizzo': "Viale Monza 50", 'latitudine': 45.5000, 'longitudine': 9.2250, 'potenza_kw': 11, 'nil_quartiere': "NIL 2", 'stato': 'libera'}
]

# *****************************************************************
# ROTTE API (Punto 3)
# *****************************************************************

@app.route('/api/v1/login', methods=['POST'])
def api_login():
    """Endpoint REST per l'autenticazione (Punto 4)."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    password_hash_input = hashlib.sha256(password.encode()).hexdigest()

    # LOGICA MOCK: Cerca l'utente nel DB simulato
    user = next((u for u in MOCK_USERS if u['email'] == email), None)

    if user and user['password_hash'] == password_hash_input:
        # Successo: restituisce solo i dati necessari alla sessione
        return jsonify({
            'user_id': user['user_id'],
            'email': user['email'],
            'nome': user['nome'],
            'role': user['ruolo']
        }), 200
    else:
        # Fallimento
        return jsonify({'message': 'Credenziali non valide'}), 401


@app.route('/api/v1/stations', methods=['GET'])
def api_get_stations():
    """Endpoint REST per ottenere tutte le colonnine (Punto 2)."""
    # LOGICA MOCK: Restituisce i dati simulati
    return jsonify(MOCK_STATIONS), 200


@app.route('/api/v1/stations/<int:station_id>/reserve', methods=['POST'])
def api_reserve_station(station_id):
    """Endpoint REST per la prenotazione (Punto 2/3)."""
    data = request.get_json()
    user_id = data.get('user_id')
    
    # LOGICA MOCK: trova la colonnina e aggiorna lo stato nella lista MOCK
    station = next((s for s in MOCK_STATIONS if s['colonnina_id'] == station_id), None)
    
    if station and station['stato'] == 'libera':
        # Simula l'aggiornamento
        station['stato'] = 'occupata'
        
        # Simula l'inserimento nella tabella 'ricariche'
        print(f"Simulazione: Utente {user_id} ha prenotato Colonnina ID {station_id}")
        
        return jsonify({'message': f'Colonnina ID {station_id} prenotata da Utente {user_id}. Stato aggiornato a occupata.'}), 200
    
    return jsonify({'message': 'Colonnina non trovata o non disponibile.'}), 400


# *****************************************************************
# ESECUZIONE DEL SERVER
# *****************************************************************

if __name__ == '__main__':
    # Usiamo la porta 5001 per il Server API
    print("API Server avviato sulla porta 5001. Attenzione: usa i dati MOCK finché non è collegato ad Aiven.")
    app.run(debug=True, port=5001)