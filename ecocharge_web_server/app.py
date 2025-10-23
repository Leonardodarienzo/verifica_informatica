# File: app.py - Server Web (Punto 2 & 4)

from flask import Flask, render_template, redirect, url_for, session, request, flash 
from functools import wraps 
import requests # Necessario per chiamare il Server API (Punto 3)

# *****************************************************************
# CONFIGURAZIONE
# *****************************************************************

app = Flask(__name__) # <--- QUESTO DEFINISCE L'OGGETTO 'app'
# La SECRET_KEY è essenziale per la gestione delle sessioni.
app.config['SECRET_KEY'] = 'la_tua_chiave_segreta_molto_lunga_e_complessa_ecocharge' 

# L'URL base del Server API (Punto 3).
API_SERVER_URL = "http://127.0.0.1:5001" 

# *****************************************************************
# DECORATORI PER LA PROTEZIONE DELLE ROTTE (Punto 4)
# *****************************************************************

def login_required(f):
    """Decorator che richiede che l'utente sia loggato."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Devi effettuare il login per accedere a questa pagina.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator che richiede che l'utente sia un amministratore."""
    @wraps(f)
    @login_required 
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Accesso negato. Solo gli amministratori possono accedere.', 'danger')
            return redirect(url_for('index')) 
        return f(*args, **kwargs)
    return decorated_function

# *****************************************************************
# ROTTE PUBBLICHE
# *****************************************************************

@app.route('/')
def index():
    """Pagina iniziale. Reindirizza gli utenti loggati in base al ruolo."""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_map'))
            
    return render_template('index.html', title='Benvenuto')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Gestisce il login, chiamando il Server API (Punto 3)."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # === CHIAMATA AL SERVER API PER L'AUTENTICAZIONE ===
        login_url = f"{API_SERVER_URL}/api/v1/login"
        
        try:
            # Invio delle credenziali all'API
            api_response = requests.post(
                login_url, 
                json={'email': email, 'password': password},
                timeout=5 
            )
        except requests.exceptions.ConnectionError:
            flash('Errore di connessione: il Server API non è disponibile (porta 5001).', 'danger')
            return render_template('login.html', title='Login')
        except requests.exceptions.Timeout:
            flash('Errore: la chiamata al Server API è scaduta.', 'danger')
            return render_template('login.html', title='Login')
        except Exception as e:
            flash(f'Si è verificato un errore inaspettato durante il login: {e}', 'danger')
            return render_template('login.html', title='Login')

        # Gestione della risposta API
        if api_response.status_code == 401:
            flash('Credenziali non valide.', 'danger')
            return render_template('login.html', title='Login')
        
        elif api_response.status_code == 200:
            user_data = api_response.json()
            
            # Setta la sessione con i dati ricevuti dall'API
            session['user_id'] = user_data['user_id']
            session['user_email'] = user_data['email']
            session['role'] = user_data['role']
            session['user_name'] = user_data['nome'] 
            
            flash(f'Benvenuto, {user_data["nome"]}!', 'success')
            return redirect(url_for('index'))

        else:
            flash(f'Errore sconosciuto dal Server API (Codice: {api_response.status_code}).', 'danger')
            return render_template('login.html', title='Login')

    return render_template('login.html', title='Login')


@app.route('/logout')
def logout():
    """Gestisce il logout e termina la sessione (Punto 4)."""
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('role', None)
    session.pop('user_name', None)
    flash('Hai effettuato il logout.', 'info')
    return redirect(url_for('index'))

# *****************************************************************
# ROTTE RISERVATE (Punto 2 & 4)
# *****************************************************************

@app.route('/user/map')
@login_required 
def user_map():
    """Visualizza la mappa delle colonnine (Punto 2)."""
    # Passiamo l'URL dell'API al template per il codice JavaScript.
    return render_template('user_map.html', title='Mappa Colonnine', API_SERVER_URL=API_SERVER_URL)

@app.route('/admin/dashboard')
@admin_required 
def admin_dashboard():
    """Pannello di controllo per l'amministratore (Punto 2)."""
    return render_template('admin_dashboard.html', title='Pannello Admin')

# *****************************************************************
# ESECUZIONE DEL SERVER
# *****************************************************************

if __name__ == '__main__':
    # Usiamo la porta 5000 per il Web Server
    app.run(debug=True, port=5000)